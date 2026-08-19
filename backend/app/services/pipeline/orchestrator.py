import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.generation import Generation, GenerationJob, GenerationStep
from app.models.payment import Payment
from app.models.project import Project
from app.repositories.generations import GenerationRepository
from app.repositories.projects import ProjectRepository
from app.schemas.pipeline import PipelineRunRequest, PipelineRunResponse, PipelineStepResponse
from app.services.ai.orchestrator import AIOrchestrator
from app.services.generations.service import GenerationService
from app.services.prompt_compiler.service import PromptCompilerService


class PipelineOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.generation_repo = GenerationRepository(db)
        self.project_repo = ProjectRepository(db)
        self.ai = AIOrchestrator(db)
        self.compiler = PromptCompilerService(db)

    async def run(self, body: PipelineRunRequest, user_id: UUID) -> PipelineRunResponse:
        project = await self.project_repo.get_by_id(body.project_id, user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        if project.status not in ("template_selected", "queued", "failed"):
            raise ConflictException(f"Невозможно запустить pipeline для статуса: {project.status}")

        existing = await self.generation_repo.get_latest_for_project(body.project_id, "final")
        if existing and existing.status in ("queued", "processing") and not body.force_restart:
            raise ConflictException("Пайплайн уже запущен")

        if existing and existing.status in ("queued", "processing") and body.force_restart:
            existing.status = "cancelled"
            await self.generation_repo.update(existing)
            await self.db.commit()

        gen_service = GenerationService(self.db)
        await gen_service._verify_payment_or_entitlement(body.project_id, user_id, project)

        generation = Generation(
            project_id=body.project_id,
            type="final",
            status="queued",
            input_json={},
        )
        generation = await self.generation_repo.create(generation)

        steps = self._build_default_steps(generation.id)
        for step in steps:
            await self.generation_repo.create_step(step)

        job = GenerationJob(
            generation_id=generation.id,
            queue_name="generation",
            status="queued",
            payload={"project_id": str(body.project_id)},
        )
        await self.generation_repo.create_job(job)

        project.status = "queued"
        await self.project_repo.update(project)
        await self.db.commit()

        step_responses = [
            PipelineStepResponse(
                id=step.id,
                step_no=step.step_no,
                step_code=step.step_code,
                type=step.type,
                status=step.status,
                input_json=step.input_json,
                output_json=step.output_json,
                error_message=step.error_message,
                created_at=step.created_at,
                started_at=step.started_at,
                completed_at=step.completed_at,
            )
            for step in steps
        ]

        return PipelineRunResponse(
            generation_id=generation.id,
            project_id=body.project_id,
            status=generation.status,
            progress=0,
            current_step=None,
            steps=step_responses,
            created_at=generation.created_at,
            completed_at=generation.completed_at,
        )

    def _build_default_steps(self, generation_id: UUID) -> list[GenerationStep]:
        return [
            GenerationStep(
                generation_id=generation_id,
                step_no=1,
                step_code="script",
                type="text",
                status="queued",
                input_json={},
            ),
            GenerationStep(
                generation_id=generation_id,
                step_no=2,
                step_code="voice",
                type="audio",
                status="queued",
                input_json={},
            ),
            GenerationStep(
                generation_id=generation_id,
                step_no=3,
                step_code="video",
                type="video",
                status="queued",
                input_json={},
            ),
            GenerationStep(
                generation_id=generation_id,
                step_no=4,
                step_code="compose",
                type="composite",
                status="queued",
                input_json={},
            ),
            GenerationStep(
                generation_id=generation_id,
                step_no=5,
                step_code="upload",
                type="storage",
                status="queued",
                input_json={},
            ),
        ]
