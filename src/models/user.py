import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID = Field(
        primary_key=True, default_factory=uuid.uuid4, index=True, nullable=False
    )
    email: str = Field(unique=True, nullable=False)
    full_name: str = Field(nullable=False)
    password_hash: str = Field(nullable=False)
    avatar_url: str = Field(nullable=True)
    is_verified: bool = Field(nullable=False, default=False)
    is_active: bool = Field(nullable=False, default=True)
    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
