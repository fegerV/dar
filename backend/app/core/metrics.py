"""Prometheus metrics middleware and instrumentation."""

import time
from collections.abc import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware

# Request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Queue metrics
queue_jobs_pending = Gauge(
    "daragent_queue_jobs_pending",
    "Number of pending jobs in queue",
)

queue_jobs_processing = Gauge(
    "daragent_queue_jobs_processing",
    "Number of processing jobs",
)

# Generation metrics
generations_total = Counter(
    "daragent_generations_total",
    "Total generations",
    ["type", "model"],
)

generations_failed_total = Counter(
    "daragent_generations_failed_total",
    "Total failed generations",
    ["type", "model", "error_code"],
)

generation_duration_seconds = Histogram(
    "daragent_generation_duration_seconds",
    "Generation duration in seconds",
    ["type", "model"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

# User metrics
users_total = Gauge(
    "daragent_users_total",
    "Total number of users",
)

active_users = Gauge(
    "daragent_active_users",
    "Number of active users (last 24h)",
)

# Revenue metrics
revenue_total = Counter(
    "daragent_revenue_total",
    "Total revenue in RUB",
    ["type"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        path = request.url.path
        method = request.method
        status = str(response.status_code)

        http_requests_total.labels(method=method, path=path, status=status).inc()
        http_request_duration_seconds.labels(method=method, path=path).observe(duration)

        return response


async def metrics_endpoint():
    """Endpoint to expose Prometheus metrics."""
    from starlette.responses import Response

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
