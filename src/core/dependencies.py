import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.security import decode_token
from src.database.session import get_session
from src.models.user import User
from src.services.user import UserServices

bearer_scheme = HTTPBearer()

user_service = UserServices()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        token = credentials.credentials

        payload = decode_token(token)

        user_id = uuid.UUID(payload["sub"])

        if payload.get("type") != "access":
            raise ValueError("Invalid token type")

    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_service.get_by_id(user_id, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
