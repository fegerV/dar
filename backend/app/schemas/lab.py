from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LabScenarioRead(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None
    category: str | None
    difficulty: str | None
    prompt_template: str | None
    negative_strategy: str | None
    target_duration_sec: int | None
    target_camera: str | None
    target_motion: str | None
    tags: list[str]
    meta: dict
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LabScenarioCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=120)
    description: str | None = None
    category: str | None = Field(default=None, max_length=50)
    difficulty: str | None = Field(default=None, max_length=20)
    prompt_template: str | None = None
    negative_strategy: str | None = None
    target_duration_sec: int | None = Field(default=None, ge=1, le=120)
    target_camera: str | None = Field(default=None, max_length=50)
    target_motion: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list)
    meta: dict = Field(default_factory=dict)
    is_active: bool = True


class LabPhotoRead(BaseModel):
    id: UUID
    scenario_code: str | None
    filename: str
    original_name: str | None
    file_url: str
    file_size_bytes: int | None
    mime_type: str | None
    width: int | None
    height: int | None
    quality_score: float | None
    face_count: int | None
    metadata: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class LabBenchmarkRead(BaseModel):
    id: UUID
    scenario_id: UUID
    photo_id: UUID | None
    model_name: str
    model_version: str | None
    status: str
    cost_estimate: float | None
    actual_cost: float | None
    generation_time_sec: float | None
    success_rate: float | None
    avg_generations: float | None
    quality_score: float | None
    output_url: str | None
    error_message: str | None
    raw_result: dict
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    scenario: LabScenarioRead | None = None
    photo: LabPhotoRead | None = None

    model_config = {"from_attributes": True}


class LabBenchmarkCreate(BaseModel):
    scenario_id: UUID
    photo_id: UUID | None = None
    model_name: str = Field(..., max_length=50)
    model_version: str | None = Field(default=None, max_length=50)
    cost_estimate: float | None = Field(default=None, ge=0)


class LabBenchmarkResultUpdate(BaseModel):
    status: str | None = None
    actual_cost: float | None = Field(default=None, ge=0)
    generation_time_sec: float | None = Field(default=None, ge=0)
    success_rate: float | None = Field(default=None, ge=0, le=1)
    avg_generations: float | None = Field(default=None, ge=0)
    quality_score: float | None = Field(default=None, ge=0, le=1)
    output_url: str | None = None
    error_message: str | None = None
    raw_result: dict | None = None


class LabRecipeProposalRead(BaseModel):
    id: UUID
    benchmark_id: UUID
    recipe_code: str
    recipe_name: str
    template_code: str
    model_name: str
    confidence_score: float | None
    auto_generated: bool
    approved: bool | None
    approved_by: str | None
    approved_at: datetime | None
    applied_to_production: bool
    metadata: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class LabRecipeProposalApprove(BaseModel):
    approved: bool
    recipe_name: str | None = Field(default=None, max_length=120)
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class LabStatsResponse(BaseModel):
    total_scenarios: int
    total_photos: int
    total_benchmarks: int
    completed_benchmarks: int
    failed_benchmarks: int
    avg_quality_score: float | None
    avg_success_rate: float | None
    avg_cost: float | None
    proposals_approved: int
    proposals_applied: int
