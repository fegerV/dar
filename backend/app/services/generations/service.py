from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.generation import Generation, GenerationJob, GenerationStep
from app.models.project import Project
from app.repositories.generations import GenerationRepository
from app.repositories.projects import ProjectRepository
from app.schemas.generation import GenerationStartRequest, GenerationResponse, GenerationStepResponse


class GenerationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GenerationRepository(db)
        self.project_repo = ProjectRepository(db)

    async def start_generation(
        self, project_id: UUID, user_id: UUID, body: GenerationStartRequest
    ) -> GenerationResponse:
        project = await self.project_repo.get_by_id(project_id, user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        existing = await self.repo.get_latest_for_project(project_id, "final")
        if existing and existing.status in ("queued", "processing"):
            if not body.force_regenerate:
                raise ConflictException("Генерация уже запущена")

        generation = Generation(
            project_id=project_id,
            type="final",
            status="queued",
            input_json=body.variables or {},
        )
        generation = await self.repo.create(generation)

        steps = [
            GenerationStep(
                generation_id=generation.id,
                step_no=1,
                step_code="script",
                type="text",
                status="queued",
                input_json={"brief": {}},
            ),
            GenerationStep(
                generation_id=generation.id,
                step_no=2,
                step_code="voice",
                type="audio",
                status="queued",
                input_json={"script": {}},
            ),
            GenerationStep(
                generation_id=generation.id,
                step_no=3,
                step_code="video",
                type="video",
                status="queued",
                input_json={"script": {}, "voice": {}},
            ),
        ]
        for step in steps:
            await self.repo.create_step(step)

        job = GenerationJob(
            generation_id=generation.id,
            queue_name="generation",
            status="queued",
            payload={"project_id": str(project_id)},
        )
        await self.repo.create_job(job)

        await self.db.commit()
        return GenerationResponse.model_validate(generation)

    async def get_generation(self, generation_id: UUID) -> GenerationResponse:
        generation = await self.repo.get_by_id(generation_id)
        if generation is None:
            raise NotFoundException("Генерация не найдена")
        steps = await self.repo.get_steps(generation_id)
        response = GenerationResponse.model_validate(generation)
        response.output_assets = []
        return response

    async def list_generations(
        self, project_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[GenerationResponse], int]:
        generations, total = await self.repo.list_by_project(project_id, page, page_size)
        return [GenerationResponse.model_validate(g) for g in generations], total

    async def cancel_generation(self, generation_id: UUID) -> GenerationResponse:
        generation = await self.repo.get_by_id(generation_id)
        if generation is None:
            raise NotFoundException("Генерация не найдена")
        generation.status = "cancelled"
        await self.repo.update(generation)
        await self.db.commit()
        return GenerationResponse.model_validate(generation)
