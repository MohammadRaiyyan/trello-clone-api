import uuid

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.schemas.manifest import (
    ManifestOrganization,
    ManifestResponse,
    ManifestUser,
    OnboardingStatus,
)
from src.services.invitation import InvitationService
from src.services.organization import OrganizationService
from src.services.user import UserServices

user_services = UserServices()
organization_services = OrganizationService()
invitation_services = InvitationService()


class ManifestServices:
    async def get_manifest(
        self, user_id: uuid.UUID, session: AsyncSession
    ) -> ManifestResponse:
        user = await user_services.get_by_id(user_id=user_id, session=session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        organizations = await organization_services.get_user_organizations(
            user_id, session
        )
        invitaitons = await invitation_services.get_pending_invitations(
            user_email=user.email, session=session
        )
        return ManifestResponse(
            user=ManifestUser.model_validate(user),
            organizations=[
                ManifestOrganization(
                    id=organization.id,
                    name=organization.name,
                    slug=organization.slug,
                    logo_url=organization.logo_url,
                    created_by=organization.created_by,
                    role=membership.role,
                )
                for organization, membership in organizations
            ],
            pending_invitations=invitaitons,
            onboarding=OnboardingStatus(
                completed=bool(organizations),
                has_organization=bool(organizations),
                has_pending_invitations=bool(invitaitons),
            ),
        )
