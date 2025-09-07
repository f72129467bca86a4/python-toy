from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine
from sqlalchemy.pool import AsyncAdaptedQueuePool
import sqlite3
from python_toy.server.infra.config import Settings
from python_toy.server.petstore.db_models import Base


def create_database_engine(settings: Settings) -> AsyncEngine:
    """Create SQLAlchemy async engine with proper configuration."""
    engine = create_async_engine(
        settings.database_url,
        echo=True,
        poolclass=AsyncAdaptedQueuePool,
        pool_size=10,  # Core connection pool size
        max_overflow=20,  # Additional connections allowed beyond pool_size
        pool_timeout=30,  # Time to wait for connection (seconds)
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Validate connections before use
    )

    # Setup SQLite FK constraints
    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_fk(
        dbapi_connection: sqlite3.Connection, connection_record: object
    ) -> None:  # pragma: no cover - sqlite specific setup
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:  # noqa: BLE001
            pass

    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create async session factory."""
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session_factory(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Create database session using session factory."""
    # Explicitly close session on dependency teardown to avoid connection leaks
    session: AsyncSession = session_factory()
    try:
        yield session
    finally:
        await session.close()


async def create_tables(engine: AsyncEngine) -> None:
    """Create database tables using the provided engine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
