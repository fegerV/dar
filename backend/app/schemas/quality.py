from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class QualityCheckRequest(BaseModel):
    generation_id: UUID
    asset_ids: list[UUID] = Field(default_factory=list)
    check_types: list[str] = Field(default_factory=lambda: ["duration", "resolution", "audio", "fps", "face_count", "semantic", "face_landmarks", "blink"])
    prompt: str | None = None


class QualityCheckResponse(BaseModel):
    id: UUID
    generation_id: UUID
    asset_id: UUID | None = None
    status: str
    checks: dict = {}
    passed: bool = False
    reviewed_by_user_id: UUID | None = None
    review_comment: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ManualReviewRequest(BaseModel):
    passed: bool
    comment: str | None = None


class ManualReviewResponse(BaseModel):
    id: UUID
    generation_id: UUID
    status: str
    passed: bool
    review_comment: str | None = None
    reviewed_at: datetime

    model_config = {"from_attributes": True}


class VideoCriticResponse(BaseModel):
    id: UUID
    generation_id: UUID
    identity_score: float | None = None
    motion_score: float | None = None
    prompt_adherence: float | None = None
    face_quality: float | None = None
    artifact_score: float | None = None
    overall: float | None = None
    decision: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class QualityGateResponse(BaseModel):
    generation_id: UUID
    status: str
    auto_checks_passed: bool
    manual_review_required: bool
    final_status: str
    checks: list[QualityCheckResponse] = []
    critic: VideoCriticResponse | None = None

    model_config = {"from_attributes": True}
