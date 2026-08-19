from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.calendar import TodayPackResponse
from app.services.calendar.engine import CalendarEngine

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/today", response_model=TodayPackResponse)
async def get_today_pack(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = CalendarEngine(db)
    pack = await service.get_today_pack(current_user.id)
    return TodayPackResponse(**pack)


@router.get("/date/{target_date}", response_model=list[dict])
async def get_holidays_for_date(
    target_date: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        d = date.fromisoformat(target_date)
    except ValueError:
        from app.core.exceptions import ValidationException
        raise ValidationException("Invalid date format, use YYYY-MM-DD")
    service = CalendarEngine(db)
    return await service.get_todays_holidays(d)


@router.get("/nearby", response_model=list[dict])
async def get_nearby_holidays(
    days_ahead: int = Query(default=30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).date()
    service = CalendarEngine(db)
    return await service.find_holiday_near(today, days_ahead)
