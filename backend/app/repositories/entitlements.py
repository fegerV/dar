from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Entitlement


class EntitlementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: UUID) -> list[Entitlement]:
        result = await self.db.execute(
            select(Entitlement).where(Entitlement.user_id == user_id)
        )
        return list(result.scalars().all())

    async def create(self, entitlement: Entitlement) -> Entitlement:
        self.db.add(entitlement)
        await self.db.flush()
        return entitlement

    async def get_by_id(self, entitlement_id: UUID, user_id: UUID | None = None) -> Entitlement | None:
        query = select(Entitlement).where(Entitlement.id == entitlement_id)
        if user_id is not None:
            query = query.where(Entitlement.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def consume(self, entitlement_id: UUID, user_id: UUID, quantity: int = 1) -> bool:
        result = await self.db.execute(
            update(Entitlement)
            .where(
                Entitlement.id == entitlement_id,
                Entitlement.user_id == user_id,
                Entitlement.consumed + quantity <= Entitlement.quantity,
            )
            .values(consumed=Entitlement.consumed + quantity)
            .returning(Entitlement.id)
        )
        return result.one_or_none() is not None
