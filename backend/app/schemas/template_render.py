from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RenderVariable(BaseModel):
    code: str
    value: str | None = None
    type: str = "text"


class RenderSceneRequest(BaseModel):
    scene_id: UUID
    variables: dict[str, str | None] = Field(default_factory=dict)


class RenderSceneResponse(BaseModel):
    scene_id: UUID
    code: str
    title: str
    rendered_prompt: str | None = None
    duration_sec: int | None = None
    assets: list[dict] = []


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
