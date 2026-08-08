from sqlmodel import Field

from src.models.base import BaseUUIDModel, TimeStampMixin


class User(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "users"  # pyright: ignore[reportAssignmentType]

    email: str = Field(unique=True, nullable=False)
    full_name: str = Field(nullable=False)
    password_hash: str = Field(nullable=False)
    avatar_url: str = Field(nullable=True)
    is_verified: bool = Field(nullable=False, default=False)
    is_active: bool = Field(nullable=False, default=True)
