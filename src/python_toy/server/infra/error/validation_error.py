from __future__ import annotations

from typing import Any, cast

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from python_toy.server.infra.error.problem import problem_response

_MAX_BYTES_PREVIEW = 2048


def _normalize_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Post-processing of FastAPI RequestValidationError.errors() results.

    - If the 'input' value is bytes/bytearray, Try to interpret as UTF-8 string.
    """

    normalized: list[dict[str, Any]] = []
    for err in errors:
        e = dict(err)  # shallow copy
        raw_input = e.get("input")
        # Use PEP 604 union in isinstance (py312 target).
        if isinstance(raw_input, bytes | bytearray):
            b = bytes(raw_input)
            truncated = False
            preview = b
            if len(b) > _MAX_BYTES_PREVIEW:
                preview = b[:_MAX_BYTES_PREVIEW]
                truncated = True
            try:
                text = preview.decode("utf-8", errors="replace")
            except Exception:  # pragma: no cover (Very unlikely)
                text = "<un-decodable bytes>"
            if truncated:
                text += f"... (truncated {len(b) - _MAX_BYTES_PREVIEW} bytes)"
            e["input"] = text
            e["inputType"] = "bytes"
            e["inputOriginalLength"] = len(b)
        normalized.append(e)
    return normalized


async def handle_fastapi_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors_raw = cast(list[dict[str, Any]], exc.errors())
    errors = _normalize_validation_errors(errors_raw)
    return problem_response(
        type="//localhost/error/validation",
        title="Request Validation failed",
        status=400,
        instance=str(request.url.path),
        extensions={"errors": errors},
    )


__all__ = ["handle_fastapi_validation"]
