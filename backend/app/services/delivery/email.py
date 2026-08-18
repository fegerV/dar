import logging
from datetime import datetime, timezone
from uuid import UUID

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.models.delivery import Delivery
from app.repositories.delivery import DeliveryRepository

logger = logging.getLogger(__name__)


class EmailDeliveryService:
    TRACKING_PIXEL = (
        '<img src="{track_url}" width="1" height="1" alt="" '
        'style="display:none;" />'
    )

    def __init__(self, db) -> None:
        self.db = db
        self.repo = DeliveryRepository(db)

    async def send(self, delivery: Delivery, video_url: str | None, thumbnail_url: str | None, title: str | None = None) -> None:
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            logger.warning("SMTP not configured")
            return

        recipient = delivery.destination
        if not recipient or "@" not in recipient:
            logger.warning("Invalid email destination: %s", recipient)
            return

        subject = title or "Ваше видеопоздравление готово"
        tracking_url = f"{settings.SMTP_FROM}/api/v1/delivery/track/email/{delivery.id}"

        html = self._render_html(
            recipient=recipient,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            title=subject,
            tracking_url=tracking_url,
        )
        text = self._render_text(
            recipient=recipient,
            video_url=video_url,
            title=subject,
        )

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.SMTP_FROM
        message["To"] = recipient
        message.attach(MIMEText(text, "plain", "utf-8"))
        message.attach(MIMEText(html, "html", "utf-8"))

        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS,
            )
            delivery.status = "sent"
            delivery.sent_at = datetime.now(timezone.utc)
            await self.repo.create_delivery(delivery)
            logger.info("Email sent to %s", recipient)
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to send email to %s: %s", recipient, e)
            delivery.status = "failed"
            delivery.error_message = str(e)
            delivery.failed_at = datetime.now(timezone.utc)
            await self.repo.create_delivery(delivery)

    def _render_html(self, recipient: str, video_url: str | None, thumbnail_url: str | None, title: str, tracking_url: str) -> str:
        thumbnail = f'<img src="{thumbnail_url}" alt="preview" style="max-width:100%;height:auto;" />' if thumbnail_url else ""
        return f"""
        <html>
          <body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">
            <h1>{title}</h1>
            <p>Привет! Для тебя подготовили видеопоздравление.</p>
            {thumbnail}
            <p><a href="{video_url}">Смотреть видео</a></p>
            {self.TRACKING_PIXEL.format(track_url=tracking_url)}
          </body>
        </html>
        """

    def _render_text(self, recipient: str, video_url: str | None, title: str) -> str:
        return f"{title}\n\nПривет! Для тебя подготовили видеопоздравление.\n\nСмотреть: {video_url}\n"
