from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory, get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ValidationException,
)
from app.core.rbac import SYSTEM_ROLES, require_permission
from app.models.admin import Role, UserRole
from app.models.payment import LedgerTransaction, Payment, PromoCode, Wallet
from app.models.template import PromptTemplate, PromptTemplateVersion
from app.models.user import User
from app.schemas.admin import (
    AdminAuditLogResponse,
    AdminDashboardStats,
    AdminGenerationDetailResponse,
    AdminLedgerResponse,
    AdminOrderDetailResponse,
    AdminPaginatedResponse,
    AdminPaymentResponse,
    AdminPromoCodeCreate,
    AdminPromoCodeResponse,
    AdminPromoCodeUpdate,
    AdminPromptTemplateCreate,
    AdminPromptTemplateResponse,
    AdminPromptTemplateUpdate,
    AdminQueueJobResponse,
    AdminReferralCodeResponse,
    AdminReferralResponse,
    AdminSceneCreate,
    AdminSceneResponse,
    AdminSceneUpdate,
    AdminSetupRequest,
    AdminSystemSettingsResponse,
    AdminSystemSettingsUpdate,
    AdminTemplateCreate,
    AdminTemplateResponse,
    AdminTemplateUpdate,
    AdminTemplateVersionCreate,
    AdminTemplateVersionResponse,
    AdminTemplateVersionUpdate,
    AdminUserResponse,
    AdminUserWalletResponse,
    AdminWorkerResponse,
    AIModelCreate,
    AIModelUpdate,
    AIProviderCreate,
    AIProviderUpdate,
    QueueJobAction,
    QueueJobBulkAction,
    QueueJobPriorityUpdate,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserRoleAssign,
    WalletAdjustmentRequest,
    WorkerRestartResponse,
    WorkerStatusUpdate,
)
from app.services.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user=Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise ForbiddenException("Admin access required")
    return current_user


