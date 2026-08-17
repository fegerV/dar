from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.feedback import Feedback


class FeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, feedback: Feedback):
        self.db.add(feedback)
        await self.db.flush()
        return feedback
