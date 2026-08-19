from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import Referral, ReferralCode


class ReferralRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id) -> ReferralCode | None:
        result = await self.db.execute(select(ReferralCode).where(ReferralCode.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_code_by_text(self, code: str) -> ReferralCode | None:
        result = await self.db.execute(select(ReferralCode).where(ReferralCode.code == code))
        return result.scalar_one_or_none()

    async def create_code(self, code: ReferralCode) -> ReferralCode:
        self.db.add(code)
        await self.db.flush()
        return code

    async def increment_code_uses(self, code_id: UUID, max_uses: int | None = None) -> bool:
        """Atomically increment uses_count if under max_uses. Returns True if incremented."""
        stmt = sa_update(ReferralCode).where(ReferralCode.id == code_id)
        if max_uses is not None:
            stmt = stmt.where(ReferralCode.uses_count < max_uses)
        stmt = stmt.values(uses_count=ReferralCode.uses_count + 1).returning(ReferralCode.id)
        result = await self.db.execute(stmt)
        return result.one_or_none() is not None

    async def get_referral_by_referee(self, referee_id) -> Referral | None:
        result = await self.db.execute(
            select(Referral).where(Referral.referred_user_id == referee_id)
        )
        return result.scalar_one_or_none()

    async def create_referral(self, referral: Referral) -> Referral:
        self.db.add(referral)
        await self.db.flush()
        return referral

    async def get_by_code(self, code: str) -> ReferralCode | None:
        result = await self.db.execute(select(ReferralCode).where(ReferralCode.code == code))
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 100):
        stmt = select(Referral).order_by(Referral.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def record_referral_view_on_link(self, link_id: UUID, referral_code: str) -> None:
        """Record a referral attribution view from a share link with ?ref= code."""
        from app.models.delivery import DeliveryLink
        from app.services.referrals.service import ReferralService

        link = await self.db.get(DeliveryLink, link_id)
        if not link:
            return

        if link.referral_code and link.referral_code != referral_code:
            return

        link.referral_code = referral_code
        link.referral_attribution_count = (link.referral_attribution_count or 0) + 1

        result = await self.db.execute(
            select(Referral).where(
                Referral.code == referral_code,
                Referral.referred_user_id.is_(None),
            )
        )
        referral = result.scalar_one_or_none()
        if referral:
            ref_service = ReferralService(self.db)
            await ref_service.record_referral_attribution(referral.id)

        await self.db.flush()
