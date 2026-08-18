from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryListResponse,
    DeliveryResponse,
    PublicShareAccessRequest,
    PublicShareView,
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


@router.post("/share/{token}/access", response_model=PublicShareView)
async def access_share(
    token: str,
    body: PublicShareAccessRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DeliveryService(db)
    return await service.get_public_share(token, password=body.password)


@router.post("/{delivery_id}/send-email", response_model=DeliveryResponse)
async def send_email_delivery(
    delivery_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.delivery import Delivery
    from app.repositories.delivery import DeliveryRepository
    from app.services.delivery.email import EmailDeliveryService

    repo = DeliveryRepository(db)
    delivery = await db.get(Delivery, delivery_id)
    if delivery is None or delivery.user_id != current_user.id:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Доставка не найдена")

    generation = await repo.get_latest_generation(delivery.project_id)
    output = generation.output_json if generation else {}
    email_service = EmailDeliveryService(db)
    await email_service.send(
        delivery=delivery,
        video_url=output.get("video_url"),
        thumbnail_url=output.get("thumbnail_url"),
    )
    return DeliveryResponse.model_validate(delivery)


@router.post("/{delivery_id}/send-telegram", response_model=DeliveryResponse)
async def send_telegram_delivery(
    delivery_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.delivery import Delivery
    from app.repositories.delivery import DeliveryRepository
    from app.services.delivery.telegram import TelegramDeliveryService

    repo = DeliveryRepository(db)
    delivery = await db.get(Delivery, delivery_id)
    if delivery is None or delivery.user_id != current_user.id:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Доставка не найдена")

    generation = await repo.get_latest_generation(delivery.project_id)
    output = generation.output_json if generation else {}
    telegram_service = TelegramDeliveryService(db)
    await telegram_service.send(
        delivery=delivery,
        video_url=output.get("video_url"),
    )
    return DeliveryResponse.model_validate(delivery)
