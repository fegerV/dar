"""Testcontainers integration tests for backend."""

import asyncio
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base
from app.models.user import User


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def testcontainers_postgres():
    """Start PostgreSQL container for integration tests."""
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16") as postgres:
        yield postgres


@pytest.fixture(scope="session")
async def testcontainers_redis():
    """Start Redis container for integration tests."""
    from testcontainers.redis import RedisContainer

    with RedisContainer("redis:7") as redis:
        yield redis


@pytest.fixture(scope="session")
async def db_engine(testcontainers_postgres):
    """Create database engine connected to testcontainers Postgres."""
    connection_url = testcontainers_postgres.get_connection_url()
    # Convert to asyncpg URL
    async_url = connection_url.replace("postgresql://", "postgresql+asyncpg://")

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

    async with AsyncClient(app=app, base_url="http://test") as ac:
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
    assert data["email"] == "newuser@example.com"
    assert "id" in data


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
        "/admin/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
