import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import AutoString, Field, SQLModel, UniqueConstraint


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID = Field(
        primary_key=True, default_factory=uuid.uuid4, index=True, nullable=False
    )
    name: str = Field(
        nullable=False,
    )
    slug: str = Field(nullable=False, unique=True)
    description: str = Field(nullable=True)
    logo_url: str = Field(nullable=True)
    created_by: uuid.UUID = Field(nullable=False, foreign_key="users.id")
    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        nullable=False,
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class OrgRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class OrganizationMember(SQLModel, table=True):
    __tablename__ = "organization_members"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID = Field(
        primary_key=True, default_factory=uuid.uuid4, index=True, nullable=False
    )
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

    joined_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_organization_user"),
    )


class InviteStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class OrganizationInvites(SQLModel, table=True):
    __tablename__ = "organization_invites"  # pyright: ignore[reportAssignmentType]

    id: uuid.UUID = Field(
        primary_key=True, default_factory=uuid.uuid4, index=True, nullable=False
    )

    organization_id: uuid.UUID = Field(
        nullable=False, foreign_key="organizations.id", ondelete="CASCADE"
    )
    email: str = Field(nullable=False)
    role: OrgRole = Field(nullable=False, default=OrgRole.MEMBER, sa_type=AutoString)
    invited_by: uuid.UUID = Field(nullable=False, foreign_key="users.id")
    token_hash: str = Field(nullable=False)
    staus: InviteStatus = Field(
        nullable=False, default=InviteStatus.PENDING, sa_type=AutoString
    )
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(
        nullable=False, default_factory=lambda: datetime.now(timezone.utc)
    )
