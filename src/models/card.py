import uuid
from datetime import datetime

from sqlmodel import (
    BigInteger,
    Double,
    Field,
    Index,
    PrimaryKeyConstraint,
    SQLModel,
    UniqueConstraint,
    text,
)

from src.models.base import BaseUUIDModel, TimeStampMixin


class Card(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "cards"
    column_id: uuid.UUID = Field(
        nullable=False, foreign_key="columns.id", ondelete="CASCADE"
    )
    title: str = Field(nullable=False)
    description: str | None = Field(default=None)
    position: float = Field(nullable=False, sa_type=Double)
    due_date: datetime | None = Field(default=None)
    start_date: datetime | None = Field(default=None)
    is_completed: bool = Field(nullable=False, default=False)
    is_archived: bool = Field(nullable=False, default=False)
    cover_image_url: str | None = Field(default=None)
    created_by: uuid.UUID = Field(nullable=False, foreign_key="users.id")

    __table_args__ = (
        Index(
            "idx_cards_column",
            "column_id",
            "position",
            postgresql_where=text("is_archived = FALSE"),
        ),
        Index(
            "idx_cards_due_date",
            "due_date",
            postgresql_where=text("is_archived = FALSE"),
        ),
    )


class CardMember(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "card_members"

    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    __table_args__ = (UniqueConstraint("card_id", "user_id", name="uq_cards_member"),)


class Label(BaseUUIDModel, table=True):
    __tablename__ = "labels"
    board_id: uuid.UUID = Field(
        nullable=False, foreign_key="boards.id", ondelete="CASCADE"
    )
    name: str = Field(nullable=False)
    color: str = Field(nullable=False)
    __table_args__ = (
        UniqueConstraint(
            "board_id",
            "name",
            name="uq_board_label_name",
        ),
    )


class CardLabel(SQLModel, table=True):
    __tablename__ = "card_labels"

    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    label_id: uuid.UUID = Field(
        nullable=False, foreign_key="labels.id", ondelete="CASCADE"
    )
    __table_args__ = (
        PrimaryKeyConstraint("card_id", "label_id", name="idx_card_label"),
    )


class Comment(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "comments"
    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(nullable=False, foreign_key="users.id")
    content: str = Field(nullable=False)
    is_edited: bool = Field(nullable=False, default=False)


class Attachment(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "attachments"
    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    uploaded_by: uuid.UUID = Field(nullable=False, foreign_key="users.id")
    file_url: str = Field(nullable=False)
    file_name: str = Field(nullable=False)
    file_size_bytes: int | None = Field(default=None, sa_type=BigInteger)
    mime_type: str | None = Field(default=None)


class Checklist(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "checklists"

    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    title: str = Field(nullable=False, default="Checklist")
    position: float = Field(nullable=False, sa_type=Double)


class ChecklistItem(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "checklist_items"

    checklist_id: uuid.UUID = Field(
        nullable=False, foreign_key="checklists.id", ondelete="CASCADE"
    )
    content: str = Field(nullable=False)
    is_completed: bool = Field(nullable=False, default=False)
    position: float = Field(nullable=False, sa_type=Double)
    assigned_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    due_date: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    completed_by_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")

    __table_args__ = (
        Index(
            "idx_checklist_item_checklists",
            "checklist_id",
            "position",
        ),
    )
