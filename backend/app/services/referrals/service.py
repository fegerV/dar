from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.referral import Referral, ReferralCode
from app.repositories.referrals import ReferralRepository
from app.schemas.referral import ReferralCodeResponse, ReferralResponse, ReferralStatsResponse


class ReferralService:
    REFERRER_BONUS_RUB = 200.00
    REFEREE_BONUS_RUB = 100.00

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ReferralRepository(db)

    async def get_my_code(self, user_id: UUID) -> ReferralCodeResponse | None:
        code = await self.repo.get_by_user(user_id)
        if not code:
            return None
        return ReferralCodeResponse.model_validate(code)

    async def get_or_create_code(self, user_id: UUID) -> ReferralCodeResponse:
        code = await self.repo.get_by_user(user_id)
        if code:
            return ReferralCodeResponse.model_validate(code)

        import secrets

        short_code = f"{secrets.token_hex(3).upper()}"
        code = ReferralCode(
            user_id=user_id,
            code=short_code,
            is_active=True,
            uses_count=0,
            created_at=datetime.now(UTC),
        )
        code = await self.repo.create_code(code)
        await self.db.commit()
        return ReferralCodeResponse.model_validate(code)

    async def apply_code(self, user_id: UUID, code_text: str) -> ReferralResponse:
        code = await self.repo.get_code_by_text(code_text)
        if not code or not code.is_active:
            raise NotFoundException("Реферальный код не найден")
        if code.user_id == user_id:
            raise ValidationException("Нельзя использовать собственный реферальный код")
        if code.max_uses is not None and code.uses_count >= code.max_uses:
            raise ValidationException("Код больше не действителен")

        existing = await self.repo.get_referral_by_referee(user_id)
        if existing:
            raise ConflictException("Реферальная связь уже установлена")

        referral = Referral(
            referrer_user_id=code.user_id,
            referred_user_id=user_id,
            code=code.code,
            status="pending",
            created_at=datetime.now(UTC),
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
        referral.completed_at = datetime.now(UTC)

        if not referral.referrer_bonus_granted:
            from app.services.payments.service import PaymentService
            payment_service = PaymentService(self.db)
            await payment_service.wallet_service.credit(
                referral.referrer_user_id, self.REFERRER_BONUS_RUB, bonus=True
            )
            referral.referrer_bonus_granted = True

        if not referral.referee_bonus_granted:
            from app.services.payments.service import PaymentService
            payment_service = PaymentService(self.db)
            await payment_service.wallet_service.credit(
                user_id, self.REFEREE_BONUS_RUB, bonus=True
            )
            referral.referee_bonus_granted = True

        await self.db.commit()
        return ReferralResponse.model_validate(referral)

    async def get_stats(self, user_id: UUID) -> ReferralStatsResponse:
        code_result = await self.db.execute(
            select(ReferralCode).where(ReferralCode.user_id == user_id)
        )
        code = code_result.scalar_one_or_none()

        referrals_result = await self.db.execute(
            select(Referral).where(Referral.referrer_user_id == user_id)
        )
        referrals = list(referrals_result.scalars().all())

        completed_count = sum(1 for r in referrals if r.status == "completed")

        return ReferralStatsResponse(
            referral_code=code.code if code else None,
            total_referrals=len(referrals),
            completed_referrals=completed_count,
            referrer_bonus_granted=sum(
                1 for r in referrals if r.referrer_bonus_granted
            ),
            referee_bonus_granted=sum(
                1 for r in referrals if r.referee_bonus_granted
            ),
            earned_rub=round(completed_count * self.REFERRER_BONUS_RUB, 2),
            referrer_bonus_rub=self.REFERRER_BONUS_RUB,
            referee_bonus_rub=self.REFEREE_BONUS_RUB,
        )
