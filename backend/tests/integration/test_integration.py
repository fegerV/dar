"""Testcontainers integration tests for backend.

These tests require Docker plus the optional `testcontainers` dependency. When
either is unavailable the whole module is skipped instead of erroring, so the
default `pytest` run stays green on machines without Docker.
"""

import re
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.models.user import User

testcontainers = pytest.importorskip(
    "testcontainers", reason="testcontainers is not installed (optional dev extra)"
)


def _docker_available() -> bool:
    try:
        import docker

        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


if not _docker_available():
    pytest.skip("Docker daemon is not available", allow_module_level=True)

pytestmark = pytest.mark.integration


# NOTE: there used to be a session-scoped `event_loop` fixture here that called
# asyncio.get_event_loop_policy().new_event_loop(). pytest-asyncio 1.x removed
# the `event_loop` fixture entirely, so nothing requested it any more, and
# get_event_loop_policy() is deprecated in 3.12+. It was dead code; removed.


@pytest.fixture(scope="session")
def testcontainers_postgres():
    """Start PostgreSQL container for integration tests.

    Deliberately a *sync* fixture: the container is a plain process and has no
    event loop affinity. Keeping it out of the async fixture machinery means
    only the engine (which really is loop-bound) has to care about loop scopes.

    The alpine image is used deliberately: it is smaller and faster to pull,
    and the Debian-based `postgres:16` image fails to initialise under
    restricted Docker daemons with
        popen failure: Operation not permitted
        initdb: error: program "postgres" is needed by initdb ...
    """
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def testcontainers_redis():
    """Start Redis container for integration tests."""
    from testcontainers.redis import RedisContainer

    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture
async def db_engine(testcontainers_postgres):
    """Create database engine connected to testcontainers Postgres.

    Function-scoped on purpose. asyncpg connections are bound to the event loop
    that created them, and pytest-asyncio 1.x runs each test (and its
    function-scoped async fixtures) in a fresh loop. A session-scoped engine
    would hand a connection created in the session loop to a test running in a
    different loop, which fails with
        RuntimeError: ... got Future ... attached to a different loop
    """
    # testcontainers hands back a psycopg2-flavoured URL
    # (postgresql+psycopg2://...) and psycopg2 is not a dependency of this
    # project - asyncpg is. Rewrite whatever driver is present, otherwise
    # SQLAlchemy resolves the psycopg2 dialect and dies with
    #   ModuleNotFoundError: No module named 'psycopg2'
    connection_url = testcontainers_postgres.get_connection_url()
    async_url = re.sub(r"^postgresql(\+\w+)?://", "postgresql+asyncpg://", connection_url)

    engine = create_async_engine(async_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncSession:
    """Create a new database session for each test."""
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_engine) -> AsyncClient:
    """Create HTTP client with overridden database dependency."""
    from app.core.database import get_db

    async def override_get_db():
        async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # httpx 0.28 removed the `app=` shortcut; ASGITransport is the supported way
    # to drive an ASGI app in-process.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        display_name="Test User",
        status="active",
        is_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_user_flow(client: AsyncClient, db_session: AsyncSession):
    """Test complete user creation flow."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "display_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    # AuthResponse is {access_token, refresh_token, token_type, expires_in, user},
    # so the account fields live under "user", not at the top level.
    assert data["user"]["email"] == "newuser@example.com"
    assert "id" in data["user"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generation_workflow(client: AsyncClient, test_user: User):
    """Test generation creation and status check."""
    # This would test the full generation workflow
    # with real database and external API mocking
    pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_endpoints(client: AsyncClient, test_user: User):
    """Test admin endpoints with real database."""
    # Create admin token
    from app.core.security import create_access_token

    token = create_access_token(str(test_user.id))

    response = await client.get(
        # admin_router is mounted on v1_router, which carries the /api/v1
        # prefix, so the route is /api/v1/admin/stats - not /admin/stats.
        "/api/v1/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
