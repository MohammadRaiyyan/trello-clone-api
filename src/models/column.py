import uuid
from datetime import datetime, timezone

from sqlmodel import Double, Field, Index, SQLModel, text


class Column(SQLModel, table=True):
    __tablename__ = "columns"
    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    board_id: uuid.UUID = Field(
        nullable=False, foreign_key="boards.id", ondelete="CASCADE"
    )
    name: str = Field(nullable=False)
    position: float = Field(nullable=False, sa_type=Double)
    is_archived: bool = Field(nullable=False, default=False)
    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    __table_args__ = (
        Index(
            "idx_columns_board",
            "board_id",
            "position",
            postgresql_where=text("is_archived = FALSE"),
        ),
    )
