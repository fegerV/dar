from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Entitlement
from app.repositories.storage import PaymentRepository


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

    async def consume(self, entitlement_id: UUID, user_id: UUID, quantity: int = 1) -> Entitlement | None:
        result = await self.db.execute(
            select(Entitlement).where(
                Entitlement.id == entitlement_id,
                Entitlement.user_id == user_id,
            )
        )
        entitlement = result.scalar_one_or_none()
        if entitlement is None:
            return None
        entitlement.consumed += quantity
        await self.db.flush()
        return entitlement
