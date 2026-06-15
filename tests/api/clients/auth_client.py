"""Service object for the auth resource (login, user management) — ADR-009."""

from __future__ import annotations

from typing import Any

from tests.api.clients.base_client import ApiResponse, BaseApiClient, to_body

BASE = "/api/auth"


class AuthClient:
    def __init__(self, base: BaseApiClient) -> None:
        self._base = base

    def login(self, email: str, password: str) -> ApiResponse:
        # Login is public — send without relying on the default bearer.
        return self._base.post(f"{BASE}/login", json={"email": email, "password": password})

    def me(self, *, token: str | None = None) -> ApiResponse:
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self._base.get(f"{BASE}/me", headers=headers)

    def create_user(self, payload: Any, *, token: str | None = None) -> ApiResponse:
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return self._base.post(f"{BASE}/users", json=to_body(payload), headers=headers)
