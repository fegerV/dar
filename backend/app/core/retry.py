"""Retry and Circuit Breaker utilities for external API calls."""

import asyncio
import logging
import random
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay between retries
    jitter: float = 0.1  # Random jitter factor (0-1)
    exceptions: tuple[type[Exception], ...] = (Exception,)
    retry_on_result: Callable[[Any], bool] | None = None  # Optional predicate to retry on result


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures before opening circuit
    success_threshold: int = 2  # Number of successes in half-open to close
    timeout: float = 60.0  # Time in seconds before attempting recovery


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """Circuit breaker implementation for external service calls."""
    
    def __init__(self, config: CircuitBreakerConfig | None = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute function through circuit breaker."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise CircuitBreakerOpen("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            await self._record_success()
            return result
        except Exception as e:
            await self._record_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.config.timeout
    
    async def _record_success(self) -> None:
        """Record successful call."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    logger.info("Circuit breaker transitioning to CLOSED")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0
    
    async def _record_failure(self) -> None:
        """Record failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker transitioning to OPEN (failure in half-open)")
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning(
                        "Circuit breaker transitioning to OPEN (threshold reached: %d)",
                        self.failure_count
                    )


def retry_with_backoff(config: RetryConfig | None = None):
    """
    Decorator for retrying async functions with exponential backoff and jitter.
    
    Usage:
        @retry_with_backoff(RetryConfig(max_retries=3, base_delay=1.0))
        async def my_api_call():
            ...
    """
    retry_config = config or RetryConfig()
    
    def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception: Exception | None = None
            
            for attempt in range(retry_config.max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Check if we should retry based on result
                    if retry_config.retry_on_result and retry_config.retry_on_result(result):
                        if attempt < retry_config.max_retries:
                            delay = _calculate_delay(retry_config, attempt)
                            logger.warning(
                                "Retry condition met for %s (attempt %d/%d), retrying in %.2fs",
                                func.__name__,
                                attempt + 1,
                                retry_config.max_retries + 1,
                                delay,
                            )
                            await asyncio.sleep(delay)
                            continue
                    
                    return result
                    
                except retry_config.exceptions as e:
                    last_exception = e
                    
                    if attempt < retry_config.max_retries:
                        delay = _calculate_delay(retry_config, attempt)
                        logger.warning(
                            "%s failed (attempt %d/%d): %s. Retrying in %.2fs",
                            func.__name__,
                            attempt + 1,
                            retry_config.max_retries + 1,
                            e,
                            delay,
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            func.__name__,
                            retry_config.max_retries + 1,
                            e,
                        )
            
            # This should not be reached, but just in case
            raise last_exception or Exception("All retries exhausted")
        
        return wrapper
    return decorator


def _calculate_delay(config: RetryConfig, attempt: int) -> float:
    """Calculate delay with exponential backoff and jitter."""
    # Exponential backoff: base_delay * 2^attempt
    exponential_delay = config.base_delay * (2 ** attempt)
    
    # Cap at max_delay
    capped_delay = min(exponential_delay, config.max_delay)
    
    # Add jitter: random value between -jitter% and +jitter%
    jitter_range = capped_delay * config.jitter
    jittered_delay = capped_delay + random.uniform(-jitter_range, jitter_range)
    
    # Ensure non-negative delay
    return max(0, jittered_delay)


@dataclass
class ResilientClient:
    """
    Client wrapper combining retry and circuit breaker patterns.
    
    Usage:
        client = ResilientClient(
            retry_config=RetryConfig(max_retries=3),
            circuit_breaker_config=CircuitBreakerConfig(failure_threshold=5)
        )
        
        @client.resilient()
        async def call_external_api():
            ...
    """
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    circuit_breaker_config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    circuit_breaker: CircuitBreaker = field(init=False)
    
    def __post_init__(self):
        self.circuit_breaker = CircuitBreaker(self.circuit_breaker_config)
    
    def resilient(
        self,
        retry_config: RetryConfig | None = None,
    ) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
        """Decorator combining retry and circuit breaker."""
        effective_retry_config = retry_config or self.retry_config
        
        def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
            @wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                # Apply retry logic
                @retry_with_backoff(effective_retry_config)
                async def retryable_call():
                    # Apply circuit breaker
                    return await self.circuit_breaker.call(func, *args, **kwargs)
                
                return await retryable_call()
            
            return wrapper
        return decorator
