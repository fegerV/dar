from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.recipient import Recipient
from app.repositories.recipients import RecipientRepository
from app.schemas.recipient import RecipientCreate, RecipientUpdate, RecipientResponse


class RecipientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RecipientRepository(db)

    async def create(self, owner_user_id: UUID, body: RecipientCreate) -> RecipientResponse:
        recipient = Recipient(
            owner_user_id=owner_user_id,
            **body.model_dump(),
        )
        recipient = await self.repo.create(recipient)
        await self.db.flush()
        return RecipientResponse.model_validate(recipient)

    async def get(self, owner_user_id: UUID, recipient_id: UUID) -> RecipientResponse:
        recipient = await self.repo.get_by_id(recipient_id, owner_user_id)
        if recipient is None:
            raise NotFoundException("Получатель не найден")
        return RecipientResponse.model_validate(recipient)

    async def list(
        self,
        owner_user_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> tuple[list[RecipientResponse], int]:
        items, total = await self.repo.list_by_owner(owner_user_id, page, page_size, search)
        return [RecipientResponse.model_validate(item) for item in items], total

    async def update(
        self, owner_user_id: UUID, recipient_id: UUID, body: RecipientUpdate
    ) -> RecipientResponse:
        recipient = await self.repo.get_by_id(recipient_id, owner_user_id)
        if recipient is None:
            raise NotFoundException("Получатель не найден")

        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(recipient, key, value)

        recipient.updated_at = datetime.now(timezone.utc)
        await self.repo.update(recipient)
        await self.db.flush()
        return RecipientResponse.model_validate(recipient)

    async def archive(self, owner_user_id: UUID, recipient_id: UUID) -> None:
        recipient = await self.repo.get_by_id(recipient_id, owner_user_id)
        if recipient is None:
            raise NotFoundException("Получатель не найден")
        await self.repo.archive(recipient)
        await self.db.flush()
