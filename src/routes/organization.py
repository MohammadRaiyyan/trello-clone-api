import uuid

from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.dependencies import get_current_user
from src.core.rate_limit import limiter
from src.database.session import get_session
from src.models.user import User
from src.schemas.invitation import CreateInvitation
from src.schemas.organization import CreateOrganization, OrganizationResponse
from src.schemas.response import APIResponse
from src.services.invitation import InvitationService
from src.services.organization import OrganizationService

organization_router = APIRouter(prefix="/organizations")

organization_services = OrganizationService()
invitation_services = InvitationService()


@organization_router.post(
    "/create",
    response_model=APIResponse[OrganizationResponse],
    status_code=status.HTTP_200_OK,
)
async def create_organization(
    payload: CreateOrganization,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> APIResponse[OrganizationResponse]:
    organization = await organization_services.create_organization(
        user_id=user.id, session=session, new_org=payload
    )
    return APIResponse(
        data=OrganizationResponse(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            logo_url=organization.logo_url,
            created_by=organization.created_by,
        ),
        message="Organization created successfully",
        status=status.HTTP_200_OK,
    )


@organization_router.post(
    "/{organization_id}/invitations",
    response_model=APIResponse[None],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def invite_member(
    request: Request,
    organization_id: uuid.UUID,
    payload: CreateInvitation,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> APIResponse[None]:
    await invitation_services.create_invitation(
        user=user,
        org_id=organization_id,
        member_email=payload.user_email,
        member_role=payload.role,
        session=session,
    )
    return APIResponse(
        message="Invitation sent successfully", status=status.HTTP_201_CREATED
    )


@organization_router.post(
    "/{organization_id}/invitations/{invitation_id}/resend",
    response_model=APIResponse[None],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def re_invite_member(
    request: Request,
    organization_id: uuid.UUID,
    invitation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> APIResponse[None]:
    await invitation_services.retry_invitation(
        user=user,
        org_id=organization_id,
        invitation_id=invitation_id,
        session=session,
    )
    return APIResponse(
        message="Invitation sent successfully", status=status.HTTP_201_CREATED
    )


@organization_router.post(
    "/{organization_id}/invitations/{invitation_id}/revoke",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def revoke_invitation(
    request: Request,
    organization_id: uuid.UUID,
    invitation_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> APIResponse[None]:
    await invitation_services.revoke_invitation(
        user=user,
        org_id=organization_id,
        invitation_id=invitation_id,
        session=session,
    )
    return APIResponse(
        message="Invitation revoked successfully", status=status.HTTP_201_CREATED
    )


@organization_router.post(
    "/invitations/accept",
    response_model=APIResponse[None],
    status_code=status.HTTP_201_CREATED,
)
async def accept_invitation(
    token: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> APIResponse[None]:
    await invitation_services.accept_invitation(
        user=user,
        token=token,
        session=session,
    )
    return APIResponse(
        message="Invitation sent successfully", status=status.HTTP_201_CREATED
    )
