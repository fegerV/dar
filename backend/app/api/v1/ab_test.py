from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException
from app.schemas.ab_test import (
    ABTestCreate,
    ABTestResponse,
    ABTestResultRecord,
    ABTestStatusUpdate,
    ABTestVariantCreate,
)
from app.services.ab_test.service import ABTestService

router = APIRouter(prefix="/ab-tests", tags=["A/B Testing"])


def require_admin(current_user=Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise ForbiddenException("Admin access required")
    return current_user


@router.get("/", response_model=list[ABTestResponse])
async def list_tests(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = ABTestService(db)
    return await service.list_tests()


@router.post("/", response_model=ABTestResponse, status_code=201)
async def create_test(
    body: ABTestCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = ABTestService(db)
    return await service.create_test(body)


@router.get("/{test_id}", response_model=ABTestResponse)
async def get_test(
    test_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = ABTestService(db)
    return await service.get_test(test_id)


@router.patch("/{test_id}/status", response_model=ABTestResponse)
async def update_status(
    test_id: UUID,
    body: ABTestStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = ABTestService(db)
    return await service.update_status(test_id, body.status)


@router.get("/{test_id}/variant", response_model=ABTestVariantCreate | None)
async def get_user_variant(
    test_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ABTestService(db)
    return await service.get_variant_for_user(test_id, current_user.id)


@router.post("/{test_id}/results", status_code=204)
async def record_result(
    test_id: UUID,
    body: ABTestResultRecord,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ABTestService(db)
    await service.record_result(
        test_id=test_id,
        variant_code=body.variant_code,
        metric=body.metric,
        value=body.value,
    )
    await db.commit()
