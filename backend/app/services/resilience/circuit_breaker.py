import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    expected_exception: type[Exception] = Exception
    _failures: int = field(default=0)
    _state: CircuitState = field(default=CircuitState.CLOSED)
    _opened_at: float = field(default=0.0)

    def is_open(self) -> bool:
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._opened_at
            if elapsed >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker half-open — allowing test call")
                return False
            return True
        return False

    def record_success(self) -> None:
        self._failures = 0
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            logger.info("Circuit breaker closed — service recovered")

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = time.time()
            logger.warning(
                "Circuit breaker opened — %d failures, entering cooldown %ss",
                self._failures,
                self.recovery_timeout,
            )

    @property
    def state(self) -> CircuitState:
        return self._state

    @property
    def failures(self) -> int:
        return self._failures


_circuits: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
) -> CircuitBreaker:
    if name not in _circuits:
        _circuits[name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
    return _circuits[name]


def circuit_breaker(name: str, failure_threshold: int = 5, recovery_timeout: float = 30.0):
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        cb = get_circuit_breaker(name, failure_threshold, recovery_timeout)

        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if cb.is_open():
                logger.warning("Circuit breaker open for %s — returning fallback", name)
                return None

            try:
                result = await func(*args, **kwargs)
                cb.record_success()
                return result
            except cb.expected_exception:
                cb.record_failure()
                return None

        return wrapper

    return decorator
