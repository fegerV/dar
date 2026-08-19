import secrets
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictException, UnauthorizedException, ValidationException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.payment import Entitlement
from app.models.user import User, UserAuthIdentity
from app.repositories.entitlements import EntitlementRepository
from app.repositories.refresh_tokens import RefreshTokenRepository
from app.repositories.users import UserRepository


class AuthService:
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register(
        self, email: str, password: str, display_name: str | None = None
    ) -> dict:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ConflictException("User with this email already exists")

        self._validate_password(password)

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

        entitlement = Entitlement(
            user_id=user.id,
            code="welcome_generation",
            quantity=1,
            consumed=0,
            source="registration",
            created_at=datetime.now(UTC),
        )
        entitlement_repo = EntitlementRepository(self.db)
        await entitlement_repo.create(entitlement)
        await self.db.commit()

        return await self._make_tokens(user.id)

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

        return await self._make_tokens(user.id)

    async def refresh(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        jti = payload.get("jti")
        if not jti:
            raise UnauthorizedException("Invalid refresh token")

        if await self.token_repo.is_revoked(jti):
            raise UnauthorizedException("Refresh token revoked")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")

        user = await self.repo.get_by_id(UUID(user_id))
        if not user or user.status != "active":
            raise UnauthorizedException("User not found or inactive")

        await self.token_repo.revoke_by_jti(jti)

        return await self._make_tokens(user.id)

    async def logout(self, refresh_token: str) -> None:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        jti = payload.get("jti")
        if jti:
            await self.token_repo.revoke_by_jti(jti)
        await self.db.commit()

    async def logout_all(self, user_id: UUID) -> None:
        await self.token_repo.revoke_all_for_user(user_id)
        await self.db.commit()

    def _validate_password(self, password: str) -> None:
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise ValidationException(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters"
            )
        if len(password) > self.MAX_PASSWORD_LENGTH:
            raise ValidationException(
                f"Password must be at most {self.MAX_PASSWORD_LENGTH} characters"
            )
        if not any(c.isupper() for c in password):
            raise ValidationException(
                "Password must contain at least one uppercase letter"
            )
        if not any(c.islower() for c in password):
            raise ValidationException(
                "Password must contain at least one lowercase letter"
            )
        if not any(c.isdigit() for c in password):
            raise ValidationException("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            raise ValidationException(
                "Password must contain at least one special character"
            )

    async def _make_tokens(self, user_id: UUID) -> dict:
        access_jti = secrets.token_urlsafe(32)
        refresh_jti = secrets.token_urlsafe(32)

        await self.token_repo.create(user_id, refresh_jti)

        return {
            "access_token": create_access_token(user_id, jti=access_jti),
            "refresh_token": create_refresh_token(user_id, jti=refresh_jti),
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
