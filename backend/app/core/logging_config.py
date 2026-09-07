"""
Конфигурация структурированного логирования с использованием structlog.

Интеграция JSON-логирования для лучшего мониторинга и анализа логов.
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor


def add_app_context(
    logger: logging.Logger, 
    method_name: str, 
    event_dict: structlog.types.EventDict
) -> structlog.types.EventDict:
    """Добавить контекст приложения к каждому лог-сообщению."""
    event_dict["app"] = "daragent"
    return event_dict


def setup_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """
    Настроить структурированное логирование.
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Если True, использовать JSON формат, иначе текстовый
    """
    # Конфигурация processors chain
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        add_app_context,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if json_format:
        # JSON формат для production
        shared_processors.append(structlog.processors.dict_tracebacks)
        shared_processors.append(structlog.processors.JSONRenderer())
        
        # Настройка стандартного logging для JSON вывода
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level.upper()),
        )
        
        # Фильтр для пропуска structlog записей в стандартный formatter
        structlog_handler = logging.StreamHandler(sys.stdout)
        structlog_handler.setFormatter(logging.Formatter("%(message)s"))
        
        root_logger = logging.getLogger()
        root_logger.handlers = [structlog_handler]
    else:
        # Текстовый формат для development
        shared_processors.append(structlog.dev.ConsoleRenderer(colors=True))
        
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level.upper()),
        )
    
    # Конфигурация structlog
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """
    Получить logger instance.
    
    Args:
        name: Имя logger (обычно __name__ модуля)
        
    Returns:
        Bound logger instance
    """
    if name is None:
        return structlog.get_logger()
    return structlog.get_logger(name)


class StructuredLoggingMiddleware:
    """
    Middleware для добавления request context к логам.
    
    Использование в FastAPI:
        @app.middleware("http")
        async def log_request(request, call_next):
            with logging_context(request_id=request.headers.get("X-Request-ID")):
                response = await call_next(request)
                return response
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        from contextvars import ContextVar
        
        request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
        
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            request_id = headers.get(b"x-request-id", b"").decode() or str(id(scope))
            
            token = request_id_var.set(request_id)
            try:
                structlog.contextvars.clear_contextvars()
                structlog.contextvars.bind_contextvars(request_id=request_id)
                return await self.app(scope, receive, send)
            finally:
                request_id_var.reset(token)
        else:
            return await self.app(scope, receive, send)


# Утилиты для логирования исключений
def log_exception(
    logger: structlog.BoundLogger,
    message: str,
    exc_info: bool = True,
    **kwargs: Any
) -> None:
    """
    Логировать исключение с полным stack trace.
    
    Args:
        logger: Logger instance
        message: Сообщение об ошибке
        exc_info: Включить информацию об исключении
        kwargs: Дополнительный контекст
    """
    logger.error(message, exc_info=exc_info, **kwargs)


# Пример использования в коде:
# from app.core.logging_config import get_logger, setup_logging
# 
# setup_logging(log_level="INFO", json_format=True)
# logger = get_logger(__name__)
# 
# logger.info("Application started", version="1.0.0")
# logger.debug("Processing request", user_id=user_id, action="login")
# 
# try:
#     risky_operation()
# except Exception as e:
#     log_exception(logger, "Operation failed", error=str(e), user_id=user_id)
