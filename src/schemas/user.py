import uuid

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=16)
    password: str = Field(min_length=8, max_length=16)
    invitation_token: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=16)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class RegisterResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    is_verified: bool
    avatar_url: str


class VerifyEmail(BaseModel):
    token: str


class ReVerifyEmail(BaseModel):
    email: EmailStr


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=16)


class RefreshSession(BaseModel):
    refresh_token: str
