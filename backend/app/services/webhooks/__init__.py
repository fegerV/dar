import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import WebhookEndpoint


async def dispatch_webhook_event(
    db: AsyncSession,
    event: str,
    payload: dict[str, Any],
) -> None:
    result = await db.execute(
        select(WebhookEndpoint).where(
            WebhookEndpoint.is_active.is_(True),
        )
    )
    endpoints: list[WebhookEndpoint] = list(result.scalars().all())

    import httpx

    timestamp = datetime.now(UTC).isoformat()

    for endpoint in endpoints:
        if event not in endpoint.events:
            continue

        body = json.dumps(
            {"event": event, "timestamp": timestamp, "data": payload},
            default=str,
        )

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "Daragent-Webhook/1.0",
        }

        if endpoint.secret:
            sig = hmac.new(
                endpoint.secret.encode("utf-8"),
                body.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            headers["X-Daragent-Signature"] = f"sha256={sig}"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(endpoint.url, headers=headers, content=body)
        except Exception:
            pass
