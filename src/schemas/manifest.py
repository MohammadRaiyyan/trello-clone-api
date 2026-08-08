import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from src.models.organization import OrgRole


class ManifestUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_verified: bool
    is_active: bool


class ManifestOrganization(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    logo_url: str
    created_by: uuid.UUID


class ManifestInvitation(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    organization_name: str
    role: OrgRole
    expires_at: datetime


class OnboardingStatus(BaseModel):
    completed: bool
    has_organization: bool
    has_pending_invitations: bool


class ManifestResponse(BaseModel):
    user: ManifestUser
    organizations: list[ManifestOrganization]
    pending_invitations: list[ManifestInvitation]
    onboarding: OnboardingStatus
