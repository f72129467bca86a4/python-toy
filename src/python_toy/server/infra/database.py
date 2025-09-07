from __future__ import annotations

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
import sqlite3
from python_toy.server.infra.config import get_settings
from python_toy.server.petstore.db_models import Base

settings = get_settings()
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
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # Explicitly close session on dependency teardown to avoid connection leaks
    session: AsyncSession = async_session()
    try:
        yield session
    finally:
        await session.close()


@asynccontextmanager
async def transactional(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Explicit transaction management context manager.

    This ensures proper commit/rollback behavior for service operations
    involving multiple repository calls or complex business logic.
    """
    if session.in_transaction():
        # Already in a transaction, just yield the session
        yield session
    else:
        # Start a new transaction
        async with session.begin():
            try:
                yield session
            except Exception:
                # SQLAlchemy automatically rolls back on exception in begin() context
                raise


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Ensure SQLite enforces FK constraints (aiosqlite driver)
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
