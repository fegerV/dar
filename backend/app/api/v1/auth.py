from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import decode_token
from app.models.user import User, UserAuthIdentity
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
