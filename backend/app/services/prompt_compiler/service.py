import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.brief import CreativeBrief
from app.models.project import Project
from app.models.recipient import Recipient
from app.models.template import Scene, SceneVariable, TemplateVersion
from app.repositories.projects import ProjectRepository
from app.repositories.recipients import RecipientRepository
from app.repositories.recommendations import TemplateRepository
from app.schemas.prompt_compiler import (
    CompilePromptRequest,
    PromptPlanResponse,
    VariableResolutionRequest,
    VariableResolutionResponse,
)


class PromptCompilerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.recipient_repo = RecipientRepository(db)
        self.template_repo = TemplateRepository(db)

    async def compile_prompt(self, body: CompilePromptRequest) -> PromptPlanResponse:
        project = await self.project_repo.get_by_id(body.project_id, body.project_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(body.project_id)
        if brief is None:
            raise NotFoundException("Бриф не найден")

        recipient = None
        if project.recipient_id:
            recipient = await self.recipient_repo.get_by_id(
                project.recipient_id, project.owner_user_id
            )

        template_version_id = body.template_version_id or project.selected_template_version_id
        if template_version_id is None:
            raise ValidationException("Шаблон не выбран. Сначала выберите рекомендацию.")

        version = await self.template_repo.get_version_by_id(template_version_id)
        if version is None:
            raise NotFoundException("Версия шаблона не найдена")

        template = await self.template_repo.get_by_id(version.template_id)
        scenes = await self._get_scenes(version.template_id)
        variables = await self._get_variables(version.id)

        context = self._build_context(project, brief, recipient, body.variables or {})
        system_prompt = self._build_system_prompt(version, context)
        user_prompt = self._build_user_prompt(version, context)

        compiled_scenes = []
        for scene in scenes:
            scene_vars = self._resolve_scene_variables(scene, variables, context)
            prompt = self._render_scene_prompt(scene, scene_vars)
            compiled_scenes.append(
                PromptPlanResponse(
                    project_id=body.project_id,
                    template_version_id=template_version_id,
                    scenes=[
                        PromptPlanScene(
                            scene_id=scene.id,
                            code=scene.code,
                            title=scene.title,
                            type=scene.scene_config.get("type", "default"),
                            prompt=prompt,
                            negative_prompt=scene.scene_config.get("negative_prompt"),
                            parameters=scene.scene_config.get("parameters", {}),
                        )
                    ],
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    constraints=version.validation_config or {},
                    created_at=datetime.now(timezone.utc),
                )
            )

        return PromptPlanResponse(
            project_id=body.project_id,
            template_version_id=template_version_id,
            scenes=[s for p in compiled_scenes for s in p.scenes],
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            constraints=version.validation_config or {},
            created_at=datetime.now(timezone.utc),
        )

    async def resolve_variables(
        self, body: VariableResolutionRequest
    ) -> VariableResolutionResponse:
        version = await self.template_repo.get_version_by_id(body.template_version_id)
        if version is None:
            raise NotFoundException("Версия шаблона не найдена")

        variables = await self._get_variables(version.id)
        resolved = {}
        missing = []
        warnings = []

        for var in variables:
            value = body.variables.get(var.code, var.default_value)
            if value is None and var.required:
                missing.append(var.code)
                warnings.append(f"Обязательная переменная '{var.code}' не заполнена")
            elif value is not None:
                resolved[var.code] = str(value)

        return VariableResolutionResponse(
            template_version_id=body.template_version_id,
            resolved=resolved,
            missing=missing,
            warnings=warnings,
        )

    async def _get_scenes(self, template_id: UUID) -> list[Scene]:
        result = await self.db.execute(
            select(Scene).where(Scene.template_id == template_id).order_by(Scene.created_at.asc())
        )
        return list(result.scalars().all())

    async def _get_variables(self, template_version_id: UUID) -> list[SceneVariable]:
        result = await self.db.execute(
            select(SceneVariable).where(SceneVariable.template_version_id == template_version_id)
        )
        return list(result.scalars().all())

    def _build_context(
        self, project: Project, brief: CreativeBrief, recipient: Recipient | None, variables: dict
    ) -> dict:
        context = {
            "project_id": str(project.id),
            "occasion_code": project.occasion_code,
            "occasion_title": project.occasion_title,
            "relationship": brief.relationship,
            "desired_mood": brief.desired_mood,
            "desired_length_sec": brief.desired_length_sec,
            "humor_level": brief.humor_level,
            "emotion_level": brief.emotion_level,
            "surprise_level": brief.surprise_level,
            "personalization_level": brief.personalization_level,
            "inside_joke": brief.inside_joke,
            "hobbies_text": brief.hobbies_text,
            "character_traits": brief.character_traits,
            "memorable_story": brief.memorable_story,
            "desired_phrase": brief.desired_phrase,
            "sender_message": brief.sender_message,
        }
        if recipient:
            context.update(
                {
                    "recipient_name": recipient.first_name,
                    "recipient_last_name": recipient.last_name,
                    "recipient_gender": recipient.gender,
                    "recipient_birth_date": recipient.birth_date.isoformat() if recipient.birth_date else None,
                    "recipient_city": recipient.city,
                    "recipient_occupation": recipient.occupation,
                    "recipient_interests": recipient.interests,
                    "recipient_traits": recipient.traits,
                }
            )
        context.update(variables)
        return context

    def _build_system_prompt(self, version: TemplateVersion, context: dict) -> str:
        base = version.prompt_config.get("system_prompt", "Ты — режиссёр видеопоздравлений.")
        return base

    def _build_user_prompt(self, version: TemplateVersion, context: dict) -> str:
        parts = []
        if context.get("occasion_code"):
            parts.append(f"Повод: {context['occasion_code']}")
        if context.get("recipient_name"):
            parts.append(f"Получатель: {context['recipient_name']}")
        if context.get("desired_mood"):
            parts.append(f"Настроение: {context['desired_mood']}")
        if context.get("inside_joke"):
            parts.append(f"Внутренняя шутка: {context['inside_joke']}")
        if context.get("sender_message"):
            parts.append(f"Сообщение отправителя: {context['sender_message']}")
        return "\n".join(parts)

    def _resolve_scene_variables(
        self, scene: Scene, variables: list[SceneVariable], context: dict
    ) -> dict[str, str | None]:
        resolved = dict(context)
        for var in variables:
            if var.scene_id == scene.id:
                value = context.get(var.code, var.default_value)
                if value is not None:
                    resolved[var.code] = str(value)
        return resolved

    def _render_scene_prompt(self, scene: Scene, variables: dict[str, str | None]) -> str:
        template_text = scene.scene_config.get("prompt_template", "")
        if not template_text:
            return scene.title

        def replace_var(match):
            var_name = match.group(1)
            value = variables.get(var_name)
            if value is None:
                return match.group(0)
            return str(value)

        pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}")
        return pattern.sub(replace_var, template_text)
