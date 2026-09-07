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


# 2FA Schemas
class TwoFactorInitiateResponse(BaseModel):
    secret: str
    provisioning_uri: str
    manual_entry_key: str


class TwoFactorEnableRequest(BaseModel):
    totp_code: str = Field(..., min_length=6, max_length=6)


class TwoFactorEnableResponse(BaseModel):
    backup_codes: list[str]
    message: str


class TwoFactorDisableRequest(BaseModel):
    totp_code: str | None = None
    backup_code: str | None = None


class TwoFactorVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=10)


class TwoFactorStatusResponse(BaseModel):
    is_enabled: bool
    setup_required: bool
    has_backup_codes: bool = False
    last_used_at: datetime | None = None


class TwoFactorRegenerateCodesResponse(BaseModel):
    backup_codes: list[str]
    message: str
