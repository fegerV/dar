from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    method: str = Field(..., pattern="^(bank_card|sbp|wallet|promo|bonus)$")
    promo_code: str | None = None
    return_url: str | None = None


class PaymentResponse(BaseModel):
    id: UUID
    project_id: UUID | None = None
    status: str
    method: str
    amount_rub: float
    bonus_amount_rub: float
    discount_rub: float
    confirmation_url: str | None = None
    created_at: datetime
    paid_at: datetime | None = None

    model_config = {"from_attributes": True}


class PaymentWebhookResponse(BaseModel):
    received: bool = True


class WalletResponse(BaseModel):
    user_id: UUID
    balance_rub: float
    bonus_balance: float
    updated_at: datetime

    model_config = {"from_attributes": True}


class EntitlementResponse(BaseModel):
    id: UUID
    code: str
    quantity: int
    consumed: int
    expires_at: datetime | None = None
    source: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
