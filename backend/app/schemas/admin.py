from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RoleResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None = None
    permissions: list[str] = []
    is_system: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=120)
    description: str | None = None
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    permissions: list[str] | None = None


class UserRoleAssign(BaseModel):
    role_id: UUID
    granted_by: UUID | None = None


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
    phone: str | None = None
    locale: str | None = None
    last_seen_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserWalletResponse(BaseModel):
    user_id: UUID
    balance_rub: float
    bonus_balance: float
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class WalletAdjustmentRequest(BaseModel):
    amount_rub: float = Field(..., gt=0, description="Amount must be positive")
    type: str = Field(..., pattern="^(adjustment|bonus|refund|penalty)$", description="Transaction type")
    is_bonus: bool = False
    reason: str = Field(..., min_length=5, description="Reason for adjustment")


class WalletLedgerEntryResponse(BaseModel):
    id: UUID
    type: str
    amount_rub: float
    is_bonus: bool
    admin_id: UUID | None = None
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminLedgerTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    user_email: str | None = None
    wallet_id: UUID | None = None
    type: str
    amount_rub: float
    is_bonus: bool
    admin_id: UUID | None = None
    reason: str
    reference_id: UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminLedgerResponse(BaseModel):
    transactions: list[AdminLedgerTransactionResponse]
    total: int
    page: int
    page_size: int

    model_config = {"from_attributes": True}


class AdminReferralCodeResponse(BaseModel):
    id: UUID
    code: str
    is_active: bool
    uses_count: int
    max_uses: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminReferralResponse(BaseModel):
    id: UUID
    code: str
    status: str
    referrer_user_id: UUID
    referred_user_id: UUID | None = None
    referrer_bonus_granted: bool
    referee_bonus_granted: bool
    metadata: dict | None = None
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
    tags: list[str] = []
    base_price_rub: float = 0
    cost_price_rub: float = 0
    estimated_duration_sec: int | None = None
    difficulty: int | None = None
    personalization_score: int | None = None


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
    tags: list[str] = []
    base_price_rub: float
    cost_price_rub: float
    estimated_duration_sec: int | None = None
    difficulty: int | None = None
    personalization_score: int | None = None
    sort_order: int
    success_rate: float | None = None
    avg_rating: float | None = None
    usage_count: int
    completion_rate: float | None = None
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


class AdminGenerationDetailResponse(BaseModel):
    id: UUID
    project_id: UUID
    parent_generation_id: UUID | None = None
    template_version_id: UUID | None = None
    type: str
    status: str
    attempt: int
    requested_by_user_id: UUID | None = None
    provider_id: UUID | None = None
    model_name: str | None = None
    input_json: dict
    output_json: dict
    error_code: str | None = None
    error_message: str | None = None
    cost_rub: float
    duration_ms: int | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    progress: int
    current_step: str | None = None
    estimated_seconds: int | None = None
    steps: list["AdminGenerationStepResponse"] = []

    model_config = {"from_attributes": True}


class AdminGenerationStepResponse(BaseModel):
    id: UUID
    step_no: int
    step_code: str
    type: str
    status: str
    provider_id: UUID | None = None
    prompt_template_id: UUID | None = None
    input_json: dict
    output_json: dict
    error_code: str | None = None
    error_message: str | None = None
    cost_rub: float
    duration_ms: int | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

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


class AdminOrderDetailResponse(BaseModel):
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
    input_json: dict | None = None
    output_json: dict | None = None

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


class WorkerStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(idle|offline|active|maintenance)$")


class WorkerRestartResponse(BaseModel):
    success: bool
    message: str = ""
    worker_id: UUID


class QueueJobAction(BaseModel):
    action: str = Field(..., pattern="^(cancel|retry|prioritize|deprioritize)$")


class QueueJobBulkAction(BaseModel):
    action: str = Field(..., pattern="^(cancel|retry|prioritize|deprioritize)$")
    job_ids: list[UUID] = Field(..., min_length=1)


class QueueJobPriorityUpdate(BaseModel):
    priority: int = Field(..., ge=0, le=1000)


class AdminSetupRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    password: str = Field(..., min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None


class AdminTemplateUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    kind: str | None = None
    status: str | None = None
    category: str | None = None
    occasion_codes: list[str] | None = None
    relationship_types: list[str] | None = None
    moods: list[str] | None = None
    tags: list[str] | None = None
    base_price_rub: float | None = None
    cost_price_rub: float | None = None
    min_price_rub: float | None = None
    estimated_duration_sec: int | None = None
    difficulty: int | None = None
    personalization_score: int | None = None
    sort_order: int | None = None
    success_rate: float | None = None
    avg_rating: float | None = None
    usage_count: int | None = None
    completion_rate: float | None = None
    metadata_: dict | None = Field(default=None, alias="metadata")

    model_config = {"populate_by_name": True}


class AdminTemplateVersionResponse(BaseModel):
    id: UUID
    template_id: UUID
    version: int
    status: str
    schema_version: str
    prompt_config: dict
    render_config: dict
    personalization_config: dict
    validation_config: dict
    max_duration_sec: int | None = None
    created_at: datetime
    published_at: datetime | None = None
    retired_at: datetime | None = None
    variant_group: str | None = None
    variant_name: str | None = None

    model_config = {"from_attributes": True}


class AdminTemplateVersionCreate(BaseModel):
    version: int = 1
    status: str = "draft"
    schema_version: str = "1.0"
    prompt_config: dict = {}
    render_config: dict = {}
    personalization_config: dict = {}
    validation_config: dict = {}
    max_duration_sec: int | None = None
    qa_checklist: dict | None = None
    variant_group: str | None = None
    variant_name: str | None = None


class AdminTemplateVersionUpdate(BaseModel):
    status: str | None = None
    schema_version: str | None = None
    prompt_config: dict | None = None
    render_config: dict | None = None
    personalization_config: dict | None = None
    validation_config: dict | None = None
    max_duration_sec: int | None = None
    published_at: datetime | None = None
    retired_at: datetime | None = None
    variant_group: str | None = None
    variant_name: str | None = None
    qa_checklist: dict | None = None


class AdminSceneResponse(BaseModel):
    id: UUID
    template_id: UUID
    code: str
    title: str
    description: str | None = None
    source_type: str | None = None
    source_reference: str | None = None
    rights_status: str | None = None
    duration_sec: int | None = None
    source_asset_id: UUID | None = None
    preview_asset_id: UUID | None = None
    scene_config: dict
    condition: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminSceneCreate(BaseModel):
    code: str
    title: str
    description: str | None = None
    source_type: str | None = None
    source_reference: str | None = None
    rights_status: str | None = None
    duration_sec: int | None = None
    source_asset_id: UUID | None = None
    preview_asset_id: UUID | None = None
    scene_config: dict = {}
    condition: dict | None = None


class AdminSceneUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    source_type: str | None = None
    source_reference: str | None = None
    rights_status: str | None = None
    duration_sec: int | None = None
    source_asset_id: UUID | None = None
    preview_asset_id: UUID | None = None
    scene_config: dict | None = None
    condition: dict | None = None


class AdminSystemSettingsUpdate(BaseModel):
    value: dict


class AdminPromoCodeResponse(BaseModel):
    id: UUID
    code: str
    discount_type: str
    discount_value: float
    max_uses: int | None = None
    used_count: int
    expires_at: datetime | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminPromoCodeCreate(BaseModel):
    code: str
    discount_type: str = Field(..., pattern="^(fixed|percentage|bonus|free)$")
    discount_value: float = Field(..., gt=0)
    max_uses: int | None = None
    expires_at: datetime | None = None
    is_active: bool = True


class AdminPromoCodeUpdate(BaseModel):
    discount_value: float | None = None
    max_uses: int | None = None
    expires_at: datetime | None = None
    is_active: bool | None = None


class AdminPromptTemplateResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None = None
    category: str | None = None
    text: str
    variables: list[str] = []
    compatible_models: list[str] = []
    is_active: bool = True
    version: int
    success_rate: float | None = None
    usage_count: int
    rating: float | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdminPromptTemplateCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    category: str | None = None
    text: str
    variables: list[str] = []
    compatible_models: list[str] = []
    is_active: bool = True


class AdminPromptTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    text: str | None = None
    variables: list[str] | None = None
    compatible_models: list[str] | None = None
    is_active: bool | None = None
    version: int | None = None


class AdminSystemSettingsUpdate(BaseModel):
    value: dict


class AIProviderResponse(BaseModel):
    id: UUID
    name: str
    provider_type: str
    base_url: str
    enabled: bool
    priority: int
    default_model: str | None = None
    config: dict
    meta: dict
    last_tested_at: datetime | None = None
    last_test_status: str | None = None
    last_test_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIProviderCreate(BaseModel):
    name: str
    provider_type: str
    base_url: str = "https://polza.ai/api/v1"
    api_key: str
    enabled: bool = True
    priority: int = 0
    default_model: str | None = None
    config: dict = {}


class AIProviderUpdate(BaseModel):
    name: str | None = None
    provider_type: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    enabled: bool | None = None
    priority: int | None = None
    default_model: str | None = None
    config: dict | None = None


class AIModelResponse(BaseModel):
    id: UUID
    provider_id: UUID
    name: str
    display_name: str
    model_type: str
    model_id: str
    max_prompt_length: int
    supports_images: bool
    supports_video: bool
    supports_audio: bool
    default_parameters: dict
    cost_per_unit: float
    unit_type: str
    enabled: bool
    is_default: bool
    config: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIModelCreate(BaseModel):
    provider_id: UUID
    name: str
    display_name: str
    model_type: str
    model_id: str
    max_prompt_length: int = 4096
    supports_images: bool = False
    supports_video: bool = False
    supports_audio: bool = False
    default_parameters: dict = {}
    cost_per_unit: float = 0
    unit_type: str = "token"
    enabled: bool = True
    is_default: bool = False
    config: dict = {}


class AIModelUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    model_type: str | None = None
    model_id: str | None = None
    max_prompt_length: int | None = None
    supports_images: bool | None = None
    supports_video: bool | None = None
    supports_audio: bool | None = None
    default_parameters: dict | None = None
    cost_per_unit: float | None = None
    unit_type: str | None = None
    enabled: bool | None = None
    is_default: bool | None = None
    config: dict | None = None


class AIProviderHealthResponse(BaseModel):
    provider_id: UUID
    provider_name: str
    status: str
    message: str | None = None
    latency_ms: int | None = None
    tested_at: datetime
