"""Service object for API-client administration (EP-12, EP-13)."""

from __future__ import annotations

from typing import Any

from tests.api.clients.base_client import ApiResponse, BaseApiClient, to_body

BASE = "/api/admin/clients"


class AdminClientsClient:
    def __init__(self, base: BaseApiClient) -> None:
        self._base = base
        self._headers = base.settings.admin_headers

    def create(self, payload: Any) -> ApiResponse:
        """POST /api/admin/clients — response carries the plaintext api_key exactly once (INV-P8)."""
        return self._base.post(BASE, json=to_body(payload), headers=self._headers)

    def get(self, client_id: int | str) -> ApiResponse:
        return self._base.get(f"{BASE}/{client_id}", headers=self._headers)

    def deactivate(self, client_id: int | str) -> ApiResponse:
        return self._base.patch(f"{BASE}/{client_id}/deactivate", headers=self._headers)
