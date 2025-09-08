from __future__ import annotations

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


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
