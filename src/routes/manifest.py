from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.dependencies import get_current_user
from src.database.session import get_session
from src.models.user import User
from src.schemas.manifest import ManifestResponse
from src.schemas.response import APIResponse
from src.services.manifest import ManifestServices

manifest_router = APIRouter(prefix="/manifest")

manifest_services = ManifestServices()


@manifest_router.get(
    "/", response_model=APIResponse[ManifestResponse], status_code=status.HTTP_200_OK
)
async def get_manifest(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)
) -> APIResponse[ManifestResponse]:
    manifest = await manifest_services.get_manifest(user_id=user.id, session=session)
    return APIResponse(
        data=ManifestResponse.model_validate(manifest),
        message="",
        status=status.HTTP_200_OK,
    )
