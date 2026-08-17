from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.delivery import PublicShareView
from app.services.delivery.service import DeliveryService

router = APIRouter(prefix="/share", tags=["Public Share"])


@router.get("/{token}", response_model=PublicShareView)
async def get_public_share(token: str, db: AsyncSession = Depends(get_db)):
    service = DeliveryService(db)
    return await service.get_public_share(token)
