import datetime
import uuid
from enum import Enum

from sqlmodel import AutoString, Field, SQLModel


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID = Field(
        primary_key=True, default_factory=uuid.uuid4, index=True, nullable=False
    )
    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    token_hash: str = Field(nullable=False)
    expires_at: datetime.datetime = Field(nullable=False)
    revoked_at: datetime.datetime = Field(nullable=True, default=None)
    created_at: datetime.datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
    )


class TokenType(str, Enum):
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"


class VerificationToken(SQLModel, table=True):
    __tablename__ = "verification_tokens"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID = Field(
        primary_key=True, default_factory=uuid.uuid4, index=True, nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    token_hash: str = Field(nullable=False)
    type: TokenType = Field(sa_type=AutoString, nullable=False, index=True)
    expires_at: datetime.datetime = Field(nullable=False)
    used_at: datetime.datetime = Field(nullable=True, default=None)
    created_at: datetime.datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
