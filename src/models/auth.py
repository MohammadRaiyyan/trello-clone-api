import datetime
import uuid
from enum import Enum

from sqlmodel import AutoString, Field, SQLModel

from src.models.base import BaseUUIModel, TimeStampMixin


class RefreshToken(BaseUUIModel, TimeStampMixin, SQLModel, table=True):
    __tablename__ = "refresh_tokens"  # pyright: ignore[reportAssignmentType]

    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    token_hash: str = Field(nullable=False)
    expires_at: datetime.datetime = Field(nullable=False)
    revoked_at: datetime.datetime = Field(nullable=True, default=None)


class TokenType(str, Enum):
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"


class VerificationToken(BaseUUIModel, TimeStampMixin, SQLModel, table=True):
    __tablename__ = "verification_tokens"  # pyright: ignore[reportAssignmentType]
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    token_hash: str = Field(nullable=False)
    type: TokenType = Field(sa_type=AutoString, nullable=False, index=True)
    expires_at: datetime.datetime = Field(nullable=False)
    used_at: datetime.datetime = Field(nullable=True, default=None)
