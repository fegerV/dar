import hashlib
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.refreshtoken import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def create(
        self,
        user_id: UUID,
        jti: str,
        device_info: dict | None = None,
        ip_address: str | None = None,
    ) -> RefreshToken:
        expires_at = (
            datetime.now(UTC)
            + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        token = RefreshToken(
            user_id=user_id,
            token_hash=self._hash_token(jti),
            jti=jti,
            expires_at=expires_at,
            device_info=device_info or {},
            ip_address=ip_address,
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def is_revoked(self, jti: str) -> bool:
        token = await self.get_by_jti(jti)
        if token is None:
            return True
        if token.revoked:
            return True

        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            return True
        return False

    async def revoke_by_jti(self, jti: str) -> bool:
        token = await self.get_by_jti(jti)
        if token is None:
            return False
        token.revoked = True
        await self.db.flush()
        return True

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        result = await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        await self.db.flush()
        return result.rowcount

    async def cleanup_expired(self) -> int:
        result = await self.db.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < datetime.now(UTC))
        )
        await self.db.flush()
        return result.rowcount
