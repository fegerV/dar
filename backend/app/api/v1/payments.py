from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundException
from app.repositories.projects import ProjectRepository
from app.schemas.payment import (
    EntitlementResponse,
    PaymentCreate,
    PaymentResponse,
    PaymentWebhookResponse,
    WalletResponse,
)
from app.services.entitlements.service import EntitlementService
from app.services.payments.service import PaymentService

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
    project_repo = ProjectRepository(db)
    project = await project_repo.get_by_id(project_id, current_user.id)
    if project is None:
        raise NotFoundException("Проект не найден")

    service = PaymentService(db)
    amount = float(project.price_rub)
    return await service.create_payment(
        current_user.id, project_id, amount=amount, method=body.method
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = PaymentService(db)
    return await service.get_payment(payment_id, current_user.id)


@router.post("/webhook/yookassa", response_model=PaymentWebhookResponse)
async def yookassa_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    signature = request.headers.get("X-Yookassa-Signature")
    service = PaymentService(db)
    result = await service.handle_webhook(body, signature)
    return PaymentWebhookResponse(**result)


@router.get("/entitlements", response_model=list[EntitlementResponse])
async def list_entitlements(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = EntitlementService(db)
    return await service.list_entitlements(current_user.id)


@router.post("/entitlements/{entitlement_id}/consume", response_model=EntitlementResponse)
async def consume_entitlement(
    entitlement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = EntitlementService(db)
    return await service.consume_entitlement(current_user.id, entitlement_id)
