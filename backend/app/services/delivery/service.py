import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.delivery import Delivery, DeliveryLink, ShareEvent
from app.models.project import Project
from app.repositories.delivery import DeliveryRepository
from app.repositories.projects import ProjectRepository
from app.schemas.delivery import (
    DeliveryCreate,
    DeliveryListResponse,
    DeliveryResponse,
    PublicShareView,
    ShareLinkResponse,
)


class DeliveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DeliveryRepository(db)
        self.project_repo = ProjectRepository(db)

    async def create_delivery(
        self, project_id: UUID, user_id: UUID, body: DeliveryCreate
    ) -> DeliveryResponse:
        project = await self.project_repo.get_by_id(project_id, user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        generation = await self.repo.get_latest_generation(project_id)
        if generation is None or generation.status != "completed":
            raise ValidationException("Видео ещё не готово к доставке")

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_in_days)

        password_hash = None
        if body.password:
            password_hash = hashlib.sha256(body.password.encode()).hexdigest()

        link = DeliveryLink(
            project_id=project_id,
            generation_id=generation.id,
            token_hash=token_hash,
            expires_at=expires_at,
            max_views=None,
            password_hash=password_hash,
            is_active=True,
        )
        link = await self.repo.create_link(link)

        public_url = f"/share/{token}"

        delivery = Delivery(
            project_id=project_id,
            generation_id=generation.id,
            user_id=user_id,
            channel=body.channel,
            status="scheduled" if body.scheduled_at else ("sent" if body.channel != "link" else "created"),
            destination=body.destination,
            delivery_link_id=link.id,
            scheduled_at=body.scheduled_at,
        )

        if body.scheduled_at and body.timezone:
            delivery.scheduled_at = self._convert_to_utc(body.scheduled_at, body.timezone)
        delivery = await self.repo.create_delivery(delivery)

        if body.scheduled_at:
            return DeliveryResponse(
                id=delivery.id,
                project_id=project_id,
                channel=body.channel,
                status="scheduled",
                destination=body.destination,
                public_url=public_url,
                created_at=delivery.created_at,
                scheduled_at=delivery.scheduled_at,
                sent_at=None,
                opened_at=None,
            )

        if body.channel == "link":
            return DeliveryResponse(
                id=delivery.id,
                project_id=project_id,
                channel=body.channel,
                status="created",
                destination=body.destination,
                public_url=public_url,
                created_at=delivery.created_at,
                sent_at=None,
                opened_at=None,
            )

        return DeliveryResponse(
            id=delivery.id,
            project_id=project_id,
            channel=body.channel,
            status=delivery.status,
            destination=body.destination,
            public_url=public_url,
            created_at=delivery.created_at,
            scheduled_at=delivery.scheduled_at,
            sent_at=delivery.sent_at,
            opened_at=delivery.opened_at,
        )

    async def list_deliveries(self, project_id: UUID, user_id: UUID) -> DeliveryListResponse:
        project = await self.project_repo.get_by_id(project_id, user_id)
        if project is None:
            raise NotFoundException("Проект не найден")

        deliveries = await self.repo.list_by_project(project_id)
        return DeliveryListResponse(
            items=[DeliveryResponse.model_validate(d) for d in deliveries]
        )

    async def get_delivery(self, delivery_id: UUID, user_id: UUID) -> DeliveryResponse:
        delivery = await self.repo.get_by_id(delivery_id)
        if delivery is None or delivery.user_id != user_id:
            raise NotFoundException("Доставка не найдена")
        return DeliveryResponse.model_validate(delivery)

    async def get_public_share(self, token: str, password: str | None = None) -> PublicShareView:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        link = await self.repo.get_link_by_token(token_hash)
        if link is None or not link.is_active:
            raise NotFoundException("Ссылка не найдена или недоступна")

        if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
            raise NotFoundException("Ссылка истекла")

        if link.max_views is not None and (link.view_count or 0) >= link.max_views:
            raise NotFoundException("Лимит просмотров исчерпан")

        if link.password_hash:
            if not password:
                raise ValidationException("Требуется пароль")
            if hashlib.sha256(password.encode()).hexdigest() != link.password_hash:
                raise ValidationException("Неверный пароль")

        await self.repo.increment_link_views(link.id)

        generation = await self.repo.get_latest_generation(link.project_id)
        output = generation.output_json if generation else {}

        return PublicShareView(
            project_id=link.project_id,
            title=None,
            status="ready",
            recipient_name=None,
            video_url=output.get("video_url"),
            thumbnail_url=output.get("thumbnail_url"),
            duration_sec=output.get("duration_sec"),
        )

    async def track_share_event(
        self, project_id: UUID, channel: str, user_id: UUID | None = None
    ) -> None:
        event = ShareEvent(
            project_id=project_id,
            user_id=user_id,
            channel=channel,
            metadata={},
        )
        await self.repo.create_share_event(event)
        await self.db.commit()

    @staticmethod
    def _convert_to_utc(scheduled_at: datetime, user_timezone: str) -> datetime:
        if scheduled_at.tzinfo is not None:
            return scheduled_at.astimezone(timezone.utc)
        from zoneinfo import ZoneInfo

        try:
            tz = ZoneInfo(user_timezone)
            return scheduled_at.replace(tzinfo=tz).astimezone(timezone.utc)
        except Exception:
            return scheduled_at.replace(tzinfo=timezone.utc)
