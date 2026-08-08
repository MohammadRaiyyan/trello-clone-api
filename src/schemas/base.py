import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.models.organization import OrgRole


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None = Field(default=None)
    logo_url: str | None = Field(default=None)
    created_by: uuid.UUID


class InvitationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    organization_name: str
    role: OrgRole
    expires_at: datetime
