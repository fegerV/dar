
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.referral import ReferralCodeResponse, ReferralResponse, ReferralStatsResponse
from app.services.referrals.service import ReferralService

router = APIRouter(prefix="/referrals", tags=["Referrals"])


@router.get("/me/code", response_model=ReferralCodeResponse)
async def get_my_code(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReferralService(db)
    code = await service.get_my_code(current_user.id)
    if not code:
        code = await service.get_or_create_code(current_user.id)
    return code


@router.get("/me/stats", response_model=ReferralStatsResponse)
async def get_my_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReferralService(db)
    return await service.get_stats(current_user.id)


@router.post("/apply", response_model=ReferralResponse)
async def apply_code(
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ReferralService(db)
    return await service.apply_code(current_user.id, body.get("code", ""))
