import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlmodel import AutoString, Field

from src.models.base import BaseUUIDModel, TimeStampMixin


class RefreshToken(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "refresh_tokens"  # pyright: ignore[reportAssignmentType]

    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    token_hash: str = Field(nullable=False)
    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        )
    )

    revoked_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
    )


class TokenType(str, Enum):
    EMAIL_VERIFY = "email_verify"
    PASSWORD_RESET = "password_reset"


class VerificationToken(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "verification_tokens"  # pyright: ignore[reportAssignmentType]
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, ondelete="CASCADE")
    token_hash: str = Field(nullable=False)
    type: TokenType = Field(sa_type=AutoString, nullable=False, index=True)
    expires_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
        )
    )
    used_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=True,
        ),
    )
