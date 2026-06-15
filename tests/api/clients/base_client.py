"""Transport layer for the API test suite (POM base object).

``BaseApiClient`` is the single place that talks HTTP. Resource/service objects build on it and
expose API operations; specs never call httpx directly (invariant INV-X4). Configuration and
credentials come from the environment via :mod:`tests.api.config.settings` (INV-X5).
"""

from __future__ import annotations

import json as _json
import logging
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any, Mapping

import httpx
from pydantic import BaseModel

from tests.api.config.settings import Settings, get_settings

try:  # Allure is optional: the suite must run without it (e.g. plain pytest).
    import allure
except ImportError:  # pragma: no cover
    allure = None  # type: ignore[assignment]

logger = logging.getLogger("tests.api")

_SENSITIVE_HEADERS = {"authorization", "x-api-key"}


def _mask_headers(headers: Mapping[str, str]) -> dict[str, str]:
    masked = {}
    for key, value in headers.items():
        masked[key] = "***" if key.lower() in _SENSITIVE_HEADERS else value
    return masked


def _attach_json(name: str, value: Any) -> None:
    if allure is None:
        return
    try:
        body = _json.dumps(value, ensure_ascii=False, indent=2, default=str)
        allure.attach(body, name=name, attachment_type=allure.attachment_type.JSON)
    except Exception:  # pragma: no cover - attachment must never break a test
        allure.attach(str(value), name=name, attachment_type=allure.attachment_type.TEXT)


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

    def set_auth(self, token: str | None) -> None:
        """Set/clear the default bearer token applied to every request (ADR-009)."""
        if token:
            self._client.headers["Authorization"] = f"Bearer {token}"
        else:
            self._client.headers.pop("Authorization", None)

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
        request_headers = dict(headers or {})
        logger.info("-> %s %s params=%s body=%s", method, path, clean_params or None, _safe(json))

        step = allure.step(f"{method.upper()} {path}") if allure else nullcontext()
        with step:
            # Attach the request side (secrets masked).
            if clean_params:
                _attach_json("request params", clean_params)
            if json is not None:
                _attach_json("request body", _safe(json))
            merged_headers = {**dict(self._client.headers), **request_headers}
            _attach_json("request headers", _mask_headers(merged_headers))

            response = self._client.request(
                method,
                path,
                json=json,
                params=clean_params or None,
                headers=request_headers,
            )
            parsed = _parse_json(response)

            # Attach the response side.
            if allure is not None:
                allure.attach(
                    str(response.status_code), name="response status", attachment_type=allure.attachment_type.TEXT
                )
                if parsed is not None:
                    _attach_json("response body", parsed)
                elif response.text:
                    allure.attach(response.text, name="response body", attachment_type=allure.attachment_type.TEXT)

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
