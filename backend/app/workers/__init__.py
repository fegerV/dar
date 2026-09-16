"""Celery workers package.

This module imports the Celery application and all task modules
to ensure they are registered when the package is imported.
"""

# Import all task modules to register them with Celery.
# This ensures autodiscover_tasks() works correctly. The imports below are
# load-bearing: each module decorates its tasks with @celery_app.task, so it is
# the import itself that registers them. They are re-exported through __all__
# rather than deleted, because removing them would silently unregister every
# task while leaving the app importable.
from app.workers import (
    bonus_tasks,
    delivery_tasks,
    generation_tasks,
    pipeline_tasks,
)
from app.workers.celery_app import celery_app

__all__ = [
    "celery_app",
    "generation_tasks",
    "delivery_tasks",
    "bonus_tasks",
    "pipeline_tasks",
]
