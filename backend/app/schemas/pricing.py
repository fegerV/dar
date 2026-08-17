from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PriceRequest(BaseModel):
    project_id: UUID
    template_version_id: UUID | None = None
    duration_sec: int | None = None
    resolution: str | None = "1080p"
    promo_code: str | None = None


class PriceResponse(BaseModel):
    project_id: UUID
    base_price_rub: Decimal
    duration_multiplier: Decimal
    resolution_multiplier: Decimal
    personalization_multiplier: Decimal
    discount_rub: Decimal
    bonus_discount_rub: Decimal
    total_rub: Decimal
    currency: str = "RUB"
    promo_code: str | None = None
    free_generation_available: bool = False


class PromoCodeValidateRequest(BaseModel):
    code: str
    project_id: UUID | None = None
    user_id: UUID | None = None


class PromoCodeValidateResponse(BaseModel):
    valid: bool
    discount_type: str | None = None
    discount_value: Decimal | None = None
    discount_rub: Decimal | None = None
    error: str | None = None
