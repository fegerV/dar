from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.payment import Payment
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

    if project.paid_rub and project.paid_rub > 0:
        raise ConflictException("Оплата для этого проекта уже существует")

    existing_paid = await db.execute(
        select(Payment).where(
            Payment.project_id == project_id,
            Payment.user_id == current_user.id,
            Payment.status == "paid",
        )
    )
    if existing_paid.scalar_one_or_none() is not None:
        raise ConflictException("Оплата для этого проекта уже существует")

    service = PaymentService(db)
    amount = float(project.price_rub)

    if amount <= 0:
        raise NotFoundException("Сумма оплаты должна быть больше нуля")

    wallet = await service.wallet_service.get_or_create_wallet(current_user.id)
    bonus_available = float(wallet.bonus_balance or 0)
    bonus_to_use = min(bonus_available, amount)
    remaining = amount - bonus_to_use

    if bonus_to_use > 0:
        try:
            await service.wallet_service.debit_bonus(current_user.id, bonus_to_use)
        except ValidationException:
            remaining = amount

    if remaining <= 0:
        project.paid_rub = float(project.price_rub)
        await project_repo.update(project)
        await db.commit()
        return await service.create_payment(
            current_user.id, project_id, amount=0.0, method=body.method
        )

    return await service.create_payment(
        current_user.id, project_id, amount=remaining, method=body.method
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
    raw_body = await request.body()
    body = await request.json()
    signature = request.headers.get("X-Yookassa-Signature")
    service = PaymentService(db)
    result = await service.handle_webhook(raw_body, body, signature)
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
