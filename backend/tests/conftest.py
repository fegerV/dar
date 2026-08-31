"""Pytest configuration for DarAgent backend tests."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("APP_ENV", "testing")

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models.base import Base
from app.models.user import User

_test_db = settings.DATABASE_URL
# Use shared in-memory SQLite so tables persist across connections
engine = create_async_engine(
    "sqlite+aiosqlite:///file:test?mode=memory&cache=shared",
    poolclass=NullPool,
    connect_args={"uri": True},
)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# SQLite doesn't natively understand postgresql JSONB or ARRAY types.
# Replace them with SQLite-compatible JSON types for test schema creation.
def _replace_pg_types(metadata):
    from sqlalchemy import BigInteger
    from sqlalchemy.dialects.postgresql import ARRAY, JSONB
    from sqlalchemy.types import JSON as SQLA_JSON
    from sqlalchemy.types import Integer as SQLA_Integer

    for table in metadata.tables.values():
        for col in table.columns:
            if isinstance(col.type, (JSONB, ARRAY)):
                col.type = SQLA_JSON()
            if isinstance(col.type, BigInteger):
                col.type = SQLA_Integer()


_original_create_all = Base.metadata.create_all


def _patched_create_all(bind=None, tables=None, checkfirst=True, **kw):
    _replace_pg_types(Base.metadata)
    return _original_create_all(bind=bind, tables=tables, checkfirst=checkfirst, **kw)


Base.metadata.create_all = _patched_create_all


@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.rollback()
        except Exception:
            await session.rollback()
            raise
        finally:
            try:
                await session.close()
            except Exception:
                pass


@pytest.fixture
async def client(db_session):
    from app.core.database import get_db as _orig_get_db

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[_orig_get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    import uuid

    user = User(
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        display_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def access_token(test_user):
    return create_access_token(test_user.id)


@pytest.fixture
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}", "X-Requested-With": "XMLHttpRequest"}


@pytest.fixture(autouse=True)
def mock_storage_provider():
    from unittest.mock import AsyncMock, patch

    with patch("app.services.recipients.service.get_storage_provider") as mock_factory, \
         patch("app.services.assets.service.get_storage_provider") as mock_assets_factory:
        mock_storage = mock_factory.return_value
        mock_storage.generate_presigned_upload_url = AsyncMock(
            return_value="https://presigned.example.com/upload/abc123"
        )
        mock_assets_storage = mock_assets_factory.return_value
        mock_assets_storage.generate_presigned_upload_url = AsyncMock(
            return_value="https://presigned.example.com/upload/abc123"
        )
        yield mock_storage
