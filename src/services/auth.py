import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from src.core.security import create_access_token, verify_password
from src.core.settings import settings
from src.models.auth import RefreshToken, TokenType, VerificationToken
from src.models.user import User
from src.schemas.user import UserCreate
from src.services.user import UserServices


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserServices(session=session)

    async def register(self, new_user: UserCreate) -> User:
        existing_user = await self.user_service.get_by_email(new_user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered!",
            )

        user = await self.user_service.create(new_user)
        await self.create_verification_token(user.id, TokenType.EMAIL_VERIFY)
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.user_service.get_by_email(email)

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account"
            )
        return user

    async def create_refresh_token(self, user_id: uuid.UUID) -> str:
        token_str = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        refresh_token = RefreshToken(
            user_id=user_id, token_hash=token_str, expires_at=expires_at
        )
        self.session.add(refresh_token)
        await self.session.commit()
        return token_str

    async def rotate_refresh_token(self, old_token_str: str) -> tuple[str, str]:
        statement = select(RefreshToken).where(RefreshToken.token_hash == old_token_str)
        result = await self.session.exec(statement)
        db_token = result.first()

        if (
            not db_token
            or db_token.revoked_at
            or db_token.expires_at < datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expire refresh token",
            )

        db_token.revoked_at = datetime.now(timezone.utc)
        self.session.add(db_token)
        user = await self.user_service.get_by_id(db_token.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
        new_access_token = create_access_token(str(user.id), email=user.email)
        new_refresh_token = await self.create_refresh_token(user.id)

        return new_access_token, new_refresh_token

    async def create_verification_token(
        self, user_id: uuid.UUID, token_type: TokenType
    ) -> str:
        token_str = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.VERIFY_REFRESH_TOKEN_EXPIRE_HR
        )

        verification_token = VerificationToken(
            user_id=user_id,
            type=token_type,
            token_hash=token_str,
            expires_at=expires_at,
        )
        self.session.add(verification_token)
        await self.session.commit()
        return token_str

    async def verify_email(self, token_str: str) -> bool:
        statement = select(VerificationToken).where(
            VerificationToken.token_hash == token_str,
            VerificationToken.type == TokenType.EMAIL_VERIFY,
        )
        result = await self.session.exec(statement)
        token_ob = result.first()

        if not token_ob or token_ob.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid or expired validation token",
            )

        user = await self.user_service.get_by_id(token_ob.user_id)
        if not user:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="User not found"
            )
        user.is_verified = True
        await self.session.delete(token_ob)
        self.session.add(user)
        await self.session.commit()
        return True
