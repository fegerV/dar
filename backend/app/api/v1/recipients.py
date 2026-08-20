from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.recipient import (
    RecipientCreate,
    RecipientUpdate,
    RecipientResponse,
    RecipientListResponse,
    RecipientPhotoUploadRequest,
    RecipientPhotoUploadResponse,
)
from app.services.recipients.service import RecipientService

router = APIRouter(prefix="/recipients", tags=["Recipients"])


@router.post("", response_model=RecipientResponse, status_code=201)
async def create_recipient(
    body: RecipientCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecipientService(db)
    return await service.create(current_user.id, body)


@router.get("", response_model=RecipientListResponse)
async def list_recipients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecipientService(db)
    items, total = await service.list(current_user.id, page, page_size, search)
    return RecipientListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{recipient_id}", response_model=RecipientResponse)
async def get_recipient(
    recipient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecipientService(db)
    return await service.get(current_user.id, recipient_id)


@router.patch("/{recipient_id}", response_model=RecipientResponse)
async def update_recipient(
    recipient_id: UUID,
    body: RecipientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecipientService(db)
    return await service.update(current_user.id, recipient_id, body)


@router.delete("/{recipient_id}", status_code=204)
async def archive_recipient(
    recipient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecipientService(db)
    await service.archive(current_user.id, recipient_id)


@router.post("/{recipient_id}/photo/upload-url", response_model=RecipientPhotoUploadResponse)
async def get_photo_upload_url(
    recipient_id: UUID,
    body: RecipientPhotoUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecipientService(db)
    return await service.get_photo_upload_url(current_user.id, recipient_id, body)


@router.post("/{recipient_id}/photo/confirm-upload", response_model=RecipientResponse)
async def confirm_photo_upload(
    recipient_id: UUID,
    asset_id: UUID,
    object_key: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = RecipientService(db)
    return await service.confirm_photo_upload(current_user.id, recipient_id, asset_id, object_key)
