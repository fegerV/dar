from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.payment import (
    EntitlementResponse,
    PaymentCreate,
    PaymentResponse,
    PaymentWebhookRequest,
    PaymentWebhookResponse,
    WalletResponse,
)
from app.services.assets.service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PaymentService(db)
    return await service.wallet_service.get_wallet(current_user.id)


@router.post("/projects/{project_id}", response_model=PaymentResponse)
async def create_payment(
    project_id: UUID,
    body: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PaymentService(db)
    return await service.create_payment(current_user.id, project_id, body)


@router.post("/webhook/yookassa", response_model=PaymentWebhookResponse)
async def yookassa_webhook(body: PaymentWebhookRequest):
    service = PaymentService(None)
    return await service.handle_webhook(body)
