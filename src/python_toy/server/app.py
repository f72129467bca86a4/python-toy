from contextlib import asynccontextmanager
import contextlib
from typing import AsyncIterator

from fastapi import FastAPI
from python_toy.server.infra import health as health_module
from python_toy.server.infra.error import middleware as error_middleware
from python_toy.server.infra import logging as logging_module
from python_toy.server.infra.middleware import SessionMiddleware
from python_toy.server.petstore.pet_api import router as pet_router
from python_toy.server.petstore.category_api import router as category_router
from python_toy.server.petstore.tag_api import router as tag_router
from python_toy.server.petstore.user_api import router as user_router
from python_toy.server.infra import container as container_module
from python_toy.server.infra.database import create_tables


def create_app() -> FastAPI:
    # Build DI container early and obtain settings from it
    container = container_module.Container()
    settings = container.settings()

    logging_module.setup(settings.logging)
    logger = logging_module.get_logger(__name__)

    logger.info("lifecycle.starting", env=settings.env)

    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.container = container

        # Create tables using engine from container
        engine = container.db_engine()
        await create_tables(engine)

        health_module.set_started()
        logger.info("lifecycle.started")

        yield

        # Stop accepting traffic on shutdown
        health_module.set_readiness_state(False)
        logger.info("lifecycle.shutdown.start")

        # cleanup DI resources/wiring
        with contextlib.suppress(Exception):
            container.shutdown_resources()
        # dispose SQLAlchemy engine to ensure all pooled connections are closed
        with contextlib.suppress(Exception):
            await engine.dispose()

    app = FastAPI(
        title="python-toy server",
        redirect_slashes=False,
        # openapi_url="/openapi.json",
        lifespan=_lifespan,
    )

    error_middleware.setup(app)

    # Add session middleware with session factory from container
    session_factory = container.db_session_factory()
    app.add_middleware(SessionMiddleware, session_factory=session_factory)

    app.include_router(health_module.router)
    app.include_router(pet_router)
    app.include_router(category_router)
    app.include_router(tag_router)
    app.include_router(user_router)

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {"service": "python-toy", "env": settings.env}

    return app


__all__ = ("create_app",)
