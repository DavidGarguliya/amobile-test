"""Service object for the Tickets resource (EP-06..EP-11)."""

from __future__ import annotations

from typing import Any

from tests.api.clients.base_client import ApiResponse, BaseApiClient, to_body

BASE = "/api/tickets"


class TicketsClient:
    def __init__(self, base: BaseApiClient) -> None:
        self._base = base
        self._headers = base.settings.admin_headers

    def create(self, payload: Any) -> ApiResponse:
        return self._base.post(BASE, json=to_body(payload), headers=self._headers)

    def list(
        self,
        *,
        status: str | None = None,
        priority: str | None = None,
        employee_id: int | None = None,
        assigned_to: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> ApiResponse:
        params = {
            "status": status,
            "priority": priority,
            "employee_id": employee_id,
            "assigned_to": assigned_to,
            "page": page,
            "limit": limit,
        }
        return self._base.get(BASE, params=params, headers=self._headers)

    def get(self, ticket_id: int | str) -> ApiResponse:
        return self._base.get(f"{BASE}/{ticket_id}", headers=self._headers)

    def assign(self, ticket_id: int | str, payload: Any) -> ApiResponse:
        return self._base.patch(f"{BASE}/{ticket_id}/assign", json=to_body(payload), headers=self._headers)

    def set_status(self, ticket_id: int | str, payload: Any) -> ApiResponse:
        return self._base.patch(f"{BASE}/{ticket_id}/status", json=to_body(payload), headers=self._headers)

    def stats(self) -> ApiResponse:
        return self._base.get(f"{BASE}/stats", headers=self._headers)
