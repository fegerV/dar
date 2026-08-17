from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "daragent",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "process-scheduled-deliveries-every-minute": {
            "task": "app.workers.delivery_tasks.process_scheduled_deliveries",
            "schedule": 60.0,
        }
    },
)

celery_app.autodiscover_tasks(["app.workers"])
