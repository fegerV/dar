from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.payment import Entitlement
from app.repositories.pricing import PricingRepository
from app.schemas.pricing import PriceResponse, PromoCodeValidateRequest, PromoCodeValidateResponse


class PricingService:
    BASE_PRICE = Decimal("590.00")
    DURATION_MULTIPLIERS = {
        (0, 30): Decimal("1.0"),
        (30, 60): Decimal("1.5"),
        (60, 120): Decimal("2.0"),
        (120, 300): Decimal("2.5"),
    }
    RESOLUTION_MULTIPLIERS = {
        "720p": Decimal("1.0"),
        "1080p": Decimal("1.2"),
        "4k": Decimal("1.8"),
    }
    PERSONALIZATION_MULTIPLIERS = {
        (0, 30): Decimal("1.0"),
        (30, 60): Decimal("1.1"),
        (60, 80): Decimal("1.25"),
        (80, 101): Decimal("1.5"),
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PricingRepository(db)

    async def calculate_price(self, body: PriceRequest) -> PriceResponse:
        project = await self.repo.get_project(body.project_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        template = None
        if body.template_version_id:
            version = await self.repo.get_template_version(body.template_version_id)
            if version:
                template = await self.repo.get_template(version.template_id)

        base_price = Decimal(str(template.base_price_rub)) if template else self.BASE_PRICE

        duration_multiplier = self._get_duration_multiplier(body.duration_sec or 30)
        resolution_multiplier = self.RESOLUTION_MULTIPLIERS.get(body.resolution or "1080p", Decimal("1.0"))
        personalization_level = project.metadata.get("personalization_level", 50) if project.metadata else 50
        personalization_multiplier = self._get_personalization_multiplier(personalization_level)

        price = base_price * duration_multiplier * resolution_multiplier * personalization_multiplier
        price = price.quantize(Decimal("0.01"))

        discount_rub = Decimal("0.00")
        bonus_discount_rub = Decimal("0.00")
        free_generation_available = False

        if body.promo_code:
            promo_result = await self._apply_promo_code(body.project_id, body.promo_code, price)
            if promo_result.valid:
                discount_rub = promo_result.discount_rub or Decimal("0.00")

        entitlement = await self.repo.get_entitlement_by_code(project.owner_user_id, "free_generation")
        if entitlement and entitlement.consumed < entitlement.quantity:
            free_generation_available = True
            bonus_discount_rub = price
            price = Decimal("0.00")

        total_rub = max(Decimal("0.00"), price - discount_rub - bonus_discount_rub)

        return PriceResponse(
            project_id=body.project_id,
            base_price_rub=base_price,
            duration_multiplier=duration_multiplier,
            resolution_multiplier=resolution_multiplier,
            personalization_multiplier=personalization_multiplier,
            discount_rub=discount_rub,
            bonus_discount_rub=bonus_discount_rub,
            total_rub=total_rub,
            promo_code=body.promo_code,
            free_generation_available=free_generation_available,
        )

    async def validate_promo_code(self, body: PromoCodeValidateRequest) -> PromoCodeValidateResponse:
        return PromoCodeValidateResponse(
            valid=True,
            discount_type="fixed",
            discount_value=Decimal("100.00"),
            discount_rub=Decimal("100.00"),
        )

    def _get_duration_multiplier(self, duration_sec: int) -> Decimal:
        for (min_d, max_d), multiplier in self.DURATION_MULTIPLIERS.items():
            if min_d <= duration_sec < max_d:
                return multiplier
        return Decimal("2.5")

    def _get_personalization_multiplier(self, level: int) -> Decimal:
        for (min_l, max_l), multiplier in self.PERSONALIZATION_MULTIPLIERS.items():
            if min_l <= level < max_l:
                return multiplier
        return Decimal("1.5")

    async def _apply_promo_code(
        self, project_id: UUID, code: str, price: Decimal
    ) -> PromoCodeValidateResponse:
        return PromoCodeValidateResponse(
            valid=True,
            discount_type="fixed",
            discount_value=Decimal("100.00"),
            discount_rub=min(Decimal("100.00"), price),
        )
