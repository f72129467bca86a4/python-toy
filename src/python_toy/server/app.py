from contextlib import asynccontextmanager
import contextlib
from typing import AsyncIterator

from fastapi import FastAPI
from python_toy.server.infra import health as health_module
from python_toy.server.infra.error import middleware as error_middleware
from python_toy.server.infra import logging as logging_module
from python_toy.server.petstore.api import router as pet_router
from python_toy.server.infra import container as container_module


def create_app() -> FastAPI:
    # Build DI container early and obtain settings from it
    container = container_module.Container()
    settings = container.settings()

    logging_module.setup(settings.logging)
    logger = logging_module.get_logger(__name__)

    logger.info("lifecycle.starting", env=settings.env)

    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
        # expose container via app.state if needed elsewhere
        app.state.container = container
        health_module.set_started()
        logger.info("lifecycle.started")

        yield

        # Stop accepting traffic on shutdown
        health_module.set_readiness_state(False)
        logger.info("lifecycle.shutdown.start")
        # cleanup DI resources/wiring
        with contextlib.suppress(Exception):
            container.shutdown_resources()

    app = FastAPI(
        title="python-toy server",
        redirect_slashes=False,
        # openapi_url="/openapi.json",
        lifespan=_lifespan,
    )

    error_middleware.setup(app)

    app.include_router(health_module.router)
    app.include_router(
        pet_router,
    )

    @app.get("/", tags=["meta"])
    async def root() -> dict[str, str]:
        return {"service": "python-toy", "env": settings.env}

    return app


__all__ = ("create_app",)
