
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.pricing import (
    PriceRequest,
    PriceResponse,
    PromoCodeValidateRequest,
    PromoCodeValidateResponse,
)
from app.services.pricing.service import PricingService

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.post("/calculate", response_model=PriceResponse)
async def calculate_price(
    body: PriceRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PricingService(db)
    return await service.calculate_price(body)


@router.post("/promo/validate", response_model=PromoCodeValidateResponse)
async def validate_promo_code(
    body: PromoCodeValidateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PricingService(db)
    return await service.validate_promo_code(body)
