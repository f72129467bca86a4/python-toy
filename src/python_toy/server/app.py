from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from python_toy.server.infra import health as health_module
from python_toy.server.infra import config as config_module
from python_toy.server.infra.error import middleware as error_middleware
from python_toy.server.infra import logging as logging_module
from python_toy.server.petstore.api import router as pet_router


def create_app() -> FastAPI:
    settings = config_module.get_settings()

    logging_module.setup(settings.logging)
    logger = logging_module.get_logger(__name__)

    logger.info("lifecycle.starting", env=settings.env)

    @asynccontextmanager
    async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
        health_module.set_started()
        logger.info("lifecycle.started")

        yield

        # Stop accepting traffic on shutdown
        health_module.set_readiness_state(False)
        logger.info("lifecycle.shutdown.start")

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
