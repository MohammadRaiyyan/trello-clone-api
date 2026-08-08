import uuid

from pydantic import BaseModel

from src.models.organization import OrgRole


class CreateInvitation(BaseModel):
    user_email: str
    org_id: uuid.UUID
    role: OrgRole
