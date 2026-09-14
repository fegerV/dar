"""Persistent queue pause/resume control.

The admin panel toggles the queue via `PATCH /admin/queue/pause|resume`.
The flag is stored in `system_settings` so that Celery workers (separate
processes) can observe it before picking up new generation jobs.
"""
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import SystemSettings

QUEUE_PAUSED_KEY = "queue_paused"


async def get_queue_state(db: AsyncSession) -> dict:
    """Return the persisted queue state (never raises on missing row)."""
    result = await db.execute(
        select(SystemSettings).where(SystemSettings.key == QUEUE_PAUSED_KEY)
    )
    setting = result.scalar_one_or_none()
    if setting is None:
        return {"paused": False, "paused_at": None, "paused_by": None}
    value = setting.value or {}
    return {
        "paused": bool(value.get("paused", False)),
        "paused_at": value.get("paused_at"),
        "paused_by": value.get("paused_by"),
    }


async def is_queue_paused(db: AsyncSession) -> bool:
    return (await get_queue_state(db))["paused"]


async def set_queue_paused(
    db: AsyncSession, paused: bool, actor_id: UUID | None = None
) -> dict:
    """Persist the queue state and return it."""
    result = await db.execute(
        select(SystemSettings).where(SystemSettings.key == QUEUE_PAUSED_KEY)
    )
    setting = result.scalar_one_or_none()

    value = {
        "paused": paused,
        "paused_at": datetime.now(UTC).isoformat() if paused else None,
        "paused_by": str(actor_id) if (paused and actor_id) else None,
    }

    if setting is None:
        setting = SystemSettings(
            key=QUEUE_PAUSED_KEY,
            value=value,
            description="Generation queue pause flag (managed by admin panel)",
            is_public=False,
        )
        db.add(setting)
    else:
        setting.value = value

    await db.commit()
    return value
