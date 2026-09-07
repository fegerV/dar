from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import decode_token
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.auth import (
    AuthResponse,
    LinkedProviderResponse,
    LinkProviderRequest,
    LoginRequest,
    OAuthRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    TwoFactorDisableRequest,
    TwoFactorEnableRequest,
    TwoFactorEnableResponse,
    TwoFactorInitiateResponse,
    TwoFactorRegenerateCodesResponse,
    TwoFactorStatusResponse,
    TwoFactorVerifyRequest,
    UserResponse,
)
from app.services.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


async def _get_user_from_token(access_token: str, db: AsyncSession) -> UserResponse:
    payload = decode_token(access_token)
    user_id = UUID(payload["sub"])
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    return UserResponse.model_validate(user)


def _normalize_provider_user_id(provider: str, raw_id: str | int) -> str:
    return f"{provider}:{raw_id}"


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    tokens = await service.register(body.email, body.password, body.display_name)
    user_resp = await _get_user_from_token(tokens["access_token"], db)
    return {**tokens, "user": user_resp}


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    tokens = await service.login(body.email, body.password)
    user_resp = await _get_user_from_token(tokens["access_token"], db)
    return {**tokens, "user": user_resp}


@router.post("/oauth/login", response_model=AuthResponse)
async def oauth_login(
    body: OAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    tokens = await service.oauth_login(
        provider=body.provider,
        access_token=body.access_token,
        id_token=body.id_token,
    )
    user_resp = await _get_user_from_token(tokens["access_token"], db)
    return {**tokens, "user": user_resp}


@router.post("/oauth/link", response_model=LinkedProviderResponse)
async def link_provider(
    body: LinkProviderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.auth.oauth_service import OAuthService
    oauth_service = OAuthService(db)
    identity = await oauth_service.link_provider(
        user_id=current_user.id,
        provider=body.provider,
        access_token=body.access_token,
    )
    return LinkedProviderResponse(
        provider=identity.provider,
        provider_user_id=identity.provider_user_id,
        email=identity.email,
    )


@router.get("/me/providers", response_model=list[LinkedProviderResponse])
async def get_linked_providers(
    current_user: User = Depends(get_current_user),
):
    return [
        LinkedProviderResponse(
            provider=identity.provider,
            provider_user_id=identity.provider_user_id,
            email=identity.email,
        )
        for identity in current_user.auth_identities
    ]


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    return await service.refresh(body.refresh_token)


@router.post("/logout", status_code=204)
async def logout(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    await service.logout(body.refresh_token)
    return None


@router.post("/logout-all", status_code=204)
async def logout_all(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AuthService(db)
    await service.logout_all(current_user.id)
    return None


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return UserResponse.model_validate(user)


# 2FA Endpoints
@router.post("/2fa/initiate", response_model=TwoFactorInitiateResponse)
async def initiate_2fa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Инициировать настройку 2FA (получить секрет и QR URI)."""
    from app.services.auth.two_factor_service import TwoFactorAuthService
    
    service = TwoFactorAuthService(db)
    return await service.initiate_2fa_setup(current_user.id)


@router.post("/2fa/enable", response_model=TwoFactorEnableResponse)
async def enable_2fa(
    body: TwoFactorEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Включить 2FA после верификации TOTP кода."""
    from app.services.auth.two_factor_service import TwoFactorAuthService
    
    service = TwoFactorAuthService(db)
    return await service.enable_2fa(current_user.id, body.totp_code)


@router.post("/2fa/disable", status_code=204)
async def disable_2fa(
    body: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Отключить 2FA."""
    from app.services.auth.two_factor_service import TwoFactorAuthService
    
    service = TwoFactorAuthService(db)
    await service.disable_2fa(
        current_user.id, 
        totp_code=body.totp_code, 
        backup_code=body.backup_code
    )
    return None


@router.get("/2fa/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить статус 2FA для текущего пользователя."""
    from app.services.auth.two_factor_service import TwoFactorAuthService
    
    service = TwoFactorAuthService(db)
    return await service.get_2fa_status(current_user.id)


@router.post("/2fa/regenerate-codes", response_model=TwoFactorRegenerateCodesResponse)
async def regenerate_backup_codes(
    body: TwoFactorEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Перегенерировать backup коды."""
    from app.services.auth.two_factor_service import TwoFactorAuthService
    
    service = TwoFactorAuthService(db)
    return await service.regenerate_backup_codes(current_user.id, body.totp_code)


@router.post("/2fa/verify", response_model={"verified": bool})
async def verify_2fa_code(
    body: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Верифицировать 2FA код (для тестирования или повторного входа)."""
    from app.services.auth.two_factor_service import TwoFactorAuthService
    
    service = TwoFactorAuthService(db)
    verified = await service.verify_2fa(current_user.id, body.code)
    return {"verified": verified}
