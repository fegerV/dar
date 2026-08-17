import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.delivery import Delivery, DeliveryLink, ShareEvent
from app.models.generation import Generation


class DeliveryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_link(self, link: DeliveryLink) -> DeliveryLink:
        self.db.add(link)
        await self.db.flush()
        return link

    async def get_link_by_token(self, token_hash: str) -> DeliveryLink | None:
        result = await self.db.execute(
            select(DeliveryLink).where(DeliveryLink.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def increment_link_views(self, link_id: UUID) -> None:
        link = await self.db.get(DeliveryLink, link_id)
        if link:
            link.view_count = (link.view_count or 0) + 1
            link.last_opened_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def create_delivery(self, delivery: Delivery) -> Delivery:
        self.db.add(delivery)
        await self.db.flush()
        return delivery

    async def list_by_project(self, project_id: UUID) -> list[Delivery]:
        result = await self.db.execute(
            select(Delivery).where(Delivery.project_id == project_id).order_by(Delivery.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_share_event(self, event: ShareEvent) -> ShareEvent:
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_latest_generation(self, project_id: UUID) -> Generation | None:
        result = await self.db.execute(
            select(Generation)
            .where(Generation.project_id == project_id, Generation.type == "final")
            .order_by(Generation.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
