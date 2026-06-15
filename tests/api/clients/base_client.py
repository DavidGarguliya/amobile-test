"""Transport layer for the API test suite (POM base object).

``BaseApiClient`` is the single place that talks HTTP. Resource/service objects build on it and
expose API operations; specs never call httpx directly (invariant INV-X4). Configuration and
credentials come from the environment via :mod:`tests.api.config.settings` (INV-X5).
"""

from __future__ import annotations

import json as _json
import logging
from dataclasses import dataclass
from typing import Any, Mapping

import httpx
from pydantic import BaseModel

from tests.api.config.settings import Settings, get_settings

logger = logging.getLogger("tests.api")


def to_body(payload: Any) -> Any:
    """Serialize a request payload: pydantic model -> dict (drop None), dict/other -> as-is.

    Specs may pass raw dicts for negative cases (e.g. missing required fields), so non-model
    payloads are forwarded unchanged.
    """
    if isinstance(payload, BaseModel):
        return payload.model_dump(exclude_none=True)
    return payload


@dataclass
class ApiResponse:
    """Normalized response wrapper. Specs assert on this, never on raw httpx objects."""

    status_code: int
    headers: Mapping[str, str]
    json: Any | None
    text: str
    method: str
    url: str

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<ApiResponse {self.method} {self.url} -> {self.status_code}>"


class BaseApiClient:
    """Thin, logged HTTP client with a shared base URL and default headers."""

    def __init__(self, settings: Settings | None = None, client: httpx.Client | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = client or httpx.Client(
            base_url=self._settings.base_url,
            timeout=self._settings.http_timeout,
            headers={"Accept": "application/json"},
        )

    @property
    def settings(self) -> Settings:
        return self._settings

    # -- lifecycle ---------------------------------------------------------------------------
    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BaseApiClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- core request ------------------------------------------------------------------------
    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> ApiResponse:
        clean_params = {k: v for k, v in (params or {}).items() if v is not None}
        logger.info("-> %s %s params=%s body=%s", method, path, clean_params or None, _safe(json))
        response = self._client.request(
            method,
            path,
            json=json,
            params=clean_params or None,
            headers=dict(headers or {}),
        )
        parsed = _parse_json(response)
        logger.info("<- %s %s %s", method, path, response.status_code)
        return ApiResponse(
            status_code=response.status_code,
            headers=response.headers,
            json=parsed,
            text=response.text,
            method=method.upper(),
            url=str(response.request.url),
        )

    # -- verb helpers ------------------------------------------------------------------------
    def get(self, path: str, **kw: Any) -> ApiResponse:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw: Any) -> ApiResponse:
        return self.request("POST", path, **kw)

    def put(self, path: str, **kw: Any) -> ApiResponse:
        return self.request("PUT", path, **kw)

    def patch(self, path: str, **kw: Any) -> ApiResponse:
        return self.request("PATCH", path, **kw)

    def delete(self, path: str, **kw: Any) -> ApiResponse:
        return self.request("DELETE", path, **kw)


def _parse_json(response: httpx.Response) -> Any | None:
    if not response.content:
        return None
    try:
        return response.json()
    except (ValueError, _json.JSONDecodeError):
        return None


def _safe(body: Any) -> Any:
    """Avoid logging obviously sensitive values (e.g. api keys) in request bodies."""
    if isinstance(body, Mapping):
        return {k: ("***" if "key" in k.lower() or "token" in k.lower() else v) for k, v in body.items()}
    return body
