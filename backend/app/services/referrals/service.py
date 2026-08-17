from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.referral import Referral, ReferralCode
from app.repositories.referrals import ReferralRepository
from app.schemas.referral import ReferralCodeResponse, ReferralResponse


class ReferralService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ReferralRepository(db)

    async def get_my_code(self, user_id: UUID) -> ReferralCodeResponse | None:
        code = await self.repo.get_by_user(user_id)
        if not code:
            return None
        return ReferralCodeResponse.model_validate(code)

    async def create_code(self, user_id: UUID) -> ReferralCodeResponse:
        existing = await self.repo.get_by_user(user_id)
        if existing:
            raise ConflictException("Referral code already exists")

        base = f"user-{str(user_id)[:8]}"
        code = ReferralCode(
            user_id=user_id,
            code=base,
            is_active=True,
            uses_count=0,
            created_at=datetime.now(timezone.utc),
        )
        code = await self.repo.create_code(code)
        await self.db.commit()
        return ReferralCodeResponse.model_validate(code)

    async def apply_code(self, user_id: UUID, code_text: str) -> ReferralResponse:
        code = await self.repo.get_code_by_text(code_text)
        if not code or not code.is_active:
            raise NotFoundException("Referral code not found")
        if code.user_id == user_id:
            raise ValidationException("Cannot use your own referral code")

        existing = await self.repo.get_referral_by_referee(user_id)
        if existing:
            raise ConflictException("Referral already applied")

        referral = Referral(
            referrer_user_id=code.user_id,
            referred_user_id=user_id,
            code=code.code,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        referral = await self.repo.create_referral(referral)
        code.uses_count += 1
        await self.db.commit()
        return ReferralResponse.model_validate(referral)

    async def mark_referral_completed(self, user_id: UUID) -> ReferralResponse | None:
        referral = await self.repo.get_referral_by_referee(user_id)
        if not referral or referral.status != "pending":
            return None
        referral.status = "completed"
        await self.db.commit()
        return ReferralResponse.model_validate(referral)
