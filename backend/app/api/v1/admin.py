from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.admin import (
    AdminAuditLogResponse,
    AdminDashboardStats,
    AdminGenerationResponse,
    AdminOrderResponse,
    AdminPaymentResponse,
    AdminQueueJobResponse,
    AdminSystemSettingsResponse,
    AdminSystemSettingsUpdate,
    AdminTemplateCreate,
    AdminTemplateResponse,
    AdminUserResponse,
    AdminWorkerResponse,
)
from app.services.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user=Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    return current_user


@router.post("/init")
async def init_admin(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    await service.ensure_single_admin(current_user.id)
    return {"status": "ok"}


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
