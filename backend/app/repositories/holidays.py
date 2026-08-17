from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.holiday import Holiday


class HolidayRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_active(self, kind: str | None = None):
        stmt = select(Holiday).where(Holiday.status == "active")
        if kind:
            stmt = stmt.where(Holiday.kind == kind)
        result = await self.db.execute(stmt.order_by(Holiday.sort_order.asc()))
        return list(result.scalars().all())

    async def get_by_code(self, code: str) -> Holiday | None:
        result = await self.db.execute(select(Holiday).where(Holiday.code == code))
        return result.scalar_one_or_none()
