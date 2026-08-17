from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserAuthIdentity


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.phone == phone, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user: User) -> User:
        await self.db.flush()
        return user

    async def get_auth_identity(
        self, provider: str, provider_user_id: str
    ) -> UserAuthIdentity | None:
        result = await self.db.execute(
            select(UserAuthIdentity).where(
                UserAuthIdentity.provider == provider,
                UserAuthIdentity.provider_user_id == provider_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_auth_identity(self, identity: UserAuthIdentity) -> UserAuthIdentity:
        self.db.add(identity)
        await self.db.flush()
        return identity
