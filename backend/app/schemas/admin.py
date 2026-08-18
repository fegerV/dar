from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AdminDashboardStats(BaseModel):
    total_users: int
    total_projects: int
    total_payments: float
    pending_reviews: int
    active_generations: int
    running_jobs: int
    queued_jobs: int
    failed_jobs: int
    ai_cost_today: float
    revenue_today: float
    profit_today: float


class AdminUserResponse(BaseModel):
    id: UUID
    status: str
    email: str | None = None
    display_name: str | None = None
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminTemplateCreate(BaseModel):
    code: str
    title: str
    description: str | None = None
    kind: str = "video"
    category: str | None = None
    occasion_codes: list[str] = []
    relationship_types: list[str] = []
    moods: list[str] = []
    base_price_rub: float = 0


class AdminTemplateResponse(BaseModel):
    id: UUID
    code: str
    title: str
    description: str | None = None
    kind: str
    status: str
    category: str | None = None
    occasion_codes: list[str] = []
    relationship_types: list[str] = []
    moods: list[str] = []
    base_price_rub: float
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminGenerationResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    progress: int
    current_step: str | None = None
    model_name: str | None = None
    attempt: int
    error_code: str | None = None
    error_message: str | None = None
    cost_rub: float
    duration_ms: int | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdminOrderResponse(BaseModel):
    id: UUID
    project_id: UUID
    requested_by_user_id: UUID | None = None
    status: str
    cost_rub: float
    template_version_id: UUID | None = None
    model_name: str | None = None
    error_code: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdminWorkerResponse(BaseModel):
    id: UUID
    name: str
    status: str
    gpu_model: str | None = None
    gpu_vram_total_gb: int | None = None
    gpu_vram_used_gb: int | None = None
    cpu_usage_percent: float | None = None
    jobs_today: int
    failures_today: int
    avg_generation_time_sec: float | None = None
    last_heartbeat_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminQueueJobResponse(BaseModel):
    id: UUID
    generation_id: UUID
    worker_id: UUID | None = None
    status: str
    priority: int
    error_code: str | None = None
    error_message: str | None = None
    retry_count: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminPaymentResponse(BaseModel):
    id: UUID
    user_id: UUID | None = None
    amount_rub: float
    method: str
    status: str
    provider_id: UUID | None = None
    external_payment_id: str | None = None
    created_at: datetime
    paid_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdminAuditLogResponse(BaseModel):
    id: UUID
    actor_user_id: UUID | None = None
    action: str
    target_type: str | None = None
    target_id: UUID | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminSystemSettingsResponse(BaseModel):
    id: UUID
    key: str
    value: dict
    description: str | None = None
    is_public: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminSystemSettingsUpdate(BaseModel):
    value: dict
