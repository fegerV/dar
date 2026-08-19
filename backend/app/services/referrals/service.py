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
    MAX_ATTRIBUTIONS_PER_CODE = 10

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

        success = await self.repo.increment_code_uses(code.id, code.max_uses)
        if not success:
            await self.db.rollback()
            raise ValidationException("Реферальный код больше не действителен")

        await self.db.commit()
        return ReferralResponse.model_validate(referral)

    async def mark_referral_completed(self, user_id: UUID) -> ReferralResponse | None:
        from sqlalchemy import update as sa_update

        from app.services.payments.service import PaymentService

        result = await self.db.execute(
            sa_update(Referral)
            .where(
                Referral.referred_user_id == user_id,
                Referral.status == "pending",
            )
            .values(
                status="completed",
                completed_at=datetime.now(UTC),
                referrer_bonus_granted=True,
                referee_bonus_granted=True,
            )
            .returning(Referral)
        )
        referral = result.one_or_none()
        if referral is None:
            return None

        payment_service = PaymentService(self.db)
        await payment_service.wallet_service.credit(
            referral.referrer_user_id, self.REFERRER_BONUS_RUB, bonus=True
        )
        await payment_service.wallet_service.credit(
            user_id, self.REFEREE_BONUS_RUB, bonus=True
        )

        await self.db.commit()
        return ReferralResponse.model_validate(referral)

    async def record_referral_attribution(self, referral_id: UUID) -> None:
        """Record that a referral was attributed via a share link view (fraud prevention)."""
        referral = await self.db.get(Referral, referral_id)
        if not referral:
            return

        metadata = dict(referral.metadata_ or {})
        attribution_count = metadata.get("share_attributions", 0)

        if attribution_count >= self.MAX_ATTRIBUTIONS_PER_CODE:
            return

        metadata["share_attributions"] = attribution_count + 1
        referral.metadata_ = metadata
        await self.db.flush()

    async def validate_referral_code(self, code: str, user_id: UUID) -> bool:
        """Fraud prevention: validate code, prevent self-referral, check limits."""
        code_obj = await self.repo.get_by_code(code)
        if not code_obj or code_obj.user_id == user_id:
            return False

        existing = await self.repo.get_referral_by_referee(user_id)
        if existing:
            return False

        return True

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
