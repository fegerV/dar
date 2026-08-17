from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CompilePromptRequest(BaseModel):
    project_id: UUID
    template_version_id: UUID | None = None
    variables: dict | None = None
    force_regenerate: bool = False


class PromptPlanScene(BaseModel):
    scene_id: UUID
    code: str
    title: str
    type: str
    prompt: str
    negative_prompt: str | None = None
    parameters: dict = {}


class PromptPlanResponse(BaseModel):
    project_id: UUID
    template_version_id: UUID | None = None
    scenes: list[PromptPlanScene]
    system_prompt: str | None = None
    user_prompt: str | None = None
    constraints: dict = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class VariableResolutionRequest(BaseModel):
    template_version_id: UUID
    variables: dict[str, str | None] = Field(default_factory=dict)


class VariableResolutionResponse(BaseModel):
    template_version_id: UUID
    resolved: dict[str, str | None]
    missing: list[str] = []
    warnings: list[str] = []
