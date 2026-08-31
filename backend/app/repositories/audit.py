from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        await self.db.flush()
        return log

    async def list_by_actor(self, actor_user_id, limit: int = 100, offset: int = 0):
        stmt = (
            select(AuditLog)
            .where(AuditLog.actor_user_id == actor_user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_user_data(self, user_id) -> None:
        await self.db.execute(delete(AuditLog).where(AuditLog.actor_user_id == user_id))
        await self.db.flush()