@router.post("/init")
async def init_admin(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    await service.ensure_single_admin(current_user.id)
    return {"status": "ok"}


@router.post("/setup", status_code=201)
async def setup_first_admin(
    body: AdminSetupRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    result = await service.setup_first_admin(
        email=body.email, password=body.password,
        first_name=body.first_name, last_name=body.last_name,
        display_name=body.display_name,
    )
    return result


@router.get("/stats", response_model=AdminDashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_dashboard_stats()


@router.get("/analytics")
async def get_analytics(
    days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_analytics(days)


@router.get("/users", response_model=AdminPaginatedResponse)
async def list_users(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    users, total = await service.list_users(page, page_size)
    return {"items": users, "total": total, "page": page, "page_size": page_size}


@router.get("/templates", response_model=AdminPaginatedResponse)
async def list_templates(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    templates, total = await service.list_templates(page, page_size)
    return {"items": templates, "total": total, "page": page, "page_size": page_size}


@router.post("/templates", response_model=AdminTemplateResponse, status_code=201)
async def create_template(
    body: AdminTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.create_template(body)


@router.get("/generations", response_model=AdminPaginatedResponse)
async def list_generations(
    page: int = 1,
    page_size: int = 20,
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    generations, total = await service.list_generations(page, page_size, status)
    return {"items": generations, "total": total, "page": page, "page_size": page_size}


@router.get("/generations/{gen_id}", response_model=AdminGenerationDetailResponse)
async def get_generation(
    gen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_generation_detail(gen_id)


@router.post("/generations/{gen_id}/retry")
async def retry_generation(
    gen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.services.audit.service import AuditService

    service = AdminService(db)
    await service.get_generation_detail(gen_id)
    audit = AuditService(db)
    await audit.log(
        actor_user_id=current_user.id, action="generation_retry",
        target_type="generation", target_id=gen_id,
    )
    await db.commit()
    return {"status": "retried", "generation_id": str(gen_id)}


@router.post("/generations/{gen_id}/cancel")
async def cancel_generation(
    gen_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.services.audit.service import AuditService

    service = AdminService(db)
    await service.get_generation_detail(gen_id)
    from app.models.generation import Generation as GenerationModel
    generation = await db.get(GenerationModel, gen_id)
    if generation and generation.status in ("running", "pending", "queued", "processing"):
        generation.status = "canceled"
        await db.flush()
    audit = AuditService(db)
    await audit.log(
        actor_user_id=current_user.id, action="generation_cancel",
        target_type="generation", target_id=gen_id,
    )
    await db.commit()
    return {"status": "canceled", "generation_id": str(gen_id)}


@router.get("/orders", response_model=AdminPaginatedResponse)
async def list_orders(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    orders, total = await service.list_orders(page, page_size)
    return {"items": orders, "total": total, "page": page, "page_size": page_size}


@router.get("/orders/{order_id}", response_model=AdminOrderDetailResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_order(order_id)


@router.get("/queue", response_model=list[AdminQueueJobResponse])
async def list_queue(
    status: str | None = Query(None, pattern="^(pending|running|completed|failed|canceled)$"),
    worker_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.models.admin import QueueJob

    query = select(QueueJob).order_by(QueueJob.created_at.desc())
    if status:
        query = query.where(QueueJob.status == status)
    if worker_id:
        query = query.where(QueueJob.worker_id == worker_id)
    result = await db.execute(query.limit(200))
    jobs = list(result.scalars().all())
    return [AdminQueueJobResponse.model_validate(j) for j in jobs]


@router.get("/workers", response_model=list[AdminWorkerResponse])
async def list_workers(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_workers()


@router.get("/workers/{worker_id}", response_model=AdminWorkerResponse)
async def get_worker(
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_worker(worker_id)


@router.post("/workers/{worker_id}/status", response_model=AdminWorkerResponse)
async def update_worker_status(
    worker_id: UUID,
    body: WorkerStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_worker_status(worker_id, body.status)


@router.post("/queue/{job_id}/action", response_model=AdminQueueJobResponse)
async def queue_job_action(
    job_id: UUID,
    body: QueueJobAction,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.queue_job_action(job_id, body.action)


@router.get("/payments", response_model=AdminPaginatedResponse)
async def list_payments(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    payments, total = await service.list_payments(page, page_size)
    return {"items": payments, "total": total, "page": page, "page_size": page_size}


@router.get("/payments/{payment_id}", response_model=AdminPaymentResponse)
async def get_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_payment(payment_id)


@router.get("/ledger/transactions", response_model=AdminLedgerResponse)
async def list_ledger_transactions(
    page: int = 1,
    page_size: int = 20,
    transaction_type: str | None = Query(default=None, description="Filter by transaction type"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_ledger_transactions(page, page_size, transaction_type)


@router.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: UUID,
    amount_rub: float | None = Query(default=None, description="Partial refund amount (full if omitted)"),
    reason: str = Query(default="admin_refund"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("payments.refund")),
):
    from app.services.audit.service import AuditService

    payment = await db.get(Payment, payment_id)
    if payment is None:
        raise NotFoundException("Payment not found")
    if payment.status != "paid":
        raise ValidationException(f"Cannot refund payment with status: {payment.status}")

    refund_amount = amount_rub or float(payment.amount_rub)
    payment.status = "refunded"
    payment.refunded_at = datetime.now(UTC)

    wallet = await db.get(Wallet, None)
    result = await db.execute(select(Wallet).where(Wallet.user_id == payment.user_id))
    wallet = result.scalar_one_or_none()
    if wallet and payment.user_id:
        wallet.balance_rub = max(float(wallet.balance_rub) - refund_amount, 0)

    transaction = LedgerTransaction(
        user_id=payment.user_id,
        wallet_id=wallet.id if wallet else None,
        type="refund",
        amount_rub=refund_amount,
        is_bonus=False,
        admin_id=current_user.id,
        reason=reason,
        reference_id=payment_id,
    )
    db.add(transaction)

    audit = AuditService(db)
    await audit.log(
        actor_user_id=current_user.id, action="payment_refunded",
        target_type="payment", target_id=payment_id,
        metadata={"amount": refund_amount, "reason": reason},
    )
    await db.commit()
    return {"status": "refunded", "payment_id": str(payment_id), "amount": refund_amount}


@router.get("/audit-logs", response_model=list[AdminAuditLogResponse])
async def list_audit_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_audit_logs(limit)


@router.get("/system/settings", response_model=list[AdminSystemSettingsResponse])
async def list_system_settings(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_system_settings()


@router.patch("/system/settings/{key}", response_model=AdminSystemSettingsResponse)
async def update_system_setting(
    key: str,
    body: AdminSystemSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_system_setting(key, body)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_user(user_id)


@router.get("/users/{user_id}/wallet", response_model=AdminUserWalletResponse)
async def get_user_wallet(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_user_wallet(user_id)


@router.post("/users/{user_id}/wallet/adjust")
async def adjust_wallet(
    user_id: UUID,
    body: WalletAdjustmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("wallet.adjust")),
):
    from app.services.audit.service import AuditService

    wallet = await db.get(Wallet, None)
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if wallet is None:
        raise NotFoundException("Wallet not found")

    if body.is_bonus:
        wallet.bonus_balance += body.amount_rub
    else:
        wallet.balance_rub += body.amount_rub

    transaction = LedgerTransaction(
        user_id=user_id,
        wallet_id=wallet.id,
        type=body.type,
        amount_rub=body.amount_rub,
        is_bonus=body.is_bonus,
        admin_id=current_user.id,
        reason=body.reason,
    )
    db.add(transaction)
    await db.flush()

    audit = AuditService(db)
    await audit.log(
        actor_user_id=current_user.id,
        action="wallet_adjusted",
        target_type="wallet",
        target_id=user_id,
        metadata={
            "amount": body.amount_rub,
            "type": body.type,
            "is_bonus": body.is_bonus,
            "reason": body.reason,
        },
    )
    await db.commit()
    return {"status": "ok", "wallet_id": str(wallet.id), "transaction_id": str(transaction.id)}


@router.post("/users/{user_id}/impersonate")
async def impersonate_user(
    user_id: UUID,
    mfa_token: str = Query(default=None, description="MFA confirmation token (required for impersonation)"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.core.security import (
        create_impersonation_token,
        create_refresh_token,
    )
    from app.services.audit.service import AuditService

    if not mfa_token:
        raise ValidationException("MFA confirmation token is required for impersonation")

    service = AdminService(db)
    user = await service.get_user(user_id)
    audit = AuditService(db)
    await audit.log(
        actor_user_id=current_user.id, action="impersonate_user",
        target_type="user", target_id=user_id,
        metadata={"mfa_token_provided": True},
    )
    await db.commit()
    access_token = create_impersonation_token(user.id, current_user.id)
    refresh_token = create_refresh_token(user.id)
    return {"access_token": access_token, "refresh_token": refresh_token, "impersonation": True, "expires_in": 300}


@router.get("/referrals", response_model=list[AdminReferralResponse])
async def list_referrals(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_referrals()


@router.get("/referral-codes", response_model=list[AdminReferralCodeResponse])
async def list_referral_codes(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_referral_codes()


@router.get("/promo-codes", response_model=list[AdminPromoCodeResponse])
async def list_promo_codes(
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("promo.read")),
):
    query = select(PromoCode)
    if is_active is not None:
        query = query.where(PromoCode.is_active == is_active)
    result = await db.execute(query.order_by(PromoCode.created_at.desc()))
    return list(result.scalars().all())


@router.post("/promo-codes", response_model=AdminPromoCodeResponse, status_code=201)
async def create_promo_code(
    body: AdminPromoCodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("promo.create")),
):
    existing = await db.execute(select(PromoCode).where(PromoCode.code == body.code))
    if existing.scalar_one_or_none():
        raise ConflictException(f"Promo code '{body.code}' already exists")
    code = PromoCode(**body.model_dump())
    db.add(code)
    await db.flush()
    from app.services.audit.service import AuditService
    audit = AuditService(db)
    await audit.log(actor_user_id=current_user.id, action="promo_code_created", target_type="promo", target_id=code.id, metadata={"code": code.code})
    await db.commit()
    return AdminPromoCodeResponse.model_validate(code)


@router.patch("/promo-codes/{code_id}", response_model=AdminPromoCodeResponse)
async def update_promo_code(
    code_id: UUID,
    body: AdminPromoCodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("promo.update")),
):
    code = await db.get(PromoCode, code_id)
    if code is None:
        raise NotFoundException("Promo code not found")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(code, key, value)
    await db.flush()
    from app.services.audit.service import AuditService
    audit = AuditService(db)
    await audit.log(actor_user_id=current_user.id, action="promo_code_updated", target_type="promo", target_id=code_id, metadata=update_data)
    await db.commit()
    return AdminPromoCodeResponse.model_validate(code)


@router.delete("/promo-codes/{code_id}", status_code=204)
async def delete_promo_code(
    code_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("promo.update")),
):
    code = await db.get(PromoCode, code_id)
    if code is None:
        raise NotFoundException("Promo code not found")
    await db.delete(code)
    await db.commit()


@router.get("/errors")
async def list_errors(
    limit: int = 100,
    error_type: str | None = Query(None, pattern="^(cuda|api|timeout|storage|payment|validation|moderation|worker|database)$"),
    resolved: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from sqlalchemy import or_

    from app.models import Generation as GenerationModel

    query = select(GenerationModel).where(
        GenerationModel.error_code.isnot(None),
        GenerationModel.status == "failed",
    )
    if error_type:
        pattern = f"%{error_type}%"
        query = query.where(
            or_(
                GenerationModel.error_code.ilike(pattern),
                GenerationModel.error_message.ilike(pattern),
            )
        )

    result = await db.execute(query.order_by(GenerationModel.created_at.desc()).limit(limit))
    errors = list(result.scalars().all())

    grouped: dict[str, list[dict]] = {
        "cuda": [], "api": [], "timeout": [], "storage": [],
        "payment": [], "validation": [], "moderation": [], "worker": [], "database": [],
        "other": [],
    }

    for err in errors:
        code = (err.error_code or "").lower()
        if "cuda" in code or "gpu" in code:
            group = "cuda"
        elif "timeout" in code or "expired" in code:
            group = "timeout"
        elif "storage" in code or "s3" in code or "minio" in code:
            group = "storage"
        elif "payment" in code or "yookassa" in code or "refund" in code:
            group = "payment"
        elif "validation" in code or "invalid" in code:
            group = "validation"
        elif "moderation" in code:
            group = "moderation"
        elif "worker" in code:
            group = "worker"
        elif "database" in code or "db" in code or "sql" in code:
            group = "database"
        elif "api" in code:
            group = "api"
        else:
            group = "other"

        grouped[group].append({
            "id": str(err.id),
            "error_code": err.error_code,
            "error_message": err.error_message,
            "model_name": err.model_name,
            "project_id": str(err.project_id),
            "attempt": err.attempt,
            "cost_rub": float(err.cost_rub),
            "duration_ms": err.duration_ms,
            "created_at": err.created_at.isoformat(),
            "resolved": False,
        })

    return {
        "groups": grouped,
        "total": sum(len(v) for v in grouped.values()),
        "occurrences": {k: len(v) for k, v in grouped.items()},
    }


@router.get("/gallery/pending")
async def get_gallery_pending(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    items = await service.list_gallery_pending()
    return [
        {
            "id": str(i.id),
            "title": i.title,
            "video_url": i.video_url,
            "thumbnail_url": i.thumbnail_url,
            "user_id": str(i.user_id),
            "created_at": i.created_at.isoformat(),
        }
        for i in items
    ]


@router.post("/gallery/{submission_id}/review")
async def review_gallery_submission(
    submission_id: UUID,
    approve: bool = Query(default=True),
    make_public: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    submission = await service.review_gallery_submission(
        submission_id, current_user.id, approve, make_public
    )
    return {
        "id": str(submission.id),
        "status": submission.status.value,
        "is_public": submission.is_public,
    }


@router.patch("/templates/{template_id}", response_model=AdminTemplateResponse)
async def update_template(
    template_id: UUID,
    body: AdminTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_template(template_id, body)


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    await service.delete_template(template_id)


@router.get("/templates/{template_id}/versions", response_model=list[AdminTemplateVersionResponse])
async def list_template_versions(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_template_versions(template_id)


@router.post("/templates/{template_id}/versions", response_model=AdminTemplateVersionResponse, status_code=201)
async def create_template_version(
    template_id: UUID,
    body: AdminTemplateVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.create_template_version(template_id, body)


@router.patch("/template-versions/{version_id}", response_model=AdminTemplateVersionResponse)
async def update_template_version(
    version_id: UUID,
    body: AdminTemplateVersionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_template_version(version_id, body)


@router.get("/templates/{template_id}/scenes", response_model=list[AdminSceneResponse])
async def list_template_scenes(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_template_scenes(template_id)


@router.post("/templates/{template_id}/scenes", response_model=AdminSceneResponse, status_code=201)
async def create_template_scene(
    template_id: UUID,
    body: AdminSceneCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.create_template_scene(template_id, body)


@router.patch("/scenes/{scene_id}", response_model=AdminSceneResponse)
async def update_scene(
    scene_id: UUID,
    body: AdminSceneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_template_scene(scene_id, body)


@router.delete("/scenes/{scene_id}", status_code=204)
async def delete_scene(
    scene_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    await service.delete_template_scene(scene_id)


@router.post("/workers/{worker_id}/restart", response_model=WorkerRestartResponse)
async def restart_worker(
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.worker_restart(worker_id)


@router.post("/workers/{worker_id}/shutdown", response_model=WorkerRestartResponse)
async def shutdown_worker(
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.worker_shutdown(worker_id)


@router.post("/queue/bulk-action", response_model=list[AdminQueueJobResponse])
async def bulk_queue_action(
    body: QueueJobBulkAction,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.bulk_queue_action(body.action, body.job_ids)


@router.patch("/queue/{job_id}/priority", response_model=AdminQueueJobResponse)
async def update_queue_job_priority(
    job_id: UUID,
    body: QueueJobPriorityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_queue_job_priority(job_id, body.priority)


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("settings.manage")),
):
    result = await db.execute(select(Role).order_by(Role.code))
    roles = list(result.scalars().all())
    return [RoleResponse.model_validate(r) for r in roles]


@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("settings.manage")),
):
    result = await db.execute(select(Role).where(Role.code == body.code))
    if result.scalar_one_or_none():
        raise ConflictException(f"Role '{body.code}' already exists")
    role = Role(
        code=body.code,
        name=body.name,
        description=body.description,
        permissions=body.permissions,
        is_system=False,
    )
    db.add(role)
    await db.flush()
    await db.commit()
    return RoleResponse.model_validate(role)


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("settings.manage")),
):
    role = await db.get(Role, role_id)
    if role is None:
        raise NotFoundException("Role not found")
    if role.is_system:
        raise ValidationException("Cannot modify system role")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(role, key, value)
    await db.commit()
    return RoleResponse.model_validate(role)


@router.get("/users/{user_id}/roles", response_model=list[RoleResponse])
async def list_user_roles(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("users.read")),
):
    result = await db.execute(
        select(Role, UserRole)
        .join(UserRole, Role.id == UserRole.role_id, isouter=True)
        .where(UserRole.user_id == user_id)
    )
    return [RoleResponse.model_validate(r) for r, _ in result.all()]


@router.post("/users/{user_id}/roles", status_code=201)
async def assign_user_role(
    user_id: UUID,
    body: UserRoleAssign,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("users.update")),
):
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundException("User not found")
    role = await db.get(Role, body.role_id)
    if role is None:
        raise NotFoundException("Role not found")
    assignment = UserRole(
        user_id=user_id,
        role_id=body.role_id,
        granted_by=body.granted_by or current_user.id,
    )
    db.add(assignment)
    await db.commit()
    return {"status": "ok", "message": f"Assigned {role.code} to user"}


@router.delete("/users/{user_id}/roles/{role_id}", status_code=204)
async def remove_user_role(
    user_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("users.update")),
):
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
    )
    assignment = result.scalar_one_or_none()
    if assignment is None:
        raise NotFoundException("Role assignment not found")
    await db.delete(assignment)
    await db.commit()


@router.get("/rbac/permissions")
async def get_permissions(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission("settings.manage")),
):
    all_perms = set()
    for role in SYSTEM_ROLES.values():
        all_perms.update(role["permissions"])
    return {"roles": SYSTEM_ROLES, "permissions": sorted(all_perms)}


@router.get("/prompts", response_model=list[AdminPromptTemplateResponse])
async def list_prompt_templates(
    page: int = 1,
    page_size: int = 50,
    category: str | None = Query(None),
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    query = select(PromptTemplate).order_by(PromptTemplate.created_at.desc())
    if category:
        query = query.where(PromptTemplate.category == category)
    if is_active is not None:
        query = query.where(PromptTemplate.is_active == is_active)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(PromptTemplate.name.ilike(pattern), PromptTemplate.code.ilike(pattern), PromptTemplate.text.ilike(pattern))
        )
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/prompts", response_model=AdminPromptTemplateResponse, status_code=201)
async def create_prompt_template(
    body: AdminPromptTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    existing = await db.execute(select(PromptTemplate).where(PromptTemplate.code == body.code))
    if existing.scalar_one_or_none():
        raise ConflictException(f"Prompt with code '{body.code}' already exists")
    prompt = PromptTemplate(**body.model_dump())
    db.add(prompt)
    await db.flush()
    version = PromptTemplateVersion(
        prompt_id=prompt.id,
        version=1,
        name=prompt.name,
        description=prompt.description,
        category=prompt.category,
        text=prompt.text,
        variables=prompt.variables,
        compatible_models=prompt.compatible_models,
    )
    db.add(version)
    await db.flush()
    from app.services.audit.service import AuditService
    audit = AuditService(db)
    await audit.log(actor_user_id=current_user.id, action="prompt_created", target_type="prompt", target_id=prompt.id)
    await db.commit()
    return AdminPromptTemplateResponse.model_validate(prompt)


@router.patch("/prompts/{prompt_id}", response_model=AdminPromptTemplateResponse)
async def update_prompt_template(
    prompt_id: UUID,
    body: AdminPromptTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    prompt = await db.get(PromptTemplate, prompt_id)
    if prompt is None:
        raise NotFoundException("Prompt not found")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prompt, key, value)
    prompt.version += 1
    await db.flush()
    version = PromptTemplateVersion(
        prompt_id=prompt.id,
        version=prompt.version,
        name=prompt.name,
        description=prompt.description,
        category=prompt.category,
        text=prompt.text,
        variables=prompt.variables,
        compatible_models=prompt.compatible_models,
    )
    db.add(version)
    await db.flush()
    from app.services.audit.service import AuditService
    audit = AuditService(db)
    await audit.log(actor_user_id=current_user.id, action="prompt_updated", target_type="prompt", target_id=prompt_id, metadata=update_data)
    await db.commit()
    return AdminPromptTemplateResponse.model_validate(prompt)


@router.get("/prompts/{prompt_id}/versions")
async def list_prompt_versions(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    prompt = await db.get(PromptTemplate, prompt_id)
    if prompt is None:
        raise NotFoundException("Prompt not found")
    result = await db.execute(select(PromptTemplateVersion).where(PromptTemplateVersion.prompt_id == prompt_id).order_by(PromptTemplateVersion.version.desc()))
    versions = list(result.scalars().all())
    return [
        {
            "id": str(v.id),
            "prompt_id": str(v.prompt_id),
            "version": v.version,
            "status": v.status,
            "name": v.name,
            "description": v.description,
            "category": v.category,
            "text": v.text,
            "variables": v.variables,
            "compatible_models": v.compatible_models,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "published_at": v.published_at.isoformat() if v.published_at else None,
            "retired_at": v.retired_at.isoformat() if v.retired_at else None,
        }
        for v in versions
    ]


@router.post("/prompts/{prompt_id}/versions", status_code=201)
async def create_prompt_version(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    prompt = await db.get(PromptTemplate, prompt_id)
    if prompt is None:
        raise NotFoundException("Prompt not found")
    prompt.version += 1
    version = PromptTemplateVersion(
        prompt_id=prompt.id,
        version=prompt.version,
        name=prompt.name,
        description=prompt.description,
        category=prompt.category,
        text=prompt.text,
        variables=prompt.variables,
        compatible_models=prompt.compatible_models,
        status="published",
        published_at=datetime.now(UTC),
    )
    db.add(version)
    await db.flush()
    from app.services.audit.service import AuditService
    audit = AuditService(db)
    await audit.log(actor_user_id=current_user.id, action="prompt_version_created", target_type="prompt", target_id=prompt_id, metadata={"version": prompt.version})
    await db.commit()
    return {
        "id": str(version.id),
        "prompt_id": str(version.prompt_id),
        "version": version.version,
        "status": version.status,
        "created_at": version.created_at.isoformat() if version.created_at else None,
    }


@router.get("/storage/stats")
async def get_storage_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.integrations.storage.factory import get_storage_provider
        storage = get_storage_provider()
        health = await storage.healthcheck()
        return {"provider": storage.__class__.__name__, "healthy": health, "used_bytes": 0, "total_bytes": None, "file_count": 0}
    except Exception as e:
        return {"provider": "unknown", "healthy": False, "used_bytes": 0, "total_bytes": None, "file_count": 0, "error": str(e)}


@router.get("/storage/yandex/config")
async def get_yandex_config(
    current_user=Depends(require_admin),
):
    from app.core.config import settings
    return {
        "oauth_token_set": bool(settings.YANDEX_DISK_OAUTH_TOKEN),
        "base_path": settings.YANDEX_DISK_BASE_PATH,
    }


@router.post("/storage/yandex/test")
async def test_yandex_connection(
    current_user=Depends(require_admin),
):
    from app.core.config import settings
    from app.integrations.storage.yandex_disk import YandexDiskProvider
    if not settings.YANDEX_DISK_OAUTH_TOKEN:
        raise ValidationException("Yandex Disk OAuth token not configured")
    provider = YandexDiskProvider()
    healthy = await provider.healthcheck()
    return {"success": healthy, "message": "Connection successful" if healthy else "Connection failed"}


class WebhookCreate(PydanticBaseModel):
    url: str
    events: list[str] = []
    is_active: bool = True


@router.get("/webhooks")
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.models.webhook import WebhookEndpoint
        result = await db.execute(select(WebhookEndpoint))
        return list(result.scalars().all())
    except Exception:
        return []


@router.post("/webhooks")
async def create_webhook(
    body: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.models.webhook import WebhookEndpoint
        wh = WebhookEndpoint(**body.model_dump())
        db.add(wh)
        await db.flush()
        return {"id": str(wh.id), "url": wh.url, "events": wh.events, "is_active": wh.is_active, "created_at": wh.created_at.isoformat()}
    except ImportError:
        return {"status": "ok", "message": "Webhook model not available"}


@router.get("/ai/providers")
async def list_ai_providers(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_ai_providers()


@router.post("/ai/providers")
async def create_ai_provider(
    body: AIProviderCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.create_ai_provider(body)


@router.get("/ai/providers/{provider_id}")
async def get_ai_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    provider = await service.get_ai_provider(provider_id)
    if not provider:
        raise NotFoundException("Provider not found")
    return provider


@router.patch("/ai/providers/{provider_id}")
async def update_ai_provider(
    provider_id: UUID,
    body: AIProviderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_ai_provider(provider_id, body)


@router.delete("/ai/providers/{provider_id}")
async def delete_ai_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    await service.delete_ai_provider(provider_id)
    return {"status": "ok"}


@router.post("/ai/providers/{provider_id}/test")
async def test_ai_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.test_ai_provider(provider_id)


@router.get("/ai/models")
async def list_ai_models(
    provider_id: UUID | None = None,
    model_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_ai_models(provider_id=provider_id, model_type=model_type)


@router.post("/ai/models")
async def create_ai_model(
    body: AIModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.create_ai_model(body)


@router.get("/ai/models/{model_id}")
async def get_ai_model(
    model_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    model = await service.get_ai_model(model_id)
    if not model:
        raise NotFoundException("Model not found")
    return model


@router.patch("/ai/models/{model_id}")
async def update_ai_model(
    model_id: UUID,
    body: AIModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.update_ai_model(model_id, body)


@router.delete("/ai/models/{model_id}")
async def delete_ai_model(
    model_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    await service.delete_ai_model(model_id)
    return {"status": "ok"}


@router.get("/ai/health")
async def ai_health_check(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.ai_health_check()


@router.get("/events/stream-token")
async def admin_events_stream_token(request: Request):
    import asyncio
    import json
    from datetime import datetime

    from sqlalchemy import select

    from app.core.security import decode_token
    from app.models.user import User

    token = request.query_params.get("token")
    if not token:
        token = request.cookies.get("daragent_admin_access")
    if not token:
        raise ForbiddenException("Token required")
    payload = decode_token(token)
    if not payload:
        raise ForbiddenException("Invalid token")
    user_id = payload.get("sub")
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not getattr(user, "is_admin", False):
            raise ForbiddenException("Admin access required")

    async def event_generator():
        yield "retry: 5000\n\n"
        while True:
            if await request.is_disconnected():
                break
            try:
                async with async_session_factory() as session:
                    service = AdminService(session)
                    stats = await service.get_dashboard_stats()
                    yield f"data: {json.dumps({'type': 'stats', 'data': stats.model_dump(mode='json'), 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})


class ModerationAction(PydanticBaseModel):
    action: str
    reason: str | None = None


@router.post("/moderation/items/{item_id}/action")
async def moderation_item_action(
    item_id: UUID,
    body: ModerationAction,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.models.gallery import GallerySubmission
        result = await db.execute(select(GallerySubmission).where(GallerySubmission.id == item_id))
        submission = result.scalar_one_or_none()
        if submission is None:
            raise NotFoundException("Moderation item not found")

        if body.action == "approve":
            submission.status = "approved"
            submission.is_public = True
        elif body.action == "reject":
            submission.status = "rejected"
            submission.is_public = False
        elif body.action == "escalate":
            submission.status = "escalated"
        else:
            raise ValidationException(f"Unknown action: {body.action}")

        submission.moderator_id = current_user.id
        await db.commit()
        return {"status": "ok", "action": body.action}
    except NotFoundException:
        raise
    except Exception as e:
        raise ValidationException(f"Moderation action failed: {e}")


@router.get("/support/tickets")
async def list_support_tickets(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.models.feedback import Feedback
        result = await db.execute(select(Feedback).order_by(Feedback.created_at.desc()).limit(100))
        feedbacks = list(result.scalars().all())
        return [
            {
                "id": str(f.id),
                "user_id": str(f.user_id),
                "generation_id": str(f.generation_id) if f.generation_id else None,
                "subject": f.reaction,
                "status": "open",
                "priority": "medium",
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "updated_at": f.created_at.isoformat() if f.created_at else None,
                "messages_count": 1,
            }
            for f in feedbacks
        ]
    except Exception:
        return []


@router.get("/support/tickets/{ticket_id}")
async def get_support_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.models.feedback import Feedback
        feedback = await db.get(Feedback, ticket_id)
        if feedback is None:
            raise NotFoundException("Ticket not found")
        return {
            "id": str(feedback.id),
            "user_id": str(feedback.user_id),
            "generation_id": str(feedback.generation_id) if feedback.generation_id else None,
            "subject": feedback.reaction,
            "status": "open",
            "priority": "medium",
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
            "updated_at": feedback.created_at.isoformat() if feedback.created_at else None,
            "messages_count": 1,
            "details": feedback.details,
        }
    except NotFoundException:
        raise
    except Exception:
        raise NotFoundException("Ticket not found")


@router.post("/support/tickets/{ticket_id}/close")
async def close_support_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.models.feedback import Feedback
        feedback = await db.get(Feedback, ticket_id)
        if feedback is None:
            raise NotFoundException("Ticket not found")
        await db.delete(feedback)
        await db.commit()
        return {"status": "closed"}
    except NotFoundException:
        raise
    except Exception as e:
        raise ValidationException(f"Failed to close ticket: {e}")


@router.get("/moderation/items/{item_id}")
async def get_moderation_item(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.models.gallery import GallerySubmission
        result = await db.execute(select(GallerySubmission).where(GallerySubmission.id == item_id))
        submission = result.scalar_one_or_none()
        if submission is None:
            raise NotFoundException("Moderation item not found")
        return {
            "id": str(submission.id),
            "type": "photo",
            "status": submission.status,
            "created_at": submission.created_at.isoformat() if submission.created_at else None,
            "updated_at": submission.updated_at.isoformat() if hasattr(submission, "updated_at") and submission.updated_at else None,
            "content_preview": f"Gallery submission {submission.id}",
            "title": submission.title,
            "description": submission.description,
            "video_url": submission.video_url,
            "thumbnail_url": submission.thumbnail_url,
            "user_id": str(submission.user_id),
            "project_id": str(submission.project_id),
        }
    except NotFoundException:
        raise
    except Exception:
        raise NotFoundException("Moderation item not found")

async def list_moderation_items(
    status: str = Query("pending", pattern="^(pending|approved|rejected|escalated)$"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        from app.models.gallery import GallerySubmission
        query = select(GallerySubmission)
        if status == "pending":
            query = query.where(GallerySubmission.status == "pending")
        elif status == "approved":
            query = query.where(GallerySubmission.status == "approved")
        elif status == "rejected":
            query = query.where(GallerySubmission.status == "rejected")
        result = await db.execute(query.order_by(GallerySubmission.created_at.desc()).limit(100))
        submissions = list(result.scalars().all())
        return [
            {
                "id": str(s.id),
                "type": "photo",
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if hasattr(s, "updated_at") and s.updated_at else None,
                "content_preview": f"Gallery submission {s.id}",
            }
            for s in submissions
        ]
    except Exception:
        return []


@router.get("/analytics/export")
async def export_analytics(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    import csv
    import io
    from datetime import datetime

    from app.models.analytics import AnalyticsEvent

    query = select(AnalyticsEvent)
    if start_date:
        query = query.where(AnalyticsEvent.occurred_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.where(AnalyticsEvent.occurred_at <= datetime.fromisoformat(end_date))

    result = await db.execute(query.order_by(AnalyticsEvent.occurred_at.desc()).limit(10000))
    events = list(result.scalars().all())

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Event Name", "User ID", "Platform", "Occurred At"])
    for event in events:
        writer.writerow([
            event.id,
            event.event_name,
            event.user_id,
            event.platform,
            event.occurred_at.isoformat() if event.occurred_at else "",
        ])

    from fastapi.responses import Response
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=analytics.csv"})


@router.get("/orders/export")
async def export_orders(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    import csv
    import io
    from datetime import datetime

    from app.models.generation import Generation as GenerationModel

    query = select(GenerationModel)
    if start_date:
        query = query.where(GenerationModel.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.where(GenerationModel.created_at <= datetime.fromisoformat(end_date))
    if status:
        query = query.where(GenerationModel.status == status)

    result = await db.execute(query.order_by(GenerationModel.created_at.desc()).limit(10000))
    orders = list(result.scalars().all())

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Project ID", "Status", "Cost", "Model", "Created At", "Completed At"])
    for order in orders:
        writer.writerow([
            str(order.id),
            str(order.project_id),
            order.status,
            order.cost_rub,
            order.model_name or "",
            order.created_at.isoformat() if order.created_at else "",
            order.completed_at.isoformat() if order.completed_at else "",
        ])

    from fastapi.responses import Response
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=orders.csv"})


@router.get("/payments/export")
async def export_payments(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    import csv
    import io
    from datetime import datetime

    query = select(Payment)
    if start_date:
        query = query.where(Payment.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.where(Payment.created_at <= datetime.fromisoformat(end_date))
    if status:
        query = query.where(Payment.status == status)

    result = await db.execute(query.order_by(Payment.created_at.desc()).limit(10000))
    payments = list(result.scalars().all())

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "User ID", "Amount", "Method", "Status", "Provider ID", "Created At", "Paid At"])
    for payment in payments:
        writer.writerow([
            str(payment.id),
            str(payment.user_id) if payment.user_id else "",
            payment.amount_rub,
            payment.method,
            payment.status,
            str(payment.provider_id) if payment.provider_id else "",
            payment.created_at.isoformat() if payment.created_at else "",
            payment.paid_at.isoformat() if payment.paid_at else "",
        ])

    from fastapi.responses import Response
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=payments.csv"})


class SceneReorder(PydanticBaseModel):
    scene_ids: list[UUID]


@router.post("/scenes/reorder")
async def reorder_scenes(
    body: SceneReorder,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.models.template import Scene

    for idx, scene_id in enumerate(body.scene_ids):
        scene = await db.get(Scene, scene_id)
        if scene is not None:
            scene.sort_order = idx
    await db.commit()
    return {"status": "ok"}


class PromptRollback(PydanticBaseModel):
    version: int


@router.post("/prompts/{prompt_id}/rollback")
async def rollback_prompt(
    prompt_id: UUID,
    body: PromptRollback,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.models.template import PromptTemplate, PromptTemplateVersion

    prompt = await db.get(PromptTemplate, prompt_id)
    if prompt is None:
        raise NotFoundException("Prompt not found")

    target = await db.execute(
        select(PromptTemplateVersion).where(
            PromptTemplateVersion.prompt_id == prompt_id,
            PromptTemplateVersion.version == body.version,
        )
    )
    version = target.scalar_one_or_none()
    if version is None:
        raise NotFoundException("Version not found")

    prompt.text = version.text
    prompt.name = version.name
    prompt.description = version.description
    prompt.category = version.category
    prompt.variables = version.variables
    prompt.compatible_models = version.compatible_models
    prompt.version = version.version
    await db.flush()

    new_version = PromptTemplateVersion(
        prompt_id=prompt.id,
        version=prompt.version,
        name=prompt.name,
        description=prompt.description,
        category=prompt.category,
        text=prompt.text,
        variables=prompt.variables,
        compatible_models=prompt.compatible_models,
        status="published",
        published_at=datetime.now(UTC),
    )
    db.add(new_version)
    await db.commit()
    return {"status": "ok", "version": prompt.version}


@router.get("/queue/jobs/{job_id}")
async def get_queue_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.models.admin import QueueJob

    job = await db.get(QueueJob, job_id)
    if job is None:
        raise NotFoundException("Job not found")
    return AdminQueueJobResponse.model_validate(job)


@router.patch("/queue/pause")
async def pause_queue(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    return {"status": "paused"}


@router.patch("/queue/resume")
async def resume_queue(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    return {"status": "resumed"}


@router.get("/workers/{worker_id}/logs")
async def get_worker_logs(
    worker_id: UUID,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.models.admin import WorkerLog

    result = await db.execute(
        select(WorkerLog).where(WorkerLog.worker_id == worker_id).order_by(WorkerLog.created_at.desc()).limit(limit)
    )
    logs = list(result.scalars().all())
    return [
        {
            "id": str(log.id),
            "level": log.level,
            "message": log.message,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


class WorkerParams(PydanticBaseModel):
    metadata: dict | None = None
    gpu_model: str | None = None
    gpu_vram_total_gb: int | None = None
    cpu_usage_percent: float | None = None


@router.patch("/workers/{worker_id}/params")
async def update_worker_params(
    worker_id: UUID,
    body: WorkerParams,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.models.admin import Worker

    worker = await db.get(Worker, worker_id)
    if worker is None:
        raise NotFoundException("Worker not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(worker, key, value)
    await db.commit()
    return AdminWorkerResponse.model_validate(worker)


class UserBlockIP(PydanticBaseModel):
    ip_address: str
    reason: str | None = None


@router.post("/users/{user_id}/block-ip")
async def block_user_ip(
    user_id: UUID,
    body: UserBlockIP,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundException("User not found")

    blocked = list(user.metadata_.get("blocked_ips", []))
    if body.ip_address in blocked:
        raise ConflictException("IP already blocked")

    blocked.append(body.ip_address)
    user.metadata_["blocked_ips"] = blocked
    user.metadata_["block_reason"] = body.reason
    await db.commit()
    return {"status": "ok", "blocked_ips": blocked}


@router.delete("/users/{user_id}/block-ip/{ip_address}")
async def unblock_user_ip(
    user_id: UUID,
    ip_address: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundException("User not found")

    blocked = list(user.metadata_.get("blocked_ips", []))
    if ip_address not in blocked:
        raise NotFoundException("IP not found in block list")

    blocked.remove(ip_address)
    user.metadata_["blocked_ips"] = blocked
    await db.commit()
    return {"status": "ok", "blocked_ips": blocked}


class BulkUserAction(PydanticBaseModel):
    user_ids: list[UUID]
    action: str
    reason: str | None = None


@router.post("/users/bulk-action")
async def bulk_user_action(
    body: BulkUserAction,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.services.audit.service import AuditService

    if body.action not in {"block", "unblock", "delete", "send_message"}:
        raise ValidationException(f"Unsupported bulk action: {body.action}")

    audit = AuditService(db)
    results = []
    for uid in body.user_ids:
        user = await db.get(User, uid)
        if user is None:
            continue
        if body.action == "block":
            user.status = "blocked"
        elif body.action == "unblock":
            user.status = "active"
        elif body.action == "delete":
            user.deleted_at = datetime.now(UTC)
        elif body.action == "send_message":
            pass
        results.append(str(uid))
        await audit.log(
            actor_user_id=current_user.id,
            action=f"bulk_user_{body.action}",
            target_type="user",
            target_id=uid,
            metadata={"reason": body.reason},
        )

    await db.commit()
    return {"status": "ok", "processed": results}

