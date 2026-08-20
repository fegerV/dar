import os
import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ValidationException
from app.integrations.storage.factory import get_storage_provider
from app.models.asset import Asset, StorageObject
from app.models.recipient import Recipient, RecipientAsset
from app.repositories.recipients import RecipientRepository
from app.schemas.recipient import RecipientCreate, RecipientUpdate, RecipientResponse
from app.schemas.recipient import RecipientPhotoUploadRequest, RecipientPhotoUploadResponse

ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


class RecipientService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RecipientRepository(db)
        self.storage = get_storage_provider()

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

    async def get_photo_upload_url(
        self, owner_user_id: UUID, recipient_id: UUID, body: RecipientPhotoUploadRequest
    ) -> RecipientPhotoUploadResponse:
        recipient = await self.repo.get_by_id(recipient_id, owner_user_id)
        if recipient is None:
            raise NotFoundException("Получатель не найден")

        safe_name = os.path.basename(body.filename)
        if not safe_name or safe_name in (".", ".."):
            raise ValidationException("Invalid filename")
        ext = os.path.splitext(safe_name)[1].lower()
        if ext not in ALLOWED_PHOTO_EXTENSIONS:
            raise ValidationException(f"File extension '{ext}' not allowed for photos")

        asset_id = uuid.uuid4()
        object_key = f"uploads/{owner_user_id}/{asset_id}_{safe_name}"
        upload_url = await self.storage.generate_presigned_upload_url(
            bucket="daragent",
            object_key=object_key,
            expires_in=900,
            content_type=body.mime_type,
        )
        return RecipientPhotoUploadResponse(asset_id=asset_id, upload_url=upload_url, expires_in=900)

    async def confirm_photo_upload(
        self, owner_user_id: UUID, recipient_id: UUID, asset_id: UUID, object_key: str
    ) -> RecipientResponse:
        recipient = await self.repo.get_by_id(recipient_id, owner_user_id)
        if recipient is None:
            raise NotFoundException("Получатель не найден")

        expected_prefix = f"uploads/{owner_user_id}/"
        if not object_key.startswith(expected_prefix):
            raise NotFoundException("Asset not found")

        existing = await self.db.execute(
            select(StorageObject).where(StorageObject.object_key == object_key)
        )
        storage_obj = existing.scalar_one_or_none()

        if storage_obj is None:
            storage_obj = StorageObject(
                bucket="daragent",
                object_key=object_key,
                original_name=object_key.split("/")[-1],
                mime_type="image/jpeg",
            )
            self.db.add(storage_obj)
            await self.db.flush()

        asset = await self.db.get(Asset, asset_id)
        if asset is not None and asset.owner_user_id != owner_user_id:
            raise NotFoundException("Asset not found")

        if asset is None:
            asset = Asset(
                id=asset_id,
                owner_user_id=owner_user_id,
                type="photo",
                status="uploaded",
                storage_object_id=storage_obj.id,
            )
            self.db.add(asset)
            await self.db.flush()

        existing_links = await self.db.execute(
            select(RecipientAsset).where(
                RecipientAsset.recipient_id == recipient_id,
                RecipientAsset.asset_id == asset_id,
            )
        )
        if existing_links.scalar_one_or_none() is None:
            link = RecipientAsset(
                recipient_id=recipient_id,
                asset_id=asset.id,
                is_primary=True,
                sort_order=0,
            )
            self.db.add(link)

        await self.db.commit()
        result = await self.db.execute(
            select(Recipient)
            .options(
                selectinload(Recipient.recipient_assets).selectinload(RecipientAsset.asset),
            )
            .where(Recipient.id == recipient_id, Recipient.owner_user_id == owner_user_id)
            .execution_options(populate_existing=True)
        )
        recipient = result.scalar_one()
        return RecipientResponse.model_validate(recipient)
