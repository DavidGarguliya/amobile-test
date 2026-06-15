"""Unified error model and centralized handlers (ADR-003, NFR-2/NFR-5, INV-X1..X3).

Every error response uses the envelope::

    { "error": true, "code": "<CODE>", "message": "...", "details": {...} }
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.error")

# Allowed error codes (brief §5.3 / NFR-3) and their default HTTP status (ADR-003).
ERROR_STATUS: dict[str, int] = {
    "VALIDATION_ERROR": 422,
    "NOT_FOUND": status.HTTP_404_NOT_FOUND,
    "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
    "FORBIDDEN": status.HTTP_403_FORBIDDEN,
    "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
    "INVALID_STATUS_TRANSITION": status.HTTP_409_CONFLICT,
    "ALREADY_PROCESSED": status.HTTP_409_CONFLICT,
    "INTERNAL_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
}


class ApiError(Exception):
    """Domain error mapped to the unified envelope."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if code not in ERROR_STATUS:
            raise ValueError(f"unknown error code: {code}")
        self.code = code
        self.message = message
        self.status_code = status_code or ERROR_STATUS[code]
        self.details = details
        super().__init__(message)


# -- convenience constructors ----------------------------------------------------------------
def not_found(message: str, **details: Any) -> ApiError:
    return ApiError("NOT_FOUND", message, details=details or None)


def validation_error(message: str, *, field: str | None = None, **extra: Any) -> ApiError:
    details = {"field": field, **extra} if field else (extra or None)
    return ApiError("VALIDATION_ERROR", message, details=details)


def unauthorized(message: str = "API key missing or invalid") -> ApiError:
    return ApiError("UNAUTHORIZED", message)


def forbidden(message: str) -> ApiError:
    return ApiError("FORBIDDEN", message)


def rate_limited(message: str = "Rate limit exceeded") -> ApiError:
    return ApiError("RATE_LIMIT_EXCEEDED", message)


def invalid_transition(message: str, **details: Any) -> ApiError:
    return ApiError("INVALID_STATUS_TRANSITION", message, details=details or None)


def already_processed(message: str = "Request is already processed") -> ApiError:
    return ApiError("ALREADY_PROCESSED", message)


# -- envelope ---------------------------------------------------------------------------------
def _envelope(code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"error": True, "code": code, "message": message, "details": details}
    return body


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
        logger.info("api_error code=%s status=%s message=%s", exc.code, exc.status_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        first = errors[0] if errors else {}
        field = ".".join(str(p) for p in first.get("loc", []) if p not in ("body", "query", "path"))
        message = first.get("msg", "Validation error")
        return JSONResponse(
            status_code=ERROR_STATUS["VALIDATION_ERROR"],
            content=_envelope("VALIDATION_ERROR", message, {"field": field or None, "errors": errors}),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
        }.get(exc.status_code, "INTERNAL_ERROR" if exc.status_code >= 500 else "VALIDATION_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(code, str(exc.detail), None),
        )

    @app.exception_handler(Exception)
    async def _unhandled_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled error: %s", exc)
        return JSONResponse(
            status_code=ERROR_STATUS["INTERNAL_ERROR"],
            content=_envelope("INTERNAL_ERROR", "Internal server error", None),
        )
