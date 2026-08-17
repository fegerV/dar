from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brief import CreativeBrief
from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: UUID, owner_user_id: UUID) -> Project | None:
        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.owner_user_id == owner_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_owner(
        self,
        owner_user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Project], int]:
        query = select(Project).where(Project.owner_user_id == owner_user_id)
        count_query = select(func.count()).select_from(Project).where(
            Project.owner_user_id == owner_user_id
        )

        if status:
            query = query.where(Project.status == status)
            count_query = count_query.where(Project.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.order_by(Project.updated_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, project: Project) -> Project:
        self.db.add(project)
        await self.db.flush()
        return project

    async def update(self, project: Project) -> Project:
        await self.db.flush()
        return project

    async def get_brief(self, project_id: UUID) -> CreativeBrief | None:
        result = await self.db.execute(
            select(CreativeBrief).where(CreativeBrief.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def create_brief(self, brief: CreativeBrief) -> CreativeBrief:
        self.db.add(brief)
        await self.db.flush()
        return brief

    async def update_brief(self, brief: CreativeBrief) -> CreativeBrief:
        await self.db.flush()
        return brief
