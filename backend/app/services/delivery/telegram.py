import logging
from datetime import datetime, timezone
from uuid import UUID

import httpx

from app.core.config import settings
from app.models.delivery import Delivery
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
        if not chat_id:
            logger.warning("Telegram chat_id missing")
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
                delivery.sent_at = datetime.now(timezone.utc)
                delivery.external_message_id = str(result.get("result", {}).get("message_id"))
                await self.repo.create_delivery(delivery)
                logger.info("Telegram message sent to %s", chat_id)
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to send telegram to %s: %s", chat_id, e)
            delivery.status = "failed"
            delivery.error_message = str(e)
            delivery.failed_at = datetime.now(timezone.utc)
            await self.repo.create_delivery(delivery)
