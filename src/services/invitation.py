import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import hash_token
from src.core.settings import settings
from src.models.organization import (
    InvitationDeliveryStatus,
    InviteStatus,
    Organization,
    OrganizationInvite,
    OrganizationMember,
    OrgRole,
)
from src.models.user import User
from src.schemas.base import InvitationResponse
from src.schemas.invitation import CreateInvitation
from src.services.email import EmailService

email_service = EmailService()


class InvitationService:
    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    async def get_pending_invitations(
        self, user_email: str, session: AsyncSession
    ) -> list[InvitationResponse]:
        statement = (
            select(OrganizationInvite, Organization)
            .join(
                Organization,
                col(OrganizationInvite.organization_id) == col(Organization.id),
            )
            .where(
                OrganizationInvite.email == user_email,
                OrganizationInvite.status == InviteStatus.PENDING,
            )
        )
        result = await session.exec(statement)
        invitations = result.all()

        return [
            InvitationResponse.model_validate(invitation) for invitation in invitations
        ]

    async def create_invitation(
        self,
        user: User,
        org_id: uuid.UUID,
        member_email: str,
        member_role: OrgRole,
        session: AsyncSession,
    ) -> None:

        if member_role is OrgRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can not invite a user as Owner",
            )

        organization = await session.get(Organization, org_id)

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        statement = select(OrganizationMember).where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.organization_id == org_id,
        )

        result = await session.exec(statement)

        membership = result.first()

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        if membership.role not in {OrgRole.ADMIN, OrgRole.OWNER}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to invite members",
            )

        token = secrets.token_urlsafe(32)

        token_hash = hash_token(token)

        expires_at = self._utc_now() + timedelta(hours=settings.INVITATION_EXPIRE_HOURS)

        invitation = OrganizationInvite(
            organization_id=org_id,
            email=member_email,
            role=member_role,
            invited_by=user.id,
            token_hash=token_hash,
            status=InviteStatus.PENDING,
            delivery_status=InvitationDeliveryStatus.PENDING,
            expires_at=expires_at,
        )

        session.add(invitation)

        # Persist invitation first.

        await session.commit()

        await session.refresh(invitation)

        try:
            await email_service.send_invitation_email(
                email=member_email,
                token=token,
                organization_name=organization.name,
                inviter_name=user.full_name,
                role=member_role.value,
            )

        except Exception:
            # Invitation exists, but email delivery failed.

            invitation.delivery_status = InvitationDeliveryStatus.FAILED

            await session.commit()

            # Don't expose provider/internal error.

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Invitation was created, but we couldn't send the "
                    "invitation email. Please try again."
                ),
            )

        invitation.delivery_status = InvitationDeliveryStatus.SENT

        await session.commit()

    async def retry_invitation(
        self,
        user: User,
        org_id: uuid.UUID,
        invitation_id: uuid.UUID,
        session: AsyncSession,
    ) -> None:

        organization = await session.get(Organization, org_id)

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        statement = select(OrganizationMember).where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.organization_id == org_id,
        )

        result = await session.exec(statement)

        membership = result.first()

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        if membership.role not in {OrgRole.ADMIN, OrgRole.OWNER}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to invite members",
            )

        statement = select(OrganizationInvite).where(
            OrganizationInvite.id == invitation_id,
            OrganizationInvite.organization_id == org_id,
        )

        result = await session.exec(statement)

        previous_invite = result.first()

        if previous_invite is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found. Please create new Invitation",
            )

        if previous_invite.status is not InviteStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation is no longer pending",
            )

        if previous_invite.delivery_status is not InvitationDeliveryStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only failed invitations can be resent",
            )

        token = secrets.token_urlsafe(32)

        token_hash = hash_token(token)

        expires_at = self._utc_now() + timedelta(hours=settings.INVITATION_EXPIRE_HOURS)

        previous_invite.expires_at = expires_at
        previous_invite.token_hash = token_hash

        await session.commit()
        await session.refresh(previous_invite)

        previous_invite.delivery_status = InvitationDeliveryStatus.PENDING
        try:
            await email_service.send_invitation_email(
                email=previous_invite.email,
                token=token,
                organization_name=organization.name,
                inviter_name=user.full_name,
                role=previous_invite.role.value,
            )

        except Exception:
            # Invitation exists, but email delivery failed.

            previous_invite.delivery_status = InvitationDeliveryStatus.FAILED

            await session.commit()

            # Don't expose provider/internal error.

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Invitation was created, but we couldn't send the "
                    "invitation email. Please try again."
                ),
            )

        previous_invite.delivery_status = InvitationDeliveryStatus.SENT

        await session.commit()

    # Todo:
    async def accept_invitation(
        self,
        user: User,
        token: str,
        session: AsyncSession,
    ) -> None:
        token_hash = hash_token(token)

        statement = select(OrganizationInvite).where(
            OrganizationInvite.token_hash == token_hash
        )
        result = await session.exec(statement)
        invitation = result.first()

        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation does not exists anymore. Please contact inviter to resend the invitation.",
            )

        if invitation.status is not InviteStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation is no longer valid",
            )
        if invitation.expires_at <= self._utc_now():
            invitation.status = InviteStatus.EXPIRED

            await session.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation has expired",
            )

        if invitation.email.lower() != user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This invitation was sent to a different email address",
            )
        # Prevent duplicate membership

        statement = select(OrganizationMember).where(
            OrganizationMember.organization_id == invitation.organization_id,
            OrganizationMember.user_id == user.id,
        )

        result = await session.exec(statement)

        existing_membership = result.first()

        if existing_membership is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this organization",
            )

        membership = OrganizationMember(
            organization_id=invitation.organization_id,
            user_id=user.id,
            role=invitation.role,
        )

        session.add(membership)

        invitation.status = InviteStatus.ACCEPTED

        await session.commit()

    async def revoke_invitation(
        self,
        user: User,
        org_id: uuid.UUID,
        invitation_id: uuid.UUID,
        session: AsyncSession,
    ) -> None:
        statement = select(OrganizationMember).where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.organization_id == org_id,
        )
        result = await session.exec(statement)
        membership = result.first()

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization",
            )

        if membership.role not in {OrgRole.ADMIN, OrgRole.OWNER}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to revoke invitations",
            )

        statement = select(OrganizationInvite).where(
            OrganizationInvite.id == invitation_id,
            OrganizationInvite.organization_id == org_id,
        )
        result = await session.exec(statement)
        invitation = result.first()

        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        if invitation.status is not InviteStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending invitations can be revoked",
            )

        invitation.status = InviteStatus.REVOKED

        await session.commit()

    async def accept_during_registration(
        self,
        invitation_token: str,
        user: User,
        session: AsyncSession,
    ) -> None:

        token_hash = hash_token(invitation_token)

        statement = select(OrganizationInvite).where(
            OrganizationInvite.token_hash == token_hash,
        )

        result = await session.exec(statement)

        invitation = result.first()

        if invitation is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid invitation",
            )

        if invitation.status is not InviteStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation is no longer valid",
            )

        if invitation.expires_at <= self._utc_now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired",
            )

        if invitation.email.lower() != user.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation email does not match registration email",
            )

        membership = OrganizationMember(
            organization_id=invitation.organization_id,
            user_id=user.id,
            role=invitation.role,
        )

        session.add(membership)

        invitation.status = InviteStatus.ACCEPTED
