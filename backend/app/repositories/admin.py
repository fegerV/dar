from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AdminUser, QueueJob, Role, SystemSettings, Worker


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_admin_user(self, user_id: UUID) -> AdminUser | None:
        result = await self.db.execute(
            select(AdminUser).where(AdminUser.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_admin_user(self, admin_user: AdminUser) -> AdminUser:
        self.db.add(admin_user)
        await self.db.flush()
        return admin_user

    async def list_roles(self) -> list[Role]:
        result = await self.db.execute(select(Role).order_by(Role.name))
        return list(result.scalars().all())

    async def get_role(self, role_id: UUID) -> Role | None:
        return await self.db.get(Role, role_id)

    async def create_role(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        return role

    async def list_workers(self) -> list[Worker]:
        result = await self.db.execute(select(Worker).order_by(Worker.name))
        return list(result.scalars().all())

    async def get_worker(self, worker_id: UUID) -> Worker | None:
        return await self.db.get(Worker, worker_id)

    async def upsert_worker(self, worker: Worker) -> Worker:
        existing = await self.db.get(Worker, worker.id)
        if existing:
            existing.name = worker.name
            existing.status = worker.status
            existing.gpu_model = worker.gpu_model
            existing.gpu_vram_total_gb = worker.gpu_vram_total_gb
            existing.gpu_vram_used_gb = worker.gpu_vram_used_gb
            existing.cpu_usage_percent = worker.cpu_usage_percent
            existing.jobs_today = worker.jobs_today
            existing.failures_today = worker.failures_today
            existing.avg_generation_time_sec = worker.avg_generation_time_sec
            existing.last_heartbeat_at = worker.last_heartbeat_at or datetime.now(UTC)
            existing.metadata_ = worker.metadata_
            await self.db.flush()
            return existing
        self.db.add(worker)
        await self.db.flush()
        return worker

    async def list_queue_jobs(self, status: str | None = None) -> list[QueueJob]:
        query = select(QueueJob).order_by(QueueJob.created_at.desc())
        if status:
            query = query.where(QueueJob.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_queue_job(self, job_id: UUID) -> QueueJob | None:
        return await self.db.get(QueueJob, job_id)

    async def create_queue_job(self, job: QueueJob) -> QueueJob:
        self.db.add(job)
        await self.db.flush()
        return job

    async def update_queue_job(self, job: QueueJob) -> QueueJob:
        await self.db.flush()
        return job

    async def list_system_settings(self) -> list[SystemSettings]:
        result = await self.db.execute(select(SystemSettings).order_by(SystemSettings.key))
        return list(result.scalars().all())

    async def get_system_setting(self, key: str) -> SystemSettings | None:
        result = await self.db.execute(
            select(SystemSettings).where(SystemSettings.key == key)
        )
        return result.scalar_one_or_none()

    async def upsert_system_setting(self, setting: SystemSettings) -> SystemSettings:
        existing = await self.db.get(SystemSettings, setting.key)
        if existing:
            existing.value = setting.value
            existing.description = setting.description
            existing.is_public = setting.is_public
            await self.db.flush()
            return existing
        self.db.add(setting)
        await self.db.flush()
        return setting
