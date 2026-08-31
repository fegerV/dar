from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RenderedAsset(BaseModel):
    asset_id: UUID | None = None
    type: str
    url: str | None = None
    width: int | None = None
    height: int | None = None
    duration_sec: float | None = None
    mime_type: str | None = None


class RenderedAudio(BaseModel):
    asset_id: UUID | None = None
    url: str | None = None
    volume: float | None = None
    offset_sec: float | None = None


class RenderSceneRequest(BaseModel):
    scene_id: UUID
    variables: dict[str, str | None] = Field(default_factory=dict)


class RenderSceneResponse(BaseModel):
    scene_id: UUID
    code: str
    title: str
    rendered_prompt: str | None = None
    duration_sec: int | None = None
    assets: list[Any] = []
    rendered_assets: list[RenderedAsset] = []
    audio_overlay: RenderedAudio | None = None


class RenderTemplateRequest(BaseModel):
    template_version_id: UUID
    variables: dict[str, str | None] = Field(default_factory=dict)
    output_format: str = Field("json", pattern="^(json|yaml|txt)$")


class RenderTemplateResponse(BaseModel):
    template_version_id: UUID
    scenes: list[RenderSceneResponse]
    total_duration_sec: int | None = None
    preview_url: str | None = None
    render_config: dict = {}
    audio_overlay: RenderedAudio | None = None
