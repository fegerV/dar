from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import decode_token
from app.repositories.users import UserRepository
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
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


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens = await service.register(body.email, body.password, body.display_name)
    user_resp = await _get_user_from_token(tokens["access_token"], db)
    return {**tokens, "user": user_resp}


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    tokens = await service.login(body.email, body.password)
    user_resp = await _get_user_from_token(tokens["access_token"], db)
    return {**tokens, "user": user_resp}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh(body.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return UserResponse.model_validate(user)
