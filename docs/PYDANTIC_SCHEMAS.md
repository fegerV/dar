# ДарАгент MVP — Pydantic Schemas v0.2

## Часть A — User & Auth Schemas

### auth.py
```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID
import re

class AuthProvider(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    GOOGLE = "google"
    YANDEX = "yandex"
    APPLE = "apple"

class UserRegister(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    auth_provider: AuthProvider
    auth_provider_id: str = Field(..., min_length=1, max_length=255)
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone format')
        return v
    
    @model_validator(mode='after')
    def check_email_or_phone(self) -> 'UserRegister':
        if not self.email and not self.phone:
            raise ValueError('Either email or phone must be provided')
        if self.auth_provider == AuthProvider.EMAIL and not self.email:
            raise ValueError('Email required for email provider')
        if self.auth_provider == AuthProvider.PHONE and not self.phone:
            raise ValueError('Phone required for phone provider')
        return self

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    
    @model_validator(mode='after')
    def check_email_or_phone(self) -> 'UserLogin':
        if not self.email and not self.phone:
            raise ValueError('Either email or phone must be provided')
        return self

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: UUID
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    auth_provider: AuthProvider
    balance: int = 0
    bonus_balance: int = 0
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = None
```

## Часть B — Recipient Schemas

### recipients.py
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    gender: Optional[Gender] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    relationship: Optional[str] = Field(None, max_length=100)
    interests: List[str] = []
    personality: List[str] = []
    additional_info: Optional[str] = None
    photo_asset_id: Optional[UUID] = None

class RecipientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    gender: Optional[Gender] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    relationship: Optional[str] = Field(None, max_length=100)
    interests: Optional[List[str]] = None
    personality: Optional[List[str]] = None
    additional_info: Optional[str] = None
    photo_asset_id: Optional[UUID] = None

class RecipientResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    gender: Optional[Gender] = None
    age: Optional[int] = None
    relationship: Optional[str] = None
    interests: List[str] = []
    personality: List[str] = []
    additional_info: Optional[str] = None
    photo_asset_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

## Часть C — Creative Brief Schema

### briefs.py
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

class BriefRecipient(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    relationship: str

class BriefSender(BaseModel):
    name: str
    relationship: str

class BriefTone(BaseModel):
    humor: float = Field(0.0, ge=0.0, le=1.0)
    emotion: float = Field(0.0, ge=0.0, le=1.0)
    seriousness: float = Field(0.0, ge=0.0, le=1.0)
    warmth: float = Field(0.0, ge=0.0, le=1.0)

class CreativeBrief(BaseModel):
    occasion: str
    recipient: BriefRecipient
    sender: BriefSender
    personality: List[str] = []
    interests: List[str] = []
    tone: BriefTone = BriefTone()
    style: str = "cinematic"
    duration: int = Field(60, ge=15, le=120)
    surprise_level: float = Field(0.5, ge=0.0, le=1.0)
    additional_info: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "occasion": "birthday",
                "recipient": {
                    "name": "Александр",
                    "age": 40,
                    "gender": "male",
                    "relationship": "friend"
                },
                "sender": {
                    "name": "Виктор",
                    "relationship": "friend"
                },
                "personality": ["funny", "confident", "energetic"],
                "interests": ["cars", "travel", "football"],
                "tone": {
                    "humor": 0.8,
                    "emotion": 0.6,
                    "seriousness": 0.2,
                    "warmth": 0.7
                },
                "style": "cinematic",
                "duration": 60,
                "surprise_level": 0.9
            }
        }

class CreativeBriefUpdate(BaseModel):
    occasion: Optional[str] = None
    recipient: Optional[BriefRecipient] = None
    sender: Optional[BriefSender] = None
    personality: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    tone: Optional[BriefTone] = None
    style: Optional[str] = None
    duration: Optional[int] = Field(None, ge=15, le=120)
    surprise_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    additional_info: Optional[str] = None
