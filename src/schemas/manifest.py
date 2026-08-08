import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from src.models.organization import OrgRole
from src.schemas.base import InvitationResponse, Organization, OrganizationResponse


class ManifestUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_verified: bool
    is_active: bool


class ManifestOrganization(OrganizationResponse):
    pass


class OnboardingStatus(BaseModel):
    completed: bool
    has_organization: bool
    has_pending_invitations: bool


class ManifestResponse(BaseModel):
    user: ManifestUser
    organizations: list[ManifestOrganization]
    pending_invitations: list[InvitationResponse]
    onboarding: OnboardingStatus
