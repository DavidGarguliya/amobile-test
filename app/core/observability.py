"""Observability helpers: optional Sentry init and a request-id middleware (NFR-6, brief §50)."""

from __future__ import annotations

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings
from app.core.logging import request_id_var

logger = logging.getLogger("app.observability")


def init_sentry() -> None:
    if not settings.sentry_dsn:
        return
    try:  # pragma: no cover - exercised only when SENTRY_DSN is configured
        import sentry_sdk

        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.0)
        logger.info("sentry initialized")
    except Exception as exc:  # pragma: no cover
        logger.warning("sentry init skipped: %s", exc)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assign/propagate an X-Request-ID and bind it to the logging context."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers["X-Request-ID"] = request_id
        return response
