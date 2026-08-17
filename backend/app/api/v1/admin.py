from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.audit import AuditRepository
from app.schemas.admin import (
    AdminDashboardStats,
    AdminTemplateCreate,
    AdminTemplateResponse,
    AdminUserResponse,
)
from app.services.admin.service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminDashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    service = AdminService(db)
    return await service.get_dashboard_stats()


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    service = AdminService(db)
    users, _ = await service.list_users(page, page_size)
    return users


@router.get("/templates", response_model=list[AdminTemplateResponse])
async def list_templates(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    service = AdminService(db)
    templates, _ = await service.list_templates(page, page_size)
    return templates


@router.post("/templates", response_model=AdminTemplateResponse, status_code=201)
async def create_template(
    body: AdminTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    service = AdminService(db)
    return await service.create_template(body)


@router.get("/audit-logs")
async def list_audit_logs(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    repo = AuditRepository(db)
    logs = await repo.list_by_actor(current_user.id, limit=limit)
    return [
        {
            "id": str(log.id),
            "action": log.action,
            "target_type": log.target_type,
            "target_id": str(log.target_id) if log.target_id else None,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
