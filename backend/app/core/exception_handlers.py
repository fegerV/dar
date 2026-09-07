"""Global exception handler for FastAPI application."""

import logging
import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppException
from app.core.metrics import http_requests_total

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers with the FastAPI app."""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        # Log with context
        logger.warning(
            "Application exception: %s",
            exc.detail,
            extra={
                "path": request.url.path,
                "method": request.method,
                "client_ip": get_client_ip(request),
                "user_agent": request.headers.get("user-agent"),
            },
        )
        
        http_requests_total.labels(
            method=request.method,
            path=request.url.path,
            status=str(exc.status_code),
        ).inc()
        
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        logger.warning(
            "Request validation error: %s",
            exc.errors(),
            extra={
                "path": request.url.path,
                "method": request.method,
                "client_ip": get_client_ip(request),
            },
        )
        
        http_requests_total.labels(
            method=request.method,
            path=request.url.path,
            status="422",
        ).inc()
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {"errors": exc.errors()},
                }
            },
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic model validation errors."""
        logger.warning(
            "Pydantic validation error: %s",
            exc.errors(),
            extra={
                "path": request.url.path,
                "method": request.method,
                "client_ip": get_client_ip(request),
            },
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Data validation failed",
                    "details": {"errors": exc.errors()},
                }
            },
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle Starlette HTTP exceptions."""
        # Don't log 404s for common paths (health checks, etc.)
        if exc.status_code != 404 or not request.url.path.startswith(("/health", "/favicon")):
            logger.warning(
                "HTTP exception: %d - %s",
                exc.status_code,
                exc.detail,
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": get_client_ip(request),
                },
            )
        
        http_requests_total.labels(
            method=request.method,
            path=request.url.path,
            status=str(exc.status_code),
        ).inc()
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                }
            },
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle SQLAlchemy database errors."""
        logger.error(
            "Database error: %s",
            str(exc),
            extra={
                "path": request.url.path,
                "method": request.method,
                "client_ip": get_client_ip(request),
                "traceback": traceback.format_exc(),
            },
            exc_info=True,
        )
        
        http_requests_total.labels(
            method=request.method,
            path=request.url.path,
            status="500",
        ).inc()
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "A database error occurred. Please try again later.",
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle all unhandled exceptions."""
        # Get correlation ID if available
        correlation_id = request.headers.get("X-Request-ID", "unknown")
        
        logger.critical(
            "Unhandled exception: %s",
            str(exc),
            extra={
                "path": request.url.path,
                "method": request.method,
                "client_ip": get_client_ip(request),
                "user_agent": request.headers.get("user-agent"),
                "correlation_id": correlation_id,
                "query_params": dict(request.query_params),
                "traceback": traceback.format_exc(),
            },
            exc_info=True,
        )
        
        http_requests_total.labels(
            method=request.method,
            path=request.url.path,
            status="500",
        ).inc()
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "correlation_id": correlation_id,
                }
            },
        )


def get_client_ip(request: Request) -> str | None:
    """Extract client IP from request, considering proxies."""
    # Check for forwarded headers (when behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    if request.client:
        return request.client.host
    
    return None


class ExceptionContextManager:
    """Context manager for enhanced exception logging with additional context."""
    
    def __init__(self, operation: str, **context: Any):
        self.operation = operation
        self.context = context
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(
                "Operation failed: %s",
                self.operation,
                extra={
                    "operation": self.operation,
                    "context": self.context,
                    "exception_type": exc_type.__name__,
                    "exception_message": str(exc_val) if exc_val else None,
                    "traceback": traceback.format_exc(),
                },
                exc_info=True,
            )
        return False  # Re-raise exception
