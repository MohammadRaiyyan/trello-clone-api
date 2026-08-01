import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlmodel import AutoString, Field, SQLModel, UniqueConstraint

from src.models.base import BaseUUIModel, TimeStampMixin


class Organization(BaseUUIModel, TimeStampMixin, SQLModel, table=True):
    __tablename__ = "organizations"  # pyright: ignore[reportAssignmentType]
    name: str = Field(
        nullable=False,
    )
    slug: str = Field(nullable=False, unique=True)
    description: str | None = Field(default=None)
    logo_url: str | None = Field(default=True)
    created_by: uuid.UUID = Field(nullable=False, foreign_key="users.id")


class OrgRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class OrganizationMember(BaseUUIModel, TimeStampMixin, SQLModel, table=True):
    __tablename__ = "organization_members"  # pyright: ignore[reportAssignmentType]

    organization_id: uuid.UUID = Field(
        nullable=False, foreign_key="organizations.id", ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        nullable=False, foreign_key="users.id", ondelete="CASCADE"
    )
    role: OrgRole = Field(
        nullable=False,
        default=OrgRole.MEMBER,
        sa_type=AutoString,
    )

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_organization_user"),
    )


class InviteStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class OrganizationInvite(BaseUUIModel, TimeStampMixin, SQLModel, table=True):
    __tablename__ = "organization_invites"  # pyright: ignore[reportAssignmentType]

    organization_id: uuid.UUID = Field(
        nullable=False, foreign_key="organizations.id", ondelete="CASCADE"
    )
    email: str = Field(nullable=False)
    role: OrgRole = Field(nullable=False, default=OrgRole.MEMBER, sa_type=AutoString)
    invited_by: uuid.UUID = Field(nullable=False, foreign_key="users.id")
    token_hash: str = Field(
        nullable=False,
        unique=True,
        index=True,
    )
    status: InviteStatus = Field(
        default=InviteStatus.PENDING,
        sa_column=Column(
            SQLEnum(
                InviteStatus,
                name="invite_status_type",
            ),
            nullable=False,
        ),
    )
    expires_at: datetime = Field(nullable=False)
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "email",
            name="uq_org_invite_email",
        ),
    )
