import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from src.core.security import (
    create_access_token,
    hash_password,
    hash_token,
    verify_password,
)
from src.core.settings import settings
from src.models.auth import RefreshToken, TokenType, VerificationToken
from src.models.user import User
from src.schemas.user import UserCreate
from src.services.email import EmailService
from src.services.user import UserServices


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserServices(session=session)
        self.email_service = EmailService()

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    async def register(self, new_user: UserCreate) -> User:
        existing_user = await self.user_service.get_by_email(new_user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered!",
            )

        user = await self.user_service.create(new_user)
        token = await self._create_verification_token(user.id, TokenType.EMAIL_VERIFY)
        await self.session.commit()
        await self.email_service.send_verification_email(
            email=user.email,
            token=token,
        )
        return user

    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self.user_service.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account"
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=403,
                detail="Please verify your email",
            )
        access_token = create_access_token(str(user.id), user.email)
        refresh_token = await self._issue_refresh_tokens(user.id)
        await self.session.commit()
        return access_token, refresh_token

    async def logout(self, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token)
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.exec(statement)
        db_token = result.first()
        if not db_token is None:
            db_token.revoked_at = self._utc_now()
            await self.session.commit()

    async def refresh_session(self, refresh_token: str) -> tuple[str, str]:
        token_hash = hash_token(refresh_token)

        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await self.session.exec(statement)
        db_token = result.first()

        if db_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expire refresh token",
            )

        if db_token.revoked_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expire refresh token",
            )
        now = self._utc_now()
        if db_token.expires_at < now:
            await self.session.delete(db_token)
            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expire refresh token",
            )

        user = await self.user_service.get_by_id(db_token.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

        if not user.is_active:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        db_token.revoked_at = now
        self.session.add(db_token)

        new_access_token = create_access_token(str(user.id), email=user.email)
        new_refresh_token = await self._issue_refresh_tokens(user.id)
        await self.session.commit()
        return new_access_token, new_refresh_token

    async def verify_email(self, token_str: str) -> None:

        token_ob = await self._get_verification_token(token_str, TokenType.EMAIL_VERIFY)

        if not token_ob or token_ob.expires_at < self._utc_now():
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid or expired validation token",
            )

        user = await self.user_service.get_by_id(token_ob.user_id)
        if not user:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="User not found"
            )
        if user.is_verified:
            return

        user.is_verified = True
        await self.session.delete(token_ob)
        self.session.add(user)
        await self.session.commit()

    async def resend_verification_email(self, email: str) -> None:
        user = await self.user_service.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified"
            )

        new_verification_token = await self._create_verification_token(
            user.id, TokenType.EMAIL_VERIFY
        )
        await self.session.commit()
        await self.email_service.send_verification_email(
            email=user.email,
            token=new_verification_token,
        )

    async def forgot_password(self, email: str) -> None:
        user = await self.user_service.get_by_email(email)
        if user is None:
            return

        reset_token = await self._create_verification_token(
            user.id, TokenType.PASSWORD_RESET
        )
        await self.session.commit()
        await self.email_service.send_reset_password(
            email=user.email,
            token=reset_token,
        )

    async def reset_password(self, token: str, new_password: str) -> None:

        token_ob = await self._get_verification_token(token, TokenType.PASSWORD_RESET)
        if token_ob is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        now = self._utc_now()
        if token_ob.expires_at < now:
            await self.session.delete(token_ob)

            await self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired"
            )
        user = await self.user_service.get_by_id(token_ob.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.password_hash = hash_password(new_password)
        self.session.add(user)

        await self._revoke_all_refresh_tokens(user.id)

        await self.session.delete(token_ob)
        await self.session.commit()

    async def logout_all_devices(self, user_id: uuid.UUID) -> None:
        user = await self.user_service.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self._revoke_all_refresh_tokens(user_id)
        await self.session.commit()

    async def _get_verification_token(
        self,
        token: str,
        token_type: TokenType,
    ) -> VerificationToken | None:
        token_hash = hash_token(token)

        statement = select(VerificationToken).where(
            VerificationToken.token_hash == token_hash,
            VerificationToken.type == token_type,
        )

        result = await self.session.exec(statement)
        return result.first()

    async def _revoke_all_refresh_tokens(
        self,
        user_id: uuid.UUID,
    ) -> None:
        result = await self.session.exec(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at == None,
            )
        )

        now = self._utc_now()

        for token in result.all():
            token.revoked_at = now

    async def _delete_verification_tokens(
        self,
        user_id: uuid.UUID,
        token_type: TokenType,
    ) -> None:
        result = await self.session.exec(
            select(VerificationToken).where(
                VerificationToken.user_id == user_id,
                VerificationToken.type == token_type,
            )
        )

        for token in result.all():
            await self.session.delete(token)

    async def _issue_refresh_tokens(self, user_id: uuid.UUID) -> str:
        token_str = secrets.token_urlsafe(32)
        token_hash = hash_token(token_str)
        expires_at = self._utc_now() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        refresh_token = RefreshToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        self.session.add(refresh_token)
        return token_str

    async def _create_verification_token(
        self, user_id: uuid.UUID, token_type: TokenType
    ) -> str:
        token_str = secrets.token_urlsafe(32)
        token_hash = hash_token(token_str)
        expires_at = self._utc_now() + timedelta(
            hours=settings.VERIFY_REFRESH_TOKEN_EXPIRE_HR
        )

        verification_token = VerificationToken(
            user_id=user_id,
            type=token_type,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self._delete_verification_tokens(user_id, token_type)
        self.session.add(verification_token)
        return token_str
