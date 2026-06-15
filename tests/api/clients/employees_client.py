"""Service object for the Employees resource (EP-01..EP-05).

Methods mirror API operations and return :class:`ApiResponse`. No business assertions here —
those live in specs (ADR-001).
"""

from __future__ import annotations

from typing import Any

from tests.api.clients.base_client import ApiResponse, BaseApiClient, to_body

BASE = "/api/employees"


class EmployeesClient:
    def __init__(self, base: BaseApiClient) -> None:
        self._base = base
        self._headers = base.settings.admin_headers

    def create(self, payload: Any) -> ApiResponse:
        return self._base.post(BASE, json=to_body(payload), headers=self._headers)

    def list(
        self,
        *,
        department: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> ApiResponse:
        params = {
            "department": department,
            "is_active": is_active,
            "search": search,
            "page": page,
            "limit": limit,
        }
        return self._base.get(BASE, params=params, headers=self._headers)

    def get(self, employee_id: int | str) -> ApiResponse:
        return self._base.get(f"{BASE}/{employee_id}", headers=self._headers)

    def update(self, employee_id: int | str, payload: Any) -> ApiResponse:
        return self._base.put(f"{BASE}/{employee_id}", json=to_body(payload), headers=self._headers)

    def deactivate(self, employee_id: int | str) -> ApiResponse:
        return self._base.patch(f"{BASE}/{employee_id}/deactivate", headers=self._headers)
