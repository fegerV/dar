from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.asset import (
    AssetListResponse,
    AssetResponse,
    AssetUploadRequest,
    AssetUploadResponse,
)
from app.services.assets.service import AssetService

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("/upload-url", response_model=AssetUploadResponse)
async def get_upload_url(
    body: AssetUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AssetService(db)
    return await service.get_upload_url(body, current_user.id)


@router.post("/confirm-upload", response_model=AssetResponse)
async def confirm_upload(
    asset_id: UUID,
    object_key: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AssetService(db)
    return await service.confirm_upload(asset_id, current_user.id, object_key)


@router.get("", response_model=AssetListResponse)
async def list_assets(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AssetService(db)
    return await service.list_assets(current_user.id, page, page_size)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AssetService(db)
    return await service.get_asset(asset_id, current_user.id)
