from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.dependencies import get_current_user
from src.database.session import get_session
from src.models.user import User
from src.schemas.organization import CreateOrganization, OrganizationResponse
from src.schemas.response import APIResponse
from src.services.organization import OrganizationService

organization_router = APIRouter(prefix="/organizations")

organization_services = OrganizationService()


@organization_router.get(
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
