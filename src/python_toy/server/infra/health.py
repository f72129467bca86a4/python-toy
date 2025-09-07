from __future__ import annotations

from fastapi import APIRouter, Response
from starlette.responses import PlainTextResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

router = APIRouter(tags=["health"])

_startup_complete = False
_accepting_traffic = False


def reset_state() -> None:
    global _startup_complete, _accepting_traffic  # noqa: PLW0603
    _startup_complete = False
    _accepting_traffic = False


def set_started() -> None:
    global _startup_complete  # noqa: PLW0603
    _startup_complete = True
    set_readiness_state(True)


def set_readiness_state(state: bool) -> None:
    global _accepting_traffic  # noqa: PLW0603
    _accepting_traffic = state


@router.get("/.internal/healthz/startup", include_in_schema=False)
async def startup_probe() -> PlainTextResponse:
    if _startup_complete:
        return PlainTextResponse(content="UP")
    return PlainTextResponse(content="DOWN", status_code=HTTP_503_SERVICE_UNAVAILABLE)


@router.get("/.internal/healthz/liveness", include_in_schema=False)
async def liveness_probe() -> Response:
    return PlainTextResponse(content="UP")


@router.get("/.internal/healthz/readiness", include_in_schema=False)
async def readiness_probe() -> Response:
    if _startup_complete and _accepting_traffic:
        return PlainTextResponse(content="UP")
    return PlainTextResponse(content="DOWN", status_code=HTTP_503_SERVICE_UNAVAILABLE)
