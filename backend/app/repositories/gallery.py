from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.gallery import GalleryStatus, GallerySubmission


class GalleryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, submission: GallerySubmission) -> GallerySubmission:
        self.db.add(submission)
        await self.db.flush()
        return submission

    async def get_by_id(self, submission_id: UUID) -> GallerySubmission | None:
        result = await self.db.execute(
            select(GallerySubmission).where(GallerySubmission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def list_pending(self, limit: int = 50) -> list[GallerySubmission]:
        result = await self.db.execute(
            select(GallerySubmission)
            .where(GallerySubmission.status == GalleryStatus.pending)
            .order_by(GallerySubmission.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_approved_public(self, limit: int = 100) -> list[GallerySubmission]:
        result = await self.db.execute(
            select(GallerySubmission)
            .where(
                GallerySubmission.status == GalleryStatus.approved,
                GallerySubmission.is_public.is_(True),
                GallerySubmission.consent_given.is_(True),
            )
            .order_by(GallerySubmission.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        submission_id: UUID,
        status: GalleryStatus,
        moderator_id: UUID | None = None,
        is_public: bool | None = None,
    ) -> GallerySubmission | None:
        submission = await self.db.get(GallerySubmission, submission_id)
        if not submission:
            return None

        from datetime import datetime

        submission.status = status
        if moderator_id is not None:
            submission.moderator_id = moderator_id
        submission.reviewed_at = datetime.now(UTC)
        if is_public is not None:
            submission.is_public = is_public
        await self.db.flush()
        return submission

    async def list_by_user(self, user_id: UUID) -> list[GallerySubmission]:
        result = await self.db.execute(
            select(GallerySubmission)
            .where(GallerySubmission.user_id == user_id)
            .order_by(GallerySubmission.created_at.desc())
        )
        return list(result.scalars().all())
