from datetime import datetime, timedelta, timezone
from uuid import UUID

from pydantic import BaseModel, ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.models.admin import AdminUser, QueueJob, SystemSettings, Worker
from app.models.generation import Generation
from app.models.payment import LedgerTransaction, Payment, Wallet
from app.models.project import Project
from app.models.referral import Referral, ReferralCode
from app.models.template import Template, TemplateVersion, Scene
from app.models.user import User, UserAuthIdentity
from app.repositories.recommendations import TemplateRepository
from app.schemas.admin import (
    AdminAuditLogResponse,
    AdminDashboardStats,
    AdminGenerationDetailResponse,
    AdminGenerationResponse,
    AdminLedgerResponse,
    AdminLedgerTransactionResponse,
    AdminOrderDetailResponse,
    AdminOrderResponse,
    AdminPaymentResponse,
    AdminQueueJobResponse,
    AdminReferralCodeResponse,
    AdminReferralResponse,
    AdminSceneResponse,
    AdminSceneCreate,
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
    WorkerRestartResponse,
)


SYSTEM_SETTING_SCHEMAS: dict[str, type[BaseModel]] = {}


def register_system_setting_schema(key: str, schema_cls: type[BaseModel]):
    SYSTEM_SETTING_SCHEMAS[key] = schema_cls


