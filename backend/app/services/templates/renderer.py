import logging
import re
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.asset import Asset, StorageObject
from app.models.template import Scene, SceneVariable, TemplateVersion
from app.repositories.recommendations import TemplateRepository
from app.schemas.template_render import (
    RenderedAsset,
    RenderedAudio,
    RenderSceneResponse,
    RenderTemplateRequest,
    RenderTemplateResponse,
)
from app.services.cache.template_cache import TemplateCacheManager

logger = logging.getLogger(__name__)


class TemplateRenderer:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.template_repo = TemplateRepository(db)
        self.cache = TemplateCacheManager(db)

    async def render_template(
        self, body: RenderTemplateRequest, fallback_to_cache: bool = True
    ) -> RenderTemplateResponse:
        try:
            return await self._render_template_internal(body)
        except Exception as e:
            if not fallback_to_cache:
                raise
            if isinstance(e, NotFoundException):
                cached = await self._get_cached_render(body.template_version_id)
                if cached:
                    logger.info(
                        "Graceful degradation: using cached template render for %s",
                        body.template_version_id,
                    )
                    return cached
            raise

    async def _render_template_internal(
        self, body: RenderTemplateRequest
    ) -> RenderTemplateResponse:
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

            raw_assets = scene.scene_config.get("assets", [])
            rendered_assets = await self._resolve_assets(raw_assets)

            audio_overlay = await self._resolve_audio(scene.scene_config)
            if audio_overlay is None:
                audio_overlay = await self._resolve_audio(version.render_config or {})

            rendered_scenes.append(
                RenderSceneResponse(
                    scene_id=scene.id,
                    code=scene.code,
                    title=scene.title,
                    rendered_prompt=rendered_prompt,
                    duration_sec=duration,
                    assets=raw_assets,
                    rendered_assets=rendered_assets,
                    audio_overlay=audio_overlay,
                )
            )

        preview_url = None
        if template.preview_asset_id:
            preview_url = await self._resolve_asset_url(template.preview_asset_id)

        template_audio = await self._resolve_audio(version.render_config or {})

        result = RenderTemplateResponse(
            template_version_id=body.template_version_id,
            scenes=rendered_scenes,
            total_duration_sec=total_duration,
            preview_url=preview_url,
            render_config=version.render_config or {},
            audio_overlay=template_audio,
        )

        await self._store_cache(body.template_version_id, result)
        return result

    async def _get_scenes(self, template_id: UUID) -> list[Scene]:
        result = await self.db.execute(
            select(Scene).where(Scene.template_id == template_id).order_by(Scene.created_at.asc())
        )
        return list(result.scalars().all())

    async def _get_variables(self, template_version_id: UUID) -> list[SceneVariable]:
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

    async def _resolve_assets(self, raw_assets: list) -> list[RenderedAsset]:
        rendered = []
        for entry in raw_assets:
            if isinstance(entry, dict):
                asset_id = entry.get("asset_id") or entry.get("id")
                if asset_id:
                    try:
                        asset_id = UUID(str(asset_id))
                    except (ValueError, TypeError):
                        pass
                    rendered.append(await self._resolve_single_asset(asset_id))
                elif entry.get("type") == "static" or entry.get("source"):
                    rendered.append(RenderedAsset(
                        asset_id=None,
                        type=entry.get("type", "text"),
                        url=entry.get("url"),
                    ))
            elif isinstance(entry, str):
                rendered.append(RenderedAsset(asset_id=None, type="text", url=entry))
        return rendered

    async def _resolve_single_asset(self, asset_id: UUID) -> RenderedAsset:
        asset = await self._get_asset(asset_id)
        if asset is None:
            return RenderedAsset(asset_id=asset_id, type="missing", url=None)

        url = await self._resolve_asset_url(asset_id)
        return RenderedAsset(
            asset_id=asset_id,
            type=asset.type,
            url=url,
            width=asset.width,
            height=asset.height,
            duration_sec=float(asset.duration_sec) if asset.duration_sec else None,
            mime_type=asset.mime_type,
        )

    async def _get_asset(self, asset_id: UUID) -> Asset | None:
        result = await self.db.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def _resolve_audio(self, config: dict | None) -> RenderedAudio | None:
        if not config:
            return None

        audio_config = config.get("audio") or config.get("audio_overlay")
        if not audio_config:
            return None

        if isinstance(audio_config, str):
            return RenderedAudio(url=audio_config)

        if isinstance(audio_config, dict):
            result = RenderedAudio(
                volume=audio_config.get("volume"),
                offset_sec=audio_config.get("offset_sec"),
            )
            asset_id = audio_config.get("asset_id") or audio_config.get("id")
            if asset_id:
                result.asset_id = asset_id if isinstance(asset_id, UUID) else UUID(asset_id)
                result.url = await self._resolve_asset_url(result.asset_id)
            elif audio_config.get("url"):
                result.url = audio_config["url"]
            return result

        return None

    async def _resolve_asset_url(self, asset_id: UUID) -> str | None:
        from app.integrations.storage.factory import get_storage_provider

        asset = await self._get_asset(asset_id)
        if asset is None:
            return None

        storage_obj_result = await self.db.execute(
            select(StorageObject).where(StorageObject.id == asset.storage_object_id)
        )
        storage_obj = storage_obj_result.scalar_one_or_none()
        if storage_obj is None:
            return None

        try:
            storage = get_storage_provider()
            return await storage.generate_presigned_url(
                bucket=storage_obj.bucket,
                object_key=storage_obj.object_key,
                expires_in=3600,
            )
        except Exception as e:
            logger.warning("Failed to generate presigned URL for asset %s: %s", asset_id, e)
            return None

    async def _get_cached_render(self, template_version_id: UUID) -> RenderTemplateResponse | None:
        return await self.cache.get_rendered_template(template_version_id)

    async def _store_cache(
        self, template_version_id: UUID, result: RenderTemplateResponse
    ) -> None:
        await self.cache.store_rendered_template(template_version_id, result)
