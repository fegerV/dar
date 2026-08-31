import logging
from datetime import UTC, datetime

import httpx
from sqlalchemy import select

from app.core.config import settings
from app.models.delivery import Delivery
from app.models.user import User
from app.repositories.delivery import DeliveryRepository

logger = logging.getLogger(__name__)


class TelegramDeliveryService:
    API_BASE = "https://api.telegram.org/bot{token}"

    def __init__(self, db) -> None:
        self.db = db
        self.repo = DeliveryRepository(db)

    async def send(self, delivery: Delivery, video_url: str | None, caption: str | None = None) -> None:
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("Telegram bot token not configured")
            return

        chat_id = delivery.destination
        if not chat_id and delivery.user_id:
            result = await self.db.execute(
                select(User.telegram_user_id).where(User.id == delivery.user_id)
            )
            chat_id = result.scalar_one_or_none()

        if not chat_id:
            logger.warning("Telegram chat_id missing for delivery %s", delivery.id)
            return

        text = caption or "Ваше видеопоздравление готово 🎬"
        payload = {
            "chat_id": chat_id,
            "caption": text,
            "parse_mode": "HTML",
        }

        if video_url:
            payload["video"] = video_url
            method = "sendVideo"
        else:
            payload["text"] = text
            method = "sendMessage"

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    self.API_BASE.format(token=settings.TELEGRAM_BOT_TOKEN) + f"/{method}",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                delivery.status = "sent"
                delivery.sent_at = datetime.now(UTC)
                delivery.external_message_id = str(result.get("result", {}).get("message_id"))
                await self.repo.create_delivery(delivery)
                logger.info("Telegram message sent to %s", chat_id)
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to send telegram to %s: %s", chat_id, e)
            delivery.status = "failed"
            delivery.error_message = str(e)
            delivery.failed_at = datetime.now(UTC)
            await self.repo.create_delivery(delivery)
