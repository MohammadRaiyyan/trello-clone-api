from pydantic import BaseModel

from src.models.organization import OrgRole


class CreateInvitation(BaseModel):
    user_email: str
    role: OrgRole
