from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReferralCodeResponse(BaseModel):
    id: UUID
    code: str
    uses_count: int
    max_uses: int | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReferralResponse(BaseModel):
    id: UUID
    referrer_user_id: UUID
    referred_user_id: UUID | None
    code: str
    status: str
    referrer_bonus_granted: bool
    referee_bonus_granted: bool
    completed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReferralStatsResponse(BaseModel):
    referral_code: str | None = None
    total_referrals: int = 0
    completed_referrals: int = 0
    referrer_bonus_granted: int = 0
    referee_bonus_granted: int = 0
    earned_rub: float = 0.0
    referrer_bonus_rub: float = 200.00
    referee_bonus_rub: float = 100.00
