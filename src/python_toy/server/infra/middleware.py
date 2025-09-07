from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from python_toy.server.infra.session_context import set_session, clear_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to manage database sessions in contextvars."""

    def __init__(self, app: ASGIApp, session_factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(app)
        self.session_factory = session_factory

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Handle the request with a database session in context."""
        # Create a new session for this request
        session: AsyncSession = self.session_factory()
        try:
            # Set the session in context
            set_session(session)

            # Process the request
            response = await call_next(request)

            # Commit the transaction if successful
            await session.commit()

            return response

        except Exception:
            # Rollback on any exception
            await session.rollback()
            raise
        finally:
            # Always close the session and clear the context
            await session.close()
            clear_session()


__all__ = ("SessionMiddleware",)
