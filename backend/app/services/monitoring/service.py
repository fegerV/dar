import os
import shutil
import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation import Generation
from app.models.payment import Payment
from app.models.user import User

DB_CONNECTION_TIME = Histogram(
    "daragent_db_query_duration_seconds",
    "Database query duration",
    ["query_type"],
)

WALLET_CREDIT = Counter(
    "daragent_wallet_credits_total",
    "Total wallet credits issued",
)

GENERATION_COUNT = Counter(
    "daragent_generations_total",
    "Total generations initiated",
    ["status"],
)

DISK_USAGE = Gauge(
    "daragent_disk_usage_bytes",
    "Disk usage in bytes",
    ["path", "type"],
)

QUEUE_DEPTH = Gauge(
    "daragent_queue_depth",
    "Number of queued jobs",
    ["queue_name"],
)

SYSTEM_HEALTH = Gauge(
    "daragent_system_health",
    "System health status (1=healthy, 0=degraded)",
    ["component"],
)


class MonitoringService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect_system_metrics(self) -> dict:
        disk = shutil.disk_usage("/")
        DISK_USAGE.labels(path="/", type="total").set(disk.total)
        DISK_USAGE.labels(path="/", type="used").set(disk.used)
        DISK_USAGE.labels(path="/", type="free").set(disk.free)

        disk_used_percent = (disk.used / disk.total) * 100 if disk.total > 0 else 0
        if disk_used_percent > 90:
            SYSTEM_HEALTH.labels(component="disk").set(0)
        else:
            SYSTEM_HEALTH.labels(component="disk").set(1)

        try:
            start = time.time()
            result = await self.db.execute(select(func.count()).select_from(User))
            user_count = result.scalar() or 0
            DB_CONNECTION_TIME.labels(query_type="count_users").observe(time.time() - start)
            SYSTEM_HEALTH.labels(component="database").set(1)
        except Exception:
            SYSTEM_HEALTH.labels(component="database").set(0)
            user_count = 0

        try:
            result = await self.db.execute(
                select(func.count()).select_from(Generation).where(
                    Generation.status.in_(["queued", "processing"])
                )
            )
            processing_count = result.scalar() or 0
            QUEUE_DEPTH.labels(queue_name="generation").set(processing_count)
        except Exception:
            QUEUE_DEPTH.labels(queue_name="generation").set(0)

        try:
            result = await self.db.execute(
                select(func.count()).select_from(Payment).where(Payment.status == "pending")
            )
            pending_payments = result.scalar() or 0
            QUEUE_DEPTH.labels(queue_name="payments").set(pending_payments)
        except Exception:
            QUEUE_DEPTH.labels(queue_name="payments").set(0)

        try:
            redis_available = self._check_redis()
            SYSTEM_HEALTH.labels(component="redis").set(1 if redis_available else 0)
        except Exception:
            SYSTEM_HEALTH.labels(component="redis").set(0)

        try:
            if os.getenv("MINIO_ENDPOINT"):
                SYSTEM_HEALTH.labels(component="storage").set(1)
            else:
                SYSTEM_HEALTH.labels(component="storage").set(0)
        except Exception:
            SYSTEM_HEALTH.labels(component="storage").set(0)

        overall_healthy = all(
            SYSTEM_HEALTH.labels(component=c)._value.get() == 1
            for c in ("database", "redis", "disk", "storage")
        )
        SYSTEM_HEALTH.labels(component="overall").set(1 if overall_healthy else 0)

        return {
            "disk": {"total": disk.total, "used": disk.used, "free": disk.free, "used_percent": disk_used_percent},
            "queue_depth": {"generation": processing_count, "payments": pending_payments},
            "user_count": user_count,
            "components": {
                "database": int(SYSTEM_HEALTH.labels(component="database")._value.get()),
                "redis": int(SYSTEM_HEALTH.labels(component="redis")._value.get()),
                "disk": int(SYSTEM_HEALTH.labels(component="disk")._value.get()),
                "storage": int(SYSTEM_HEALTH.labels(component="storage")._value.get()),
            },
        }

    def _check_redis(self) -> bool:
        from app.core.config import settings

        redis_url = settings.REDIS_URL
        if not redis_url:
            return False
        try:
            import redis.asyncio as redis
            client = redis.from_url(redis_url, socket_connect_timeout=5, socket_timeout=5)
            import asyncio
            asyncio.get_event_loop().run_until_complete(client.ping())
            return True
        except Exception:
            return False

    def get_metrics(self) -> str:
        return generate_latest()

    CONTENT_TYPE = CONTENT_TYPE_LATEST
