"""Test configuration and fixtures."""

from __future__ import annotations

import asyncio
import pytest
from typing import AsyncGenerator, Iterator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient

from python_toy.server.petstore.db_models import Base
from python_toy.server.app import create_app
from python_toy.server.infra import health


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    # Use in-memory SQLite for tests
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    session = async_session()
    try:
        # Clear all tables before each test
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
        yield session
    finally:
        await session.rollback()  # Rollback to ensure test isolation
        await session.close()


@pytest.fixture
def session_supplier(db_session: AsyncSession):
    """Create session supplier for repository tests."""
    return lambda: db_session


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Create FastAPI test client with isolated in-memory DB."""
    # Ensure app uses an in-memory sqlite for full isolation
    monkeypatch.setenv("APP_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    app = create_app()
    health.reset_state()

    with TestClient(app, raise_server_exceptions=False) as c:
        health.set_started()
        yield c


__all__ = ("event_loop", "test_engine", "db_session", "session_supplier", "client")
