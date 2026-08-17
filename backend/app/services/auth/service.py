from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserAuthIdentity
from app.repositories.users import UserRepository


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def register(self, email: str, password: str, display_name: str | None = None) -> dict:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ConflictException("User with this email already exists")

        user = User(
            email=email,
            display_name=display_name,
            status="active",
        )
        user = await self.repo.create(user)

        identity = UserAuthIdentity(
            user_id=user.id,
            provider="email",
            provider_user_id=email,
            email=email,
            credentials_json={"password_hash": hash_password(password)},
        )
        await self.repo.create_auth_identity(identity)

        return self._make_tokens(user.id)

    async def login(self, email: str, password: str) -> dict:
        user = await self.repo.get_by_email(email)
        if not user or user.status != "active":
            raise UnauthorizedException("Invalid credentials")

        identity = await self.repo.get_auth_identity("email", email)
        if not identity:
            raise UnauthorizedException("Invalid credentials")

        stored_hash = identity.credentials_json.get("password_hash", "")
        if not verify_password(password, stored_hash):
            raise UnauthorizedException("Invalid credentials")

        return self._make_tokens(user.id)

    async def refresh(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")

        user = await self.repo.get_by_id(UUID(user_id))
        if not user or user.status != "active":
            raise UnauthorizedException("User not found or inactive")

        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def _make_tokens(self, user_id: UUID) -> dict:
        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id),
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
