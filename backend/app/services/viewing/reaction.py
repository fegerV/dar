from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.viewing import ViewingReaction
from app.schemas.viewing import ReactionStatsResponse


class ReactionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_reaction(
        self,
        project_id: UUID,
        user_id: UUID | None,
        emoji: str,
        rating: int | None = None,
        comment: str | None = None,
        negative_details: dict | None = None,
    ) -> ViewingReaction:
        reaction = ViewingReaction(
            project_id=project_id,
            user_id=user_id,
            emoji=emoji,
            rating=rating,
            comment=comment,
            negative_details=negative_details,
            created_at=datetime.now(UTC),
        )
        self.db.add(reaction)
        await self.db.flush()
        return reaction

    async def get_stats(
        self, project_id: UUID, user_id: UUID | None = None
    ) -> ReactionStatsResponse:
        if user_id is not None:
            project_result = await self.db.execute(
                select(Project).where(
                    Project.id == project_id,
                    Project.owner_user_id == user_id,
                )
            )
            project = project_result.scalar_one_or_none()
            if project is None:
                from app.core.exceptions import NotFoundException
                raise NotFoundException("Project not found")

        result = await self.db.execute(
            select(
                ViewingReaction.emoji,
                func.count().label("count"),
            ).where(ViewingReaction.project_id == project_id).group_by(ViewingReaction.emoji)
        )
        by_emoji = {row.emoji: row.count for row in result.all()}

        total_result = await self.db.execute(
            select(func.count()).select_from(ViewingReaction).where(
                ViewingReaction.project_id == project_id
            )
        )
        total = total_result.scalar() or 0

        rating_result = await self.db.execute(
            select(func.avg(ViewingReaction.rating)).where(
                ViewingReaction.project_id == project_id,
                ViewingReaction.rating.is_not(None),
            )
        )
        avg_rating = rating_result.scalar()
        avg_rating = round(float(avg_rating), 2) if avg_rating is not None else None

        negative_count = by_emoji.get("cry", 0)

        return ReactionStatsResponse(
            project_id=project_id,
            total_reactions=total,
            by_emoji=by_emoji,
            average_rating=avg_rating,
            negative_count=negative_count,
        )

    async def get_comment_details(
        self, project_id: UUID, user_id: UUID | None = None
    ) -> list[dict]:
        if user_id is not None:
            project_result = await self.db.execute(
                select(Project).where(
                    Project.id == project_id,
                    Project.owner_user_id == user_id,
                )
            )
            project = project_result.scalar_one_or_none()
            if project is None:
                from app.core.exceptions import NotFoundException
                raise NotFoundException("Project not found")

        result = await self.db.execute(
            select(ViewingReaction)
            .where(
                ViewingReaction.project_id == project_id,
                ViewingReaction.comment.is_not(None),
            )
            .order_by(ViewingReaction.created_at.desc())
        )
        return [
            {
                "emoji": r.emoji,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in result.scalars().all()
        ]
