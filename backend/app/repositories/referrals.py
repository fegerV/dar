from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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

    async def get_referral_by_referee(self, referee_id) -> Referral | None:
        result = await self.db.execute(select(Referral).where(Referral.referred_user_id == referee_id))
        return result.scalar_one_or_none()

    async def create_referral(self, referral: Referral) -> Referral:
        self.db.add(referral)
        await self.db.flush()
        return referral
