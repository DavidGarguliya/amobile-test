"""Service object for the external integration ingress (EP-14).

Authentication is via the ``X-API-Key`` header (brief §4.5). The key is passed per call so specs
can cover missing/invalid/valid cases (FR-I5, FR-I6). The header name is configurable (Q-2).
"""

from __future__ import annotations

from typing import Any

from tests.api.clients.base_client import ApiResponse, BaseApiClient, to_body

BASE = "/api/integration/requests"


class IntegrationClient:
    def __init__(self, base: BaseApiClient) -> None:
        self._base = base
        self._key_header = base.settings.api_key_header

    def submit(
        self,
        payload: Any,
        *,
        api_key: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> ApiResponse:
        headers: dict[str, str] = dict(extra_headers or {})
        if api_key is not None:
            headers[self._key_header] = api_key
        return self._base.post(BASE, json=to_body(payload), headers=headers)
