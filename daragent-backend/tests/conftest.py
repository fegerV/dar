"""Shared pytest fixtures and configuration."""
from __future__ import annotations

import os
import sys

from core.config import get_settings
from core.database import Base, get_db
from httpx import AsyncClient
from main import create_app
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

get_settings.cache_clear()

# Ensure backend directory is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set test database URL before importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_daragent.db"

# Test engine
engine = create_async_engine("sqlite+aiosqlite:///./test_daragent.db", echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    """Create all tables once per test session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if os.path.exists("./test_daragent.db"):
        os.remove("./test_daragent.db")


@pytest_asyncio.fixture(autouse=True)
async def clean_db(setup_db):
    """Clear all table data before each test."""
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"DELETE FROM {table.name}"))
    yield


@pytest_asyncio.fixture
async def client(setup_db):
    """Create an async test client with overridden database dependency."""
    app = create_app()

    async def override_get_db():
        async with async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
