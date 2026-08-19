import hashlib
from datetime import UTC, datetime
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

    async def set_referral_data(
        self, link_id: UUID, referral_code: str | None, referrer_user_id: UUID | None
    ) -> None:
        link = await self.db.get(DeliveryLink, link_id)
        if link:
            link.referral_code = referral_code
            link.referrer_user_id = referrer_user_id
            await self.db.flush()

    async def track_referral_view(self, link_id: UUID) -> None:
        link = await self.db.get(DeliveryLink, link_id)
        if link and link.referral_code:
            link.referral_attribution_count = (link.referral_attribution_count or 0) + 1

            from app.models.referral import Referral
            from app.services.referrals.service import ReferralService

            ref_service = ReferralService(self.db)
            code_obj = await ref_service.repo.get_by_code(link.referral_code)
            if code_obj:
                result = await self.db.execute(
                    select(Referral).where(
                        Referral.code == code_obj.code,
                        Referral.referred_user_id.is_(None),
                    )
                )
                referral = result.scalar_one_or_none()
                if referral:
                    await ref_service.record_referral_attribution(referral.id)
            await self.db.flush()

    async def track_referral_view_by_code(self, token: str, referral_code: str) -> None:
        """Track referral attribution when a viewer uses a ?ref= code on a share link."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        result = await self.db.execute(
            select(DeliveryLink).where(DeliveryLink.token_hash == token_hash)
        )
        link = result.scalar_one_or_none()
        if link:
            from app.services.referrals.service import ReferralService

            ref_service = ReferralService(self.db)
            await ref_service.repo.record_referral_view_on_link(link.id, referral_code)

    async def get_link_by_token(self, token_hash: str) -> DeliveryLink | None:
        result = await self.db.execute(
            select(DeliveryLink).where(DeliveryLink.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def increment_link_views(self, link_id: UUID) -> None:
        link = await self.db.get(DeliveryLink, link_id)
        if link:
            link.view_count = (link.view_count or 0) + 1
            link.last_opened_at = datetime.now(UTC)
            await self.db.flush()

    async def create_delivery(self, delivery: Delivery) -> Delivery:
        self.db.add(delivery)
        await self.db.flush()
        return delivery

    async def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        result = await self.db.execute(select(Delivery).where(Delivery.id == delivery_id))
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: UUID) -> list[Delivery]:
        result = await self.db.execute(
            select(Delivery)
            .where(Delivery.project_id == project_id)
            .order_by(Delivery.created_at.desc())
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
