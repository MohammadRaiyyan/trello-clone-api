import uuid

from pydantic import BaseModel, ConfigDict, EmailStr

from src.models.organization import OrgRole
from src.schemas.base import InvitationResponse, OrganizationResponse


class ManifestUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_verified: bool
    is_active: bool


class ManifestOrganization(OrganizationResponse):
    role: OrgRole


class OnboardingStatus(BaseModel):
    completed: bool
    has_organization: bool
    has_pending_invitations: bool


class ManifestResponse(BaseModel):
    user: ManifestUser
    organizations: list[ManifestOrganization]
    pending_invitations: list[InvitationResponse]
    onboarding: OnboardingStatus
