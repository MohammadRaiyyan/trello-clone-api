from datetime import datetime, timedelta, timezone
import secrets
import uuid

from fastapi import HTTPException,status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import hash_token
from src.core.settings import settings
from src.models.organization import InviteStatus, OrgRole, Organization, OrganizationInvite, OrganizationMember
from src.schemas.base import InvitationResponse
from src.schemas.invitation import CreateInvitation


class InvitationService:
    @staticmethod
    def _utc_now() -> datetime:
      return datetime.now(timezone.utc)

    async def get_pending_invitations(
        self, user_email: str, session: AsyncSession
    ) -> list[InvitationResponse]:
        statement =
        select(OrganizationInvite,Organization).join(Organization,
          col(OrganizationInvite.organization_id) == col(Organization.id)
        ).where(
            OrganizationInvite.email == user_email,
            OrganizationInvite.status == InviteStatus.PENDING,
        )
        result = await session.exec(statement)
        invitations = result.all()

        return [
            InvitationResponse.model_validate(invitation) for invitation in invitations
        ]

    async def create_invitation(
        self, user_id: uuid.UUID, data:CreateInvitation, session: AsyncSession
    ) -> None:
      if data.role is OrgRole.OWNER:
        raise(
          HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can not invite a user as Owner"
          )
        )
      statement = select(OrganizationMember).where(
        OrganizationMember.user_id == user_id,
        OrganizationMember.organization_id == data.org_id
      )
      result = await session.exec(statement)
      membership = result.first()

      if membership is None:
        raise(
          HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member"
          )
        )

      if membership.role not in {OrgRole.ADMIN, OrgRole.OWNER}:
        raise(
          HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't have permission to invite members"
          )
        )

      token_str = secrets.token_urlsafe(32)
      token_hash = hash_token(token_str)
      expires_at = self._utc_now() + timedelta(
          hours=settings.VERIFY_REFRESH_TOKEN_EXPIRE_HR
      )
      invitation = OrganizationInvite(
                  role=data.role,
                  invited_by=user_id,
                  expires_at=expires_at,
                  organization_id=data.org_id,
                  status=InviteStatus.PENDING,
                  token_hash=token_hash,
                  email=data.user_email
      )

      session.add(invitation)
      await session.commit()

# Todo:
    async def accept_invitation(
        self, user_id: uuid.UUID, org_id: uuid.UUID, session: AsyncSession
    ) -> None:
        pass

    async def revoke_invitation(
        self, user_id: uuid.UUID, org_id: uuid.UUID, session: AsyncSession
   ) -> None:
       pass
