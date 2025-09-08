from __future__ import annotations

from contextvars import ContextVar
from typing import TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

# Context variable to store the current database session
_session_context: ContextVar[AsyncSession | None] = ContextVar("db_session", default=None)

T = TypeVar("T")


def get_current_session() -> AsyncSession:
    """Get the current database session from context.

    Returns:
        The current AsyncSession instance

    Raises:
        RuntimeError: If no session is found in the current context
    """
    session = _session_context.get()
    if session is None:
        msg = "No database session found in context. Make sure the session middleware is properly configured."
        raise RuntimeError(msg)
    return session


def set_session(session: AsyncSession) -> None:
    """Set the database session in the current context.

    Args:
        session: The AsyncSession to set in context
    """
    _session_context.set(session)


def clear_session() -> None:
    """Clear the database session from context."""
    _session_context.set(None)


__all__ = ("get_current_session", "set_session", "clear_session")
