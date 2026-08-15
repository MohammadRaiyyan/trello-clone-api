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
from src.services.invitation import InvitationService
from src.services.user import UserServices

user_service = UserServices()
email_service = EmailService()
invitation_service = InvitationService()


class AuthService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    async def register(
        self,
        new_user: UserCreate,
        session: AsyncSession,
    ) -> User:

        existing_user = await user_service.get_by_email(
            new_user.email,
            session,
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered!",
            )

        user = await user_service.create(
            new_user,
            session,
        )

        # Flush so user.id is guaranteed to be available
        # before creating OrganizationMember.
        await session.flush()

        if new_user.invitation_token:
            await invitation_service.accept_during_registration(
                invitation_token=new_user.invitation_token,
                user=user,
                session=session,
            )

        verification_token = await self._create_verification_token(
            user.id,
            TokenType.EMAIL_VERIFY,
            session,
        )

        await session.commit()

        try:
            await email_service.send_verification_email(
                email=user.email,
                token=verification_token,
            )
        except Exception:
            pass

        return user

    async def login(
        self, email: str, password: str, session: AsyncSession
    ) -> tuple[str, str]:
        user = await user_service.get_by_email(email, session)

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
        refresh_token = await self._issue_refresh_tokens(user.id, session)
        await session.commit()
        return access_token, refresh_token

    async def logout(self, refresh_token: str, session: AsyncSession) -> None:
        token_hash = hash_token(refresh_token)
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await session.exec(statement)
        db_token = result.first()
        if not db_token is None:
            db_token.revoked_at = self._utc_now()
            await session.commit()

    async def refresh_session(
        self, refresh_token: str, session: AsyncSession
    ) -> tuple[str, str]:
        token_hash = hash_token(refresh_token)

        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        result = await session.exec(statement)
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
            await session.delete(db_token)
            await session.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expire refresh token",
            )

        user = await user_service.get_by_id(db_token.user_id, session)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

        if not user.is_active:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        db_token.revoked_at = now
        session.add(db_token)

        new_access_token = create_access_token(str(user.id), email=user.email)
        new_refresh_token = await self._issue_refresh_tokens(user.id, session)
        await session.commit()
        return new_access_token, new_refresh_token

    async def verify_email(
        self, token_str: str, session: AsyncSession
    ) -> tuple[str, str]:

        token_ob = await self._get_verification_token(
            token_str, TokenType.EMAIL_VERIFY, session
        )

        if not token_ob or token_ob.expires_at < self._utc_now():
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid or expired validation token",
            )

        user = await user_service.get_by_id(token_ob.user_id, session)
        if not user:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="User not found"
            )

        user.is_verified = True
        await session.delete(token_ob)
        session.add(user)
        new_access_token = create_access_token(str(user.id), email=user.email)
        new_refresh_token = await self._issue_refresh_tokens(user.id, session)
        await session.commit()
        return new_access_token, new_refresh_token

    async def resend_verification_email(
        self, email: str, session: AsyncSession
    ) -> None:
        user = await user_service.get_by_email(email, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified"
            )

        new_verification_token = await self._create_verification_token(
            user.id, TokenType.EMAIL_VERIFY, session
        )
        await session.commit()
        await email_service.send_verification_email(
            email=user.email,
            token=new_verification_token,
        )

    async def forgot_password(self, email: str, session: AsyncSession) -> None:
        user = await user_service.get_by_email(email, session)
        if user is None:
            return

        reset_token = await self._create_verification_token(
            user.id, TokenType.PASSWORD_RESET, session
        )
        await session.commit()
        await email_service.send_reset_password(
            email=user.email,
            token=reset_token,
        )

    async def reset_password(
        self, token: str, new_password: str, session: AsyncSession
    ) -> None:

        token_ob = await self._get_verification_token(
            token, TokenType.PASSWORD_RESET, session
        )
        if token_ob is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        now = self._utc_now()
        if token_ob.expires_at < now:
            await session.delete(token_ob)

            await session.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired"
            )
        user = await user_service.get_by_id(token_ob.user_id, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.password_hash = hash_password(new_password)
        session.add(user)

        await self._revoke_all_refresh_tokens(user.id, session)

        await session.delete(token_ob)
        await session.commit()

    async def logout_all_devices(
        self, user_id: uuid.UUID, session: AsyncSession
    ) -> None:
        user = await user_service.get_by_id(user_id, session=session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        await self._revoke_all_refresh_tokens(user_id, session)
        await session.commit()

    async def _get_verification_token(
        self, token: str, token_type: TokenType, session: AsyncSession
    ) -> VerificationToken | None:
        token_hash = hash_token(token)

        statement = select(VerificationToken).where(
            VerificationToken.token_hash == token_hash,
            VerificationToken.type == token_type,
        )

        result = await session.exec(statement)
        return result.first()

    async def _revoke_all_refresh_tokens(
        self, user_id: uuid.UUID, session: AsyncSession
    ) -> None:
        result = await session.exec(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at == None,
            )
        )

        now = self._utc_now()

        for token in result.all():
            token.revoked_at = now

    async def _delete_verification_tokens(
        self, user_id: uuid.UUID, token_type: TokenType, session: AsyncSession
    ) -> None:
        result = await session.exec(
            select(VerificationToken).where(
                VerificationToken.user_id == user_id,
                VerificationToken.type == token_type,
            )
        )

        for token in result.all():
            await session.delete(token)

    async def _issue_refresh_tokens(
        self, user_id: uuid.UUID, session: AsyncSession
    ) -> str:
        token_str = secrets.token_urlsafe(32)
        token_hash = hash_token(token_str)
        expires_at = self._utc_now() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        refresh_token = RefreshToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        session.add(refresh_token)
        return token_str

    async def _create_verification_token(
        self, user_id: uuid.UUID, token_type: TokenType, session: AsyncSession
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
        await self._delete_verification_tokens(user_id, token_type, session)
        session.add(verification_token)
        return token_str
