import uuid
from datetime import datetime, timezone

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


class Card(SQLModel, table=True):
    __tablename__ = "cards"
    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    column_id: uuid.UUID = Field(
        nullable=False, foreign_key="columns.id", ondelete="CASCADE"
    )
    title: str = Field(nullable=False)
    description: str = Field(nullable=True)
    position: float = Field(nullable=False, sa_type=Double)
    due_date: datetime = Field(nullable=True)
    start_date: datetime = Field(nullable=True)
    is_completed: bool = Field(nullable=False, default=False)
    is_archived: bool = Field(nullable=False, default=False)
    cover_image_url: str = Field(nullable=True)
    created_by: uuid.UUID = Field(nullable=False, foreign_key="users.id")
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


class CardMember(SQLModel, table=True):
    __tablename__ = "card_members"
    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    assigned_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
    __table_args__ = (UniqueConstraint("card_id", "user_id", name="uq_cards_member"),)


class Label(SQLModel, table=True):
    __tablename__ = "labels"

    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    board_id: uuid.UUID = Field(
        nullable=False, foreign_key="boards.id", ondelete="CASCADE"
    )
    name: str = Field(nullable=False)
    color: str = Field(nullable=False)


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


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(nullable=False, foreign_key="users.id")
    content: str = Field(nullable=False)
    is_edited: bool = Field(nullable=False, default=False)

    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class Attachment(SQLModel, table=True):
    __tablename__ = "attachments"

    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    uploaded_by: uuid.UUID = Field(nullable=False, foreign_key="users.id")
    file_url: str = Field(nullable=False)
    file_name: str = Field(nullable=False)
    file_size_bytes: int = Field(nullable=True, sa_type=BigInteger)
    mime_type: str = Field(nullable=True)
    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )


class Checklist(SQLModel, table=True):
    __tablename__ = "checklists"

    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    card_id: uuid.UUID = Field(
        nullable=False, foreign_key="cards.id", ondelete="CASCADE"
    )
    title: str = Field(nullable=False, default="Checklist")
    position: float = Field(nullable=False, sa_type=Double)
    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )


class ChecklistItem(SQLModel, table=True):
    __tablename__ = "checklists_items"

    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    checklist_id: uuid.UUID = Field(
        nullable=False, foreign_key="checklists.id", ondelete="CASCADE"
    )
    content: str = Field(nullable=False)
    is_completed: bool = Field(nullable=False, default=False)
    position: float = Field(nullable=False, sa_type=Double)
    assigned_to: uuid.UUID = Field(nullable=True, foreign_key="users.id")
    due_date: datetime = Field(nullable=True)
    completed_at: datetime = Field(nullable=True)
    completed_by: uuid.UUID = Field(nullable=True, foreign_key="users.id")
    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index(
            "idx_checklist_item_checklists",
            "checklist_id",
            "position",
        ),
    )
