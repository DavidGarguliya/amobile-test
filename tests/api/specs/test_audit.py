"""Specs for Module 3 — audit log (EP-17). Traceability: FR-I11, FR-I12, FR-I18; INV-P10."""

from __future__ import annotations

import pytest

from tests.api.fixtures import factories
from tests.api.schemas.common import extract_items
from tests.api.schemas.integration import AuditOut
from tests.api.utils.asserts import assert_pagination, assert_schema, assert_status
from tests.api.utils.markers import req

pytestmark = [pytest.mark.integration, pytest.mark.audit]

CREATED = (200, 201)


def _new_client(admin_clients, **overrides) -> tuple[int, str]:
    response = admin_clients.create(factories.client_payload(**overrides))
    assert_status(response, *CREATED)
    return response.json["client_id"], response.json["api_key"]


@req("FR-I11", "INV-P10")
@pytest.mark.positive
def test_audit_records_each_attempt(admin_clients, integration, audit):
    client_id, api_key = _new_client(admin_clients)
    integration.submit(factories.employee_sync_payload(), api_key=api_key)
    response = audit.list(client_id=client_id, limit=100)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=100)
    assert items, "каждая попытка обращения должна попадать в аудит"


@req("FR-I12", "INV-P10")
@pytest.mark.positive
@pytest.mark.contract
def test_audit_has_ip_and_user_agent(admin_clients, integration, audit):
    client_id, api_key = _new_client(admin_clients)
    integration.submit(factories.employee_sync_payload(), api_key=api_key)
    response = audit.list(client_id=client_id, limit=100)
    assert_status(response, 200)
    items = extract_items(response.json)
    record = assert_schema(items[0], AuditOut)
    assert record.ip_address, "в аудите должен сохраняться IP-адрес"
    assert record.user_agent, "в аудите должен сохраняться User-Agent"


@req("FR-I11", "INV-P10")
@pytest.mark.negative
def test_audit_records_failed_attempt(integration, audit):
    # Unauthenticated attempt → 401, but the attempt must still be audited (success=false).
    integration.submit(factories.employee_sync_payload(), api_key="company_live_invalid_key")
    response = audit.list(success=False, limit=100)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=100)
    assert any(item.get("success") is False for item in items), "неуспешная попытка должна аудироваться"


@req("FR-I18")
@pytest.mark.positive
def test_list_audit_filter_success_true(admin_clients, integration, audit):
    client_id, api_key = _new_client(admin_clients)
    integration.submit(factories.employee_sync_payload(), api_key=api_key)
    response = audit.list(client_id=client_id, success=True, limit=100)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=100)
    assert all(item.get("success") is True for item in items)
