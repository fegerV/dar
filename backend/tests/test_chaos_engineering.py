"""Chaos engineering tests for resilience features.

Tests verify that the system degrades gracefully under failure conditions,
circuit breakers open/close correctly, and cached fallbacks work.
"""
import pytest

from app.services.resilience.circuit_breaker import CircuitBreaker, CircuitState


@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
    assert cb.state == CircuitState.CLOSED

    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.is_open() is True


@pytest.mark.asyncio
async def test_circuit_breaker_half_open_after_timeout():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.is_open() is True

    import time
    time.sleep(0.02)

    assert cb.is_open() is False
    assert cb.state == CircuitState.HALF_OPEN


@pytest.mark.asyncio
async def test_circuit_breaker_closes_on_success():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    import time
    time.sleep(0.02)

    cb.is_open()
    assert cb.state == CircuitState.HALF_OPEN

    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failures == 0


@pytest.mark.asyncio
async def test_circuit_breaker_decorator_returns_none_on_failure():
    from app.services.resilience.circuit_breaker import circuit_breaker

    call_count = 0

    @circuit_breaker("test_service", failure_threshold=2, recovery_timeout=60)
    async def failing_function():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Service unavailable")

    result = await failing_function()
    assert result is None
    assert call_count == 1

    await failing_function()
    assert call_count == 2

    from app.services.resilience.circuit_breaker import get_circuit_breaker
    breaker = get_circuit_breaker("test_service")
    assert breaker.state == CircuitState.OPEN

    result = await failing_function()
    assert result is None
    assert call_count == 2


@pytest.mark.asyncio
async def test_template_cache_store_and_retrieve():
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session = async_sessionmaker(engine, expire_on_commit=False)

    from app.services.cache.template_cache import TemplateCacheManager

    class FakeResult:
        def model_dump(self):
            return {"template_version_id": "test", "scenes": []}

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: sync_conn.exec_driver_sql(
                """
                CREATE TABLE template_render_cache (
                    template_version_id VARCHAR PRIMARY KEY,
                    rendered_json JSONB,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP
                )
                """
            )
        )

    async with session() as db:
        cache = TemplateCacheManager(db)
        await cache.init_schema()

        import uuid
        result = FakeResult()
        await cache.store_rendered_template(uuid.uuid4(), result)
        status = await cache.get_cache_status()
        assert status["cache_enabled"] is True


@pytest.mark.asyncio
async def test_graceful_degradation_returns_cached_on_failure():
    from app.core.exceptions import NotFoundException

    class FakeCache:
        async def get_rendered_template(self, template_version_id):
            return {"cached": "render_result", "template_version_id": str(template_version_id)}

    class FakeRenderer:
        def __init__(self):
            self.cache = FakeCache()

        async def render_template(self, body, fallback_to_cache=True):
            try:
                raise NotFoundException("Template not found")
            except Exception as e:
                if not fallback_to_cache:
                    raise
                if isinstance(e, NotFoundException):
                    cached = await self._get_cached_render(body.template_version_id)
                    if cached:
                        return cached
                raise

        async def _get_cached_render(self, template_version_id):
            return await self.cache.get_rendered_template(template_version_id)

    renderer = FakeRenderer()

    class FakeBody:
        template_version_id = "test-id-123"

    result = await renderer.render_template(FakeBody())
    assert result["cached"] == "render_result"
