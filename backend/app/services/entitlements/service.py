from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.payment import Entitlement
from app.repositories.entitlements import EntitlementRepository
from app.schemas.payment import EntitlementResponse


class EntitlementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EntitlementRepository(db)

    async def list_entitlements(self, user_id: UUID) -> list[EntitlementResponse]:
        entitlements = await self.repo.get_by_user(user_id)
        return [EntitlementResponse.model_validate(e) for e in entitlements]

    async def grant_entitlement(
        self, user_id: UUID, code: str, quantity: int = 1, source: str | None = None
    ) -> EntitlementResponse:
        entitlement = Entitlement(
            user_id=user_id,
            code=code,
            quantity=quantity,
            consumed=0,
            source=source,
            created_at=datetime.now(UTC),
        )
        entitlement = await self.repo.create(entitlement)
        await self.db.commit()
        return EntitlementResponse.model_validate(entitlement)

    async def consume_entitlement(
        self, user_id: UUID, entitlement_id: UUID, quantity: int = 1
    ) -> EntitlementResponse:
        result = await self.repo.consume(entitlement_id, user_id, quantity)
        if not result:
            raise NotFoundException("Entitlement not found or exhausted")
        await self.db.commit()
        entitlement = await self.repo.get_by_id(entitlement_id)
        return EntitlementResponse.model_validate(entitlement)
