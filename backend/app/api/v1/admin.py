from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.audit import AuditRepository
from app.repositories.entitlements import EntitlementRepository
from app.repositories.feedback import FeedbackRepository
from app.repositories.referrals import ReferralRepository
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


@router.get("/generations")
async def admin_list_generations(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    result = await db.execute(
        __import__("sqlalchemy").select(__import__("app.models.generation", fromlist=["Generation"]).Generation)
        .order_by(__import__("app.models.generation", fromlist=["Generation"]).Generation.created_at.desc())
        .limit(limit)
    )
    generations = result.scalars().all()
    return [
        {
            "id": str(g.id),
            "project_id": str(g.project_id),
            "status": g.status,
            "progress": g.progress,
            "current_step": g.current_step,
            "created_at": g.created_at.isoformat() if g.created_at else None,
        }
        for g in generations
    ]


@router.get("/payments")
async def admin_list_payments(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    result = await db.execute(
        __import__("sqlalchemy").select(__import__("app.models.payment", fromlist=["Payment"]).Payment)
        .order_by(__import__("app.models.payment", fromlist=["Payment"]).Payment.created_at.desc())
        .limit(limit)
    )
    payments = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "user_id": str(p.user_id),
            "amount": float(p.amount),
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in payments
    ]


@router.get("/referrals")
async def admin_list_referrals(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    repo = ReferralRepository(db)
    referrals = await repo.list_recent(limit=limit)
    return [
        {
            "id": str(r.id),
            "referrer_user_id": str(r.referrer_user_id),
            "referred_user_id": str(r.referred_user_id) if r.referred_user_id else None,
            "code": r.code,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in referrals
    ]


@router.get("/feedback")
async def admin_list_feedback(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not current_user.is_admin:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")
    repo = FeedbackRepository(db)
    items = await repo.list_recent(limit=limit)
    return [
        {
            "id": str(f.id),
            "user_id": str(f.user_id),
            "generation_id": str(f.generation_id) if f.generation_id else None,
            "reaction": f.reaction,
            "details": f.details,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        }
        for f in items
    ]
