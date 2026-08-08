import uuid
from enum import Enum
from typing import Any

from sqlalchemy import Column
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Index, desc

from src.models.base import BaseUUIDModel, TimeStampMixin


class ActivityActionType(str, Enum):
    # Organization
    ORG_CREATED = "org_created"
    ORG_RENAMED = "org_renamed"
    ORG_MEMBER_ADDED = "org_member_added"
    ORG_MEMBER_REMOVED = "org_member_removed"
    ORG_MEMBER_ROLE_CHANGED = "org_member_role_changed"

    # Board
    BOARD_CREATED = "board_created"
    BOARD_RENAMED = "board_renamed"
    BOARD_ARCHIVED = "board_archived"
    BOARD_RESTORED = "board_restored"
    BOARD_DELETED = "board_deleted"
    BOARD_VISIBILITY_CHANGED = "board_visibility_changed"
    BOARD_MEMBER_ADDED = "board_member_added"
    BOARD_MEMBER_REMOVED = "board_member_removed"
    BOARD_MEMBER_ROLE_CHANGED = "board_member_role_changed"

    # Column
    COLUMN_CREATED = "column_created"
    COLUMN_RENAMED = "column_renamed"
    COLUMN_MOVED = "column_moved"
    COLUMN_ARCHIVED = "column_archived"
    COLUMN_RESTORED = "column_restored"

    # Card
    CARD_CREATED = "card_created"
    CARD_RENAMED = "card_renamed"
    CARD_MOVED = "card_moved"  # column change or position change
    CARD_DESCRIPTION_UPDATED = "card_description_updated"
    CARD_DUE_DATE_SET = "card_due_date_set"
    CARD_DUE_DATE_REMOVED = "card_due_date_removed"
    CARD_MARKED_COMPLETE = "card_marked_complete"
    CARD_MARKED_INCOMPLETE = "card_marked_incomplete"
    CARD_ARCHIVED = "card_archived"
    CARD_RESTORED = "card_restored"
    CARD_DELETED = "card_deleted"
    CARD_MEMBER_ASSIGNED = "card_member_assigned"
    CARD_MEMBER_UNASSIGNED = "card_member_unassigned"
    CARD_LABEL_ADDED = "card_label_added"
    CARD_LABEL_REMOVED = "card_label_removed"
    CARD_COVER_SET = "card_cover_set"
    CARD_COVER_REMOVED = "card_cover_removed"

    # Checklist
    CHECKLIST_CREATED = "checklist_created"
    CHECKLIST_RENAMED = "checklist_renamed"
    CHECKLIST_DELETED = "checklist_deleted"
    CHECKLIST_ITEM_ADDED = "checklist_item_added"
    CHECKLIST_ITEM_COMPLETED = "checklist_item_completed"
    CHECKLIST_ITEM_REOPENED = "checklist_item_reopened"
    CHECKLIST_ITEM_DELETED = "checklist_item_deleted"
    CHECKLIST_ITEM_ASSIGNED = "checklist_item_assigned"

    # Comment
    COMMENT_ADDED = "comment_added"
    COMMENT_EDITED = "comment_edited"
    COMMENT_DELETED = "comment_deleted"

    # Attachment
    ATTACHMENT_ADDED = "attachment_added"
    ATTACHMENT_REMOVED = "attachment_removed"

    # Label (board-level definition changes)
    LABEL_CREATED = "label_created"
    LABEL_RENAMED = "label_renamed"
    LABEL_COLOR_CHANGED = "label_color_changed"
    LABEL_DELETED = "label_deleted"


class Activity(BaseUUIDModel, TimeStampMixin, table=True):
    __tablename__ = "activity_logs"

    board_id: uuid.UUID = Field(
        nullable=False,
        foreign_key="boards.id",
        ondelete="CASCADE",
    )

    user_id: uuid.UUID = Field(
        nullable=False,
        foreign_key="users.id",
    )

    action_type: ActivityActionType = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                ActivityActionType,
                name="activity_action_type",
            ),
            nullable=False,
        )
    )

    meta_data: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(
            "metadata",
            JSONB,
            nullable=True,
        ),
    )

    __table_args__ = (
        Index(
            "idx_activity_board",
            "board_id",
            desc("created_at"),
        ),
    )
