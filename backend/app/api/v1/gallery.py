from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.gallery import (
    GalleryListResponse,
    GallerySubmissionCreate,
    GallerySubmissionResponse,
)
from app.services.gallery.service import GalleryService

router = APIRouter(prefix="/gallery", tags=["Gallery"])


@router.post("/", response_model=GallerySubmissionResponse)
async def submit_to_gallery(
    body: GallerySubmissionCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = GalleryService(db)
    return await service.submit(current_user.id, body)


@router.get("/my", response_model=GalleryListResponse)
async def get_my_submissions(
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = GalleryService(db)
    items = await service.list_my_submissions(current_user.id)
    return GalleryListResponse(items=items)


@router.get("/public", response_model=GalleryListResponse)
async def list_public_gallery(
    db=Depends(get_db),
):
    service = GalleryService(db)
    items = await service.list_public()
    return GalleryListResponse(items=items)


@router.get("/{submission_id}", response_model=GallerySubmissionResponse)
async def get_submission(
    submission_id: UUID,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = GalleryService(db)
    submission = await service.repo.get_by_id(submission_id)
    if submission is None or submission.user_id != current_user.id:
        from app.core.exceptions import NotFoundException

        raise NotFoundException("Подача не найдена")
    return GallerySubmissionResponse.model_validate(submission)
