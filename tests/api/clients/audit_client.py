"""Service object for the audit log (EP-17)."""

from __future__ import annotations

from tests.api.clients.base_client import ApiResponse, BaseApiClient

BASE = "/api/admin/audit"


class AuditClient:
    def __init__(self, base: BaseApiClient) -> None:
        self._base = base
        self._headers = base.settings.admin_headers

    def list(
        self,
        *,
        client_id: int | None = None,
        success: bool | None = None,
        action: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> ApiResponse:
        params = {
            "client_id": client_id,
            "success": success,
            "action": action,
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "limit": limit,
        }
        return self._base.get(BASE, params=params, headers=self._headers)
