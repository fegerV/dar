from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.core.exceptions import NotFoundException
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


class PromptCompilerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)

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

    async def compile_prompt(self, body: CompilePromptRequest, user_id: UUID | None = None) -> PromptPlanResponse:
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

        system_prompt = template_version.prompt_config.get("system_prompt", "") if template_version else None
        user_prompt = template_version.prompt_config.get("style", "") if template_version else None

        scenes = []
        if template_version:
            scene_rows = await self.db.execute(
                select(Scene).where(Scene.template_version_id == body.template_version_id)
            )
            for scene in scene_rows.scalars().all():
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
            created_at=datetime.now(timezone.utc),
        )

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

    def _character_block(self, brief: CreativeBriefRead) -> str:
        parts = []
        if brief.recipient:
            parts.append(f"{brief.recipient.get('name','')}, {brief.recipient.get('age','')} years old")
        if brief.relationship_:
            parts.append(f"relationship: {brief.relationship_}")
        return ", ".join(parts) if parts else ""

    def _resolve(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value)
