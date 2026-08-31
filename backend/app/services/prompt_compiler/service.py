from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.project import Project
from app.models.template import Scene, TemplateVersion
from app.repositories.projects import ProjectRepository
from app.schemas.brief import CreativeBriefRead
from app.schemas.prompt_compiler import (
    CompilePromptRequest,
    PromptPlanResponse,
    PromptPlanScene,
    VariableResolutionRequest,
    VariableResolutionResponse,
)
from app.services.calendar.engine import CalendarEngine
from app.services.relationships.service import RelationshipContextService


class PromptCompilerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.calendar = CalendarEngine(db)
        self.relationship_service = RelationshipContextService(db)

    def compile(self, template_version: TemplateVersion, brief: CreativeBriefRead, scene: Scene | None = None) -> str:
        sections: list[str] = []
        sections.append("SYSTEM:\n" + self._resolve(template_version.prompt_config.get("system_prompt", "")))
        sections.append("CHARACTER:\n" + self._character_block(brief))
        sections.append("PERSONALITY:\n" + ", ".join(brief.personality or []))
        if brief.interests:
            sections.append("INTERESTS:\n" + ", ".join(brief.interests))
        if scene:
            sections.append("SCENE:\n" + self._resolve(scene.scene_config.get("prompt", scene.title)))
        sections.append("STYLE:\n" + self._resolve(template_version.prompt_config.get("style", "")))
        if brief.inside_joke:
            sections.append("INSIDE_JOKE:\n" + brief.inside_joke)
        if brief.sender_message:
            sections.append("MESSAGE:\n" + brief.sender_message)
        negative = template_version.prompt_config.get("negative_prompt")
        if negative:
            sections.append("NEGATIVE:\n" + negative)
        return "\n\n".join(sections)

    def compile_deterministic(
        self,
        template_version: TemplateVersion,
        brief: CreativeBriefRead,
        scene: Scene | None = None,
        recipient: object | None = None,
    ) -> str:
        context = self._build_context(brief, recipient)

        system_prompt = self._resolve(template_version.prompt_config.get("system_prompt", ""), context)
        character_block = self._character_block(brief, context)
        personality = ", ".join(brief.personality or [])
        interests = ", ".join(brief.interests or [])
        scene_prompt = ""
        if scene:
            scene_prompt = self._resolve(scene.scene_config.get("prompt", scene.title), context)
        style = self._resolve(template_version.prompt_config.get("style", ""), context)
        inside_joke = self._resolve(brief.inside_joke or "", context)
        sender_message = self._resolve(brief.sender_message or "", context)
        negative = template_version.prompt_config.get("negative_prompt", "")

        sections: list[str] = []
        if system_prompt:
            sections.append(f"SYSTEM:\n{system_prompt}")
        if character_block:
            sections.append(f"CHARACTER:\n{character_block}")
        if personality:
            sections.append(f"PERSONALITY:\n{personality}")
        if interests:
            sections.append(f"INTERESTS:\n{interests}")
        if scene_prompt:
            sections.append(f"SCENE:\n{scene_prompt}")
        if style:
            sections.append(f"STYLE:\n{style}")
        if inside_joke:
            sections.append(f"INSIDE_JOKE:\n{inside_joke}")
        if sender_message:
            sections.append(f"MESSAGE:\n{sender_message}")
        if negative:
            sections.append(f"NEGATIVE:\n{negative}")

        return "\n\n".join(sections)

    def _build_context(
        self, brief: CreativeBriefRead, recipient: object | None = None
    ) -> dict[str, Any]:
        context: dict[str, Any] = {}

        if hasattr(recipient, "first_name"):
            context["first_name"] = recipient.first_name
        if hasattr(recipient, "last_name"):
            context["last_name"] = recipient.last_name or ""
        if hasattr(recipient, "nickname"):
            context["nickname"] = recipient.nickname or ""
        if hasattr(recipient, "birth_date"):
            today = datetime.now(UTC).date()
            if recipient.birth_date:
                age = today.year - recipient.birth_date.year
                if (today.month, today.day) < (recipient.birth_date.month, recipient.birth_date.day):
                    age -= 1
                context["recipient_age"] = age
                context["recipient_birth_year"] = recipient.birth_date.year

        context["relationship"] = brief.relationship_ or ""
        context["relationship_text"] = brief.relationship_text or ""
        context["desired_mood"] = brief.desired_mood or ""
        context["occasion_text"] = brief.occasion_text or ""
        context["sender_role"] = brief.sender_role or ""
        context["recipient_role"] = brief.recipient_role or ""
        context["inside_joke"] = brief.inside_joke or ""
        context["sender_message"] = brief.sender_message or ""
        context["memorable_story"] = brief.memorable_story or ""
        context["hobbies_text"] = brief.hobbies_text or ""
        context["character_traits"] = brief.character_traits or ""
        context["desired_phrase"] = brief.desired_phrase or ""
        context["forbidden_topics"] = brief.forbidden_topics or ""
        context["humor_level"] = brief.humor_level or 50
        context["emotion_level"] = brief.emotion_level or 50
        context["surprise_level"] = brief.surprise_level or 50
        context["personalization_level"] = brief.personalization_level or 50

        if brief.personalization_answers:
            for k, v in brief.personalization_answers.items():
                context[f"answer_{k}"] = v

        return context

    async def compile_prompt(
        self, body: CompilePromptRequest, user_id: UUID | None = None
    ) -> PromptPlanResponse:
        if user_id is not None:
            project = await self.project_repo.get_by_id(body.project_id, user_id)
        else:
            project = await self.project_repo.get_by_id(body.project_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        brief = await self.project_repo.get_brief(body.project_id)

        template_version: TemplateVersion | None = None
        if body.template_version_id:
            result = await self.db.execute(
                select(TemplateVersion).where(TemplateVersion.id == body.template_version_id)
            )
            template_version = result.scalar_one_or_none()

        system_prompt = None
        user_prompt = None
        scenes = []

        if template_version:
            system_prompt = template_version.prompt_config.get("system_prompt", "") or None
            user_prompt = template_version.prompt_config.get("style", "") or None

            should_skip = self._evaluate_conditions(template_version, project, brief)
            if should_skip:
                return PromptPlanResponse(
                    project_id=body.project_id,
                    template_version_id=body.template_version_id,
                    scenes=[],
                    system_prompt="TEMPLATE_CONDITION_SKIPPED",
                    user_prompt="",
                    constraints={"skipped": True, "reason": should_skip},
                    created_at=datetime.now(UTC),
                )

            scene_rows = await self.db.execute(
                select(Scene).where(Scene.template_id == template_version.template_id)
            )
            for scene in scene_rows.scalars().all():
                if self._evaluate_scene_conditions(scene, project, brief):
                    scenes.append(
                        PromptPlanScene(
                            scene_id=scene.id,
                            code=scene.code,
                            title=scene.title,
                            type=scene.type,
                            prompt=scene.scene_config.get("prompt", "") if isinstance(scene.scene_config, dict) else "",
                            negative_prompt=scene.scene_config.get("negative_prompt") if isinstance(scene.scene_config, dict) else None,
                            parameters=body.variables or {},
                        )
                    )

        return PromptPlanResponse(
            project_id=body.project_id,
            template_version_id=body.template_version_id,
            scenes=scenes,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            constraints={},
            created_at=datetime.now(UTC),
        )

    def _evaluate_conditions(self, template_version: TemplateVersion, project: Project, brief: CreativeBriefRead) -> str | None:
        conditions = template_version.prompt_config.get("conditions", [])
        if not conditions:
            return None

        context = self._build_context(brief)
        for condition in conditions:
            if not self._evaluate_condition(condition, context):
                return condition.get("on_fail", "Condition not met")
        return None

    def _evaluate_scene_conditions(self, scene: Scene, project: Project, brief: CreativeBriefRead) -> bool:
        if not scene.condition:
            return True
        context = self._build_context(brief)
        return self._evaluate_condition(scene.condition, context)

    def _evaluate_condition(self, condition: dict, context: dict) -> bool:
        logic = condition.get("logic", "and")
        rules = condition.get("rules", [])
        if not rules:
            return True

        results = []
        for rule in rules:
            field = rule.get("field", "")
            op = rule.get("op", "eq")
            value = rule.get("value")
            actual = context.get(field)

            if op == "eq":
                result = actual == value
            elif op == "ne":
                result = actual != value
            elif op == "gt":
                result = actual is not None and actual > value
            elif op == "gte":
                result = actual is not None and actual >= value
            elif op == "lt":
                result = actual is not None and actual < value
            elif op == "lte":
                result = actual is not None and actual <= value
            elif op == "in":
                result = actual in value
            elif op == "not_in":
                result = actual not in value
            else:
                result = False
            results.append(result)

        if logic == "or":
            return any(results)
        return all(results)

    async def resolve_variables(self, body: VariableResolutionRequest) -> VariableResolutionResponse:
        template_version = await self.db.get(TemplateVersion, body.template_version_id)
        if template_version is None:
            raise NotFoundException("Template version not found")

        required = template_version.metadata_.get("required_variables", []) if template_version.metadata_ else []
        resolved = dict(body.variables)
        missing = [v for v in required if v not in body.variables or not body.variables[v]]
        warnings = [f"Variable '{v}' is required but missing" for v in missing]

        return VariableResolutionResponse(
            template_version_id=body.template_version_id,
            resolved=resolved,
            missing=missing,
            warnings=warnings,
        )

    def _character_block(self, brief: CreativeBriefRead, context: dict | None = None) -> str:
        context = context or self._build_context(brief)
        parts = []
        first_name = context.get("first_name", "")
        age = context.get("recipient_age")
        if first_name:
            if age:
                parts.append(f"{first_name}, {age} years old")
            else:
                parts.append(first_name)
        if context.get("relationship"):
            parts.append(f"relationship: {context['relationship']}")
        return ", ".join(parts) if parts else ""

    def _resolve(self, value: Any, context: dict | None = None) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            if context:
                try:
                    return value.format(**context)
                except (KeyError, ValueError):
                    return value
            return str(value)
        return str(value)
