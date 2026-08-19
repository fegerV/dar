import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.generation import Generation, GenerationJob, GenerationStep
from app.models.payment import Entitlement, Payment
from app.models.project import Project
from app.repositories.generations import GenerationRepository
from app.repositories.projects import ProjectRepository
from app.schemas.generation import GenerationResponse, GenerationStartRequest

logger = logging.getLogger(__name__)


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
            existing.status = "cancelled"
            await self.repo.update(existing)

        await self._verify_payment_or_entitlement(project_id, user_id, project)

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

        try:
            from app.workers.generation_tasks import process_generation_job

            process_generation_job.apply_async(args=[str(job.id)], countdown=5)
        except ImportError:
            logger.warning("Celery not available — job %s queued but not dispatched", job.id)

        return GenerationResponse.model_validate(generation)

    async def _verify_payment_or_entitlement(
        self, project_id: UUID, user_id: UUID, project: Project
    ) -> None:
        """Check if user has paid or has an available entitlement before allowing generation."""
        price = float(project.price_rub or 0)

        if price <= 0:
            entitlement = await self._check_entitlement(user_id)
            if not entitlement:
                raise ValidationException(
                    "Entitlement required for free generation"
                )
            await self._consume_entitlement(user_id, project, entitlement)
            return

        payment_result = await self.db.execute(
            select(Payment).where(
                Payment.project_id == project_id,
                Payment.user_id == user_id,
                Payment.status == "paid",
            )
        )
        paid = payment_result.scalar_one_or_none()
        if paid is None:
            if project.paid_rub and project.paid_rub > 0:
                return
            entitlement = await self._check_entitlement(user_id)
            if not entitlement:
                raise ValidationException(
                    "Payment required before generation"
                )
            await self._consume_entitlement(user_id, project, entitlement)

    async def _check_entitlement(self, user_id: UUID):
        result = await self.db.execute(
            select(Entitlement).where(
                Entitlement.user_id == user_id,
                Entitlement.code == "welcome_generation",
                Entitlement.consumed < Entitlement.quantity,
            )
        )
        return result.scalar_one_or_none()

    async def _consume_entitlement(
        self, user_id: UUID, project: Project, entitlement: Entitlement
    ) -> None:
        from app.repositories.entitlements import EntitlementRepository

        ent_repo = EntitlementRepository(self.db)
        success = await ent_repo.consume(entitlement.id, user_id, 1)
        if not success:
            raise ValidationException("Entitlement already consumed")
        project.paid_rub = float(project.price_rub or 0)
        await self.project_repo.update(project)
        await self.db.commit()

    async def get_generation(
        self, generation_id: UUID, user_id: UUID | None = None
    ) -> GenerationResponse:
        generation = await self.repo.get_by_id(generation_id)
        if generation is None:
            raise NotFoundException("Генерация не найдена")
        if user_id is not None:
            project = await self.project_repo.get_by_id(generation.project_id, user_id)
            if project is None:
                raise NotFoundException("Генерация не найдена")
        response = GenerationResponse.model_validate(generation)
        response.output_assets = []
        return response

    async def list_generations(
        self, project_id: UUID, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[GenerationResponse], int]:
        project = await self.project_repo.get_by_id(project_id, user_id)
        if project is None:
            raise NotFoundException("Проект не найден")
        generations, total = await self.repo.list_by_project(project_id, page, page_size)
        return [GenerationResponse.model_validate(g) for g in generations], total

    async def cancel_generation(self, generation_id: UUID, user_id: UUID) -> GenerationResponse:
        generation = await self.repo.get_by_id(generation_id)
        if generation is None:
            raise NotFoundException("Генерация не найдена")
        project = await self.project_repo.get_by_id(generation.project_id, user_id)
        if project is None:
            raise NotFoundException("Генерация не найдена")
        generation.status = "cancelled"
        await self.repo.update(generation)
        await self.db.commit()
        return GenerationResponse.model_validate(generation)
