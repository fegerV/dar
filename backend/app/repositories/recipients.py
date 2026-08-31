from datetime import UTC
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recipient import Recipient, RecipientAsset


class RecipientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, recipient_id: UUID, owner_user_id: UUID) -> Recipient | None:
        result = await self.db.execute(
            select(Recipient)
            .options(
                selectinload(Recipient.recipient_assets).selectinload(RecipientAsset.asset),
            )
            .where(
                Recipient.id == recipient_id,
                Recipient.owner_user_id == owner_user_id,
                Recipient.archived_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_owner(
        self,
        owner_user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[Recipient], int]:
        query = (
            select(Recipient)
            .options(
                selectinload(Recipient.recipient_assets).selectinload(RecipientAsset.asset),
            )
            .where(
                Recipient.owner_user_id == owner_user_id,
                Recipient.archived_at.is_(None),
            )
        )
        count_query = select(func.count()).select_from(Recipient).where(
            Recipient.owner_user_id == owner_user_id,
            Recipient.archived_at.is_(None),
        )

        if search:
            pattern = f"%{search}%"
            query = query.where(
                (Recipient.first_name.ilike(pattern))
                | (Recipient.last_name.ilike(pattern))
                | (Recipient.nickname.ilike(pattern))
            )
            count_query = count_query.where(
                (Recipient.first_name.ilike(pattern))
                | (Recipient.last_name.ilike(pattern))
                | (Recipient.nickname.ilike(pattern))
            )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = query.order_by(Recipient.updated_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, recipient: Recipient) -> Recipient:
        self.db.add(recipient)
        await self.db.flush()
        return recipient

    async def update(self, recipient: Recipient) -> Recipient:
        await self.db.flush()
        return recipient

    async def archive(self, recipient: Recipient) -> Recipient:
        from datetime import datetime

        recipient.archived_at = datetime.now(UTC)
        await self.db.flush()
        return recipient
