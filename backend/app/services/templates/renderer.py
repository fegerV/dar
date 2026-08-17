import re
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.template import Scene, SceneVariable, TemplateVersion
from app.repositories.recommendations import TemplateRepository
from app.schemas.template_render import (
    RenderSceneRequest,
    RenderSceneResponse,
    RenderTemplateRequest,
    RenderTemplateResponse,
)


class TemplateRenderer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.template_repo = TemplateRepository(db)

    async def render_template(self, body: RenderTemplateRequest) -> RenderTemplateResponse:
        version = await self.template_repo.get_version_by_id(body.template_version_id)
        if version is None:
            raise NotFoundException("Версия шаблона не найдена")

        template = await self.template_repo.get_by_id(version.template_id)
        if template is None:
            raise NotFoundException("Шаблон не найден")

        scenes = await self._get_scenes(version.template_id)
        variables = await self._get_variables(version.id)

        rendered_scenes = []
        total_duration = 0

        for scene in scenes:
            scene_vars = {
                var.code: body.variables.get(var.code, var.default_value)
                for var in variables
                if var.scene_id == scene.id
            }
            scene_vars.update(body.variables)

            rendered_prompt = self._substitute_variables(
                scene.scene_config.get("prompt_template", ""),
                scene_vars,
            )

            duration = scene.duration_sec or version.max_duration_sec or 30
            total_duration += duration

            rendered_scenes.append(
                RenderSceneResponse(
                    scene_id=scene.id,
                    code=scene.code,
                    title=scene.title,
                    rendered_prompt=rendered_prompt,
                    duration_sec=duration,
                    assets=scene.scene_config.get("assets", []),
                )
            )

        preview_url = None
        if template.preview_asset_id:
            preview_url = f"/assets/{template.preview_asset_id}"

        return RenderTemplateResponse(
            template_version_id=body.template_version_id,
            scenes=rendered_scenes,
            total_duration_sec=total_duration,
            preview_url=preview_url,
            render_config=version.render_config or {},
        )

    async def _get_scenes(self, template_id: UUID) -> list[Scene]:
        from sqlalchemy import select
        result = await self.db.execute(
            select(Scene).where(Scene.template_id == template_id).order_by(Scene.created_at.asc())
        )
        return list(result.scalars().all())

    async def _get_variables(self, template_version_id: UUID) -> list[SceneVariable]:
        from sqlalchemy import select
        result = await self.db.execute(
            select(SceneVariable)
            .join(Scene, SceneVariable.scene_id == Scene.id)
            .join(TemplateVersion, Scene.template_id == TemplateVersion.template_id)
            .where(TemplateVersion.id == template_version_id)
        )
        return list(result.scalars().all())

    def _substitute_variables(self, template_text: str, variables: dict[str, str | None]) -> str:
        if not template_text:
            return ""

        def replace_var(match):
            var_name = match.group(1)
            value = variables.get(var_name)
            if value is None:
                return match.group(0)
            return str(value)

        pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}")
        return pattern.sub(replace_var, template_text)

    def validate_render(self, render_result: RenderTemplateResponse) -> None:
        if render_result.total_duration_sec and render_result.total_duration_sec < 5:
            raise ValidationException("Видео слишком короткое (минимум 5 секунд)")

        if render_result.total_duration_sec and render_result.total_duration_sec > 300:
            raise ValidationException("Видео слишком длинное (максимум 5 минут)")

        for scene in render_result.scenes:
            if not scene.rendered_prompt:
                raise ValidationException(f"Не заполнена сцена: {scene.code}")
