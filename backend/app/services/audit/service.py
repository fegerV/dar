from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.audit import AuditRepository


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AuditRepository(db)

    async def log(self, actor_user_id: UUID | None, action: str, target_type: str | None = None, target_id: UUID | None = None, ip_address: str | None = None, user_agent: str | None = None, metadata: dict | None = None) -> AuditLog:
        log = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_=metadata or {},
            created_at=datetime.now(UTC),
        )
        return await self.repo.create(log)

    async def list_actor(self, actor_user_id: UUID, limit: int = 100, offset: int = 0):
        return await self.repo.list_by_actor(actor_user_id, limit=limit, offset=offset)

    async def delete_user_audit(self, user_id: UUID) -> None:
        await self.repo.delete_user_data(user_id)
        await self.db.commit()
