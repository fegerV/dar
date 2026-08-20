import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.integrations.ai.base import ProviderRegistry
from app.integrations.ai.registry import create_provider_registry
from app.models.brief import CreativeBrief
from app.models.generation import GenerationStep
from app.models.template import PromptTemplate
from app.repositories.projects import ProjectRepository
from app.repositories.recipients import RecipientRepository
from app.schemas.brief import CreativeBriefRead
from app.services.prompt_compiler.service import PromptCompilerService

logger = logging.getLogger(__name__)


class ScriptGenerationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.prompt_compiler = PromptCompilerService(db)
        self._registry: ProviderRegistry | None = None

    @property
    def registry(self) -> ProviderRegistry:
        if self._registry is None:
            self._registry = create_provider_registry()
        return self._registry

    @property
    def recipient_repo(self) -> RecipientRepository:
        if not hasattr(self, "_recipient_repo"):
            self._recipient_repo = RecipientRepository(self.db)
        return self._recipient_repo

    async def generate_script(
        self,
        project_id: UUID,
        owner_user_id: UUID,
        generation_step_id: UUID,
    ) -> dict[str, Any]:
        project = await self.project_repo.get_by_id(project_id, owner_user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(project_id)
        if brief is None:
            raise NotFoundException("Бриф не найден")

        brief_read = CreativeBriefRead.model_validate(brief)

        recipient = None
        if project.recipient_id:
            recipient = await self.recipient_repo.get_by_id(
                project.recipient_id, owner_user_id
            )

        from dataclasses import dataclass

        @dataclass
        class _TemplateVersion:
            prompt_config: dict[str, Any]

        tv = _TemplateVersion(prompt_config={})

        prompt = self.prompt_compiler.compile_deterministic(
            tv,
            brief_read,
            recipient=recipient,
        )

        ai_result = await self._generate_with_ai(prompt, brief)
        if ai_result is not None and ai_result.get("text"):
            script = ai_result["text"]
            provider_used = ai_result.get("model", "ai")
            source = "ai"
            logger.info("Script generated via AI for step %s", generation_step_id)
        else:
            template = await self._find_cached_template(project, brief)
            if template:
                script = self._render_cached_template(template, prompt)
                provider_used = "cached_template"
                source = "fallback_template"
                logger.warning(
                    "AI generation failed for step %s — fell back to cached template %s",
                    generation_step_id,
                    template.code,
                )
            else:
                script = prompt
                provider_used = "raw_prompt"
                source = "raw_prompt"
                logger.warning(
                    "No AI and no cached template for step %s — using raw prompt",
                    generation_step_id,
                )

        result = {
            "script": script,
            "source": source,
            "provider": provider_used,
            "generated_at": datetime.now(UTC).isoformat(),
        }

        step_result = await self.db.execute(
            select(GenerationStep).where(GenerationStep.id == generation_step_id)
        )
        step = step_result.scalar_one_or_none()
        if step:
            step.output_json = result
            step.status = "completed"
            step.completed_at = datetime.now(UTC)
            await self.db.flush()

        await self.db.commit()
        return result

    async def _generate_with_ai(
        self, prompt: str, brief: CreativeBrief
    ) -> dict[str, Any] | None:
        provider = self.registry.get_text()
        if provider is None or not provider.enabled:
            logger.warning("No text AI provider available")
            return None

        try:
            result = await provider.generate_text(prompt, {
                "temperature": (brief.humor_level or 50) / 100,
                "max_tokens": brief.desired_length_sec or 1000,
            })
        except Exception as exc:
            logger.warning("AI text provider %s raised: %s", provider.name, exc)
            return None

        if result is None:
            logger.warning("AI provider %s returned None", provider.name)
            return None

        if result.get("error"):
            logger.warning("AI provider %s returned error: %s", provider.name, result["error"])
            return None

        if not result.get("text"):
            logger.warning("AI provider %s returned empty text", provider.name)
            return None

        return result

    async def _find_cached_template(
        self, project, brief: CreativeBrief
    ) -> PromptTemplate | None:
        query = select(PromptTemplate).where(
            PromptTemplate.is_active == True,  # noqa: E712
        )

        or_conditions = []
        if project.occasion_code:
            or_conditions.append(PromptTemplate.category == project.occasion_code)
        if brief.relationship_:
            or_conditions.append(PromptTemplate.category == brief.relationship_)

        if or_conditions:
            from sqlalchemy import or_
            query = query.where(or_(*or_conditions))
        else:
            query = query.where(PromptTemplate.category == "default")

        query = query.order_by(PromptTemplate.success_rate.desc()).limit(5)
        result = await self.db.execute(query)
        return result.scalars().first()

    def _render_cached_template(
        self, template: PromptTemplate, prompt: str
    ) -> str:
        text = template.text
        variables = template.variables
        context = {
            "base_prompt": prompt,
            "occasion": "",
            "relationship": "",
        }
        for var in variables:
            if var not in context:
                context[var] = ""

        try:
            rendered = text.format(**context)
        except (KeyError, ValueError, IndexError):
            rendered = text

        return rendered
