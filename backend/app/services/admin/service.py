from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.admin import AdminUser, QueueJob, SystemSettings, Worker
from app.models.generation import Generation
from app.models.payment import Payment, Wallet
from app.models.referral import Referral, ReferralCode
from app.models.template import Template, TemplateVersion
from app.models.user import User
from app.repositories.recommendations import TemplateRepository
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
    AdminSystemSettingsResponse,
    AdminSystemSettingsUpdate,
    AdminTemplateCreate,
    AdminTemplateResponse,
    AdminUserResponse,
    AdminUserWalletResponse,
    AdminWorkerResponse,
)


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.template_repo = TemplateRepository(db)

    async def ensure_single_admin(self, user_id: UUID) -> AdminUser:
        existing = await self.db.execute(select(AdminUser).where(AdminUser.user_id == user_id))
        admin = existing.scalar_one_or_none()
        if admin:
            if not admin.is_active:
                admin.is_active = True
                await self.db.flush()
            return admin

        count_result = await self.db.execute(select(func.count()).select_from(AdminUser))
        if (count_result.scalar() or 0) > 0:
            raise ConflictException("Admin already exists")

        admin_user = AdminUser(
            user_id=user_id,
            role="admin",
            is_active=True,
        )
        self.db.add(admin_user)
        await self.db.flush()
        return admin_user

    async def get_dashboard_stats(self) -> AdminDashboardStats:
        users_count = await self.db.execute(select(func.count()).select_from(User))
        total_users = users_count.scalar() or 0

        projects_count = await self.db.execute(select(func.count()).select_from(Generation))
        total_projects = projects_count.scalar() or 0

        payments_sum = await self.db.execute(select(func.coalesce(func.sum(Payment.amount_rub), 0)))
        total_payments = float(payments_sum.scalar() or 0)

        pending_reviews = await self.db.execute(
            select(func.count()).select_from(Generation).where(Generation.status == "review")
        )
        active_generations = await self.db.execute(
            select(func.count()).select_from(Generation).where(Generation.status == "processing")
        )
        running_jobs = await self.db.execute(
            select(func.count()).select_from(QueueJob).where(QueueJob.status == "running")
        )
        queued_jobs = await self.db.execute(
            select(func.count()).select_from(QueueJob).where(QueueJob.status == "pending")
        )
        failed_jobs = await self.db.execute(
            select(func.count()).select_from(QueueJob).where(QueueJob.status == "failed")
        )

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        ai_cost_today = await self.db.execute(
            select(func.coalesce(func.sum(Generation.cost_rub), 0)).where(Generation.started_at >= today_start)
        )
        revenue_today = await self.db.execute(
            select(func.coalesce(func.sum(Payment.amount_rub), 0)).where(Payment.created_at >= today_start)
        )
        ai_cost = float(ai_cost_today.scalar() or 0)
        revenue = float(revenue_today.scalar() or 0)

        return AdminDashboardStats(
            total_users=total_users,
            total_projects=total_projects,
            total_payments=total_payments,
            pending_reviews=pending_reviews.scalar() or 0,
            active_generations=active_generations.scalar() or 0,
            running_jobs=running_jobs.scalar() or 0,
            queued_jobs=queued_jobs.scalar() or 0,
            failed_jobs=failed_jobs.scalar() or 0,
            ai_cost_today=ai_cost,
            revenue_today=revenue,
            profit_today=revenue - ai_cost,
        )

    async def list_users(self, page: int = 1, page_size: int = 20) -> tuple[list[AdminUserResponse], int]:
        count_result = await self.db.execute(select(func.count()).select_from(User))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).offset(offset).limit(page_size)
        )
        users = list(result.scalars().all())
        return [AdminUserResponse.model_validate(u) for u in users], total

    async def list_templates(self, page: int = 1, page_size: int = 20) -> tuple[list[AdminTemplateResponse], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Template))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Template).order_by(Template.created_at.desc()).offset(offset).limit(page_size)
        )
        templates = list(result.scalars().all())
        return [AdminTemplateResponse.model_validate(t) for t in templates], total

    async def create_template(self, body: AdminTemplateCreate) -> AdminTemplateResponse:
        existing = await self.db.execute(
            select(Template).where(Template.code == body.code)
        )
        if existing.scalar_one_or_none():
            raise ConflictException("Template with this code already exists")

        template = Template(
            code=body.code,
            title=body.title,
            description=body.description,
            kind=body.kind,
            status="draft",
            category=body.category,
            occasion_codes=body.occasion_codes,
            relationship_types=body.relationship_types,
            moods=body.moods,
            base_price_rub=body.base_price_rub,
        )
        self.db.add(template)
        await self.db.flush()

        version = TemplateVersion(
            template_id=template.id,
            version=1,
            status="draft",
            schema_version="1.0",
            prompt_config={},
            render_config={},
            personalization_config={},
            validation_config={},
        )
        self.db.add(version)
        await self.db.commit()

        return AdminTemplateResponse.model_validate(template)

    async def list_generations(self, page: int = 1, page_size: int = 20) -> tuple[list[AdminGenerationResponse], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Generation))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Generation).order_by(Generation.created_at.desc()).offset(offset).limit(page_size)
        )
        generations = list(result.scalars().all())
        return [AdminGenerationResponse.model_validate(g) for g in generations], total

    async def list_orders(self, page: int = 1, page_size: int = 20) -> tuple[list[AdminOrderResponse], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Generation))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Generation).order_by(Generation.created_at.desc()).offset(offset).limit(page_size)
        )
        generations = list(result.scalars().all())
        return [AdminOrderResponse.model_validate(g) for g in generations], total

    async def list_queue_jobs(self, status: str | None = None) -> list[AdminQueueJobResponse]:
        query = select(QueueJob).order_by(QueueJob.created_at.desc())
        if status:
            query = query.where(QueueJob.status == status)
        result = await self.db.execute(query)
        jobs = list(result.scalars().all())
        return [AdminQueueJobResponse.model_validate(j) for j in jobs]

    async def list_workers(self) -> list[AdminWorkerResponse]:
        result = await self.db.execute(select(Worker).order_by(Worker.name))
        workers = list(result.scalars().all())
        return [AdminWorkerResponse.model_validate(w) for w in workers]

    async def list_payments(self, page: int = 1, page_size: int = 20) -> tuple[list[AdminPaymentResponse], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Payment))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(Payment).order_by(Payment.created_at.desc()).offset(offset).limit(page_size)
        )
        payments = list(result.scalars().all())
        return [AdminPaymentResponse.model_validate(p) for p in payments], total

    async def list_audit_logs(self, limit: int = 100) -> list[AdminAuditLogResponse]:
        from app.models.audit import AuditLog
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        logs = list(result.scalars().all())
        return [AdminAuditLogResponse.model_validate(log) for log in logs]

    async def get_system_settings(self) -> list[AdminSystemSettingsResponse]:
        result = await self.db.execute(select(SystemSettings).order_by(SystemSettings.key))
        settings = list(result.scalars().all())
        return [AdminSystemSettingsResponse.model_validate(s) for s in settings]

    async def update_system_setting(self, key: str, body: AdminSystemSettingsUpdate) -> AdminSystemSettingsResponse:
        setting = await self.db.get(SystemSettings, key)
        if setting is None:
            raise NotFoundException("Setting not found")
        setting.value = body.value
        await self.db.flush()
        return AdminSystemSettingsResponse.model_validate(setting)

    async def get_user(self, user_id: UUID) -> AdminUserResponse:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundException("User not found")
        return AdminUserResponse.model_validate(user)

    async def get_user_wallet(self, user_id: UUID) -> AdminUserWalletResponse:
        result = await self.db.execute(
            select(Wallet).where(Wallet.user_id == user_id)
        )
        wallet = result.scalar_one_or_none()
        if wallet is None:
            from app.core.exceptions import ConflictException
            raise ConflictException("User has no wallet")
        return AdminUserWalletResponse.model_validate(wallet)

    async def list_referrals(self) -> list[AdminReferralResponse]:
        result = await self.db.execute(
            select(Referral).order_by(Referral.created_at.desc())
        )
        referrals = list(result.scalars().all())
        return [AdminReferralResponse.model_validate(r) for r in referrals]

    async def list_referral_codes(self) -> list[AdminReferralCodeResponse]:
        result = await self.db.execute(
            select(ReferralCode).order_by(ReferralCode.created_at.desc())
        )
        codes = list(result.scalars().all())
        return [AdminReferralCodeResponse.model_validate(c) for c in codes]

    async def get_order(self, order_id: UUID) -> AdminOrderDetailResponse:
        result = await self.db.execute(select(Generation).where(Generation.id == order_id))
        generation = result.scalar_one_or_none()
        if generation is None:
            raise NotFoundException("Order not found")
        return AdminOrderDetailResponse.model_validate(generation)
