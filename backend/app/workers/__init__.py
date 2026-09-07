"""Celery workers package.

This module imports the Celery application and all task modules
to ensure they are registered when the package is imported.
"""

from app.workers.celery_app import celery_app

# Import all task modules to register them with Celery
# This ensures autodiscover_tasks() works correctly
from app.workers import (
    generation_tasks,
    delivery_tasks,
    bonus_tasks,
    pipeline_tasks,
)

__all__ = ["celery_app"]