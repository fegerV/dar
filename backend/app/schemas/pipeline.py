from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineStepRequest(BaseModel):
    step_code: str = Field(..., pattern="^(script|voice|video|compose|upload)$")
    parameters: dict = Field(default_factory=dict)


class PipelineRunRequest(BaseModel):
    project_id: UUID
    steps: list[PipelineStepRequest] = Field(default_factory=list)
    force_restart: bool = False


class PipelineStepResponse(BaseModel):
    id: UUID
    step_no: int
    step_code: str
    type: str
    status: str
    input_json: dict = {}
    output_json: dict = {}
    error_message: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class PipelineRunResponse(BaseModel):
    generation_id: UUID
    project_id: UUID
    status: str
    progress: int
    current_step: str | None = None
    steps: list[PipelineStepResponse] = []
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}
