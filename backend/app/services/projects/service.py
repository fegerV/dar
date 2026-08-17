from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.brief import CreativeBrief
from app.models.project import Project
from app.repositories.projects import ProjectRepository
from app.repositories.recipients import RecipientRepository
from app.schemas.brief import BriefCompleteResponse, BriefUpdate
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.recipient_repo = RecipientRepository(db)

    async def create(self, owner_user_id: UUID, body: ProjectCreate) -> ProjectResponse:
        recipient = await self.recipient_repo.get_by_id(body.recipient_id, owner_user_id)
        if recipient is None:
            raise NotFoundException("Получатель не найден")

        project = Project(
            owner_user_id=owner_user_id,
            **body.model_dump(),
        )
        project = await self.project_repo.create(project)
        await self.db.flush()
        return ProjectResponse.model_validate(project)

    async def get(self, owner_user_id: UUID, project_id: UUID) -> ProjectResponse:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")
        return ProjectResponse.model_validate(project)

    async def list(
        self,
        owner_user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[ProjectResponse], int]:
        projects, total = await self.project_repo.list_by_owner(
            owner_user_id, page, page_size, status
        )
        return [ProjectResponse.model_validate(p) for p in projects], total

    async def update(
        self, owner_user_id: UUID, project_id: UUID, body: ProjectUpdate
    ) -> ProjectResponse:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)

        project.updated_at = datetime.now(timezone.utc)
        await self.project_repo.update(project)
        await self.db.flush()
        return ProjectResponse.model_validate(project)

    async def get_brief(self, owner_user_id: UUID, project_id: UUID) -> BriefUpdate:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            return BriefUpdate()
        return BriefUpdate.model_validate(brief)

    async def save_brief(
        self, owner_user_id: UUID, project_id: UUID, body: BriefUpdate
    ) -> BriefUpdate:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            brief = CreativeBrief(project_id=project_id)
            brief = await self.project_repo.create_brief(brief)

        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(brief, key, value)

        brief.updated_at = datetime.now(timezone.utc)
        await self.project_repo.update_brief(brief)
        await self.db.flush()
        return BriefUpdate.model_validate(brief)

    async def complete_brief(
        self, owner_user_id: UUID, project_id: UUID
    ) -> BriefCompleteResponse:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            raise NotFoundException("Бриф не найден")

        brief.status = "completed"
        brief.completed_at = datetime.now(timezone.utc)
        project.status = "recommendations_ready"
        project.updated_at = datetime.now(timezone.utc)

        await self.project_repo.update_brief(brief)
        await self.project_repo.update(project)
        await self.db.flush()

        return BriefCompleteResponse(project_id=project_id, status=project.status)
