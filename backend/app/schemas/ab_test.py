from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ABTestVariantSchema(BaseModel):
    code: str
    title: str
    config: dict = Field(default_factory=dict)
    traffic_weight: int = 50
    is_control: bool = False


class ABTestVariantCreate(BaseModel):
    code: str
    title: str
    config: dict = Field(default_factory=dict)
    traffic_weight: int = 50
    is_control: bool = False


class ABTestVariantResponse(BaseModel):
    id: UUID
    code: str
    title: str
    config: dict = Field(default_factory=dict)
    traffic_weight: int
    is_control: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ABTestCreate(BaseModel):
    name: str
    description: str | None = None
    target: str
    traffic_allocation: int = 100
    variants: list[ABTestVariantCreate]


class ABTestResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    target: str
    status: str
    traffic_allocation: int
    start_date: datetime | None = None
    end_date: datetime | None = None
    variants: list[ABTestVariantResponse] = Field(default_factory=list)
    metrics: list[dict] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ABTestStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(draft|running|completed|archived)$")


class ABTestResultRecord(BaseModel):
    variant_code: str
    metric: str
    value: float
