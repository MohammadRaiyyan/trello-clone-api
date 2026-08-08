import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import decode_token
from src.database.session import get_session
from src.models.user import User
from src.services.user import UserServices

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

oauth2_dependency = Depends(oauth2_scheme)
session_dependency = Depends(get_session)

user_service = UserServices()


async def get_current_user(
    token: str = oauth2_dependency,
    session: AsyncSession = session_dependency,
) -> User:
    try:
        payload = decode_token(token)
        user_id = uuid.UUID(payload.get("sub"))
    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = await user_service.get_by_id(user_id, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
