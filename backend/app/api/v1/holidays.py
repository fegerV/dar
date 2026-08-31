
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.holidays import HolidayRepository
from app.schemas.holiday import HolidayResponse

router = APIRouter(prefix="/holidays", tags=["Holidays"])


@router.get("", response_model=list[HolidayResponse])
async def list_holidays(
    kind: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repo = HolidayRepository(db)
    holidays = await repo.list_active(kind=kind)
    return [HolidayResponse.model_validate(h) for h in holidays]