```

## Часть D — Project Schemas

### projects.py
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    BRIEF_READY = "brief_ready"
    RECOMMENDATIONS_READY = "recommendations_ready"
    TEMPLATE_SELECTED = "template_selected"
    SCRIPT_GENERATING = "script_generating"
    SCRIPT_READY = "script_ready"
    ASSETS_GENERATING = "assets_generating"
    RENDERING = "rendering"
    PREVIEW_READY = "preview_ready"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Occasion(str, Enum):
    BIRTHDAY = "birthday"
    WEDDING = "wedding"
    ANNIVERSARY = "anniversary"
    NEW_YEAR = "new_year"
    MARCH_8 = "march_8"
    FEBRUARY_23 = "february_23"
    GRADUATION = "graduation"
    PROMOTION = "promotion"
    RETIREMENT = "retirement"
    BABY_SHOWER = "baby_shower"
    CHRISTENING = "christening"
    HOUSEWARMING = "housewarming"
    PROFESSIONAL_HOLIDAY = "professional_holiday"
    OTHER = "other"

class Format(str, Enum):
    SHORT_15S = "short_15s"
    MEDIUM_30S = "medium_30s"
    LONG_60S = "long_60s"
    EXTENDED_90S = "extended_90s"

class ProjectCreate(BaseModel):
    recipient_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    occasion: Occasion
    format: Format = Format.MEDIUM_30S

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    occasion: Optional[Occasion] = None
    format: Optional[Format] = None

class ProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    recipient_id: UUID
    title: str
    status: ProjectStatus
    occasion: Occasion
    format: Format
    creative_brief: Optional[Dict[str, Any]] = None
    selected_template_id: Optional[UUID] = None
    selected_template_version_id: Optional[UUID] = None
    price: int = 0
    currency: str = "RUB"
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
```

## Часть E — Template Schemas

### templates.py
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class TemplateCategory(str, Enum):
    CINEMATIC = "cinematic"
    HUMOR = "humor"
    ROMANTIC = "romantic"
    FAMILY = "family"
    CORPORATE = "corporate"
    SPECIAL = "special"

