import uuid

from sqlmodel import Double, Field, Index, SQLModel, text

from src.models.base import BaseUUIModel, TimeStampMixin


class BoardColumn(BaseUUIModel, TimeStampMixin, SQLModel, table=True):
    __tablename__ = "columns"
    board_id: uuid.UUID = Field(
        nullable=False, foreign_key="boards.id", ondelete="CASCADE"
    )
    name: str = Field(nullable=False)
    position: float = Field(nullable=False, sa_type=Double)
    is_archived: bool = Field(nullable=False, default=False)

    __table_args__ = (
        Index(
            "idx_columns_board",
            "board_id",
            "position",
            postgresql_where=text("is_archived = FALSE"),
        ),
    )
