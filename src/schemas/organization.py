from pydantic import BaseModel, ConfigDict, Field

from src.models.organization import OrgRole
from src.schemas.base import uuid


class CreateOrganization(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )
    description: str | None = None
    logo_url: str | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    slug: str
    description: str | None = Field(default=None)
    logo_url: str | None = Field(default=None)
    created_by: uuid.UUID