class PriceTier(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    EXCLUSIVE = "exclusive"

class TemplateResponse(BaseModel):
    id: UUID
    template_id: str
    name: str
    description: Optional[str] = None
    category: TemplateCategory
    price_tier: PriceTier
    base_price: int
    is_published: bool = False
    popularity_score: int = 0
    conversion_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TemplateVersionResponse(BaseModel):
    id: UUID
    template_id: UUID
    version: int
    name: str
    requirements: Dict[str, Any] = {}
    variables: List[str] = []
    scenes: List[Dict[str, Any]] = []
    conditions: List[Dict[str, Any]] = []
    prompts: Dict[str, Any] = {}
    audio_settings: Dict[str, Any] = {}
    render_settings: Dict[str, Any] = {}
    fallback_scene_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class TemplateFilter(BaseModel):
    category: Optional[TemplateCategory] = None
    occasion: Optional[str] = None
    price_tier: Optional[PriceTier] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    published_only: bool = True
```

## Часть F — Recommendation Schemas

### recommendations.py
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID

class RecommendationItem(BaseModel):
    template_id: UUID
    template_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str
    preview_url: Optional[str] = None
    price: int
    category: str
    duration_estimate: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "550e8400-e29b-41d4-a716-446655440000",
                "template_name": "Герой фильма",
                "score": 0.94,
                "reason": "Подходит для близкого друга с хорошим чувством юмора",
                "price": 299,
                "category": "cinematic",
                "duration_estimate": 60
            }
        }

class RecommendationsResponse(BaseModel):
    project_id: UUID
    recommendations: List[RecommendationItem]
    generated_at: datetime

class RecommendationRequest(BaseModel):
    project_id: UUID
```

## Часть G — Generation Schemas

### generations.py
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class GenerationStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    PREPARING = "preparing"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_ASSETS = "generating_assets"
    GENERATING_VIDEO = "generating_video"
    RENDERING = "rendering"
    UPLOADING = "uploading"
    READY = "ready"
    FAILED = "failed"

class GenerationStepType(str, Enum):
    SCRIPT = "script"
    IMAGE = "image"
    VIDEO = "video"
    VOICE = "voice"
    RENDER = "render"
    UPLOAD = "upload"

class GenerationStepResponse(BaseModel):
    id: UUID
    generation_id: UUID
    step_type: GenerationStepType
    step_order: int
    status: GenerationStatus
    error_message: Optional[str] = None
    retry_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class GenerationResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: GenerationStatus
    retry_count: int = 0
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    script_content: Optional[str] = None
    assets_json: List[Dict[str, Any]] = []
    video_url: Optional[str] = None
    preview_url: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    steps: Optional[List[GenerationStepResponse]] = None
    
    class Config:
        from_attributes = True

class GenerationCreate(BaseModel):
    project_id: UUID

class GenerationRetry(BaseModel):
    generation_id: UUID
```

## Часть H — Payment Schemas

### payments.py
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    YOOKASSA = "yookassa"
    WALLET = "wallet"
    BONUS = "bonus"

class PaymentCreate(BaseModel):
    project_id: UUID
    amount: int = Field(..., gt=0)
    payment_method: PaymentMethod = PaymentMethod.YOOKASSA
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    id: UUID
    user_id: UUID
    project_id: Optional[UUID] = None
    amount: int
    currency: str = "RUB"
    status: PaymentStatus
    payment_method: PaymentMethod
    provider_payment_id: Optional[str] = None
    description: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class YooKassaWebhook(BaseModel):
    type: str
    event: str
    object: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "notification",
                "event": "payment.succeeded",
                "object": {
                    "id": "2d3df78f-000e-500b-9000-jk8441zxjzPP",
                    "status": "succeeded",
                    "amount": {
                        "value": "199.00",
                        "currency": "RUB"
                    },
                    "metadata": {
                        "project_id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "660e8400-e29b-41d4-a716-446655440001"
                    }
                }
            }
        }
```

## Часть I — Wallet Schemas

### wallet.py
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    GENERATION = "generation"
    REFUND = "refund"
    BONUS_GRANT = "bonus_grant"
    BONUS_USAGE = "bonus_usage"
    ADJUSTMENT = "adjustment"

class WalletTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    transaction_type: TransactionType
    amount: int
    balance_after: int
    bonus_amount: int = 0
    bonus_balance_after: int = 0
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class WalletBalanceResponse(BaseModel):
    user_id: UUID
    balance: int = 0
    bonus_balance: int = 0
    currency: str = "RUB"
    updated_at: datetime

class BonusType(str, Enum):
    REGISTRATION = "registration"
    REFERRAL = "referral"
    FIRST_PAYMENT = "first_payment"
    PROMOTIONAL = "promotional"
    COMPENSATION = "compensation"

class BonusResponse(BaseModel):
    id: UUID
    user_id: UUID
    bonus_type: BonusType
    amount: int
    remaining_amount: int
    expires_at: Optional[datetime] = None
    is_active: bool = True
    granted_at: datetime
    used_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

## Часть J — Analytics Schemas

### analytics.py
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class AnalyticsEventName(str, Enum):
    APP_OPEN = "app_open"
    REGISTRATION = "registration"
    BRIEF_STARTED = "brief_started"
    BRIEF_COMPLETED = "brief_completed"
    RECOMMENDATIONS_VIEWED = "recommendations_viewed"
    TEMPLATE_VIEWED = "template_viewed"
    TEMPLATE_SELECTED = "template_selected"
    GENERATION_STARTED = "generation_started"
    GENERATION_COMPLETED = "generation_completed"
    PREVIEW_OPENED = "preview_opened"
    PAYMENT_STARTED = "payment_started"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SHARE_CLICKED = "share_clicked"
    SHARE_COMPLETED = "share_completed"

class AnalyticsEventCreate(BaseModel):
    event_name: AnalyticsEventName
    user_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    properties: Dict[str, Any] = {}
    session_id: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_name": "template_selected",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "project_id": "660e8400-e29b-41d4-a716-446655440001",
                "properties": {
                    "template_id": "movie_hero_001"
                },
                "session_id": "sess_abc123"
            }
        }

class AnalyticsEventResponse(BaseModel):
    id: UUID
    event_name: str
    user_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    properties: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## Часть K — Asset Schemas

### assets.py
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class AssetType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"

class AssetUploadResponse(BaseModel):
    asset_id: UUID
    upload_url: str
    storage_path: str
    expires_at: datetime

class AssetResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    asset_type: AssetType
    storage_path: str
    public_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None
    is_temp: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
```
