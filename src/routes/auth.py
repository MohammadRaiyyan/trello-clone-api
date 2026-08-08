from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from src.core.rate_limit import limiter
from src.database import get_session
from src.schemas.response import APIResponse
from src.schemas.user import (
    ForgotPassword,
    RefreshSession,
    RegisterResponse,
    ResetPassword,
    ReVerifyEmail,
    TokenResponse,
    UserCreate,
    UserLogin,
    VerifyEmail,
)
from src.services.auth import AuthService

auth_router = APIRouter(prefix="auth")
auth_service: AuthService = AuthService()


@auth_router.post(
    "/login", response_model=APIResponse[TokenResponse], status_code=status.HTTP_200_OK
)
@limiter.limit("5/minute")
async def login(
    creds: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> APIResponse[TokenResponse]:
    access_token, refresh_token = await auth_service.login(
        email=creds.email, password=creds.password, session=session
    )
    return APIResponse(
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        message="Login successful",
        status=200,
    )


@auth_router.post(
    "/register",
    response_model=APIResponse[RegisterResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/hour")
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
) -> APIResponse[RegisterResponse]:
    user = await auth_service.register(user_data, session)
    return APIResponse(
        status=status.HTTP_201_CREATED,
        message="Registration successful",
        data=RegisterResponse.model_validate(user),
    )


@auth_router.post(
    "/verifiy-email",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
@limiter.limit("10/minute")
async def verify_email(
    payload: VerifyEmail, session: AsyncSession = Depends(get_session)
) -> APIResponse[TokenResponse]:
    access_token, refresh_token = await auth_service.verify_email(
        token_str=payload.token, session=session
    )
    return APIResponse(
        status=status.HTTP_200_OK,
        message="Email verification successful",
        data=TokenResponse(access_token=access_token, refresh_token=refresh_token),
    )


@auth_router.post(
    "/resend-verifiy-email", response_model=APIResponse, status_code=status.HTTP_200_OK
)
@limiter.limit("3/hour")
async def resend_verify_email(
    payload: ReVerifyEmail, session: AsyncSession = Depends(get_session)
):
    await auth_service.resend_verification_email(email=payload.email, session=session)
    return APIResponse(
        status=status.HTTP_200_OK,
        message="Email verification link sent on your registered email successful",
    )


@auth_router.post(
    "/refresh-token",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    payload: RefreshSession, session: AsyncSession = Depends(get_session)
) -> APIResponse[TokenResponse]:
    access_token, refresh_token = await auth_service.refresh_session(
        refresh_token=payload.refresh_token, session=session
    )
    return APIResponse(
        status=status.HTTP_200_OK,
        message="",
        data=TokenResponse(access_token=access_token, refresh_token=refresh_token),
    )


@auth_router.post(
    "/logout",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(
    payload: RefreshSession, session: AsyncSession = Depends(get_session)
) -> APIResponse:
    await auth_service.logout(refresh_token=payload.refresh_token, session=session)
    return APIResponse(
        status=status.HTTP_200_OK,
        message="Logout successful",
    )


@auth_router.post(
    "/forgot-password",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    payload: ForgotPassword, session: AsyncSession = Depends(get_session)
) -> APIResponse:
    await auth_service.forgot_password(email=payload.email, session=session)
    return APIResponse(
        status=status.HTTP_200_OK,
        message="Account verification link send successfully on your email",
    )


@auth_router.post(
    "/reset-password",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    payload: ResetPassword, session: AsyncSession = Depends(get_session)
) -> APIResponse:
    await auth_service.reset_password(
        token=payload.token, new_password=payload.new_password, session=session
    )
    return APIResponse(
        status=status.HTTP_200_OK,
        message="Password reset successful",
    )
