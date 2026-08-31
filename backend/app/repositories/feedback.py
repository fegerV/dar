from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback


class FeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, feedback: Feedback):
        self.db.add(feedback)
        await self.db.flush()
        return feedback

    async def list_recent(self, limit: int = 100):
        stmt = select(Feedback).order_by(Feedback.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
