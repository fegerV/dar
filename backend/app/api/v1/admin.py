from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, ValidationException
from app.schemas.admin import (
    AdminAuditLogResponse,
    AdminDashboardStats,
    AdminGenerationResponse,
    AdminOrderDetailResponse,
    AdminOrderResponse,
    AdminPaymentResponse,
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
    QueueJobAction,
    QueueJobBulkAction,
    QueueJobPriorityUpdate,
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


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    users, _ = await service.list_users(page, page_size)
    return users


@router.get("/templates", response_model=list[AdminTemplateResponse])
async def list_templates(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    templates, _ = await service.list_templates(page, page_size)
    return templates


@router.post("/templates", response_model=AdminTemplateResponse, status_code=201)
async def create_template(
    body: AdminTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.create_template(body)


@router.get("/generations", response_model=list[AdminGenerationResponse])
async def list_generations(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    generations, _ = await service.list_generations(page, page_size)
    return generations


@router.get("/orders", response_model=list[AdminOrderResponse])
async def list_orders(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    orders, _ = await service.list_orders(page, page_size)
    return orders


@router.get("/queue", response_model=list[AdminQueueJobResponse])
async def list_queue(
    status: str | None = Query(None, pattern="^(pending|running|completed|failed|canceled)$"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_queue_jobs(status)


@router.get("/workers", response_model=list[AdminWorkerResponse])
async def list_workers(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.list_workers()


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


@router.get("/payments", response_model=list[AdminPaymentResponse])
async def list_payments(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    payments, _ = await service.list_payments(page, page_size)
    return payments


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


@router.post("/users/{user_id}/impersonate")
async def impersonate_user(
    user_id: UUID,
    mfa_token: str = Query(default=None, description="MFA confirmation token (required for impersonation)"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    from app.core.security import create_access_token, create_impersonation_token, create_refresh_token
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


@router.get("/orders/{order_id}", response_model=AdminOrderDetailResponse)
async def get_order(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = AdminService(db)
    return await service.get_order(order_id)


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