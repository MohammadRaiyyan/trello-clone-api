from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class BaseUUIModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)


class TimeStampMixin(SQLModel):
    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
