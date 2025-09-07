from __future__ import annotations

from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from python_toy.server.infra.error import ResourceNotFoundException
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import HTTPExceptionHandler

from python_toy.server.infra.error.problem import problem_response
from python_toy.server.infra.error.validation_error import handle_fastapi_validation
from python_toy.server.infra.logging import get_logger

_logger = get_logger(__name__)


async def handle_resource_not_found(request: Request, exc: ResourceNotFoundException) -> JSONResponse:
    return problem_response(
        status=404,
        detail=str(exc),
        instance=str(request.url.path),
    )


async def _handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return problem_response(status=exc.status_code, detail=detail, instance=str(request.url.path))


async def _catch_all(request: Request, exc: Exception) -> JSONResponse:
    # Include stack trace for observability using explicit (type, value, tb) tuple.
    _logger.exception("exception.unhandled", path=str(request.url.path))
    return problem_response(
        status=500,
        detail="Internal Server Error",
        instance=str(request.url.path),
    )


def setup(app: FastAPI) -> None:
    app.add_exception_handler(ResourceNotFoundException, cast(HTTPExceptionHandler, handle_resource_not_found))
    app.add_exception_handler(RequestValidationError, cast(HTTPExceptionHandler, handle_fastapi_validation))
    app.add_exception_handler(StarletteHTTPException, cast(HTTPExceptionHandler, _handle_http_exception))
    app.add_exception_handler(Exception, _catch_all)


__all__ = ["setup"]
