import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import AutoString, Field, Index, SQLModel, UniqueConstraint, text


class BoardVisibility(str, Enum):
    PRIVATE = "private"
    ORG_VISIBLE = "org_visible"
    PUBLIC = "public"


class Board(SQLModel, table=True):
    __tablename__ = "boards"

    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    organization_id: uuid.UUID = Field(
        nullable=False, foreign_key="organizations.id", ondelete="CASCADE"
    )
    name: str = Field(nullable=False)
    description: str = Field(nullable=True)
    background: str = Field(nullable=True)
    visibility: BoardVisibility = Field(
        nullable=False, default=BoardVisibility.PRIVATE, sa_type=AutoString
    )
    is_archived: bool = Field(nullable=False, default=False)
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
            "idx_boards_org",
            "organization_id",
            postgresql_where=text("is_archived = FALSE"),
        ),
    )


class BoardRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class BoardMember(SQLModel, table=True):
    __tablename__ = "board_members"
    id: uuid.UUID = Field(
        nullable=False, index=True, primary_key=True, default_factory=uuid.uuid4
    )
    board_id: uuid.UUID = Field(
        nullable=False, foreign_key="boards.id", ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    role: BoardRole = Field(
        nullable=False, default=BoardRole.EDITOR, sa_type=AutoString
    )
    added_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (UniqueConstraint("board_id", "user_id", name="uq_board_member"),)
