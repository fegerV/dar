from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(TokenResponse):
    user: "UserResponse"


class UserResponse(BaseModel):
    id: UUID
    status: str
    is_admin: bool = False
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    locale: str
    timezone: str
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OAuthRequest(BaseModel):
    provider: str = Field(..., pattern="^(yandex|vk)$")
    access_token: str
    id_token: str | None = None


class LinkProviderRequest(BaseModel):
    provider: str = Field(..., pattern="^(yandex|vk)$")
    access_token: str


class LinkedProviderResponse(BaseModel):
    provider: str
    provider_user_id: str
    email: str | None = None
