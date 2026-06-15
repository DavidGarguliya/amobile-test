"""Pytest fixtures wiring the POM layer for specs.

Resource clients are built on a single session-scoped transport (:class:`BaseApiClient`). Specs
receive ready-to-use service objects and prerequisite-data fixtures. No HTTP happens at collection
time, so ``pytest --collect-only`` succeeds even without a running API (type B / TDD).
"""

from __future__ import annotations

import logging
from typing import Any, Iterator

import pytest

from tests.api.clients.admin_clients_client import AdminClientsClient
from tests.api.clients.admin_integration_client import AdminIntegrationClient
from tests.api.clients.audit_client import AuditClient
from tests.api.clients.auth_client import AuthClient
from tests.api.clients.base_client import ApiResponse, BaseApiClient
from tests.api.clients.employees_client import EmployeesClient
from tests.api.clients.integration_client import IntegrationClient
from tests.api.clients.tickets_client import TicketsClient
from tests.api.config.settings import Settings, get_settings
from tests.api.fixtures import factories
from tests.api.utils.asserts import assert_status


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session", autouse=True)
def _configure_logging(settings: Settings) -> None:
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))


@pytest.fixture(scope="session")
def base_client(settings: Settings) -> Iterator[BaseApiClient]:
    client = BaseApiClient(settings=settings)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture
def anon_client(settings: Settings) -> Iterator[BaseApiClient]:
    """A client with no bearer token (for authentication-failure specs)."""
    client = BaseApiClient(settings=settings)
    try:
        yield client
    finally:
        client.close()


# -- authentication (ADR-009) ----------------------------------------------------------------
@pytest.fixture(scope="session")
def admin_token(base_client: BaseApiClient, settings: Settings) -> str:
    response = base_client.post(
        "/api/auth/login",
        json={"email": settings.admin_email, "password": settings.admin_password},
    )
    assert response.status_code == 200, f"admin login failed: {response.status_code} {response.text}"
    return response.json["access_token"]


@pytest.fixture(scope="session", autouse=True)
def _apply_admin_auth(base_client: BaseApiClient, admin_token: str) -> Iterator[None]:
    """Authenticate the shared client as admin for the whole session."""
    base_client.set_auth(admin_token)
    yield
    base_client.set_auth(None)


@pytest.fixture
def auth(base_client: BaseApiClient) -> AuthClient:
    return AuthClient(base_client)


# -- resource service objects ----------------------------------------------------------------
@pytest.fixture
def employees(base_client: BaseApiClient) -> EmployeesClient:
    return EmployeesClient(base_client)


@pytest.fixture
def tickets(base_client: BaseApiClient) -> TicketsClient:
    return TicketsClient(base_client)


@pytest.fixture
def admin_clients(base_client: BaseApiClient) -> AdminClientsClient:
    return AdminClientsClient(base_client)


@pytest.fixture
def integration(base_client: BaseApiClient) -> IntegrationClient:
    return IntegrationClient(base_client)


@pytest.fixture
def admin_integration(base_client: BaseApiClient) -> AdminIntegrationClient:
    return AdminIntegrationClient(base_client)


@pytest.fixture
def audit(base_client: BaseApiClient) -> AuditClient:
    return AuditClient(base_client)


# -- prerequisite data fixtures (execute only when a test uses them) --------------------------
def _created_body(response: ApiResponse, settings: Settings) -> dict[str, Any]:
    assert_status(response, settings.expect_created_code, 200, 201)
    assert isinstance(response.json, dict), f"expected an object body, got {response.text!r}"
    return response.json


@pytest.fixture
def created_employee(employees: EmployeesClient, settings: Settings) -> dict[str, Any]:
    """Create a fresh active employee and return its representation."""
    return _created_body(employees.create(factories.employee_payload()), settings)


@pytest.fixture
def new_ticket(
    tickets: TicketsClient, created_employee: dict[str, Any], settings: Settings
) -> dict[str, Any]:
    """Create a ticket (status=new) owned by a fresh employee."""
    payload = factories.ticket_payload(employee_id=created_employee["id"])
    return _created_body(tickets.create(payload), settings)


@pytest.fixture
def active_client_key(admin_clients: AdminClientsClient, settings: Settings) -> dict[str, Any]:
    """Create an API client and return the create response (contains client_id + plaintext api_key)."""
    return _created_body(admin_clients.create(factories.client_payload()), settings)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write Allure ``environment.properties`` into the results dir (shown in the report's Environment)."""
    results_dir = getattr(session.config.option, "allure_report_dir", None)
    if not results_dir:
        return
    import os

    cfg = get_settings()
    os.makedirs(results_dir, exist_ok=True)
    lines = [
        f"API_BASE_URL={cfg.base_url}",
        "Auth=JWT bearer (admin)",
        f"API_Key_Header={cfg.api_key_header}",
        f"Expect_Created_Code={cfg.expect_created_code}",
    ]
    with open(os.path.join(results_dir, "environment.properties"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