def _validate_system_setting(key: str, value: dict) -> None:
    schema_cls = SYSTEM_SETTING_SCHEMAS.get(key)
    if schema_cls:
        try:
            schema_cls.model_validate(value)
        except ValidationError as e:
            raise ValidationException(f"Invalid value for setting '{key}': {e}")


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
        count = count_result.scalar() or 0
        if count > 0 and not admin:
            raise ConflictException("Admin already exists")

        admin_user = AdminUser(
            user_id=user_id,
            role="admin",
            is_active=True,
        )
        self.db.add(admin_user)
        await self.db.flush()
        return admin_user

    async def setup_first_admin(
        self, email: str, password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        display_name: str | None = None,
    ) -> dict:
        from app.core.security import hash_password

        existing_admin = await self.db.execute(select(AdminUser))
        admin_exists = (await self.db.execute(select(func.count()).select_from(AdminUser))).scalar() or 0
        if admin_exists > 0:
            raise ConflictException("Admin already exists; setup is only allowed for first admin")

        existing_user = await self.db.execute(select(User).where(User.email == email))
        user = existing_user.scalar_one_or_none()

        if user:
            user.is_admin = True
            user.display_name = display_name or user.display_name or email
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
        else:
            from app.core.config import settings
            user = User(
                email=email,
                display_name=display_name or email,
                first_name=first_name,
                last_name=last_name,
                status="active",
                is_admin=True,
            )
            self.db.add(user)
            await self.db.flush()

            identity = UserAuthIdentity(
                user_id=user.id,
                provider="email",
                provider_user_id=email,
                email=email,
                credentials_json={"password_hash": hash_password(password)},
            )
            self.db.add(identity)

        admin_user = AdminUser(user_id=user.id, role="admin", is_active=True)
        self.db.add(admin_user)
        await self.db.commit()
        return {
            "status": "created",
            "user_id": str(user.id),
            "admin_id": str(admin_user.id),
        }

    async def get_dashboard_stats(self) -> AdminDashboardStats:
        users_count = await self.db.execute(select(func.count()).select_from(User))
        total_users = users_count.scalar() or 0

        projects_count = await self.db.execute(select(func.count()).select_from(Project))
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

    async def list_generations(self, page: int = 1, page_size: int = 20, status: str | None = None) -> tuple[list[AdminGenerationResponse], int]:
        query = select(Generation)
        if status:
            query = query.where(Generation.status == status)
        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Generation.created_at.desc()).offset(offset).limit(page_size)
        )
        generations = list(result.scalars().all())
        return [AdminGenerationResponse.model_validate(g) for g in generations], total

    async def get_generation_detail(self, gen_id: UUID) -> AdminGenerationDetailResponse:
        generation = await self.db.get(Generation, gen_id)
        if generation is None:
            raise NotFoundException("Generation not found")
        result = await self.db.execute(
            select(Generation).options(joinedload(Generation.steps)).where(Generation.id == gen_id)
        )
        generation = result.scalar_one_or_none()
        if generation is None:
            raise NotFoundException("Generation not found")
        return AdminGenerationDetailResponse.model_validate(generation)

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

    async def list_ledger_transactions(
        self, page: int = 1, page_size: int = 20, transaction_type: str | None = None
    ) -> AdminLedgerResponse:
        query = select(LedgerTransaction).order_by(LedgerTransaction.created_at.desc())
        count_query = select(func.count()).select_from(LedgerTransaction)

        if transaction_type:
            query = query.where(LedgerTransaction.type == transaction_type)
            count_query = count_query.where(LedgerTransaction.type == transaction_type)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self.db.execute(query.offset(offset).limit(page_size))
        transactions = list(result.scalars().all())

        tx_dtos = []
        for tx in transactions:
            user_email = None
            if tx.user_id is not None:
                user_result = await self.db.execute(select(User.email).where(User.id == tx.user_id))
                user_email = user_result.scalar_one_or_none()
            tx_dtos.append(
                AdminLedgerTransactionResponse(
                    id=tx.id,
                    user_id=tx.user_id,
                    user_email=user_email,
                    wallet_id=tx.wallet_id,
                    type=tx.type,
                    amount_rub=float(tx.amount_rub),
                    is_bonus=tx.is_bonus,
                    admin_id=tx.admin_id,
                    reason=tx.reason,
                    reference_id=tx.reference_id,
                    created_at=tx.created_at,
                )
            )

        return AdminLedgerResponse(
            transactions=tx_dtos,
            total=total,
            page=page,
            page_size=page_size,
        )

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

        _validate_system_setting(key, body.value)
        setting.value = body.value
        from datetime import datetime as _dt, timezone as _tz
        setting.updated_at = _dt.now(_tz.utc)
        await self.db.flush()
        return AdminSystemSettingsResponse.model_validate(setting)

    async def ensure_default_settings(self) -> None:
        defaults = [
            ("feature_flags", {"NEW_RECOMMENDATION_ENGINE": False, "NEW_TEMPLATE_EDITOR": True, "VIDEO_LAB": False, "AUTO_MODERATION": False}),
            ("generation", {"default_model": "kling", "max_retries": 3, "queue_timeout_sec": 300, "generation_timeout_sec": 600}),
            ("payments", {"yookassa_enabled": True, "yookassa_webhook_secret": ""}),
            ("notifications", {"telegram_enabled": False, "email_enabled": True}),
        ]
        for key, value in defaults:
            result = await self.db.execute(select(SystemSettings).where(SystemSettings.key == key))
            existing = result.scalar_one_or_none()
            if existing is None:
                setting = SystemSettings(key=key, value=value, description=f"Default {key}", is_public=False)
                self.db.add(setting)
        await self.db.commit()

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

    async def list_gallery_pending(self) -> list:
        from app.models.gallery import GalleryStatus, GallerySubmission

        result = await self.db.execute(
            select(GallerySubmission)
            .where(GallerySubmission.status == GalleryStatus.pending)
            .order_by(GallerySubmission.created_at.desc())
        )
        return list(result.scalars().all())

    async def review_gallery_submission(self, submission_id, moderator_id, approve, make_public):
        from app.models.gallery import GalleryStatus, GallerySubmission

        submission = await self.db.get(GallerySubmission, submission_id)
        if submission is None:
            raise NotFoundException("Submission not found")
        submission.status = GalleryStatus.approved if approve else GalleryStatus.rejected
        submission.moderator_id = moderator_id
        submission.reviewed_at = datetime.now(timezone.utc)
        if approve:
            submission.is_public = make_public
        await self.db.flush()
        return submission

    async def get_order(self, order_id: UUID) -> AdminOrderDetailResponse:
        result = await self.db.execute(select(Generation).where(Generation.id == order_id))
        generation = result.scalar_one_or_none()
        if generation is None:
            raise NotFoundException("Order not found")
        return AdminOrderDetailResponse.model_validate(generation)

    async def update_worker_status(self, worker_id: UUID, status: str) -> AdminWorkerResponse:
        worker = await self.db.get(Worker, worker_id)
        if worker is None:
            raise NotFoundException("Worker not found")
        worker.status = status
        await self.db.flush()
        return AdminWorkerResponse.model_validate(worker)

    async def queue_job_action(self, job_id: UUID, action: str) -> AdminQueueJobResponse:
        job = await self.db.get(QueueJob, job_id)
        if job is None:
            raise NotFoundException("Job not found")
        if action == "cancel":
            job.status = "canceled"
        elif action == "retry":
            job.status = "pending"
            job.retry_count = 0
        elif action == "prioritize":
            job.priority = max((job.priority or 0) + 10, 0)
        elif action == "deprioritize":
            job.priority = min((job.priority or 0) - 10, 0)
        await self.db.flush()
        return AdminQueueJobResponse.model_validate(job)

    async def update_template(
        self, template_id: UUID, body: AdminTemplateUpdate
    ) -> AdminTemplateResponse:

        template = await self.db.get(Template, template_id)
        if template is None:
            raise NotFoundException("Template not found")

        update_data = body.model_dump(exclude_unset=True, by_alias=True, exclude={"metadata": True})
        if body.metadata_ is not None:
            update_data["metadata_"] = body.metadata_

        for key, value in update_data.items():
            setattr(template, key, value)

        await self.db.flush()
        return AdminTemplateResponse.model_validate(template)

    async def delete_template(self, template_id: UUID) -> None:
        template = await self.db.get(Template, template_id)
        if template is None:
            raise NotFoundException("Template not found")
        await self.db.delete(template)
        await self.db.flush()

    async def list_template_versions(self, template_id: UUID) -> list[AdminTemplateVersionResponse]:
        template = await self.db.get(Template, template_id)
        if template is None:
            raise NotFoundException("Template not found")
        result = await self.db.execute(
            select(TemplateVersion).where(TemplateVersion.template_id == template_id)
            .order_by(TemplateVersion.version.desc())
        )
        return [AdminTemplateVersionResponse.model_validate(v) for v in result.scalars().all()]

    async def create_template_version(
        self, template_id: UUID, body: AdminTemplateVersionCreate
    ) -> AdminTemplateVersionResponse:
        template = await self.db.get(Template, template_id)
        if template is None:
            raise NotFoundException("Template not found")

        version = TemplateVersion(
            template_id=template_id,
            **body.model_dump(exclude_unset=True),
        )
        self.db.add(version)
        await self.db.flush()
        return AdminTemplateVersionResponse.model_validate(version)

    async def update_template_version(
        self, version_id: UUID, body: AdminTemplateVersionUpdate
    ) -> AdminTemplateVersionResponse:
        version = await self.db.get(TemplateVersion, version_id)
        if version is None:
            raise NotFoundException("Template version not found")

        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(version, key, value)

        await self.db.flush()
        return AdminTemplateVersionResponse.model_validate(version)

    async def list_template_scenes(self, template_id: UUID) -> list[AdminSceneResponse]:
        template = await self.db.get(Template, template_id)
        if template is None:
            raise NotFoundException("Template not found")
        result = await self.db.execute(
            select(Scene).where(Scene.template_id == template_id)
            .order_by(Scene.created_at.asc())
        )
        return [AdminSceneResponse.model_validate(s) for s in result.scalars().all()]

    async def create_template_scene(
        self, template_id: UUID, body: AdminSceneCreate
    ) -> AdminSceneResponse:
        template = await self.db.get(Template, template_id)
        if template is None:
            raise NotFoundException("Template not found")

        scene = Scene(
            template_id=template_id,
            **body.model_dump(exclude_unset=True),
        )
        self.db.add(scene)
        await self.db.flush()
        return AdminSceneResponse.model_validate(scene)

    async def update_template_scene(
        self, scene_id: UUID, body: AdminSceneUpdate
    ) -> AdminSceneResponse:
        scene = await self.db.get(Scene, scene_id)
        if scene is None:
            raise NotFoundException("Scene not found")

        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(scene, key, value)

        await self.db.flush()
        return AdminSceneResponse.model_validate(scene)

    async def delete_template_scene(self, scene_id: UUID) -> None:
        scene = await self.db.get(Scene, scene_id)
        if scene is None:
            raise NotFoundException("Scene not found")
        await self.db.delete(scene)
        await self.db.flush()

    async def worker_restart(self, worker_id: UUID) -> WorkerRestartResponse:
        worker = await self.db.get(Worker, worker_id)
        if worker is None:
            raise NotFoundException("Worker not found")
        worker.status = "restarting"
        await self.db.flush()
        return WorkerRestartResponse(success=True, message=f"Restart signal sent to worker {worker.name}", worker_id=worker_id)

    async def worker_shutdown(self, worker_id: UUID) -> WorkerRestartResponse:
        worker = await self.db.get(Worker, worker_id)
        if worker is None:
            raise NotFoundException("Worker not found")
        worker.status = "offline"
        await self.db.flush()
        return WorkerRestartResponse(success=True, message=f"Shutdown signal sent to worker {worker.name}", worker_id=worker_id)

    async def bulk_queue_action(self, action: str, job_ids: list[UUID]) -> list[AdminQueueJobResponse]:
        result = await self.db.execute(
            select(QueueJob).where(QueueJob.id.in_(job_ids))
        )
        jobs = list(result.scalars().all())
        results = []
        for job in jobs:
            if action == "cancel":
                job.status = "canceled"
            elif action == "retry":
                job.status = "pending"
                job.retry_count = 0
            elif action == "prioritize":
                job.priority = max((job.priority or 0) + 10, 0)
            elif action == "deprioritize":
                job.priority = min((job.priority or 0) - 10, 0)
            results.append(AdminQueueJobResponse.model_validate(job))
        await self.db.flush()
        return results

    async def update_queue_job_priority(self, job_id: UUID, priority: int) -> AdminQueueJobResponse:
        job = await self.db.get(QueueJob, job_id)
        if job is None:
            raise NotFoundException("Job not found")
        job.priority = priority
        await self.db.flush()
        return AdminQueueJobResponse.model_validate(job)

    async def get_analytics(self, days: int = 7) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        total_generations = await self.db.execute(
            select(func.count()).select_from(Generation).where(Generation.created_at >= since)
        )
        total_payments = await self.db.execute(
            select(func.sum(Payment.amount_rub)).where(Payment.created_at >= since, Payment.status == "paid")
        )
        total_users = await self.db.execute(
            select(func.count()).select_from(User).where(User.created_at >= since)
        )

        status_counts = {}
        status_result = await self.db.execute(
            select(Generation.status, func.count())
            .where(Generation.created_at >= since)
            .group_by(Generation.status)
        )
        for status, count in status_result.all():
            status_counts[status] = count

        model_stats = {}
        model_result = await self.db.execute(
            select(Generation.model_name, func.count(), func.sum(Generation.cost_rub))
            .where(Generation.created_at >= since)
            .group_by(Generation.model_name)
        )
        for model, count, cost in model_result.all():
            if model:
                model_stats[model] = {"count": count, "cost": float(cost or 0)}

        daily_revenue = {}
        daily_result = await self.db.execute(
            select(
                func.date(Payment.created_at).label("date"),
                func.sum(Payment.amount_rub).label("total"),
            )
            .where(Payment.created_at >= since, Payment.status == "paid")
            .group_by(func.date(Payment.created_at))
        )
        for date, total in daily_result.all():
            daily_revenue[str(date)] = float(total or 0)

        daily_generations = {}
        daily_gen_result = await self.db.execute(
            select(
                func.date(Generation.created_at).label("date"),
                Generation.status,
                func.count().label("count"),
            )
            .where(Generation.created_at >= since)
            .group_by(func.date(Generation.created_at), Generation.status)
        )
        for date, status, count in daily_gen_result.all():
            key = str(date)
            if key not in daily_generations:
                daily_generations[key] = {}
            daily_generations[key][status] = count

        return {
            "period_days": days,
            "total_generations": total_generations.scalar() or 0,
            "total_revenue": float(total_payments.scalar() or 0),
            "total_new_users": total_users.scalar() or 0,
            "generation_status_breakdown": status_counts,
            "cost_by_model": model_stats,
            "daily_revenue": daily_revenue,
            "daily_generations": daily_generations,
        }
