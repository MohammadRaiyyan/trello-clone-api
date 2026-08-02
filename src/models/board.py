import uuid
from enum import Enum

from sqlmodel import AutoString, Field, Index, SQLModel, UniqueConstraint, text

from src.models.base import BaseUUIModel, TimeStampMixin


class BoardVisibility(str, Enum):
    PRIVATE = "private"
    ORG_VISIBLE = "org_visible"
    PUBLIC = "public"


class Board(BaseUUIModel, TimeStampMixin, SQLModel, table=True):
    __tablename__ = "boards"

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

    __table_args__ = (
        Index(
            "idx_boards_org",
            "organization_id",
            postgresql_where=text("is_archived = FALSE"),
        ),
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_org_board_name",
        ),
    )


class BoardRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class BoardMember(BaseUUIModel, TimeStampMixin, SQLModel, table=True):
    __tablename__ = "board_members"
    board_id: uuid.UUID = Field(
        nullable=False, foreign_key="boards.id", ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    invited_by: uuid.UUID = Field(
        nullable=False,
        foreign_key="users.id",
    )
    role: BoardRole = Field(
        nullable=False, default=BoardRole.EDITOR, sa_type=AutoString
    )

    __table_args__ = (UniqueConstraint("board_id", "user_id", name="uq_board_member"),)
