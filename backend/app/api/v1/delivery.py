from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryListResponse,
    DeliveryResponse,
    ShareLinkResponse,
)
from app.services.delivery.service import DeliveryService

router = APIRouter(prefix="/delivery", tags=["Delivery"])


@router.post("/projects/{project_id}", response_model=DeliveryResponse)
async def create_delivery(
    project_id: UUID,
    body: DeliveryCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DeliveryService(db)
    return await service.create_delivery(project_id, current_user.id, body)


@router.get("/projects/{project_id}", response_model=DeliveryListResponse)
async def list_deliveries(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DeliveryService(db)
    return await service.list_deliveries(project_id, current_user.id)


@router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(
    delivery_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DeliveryService(db)
    return await service.get_delivery(delivery_id, current_user.id)
