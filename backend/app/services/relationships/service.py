from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relationship import RecipientGroup, RecipientSharedMemory, RelationshipSubtype


class RelationshipContextService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_subtypes(self, parent_code: str | None = None) -> list[RelationshipSubtype]:
        query = select(RelationshipSubtype).where(RelationshipSubtype.is_active.is_(True))
        if parent_code:
            query = query.where(RelationshipSubtype.parent_code == parent_code)
        query = query.order_by(RelationshipSubtype.sort_order.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_group(self, user_id: UUID, code: str, title: str) -> RecipientGroup:
        group = RecipientGroup(
            owner_user_id=user_id,
            code=code,
            title=title,
            is_active=True,
        )
        self.db.add(group)
        await self.db.flush()
        return group

    async def list_groups(self, user_id: UUID) -> list[RecipientGroup]:
        result = await self.db.execute(
            select(RecipientGroup)
            .where(
                RecipientGroup.owner_user_id == user_id,
                RecipientGroup.is_active.is_(True),
            )
            .order_by(RecipientGroup.sort_order.asc())
        )
        return list(result.scalars().all())

    async def create_shared_memory(
        self,
        recipient_id: UUID,
        title: str,
        description: str,
        tags: list[str] | None = None,
        group_id: UUID | None = None,
        remind_before_days: int | None = None,
    ) -> RecipientSharedMemory:
        memory = RecipientSharedMemory(
            recipient_id=recipient_id,
            group_id=group_id,
            title=title,
            description=description,
            tags=tags or [],
            remind_before_days=remind_before_days,
            is_active=True,
        )
        self.db.add(memory)
        await self.db.flush()
        return memory

    async def list_shared_memories(self, recipient_id: UUID) -> list[RecipientSharedMemory]:
        result = await self.db.execute(
            select(RecipientSharedMemory)
            .where(
                RecipientSharedMemory.recipient_id == recipient_id,
                RecipientSharedMemory.is_active.is_(True),
            )
            .order_by(RecipientSharedMemory.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_recipient_context(self, recipient_id: UUID) -> dict:
        memories = await self.list_shared_memories(recipient_id)
        inside_jokes = [m.title for m in memories if "joke" in m.tags]
        return {
            "inside_jokes": inside_jokes,
            "shared_memories": memories,
        }
