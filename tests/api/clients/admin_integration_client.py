"""Service object for admin-side integration request management (EP-15, EP-16)."""

from __future__ import annotations

from tests.api.clients.base_client import ApiResponse, BaseApiClient

BASE = "/api/admin/integration/requests"


class AdminIntegrationClient:
    def __init__(self, base: BaseApiClient) -> None:
        self._base = base
        self._headers = base.settings.admin_headers

    def list(
        self,
        *,
        client_id: int | None = None,
        status: str | None = None,
        request_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> ApiResponse:
        params = {
            "client_id": client_id,
            "status": status,
            "request_type": request_type,
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "limit": limit,
        }
        return self._base.get(BASE, params=params, headers=self._headers)

    def process(self, request_id: int | str) -> ApiResponse:
        """POST .../{id}/process — idempotent: processing a 'processed' request -> 409 (INV-P11)."""
        return self._base.post(f"{BASE}/{request_id}/process", headers=self._headers)
