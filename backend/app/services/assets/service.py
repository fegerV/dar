import os
import uuid
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.integrations.storage.factory import get_storage_provider
from app.models.asset import Asset, StorageObject
from app.repositories.storage import StorageRepository
from app.schemas.asset import AssetUploadRequest, AssetUploadResponse, AssetResponse, AssetListResponse

ALLOWED_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".avi", ".mp3", ".wav", ".ogg", ".pdf", ".txt"}


class AssetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage_repo = StorageRepository(db)
        self.storage = get_storage_provider()

    async def get_upload_url(self, body: AssetUploadRequest, user_id: UUID) -> AssetUploadResponse:
        safe_name = os.path.basename(body.filename)
        if not safe_name or safe_name in (".", ".."):
            raise ValidationException("Invalid filename")
        ext = os.path.splitext(safe_name)[1].lower()
        if ext not in ALLOWED_FILE_EXTENSIONS:
            raise ValidationException(f"File extension '{ext}' not allowed")
        asset_id = uuid.uuid4()
        object_key = f"uploads/{user_id}/{asset_id}_{safe_name}"
        upload_url = await self.storage.generate_presigned_upload_url(
            bucket="daragent",
            object_key=object_key,
            expires_in=900,
            content_type=body.mime_type,
        )
        return AssetUploadResponse(asset_id=asset_id, upload_url=upload_url, expires_in=900)

    async def confirm_upload(self, asset_id: UUID, user_id: UUID, object_key: str) -> AssetResponse:
        expected_prefix = f"uploads/{user_id}/"
        if not object_key.startswith(expected_prefix):
            raise NotFoundException("Asset not found")

        existing = await self.storage_repo.get_asset(asset_id)
        if existing is not None and existing.owner_user_id != user_id:
            raise NotFoundException("Asset not found")

        storage_obj = StorageObject(
            bucket="daragent",
            object_key=object_key,
            original_name=object_key.split("/")[-1],
        )
        storage_obj = await self.storage_repo.create_object(storage_obj)

        asset = Asset(
            owner_user_id=user_id,
            type="file",
            status="uploaded",
            storage_object_id=storage_obj.id,
        )
        asset = await self.storage_repo.create_asset(asset)
        await self.db.commit()
        return AssetResponse.model_validate(asset)

    async def list_assets(
        self, user_id: UUID, page: int = 1, page_size: int = 20
    ) -> AssetListResponse:
        from sqlalchemy import select, func
        from app.models.asset import Asset

        count_query = select(func.count()).select_from(Asset).where(Asset.owner_user_id == user_id)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = (
            select(Asset)
            .where(Asset.owner_user_id == user_id)
            .order_by(Asset.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        items = [AssetResponse.model_validate(a) for a in result.scalars().all()]
        return AssetListResponse(items=items, total=total, page=page, page_size=page_size)

    async def get_asset(self, asset_id: UUID, user_id: UUID) -> AssetResponse:
        asset = await self.storage_repo.get_asset(asset_id)
        if asset is None or asset.owner_user_id != user_id:
            raise NotFoundException("Asset not found")
        return AssetResponse.model_validate(asset)
