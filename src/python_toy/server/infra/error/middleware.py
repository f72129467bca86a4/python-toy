from __future__ import annotations

from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from python_toy.server.infra.error import (
    BadRequestException,
    ConcurrentModificationException,
    ConflictException,
    DuplicateEntityException,
    ForeignKeyViolationException,
    ResourceNotFoundException,
)
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


async def handle_duplicate_entity(request: Request, exc: DuplicateEntityException) -> JSONResponse:
    """Handle duplicate entity exceptions with structured error details."""
    return problem_response(
        type="//localhost/error/duplicate-entity",
        title="Duplicate Entity",
        status=409,  # Conflict is more appropriate for duplicates
        detail=str(exc),
        instance=str(request.url.path),
        extensions={
            "entity_type": exc.entity_type,
            "field": exc.field,
            "value": exc.value,
        },
    )


async def handle_foreign_key_violation(request: Request, exc: ForeignKeyViolationException) -> JSONResponse:
    """Handle foreign key violations with structured error details."""
    return problem_response(
        type="//localhost/error/foreign-key-violation",
        title="Foreign Key Violation",
        status=400,
        detail=str(exc),
        instance=str(request.url.path),
        extensions={
            "field": exc.field,
            "value": exc.value,
            "referenced_entity": exc.referenced_entity,
        },
    )


async def handle_concurrent_modification_exception(
    request: Request, exc: ConcurrentModificationException
) -> JSONResponse:
    """Handle concurrent modification exceptions with structured error details."""
    return problem_response(
        type="//localhost/error/concurrent-modification",
        title="Concurrent Modification Conflict",
        status=409,  # Conflict
        detail=str(exc),
        instance=str(request.url.path),
        extensions={
            "entity_type": exc.entity_type,
            "entity_id": exc.entity_id,
        },
    )


async def handle_conflict_exception(request: Request, exc: ConflictException) -> JSONResponse:
    """Handle generic conflict exceptions with structured error details."""
    return problem_response(
        type="//localhost/error/conflict",
        title="Conflict",
        status=409,
        detail=str(exc),
        instance=str(request.url.path),
    )


def setup(app: FastAPI) -> None:
    # More specific exception handlers first
    app.add_exception_handler(DuplicateEntityException, cast(HTTPExceptionHandler, handle_duplicate_entity))
    app.add_exception_handler(ForeignKeyViolationException, cast(HTTPExceptionHandler, handle_foreign_key_violation))
    app.add_exception_handler(
        ConcurrentModificationException, cast(HTTPExceptionHandler, handle_concurrent_modification_exception)
    )
    app.add_exception_handler(ConflictException, cast(HTTPExceptionHandler, handle_conflict_exception))

    # More general exception handlers
    app.add_exception_handler(ResourceNotFoundException, cast(HTTPExceptionHandler, handle_resource_not_found))
    app.add_exception_handler(
        BadRequestException,
        cast(
            HTTPExceptionHandler,
            lambda request, exc: problem_response(
                status=400,
                detail=str(exc),
                instance=str(request.url.path),
            ),
        ),
    )
    app.add_exception_handler(RequestValidationError, cast(HTTPExceptionHandler, handle_fastapi_validation))
    app.add_exception_handler(StarletteHTTPException, cast(HTTPExceptionHandler, _handle_http_exception))
    app.add_exception_handler(Exception, _catch_all)


__all__ = ["setup"]
