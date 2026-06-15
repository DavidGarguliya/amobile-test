"""Specs for Module 3 — integration ingress & processing (EP-14, EP-15, EP-16).

Traceability: FR-I4..FR-I10, FR-I13..FR-I17, FR-I19; invariants INV-P8..P12.
"""

from __future__ import annotations

import pytest

from tests.api.fixtures import factories
from tests.api.schemas.common import extract_items
from tests.api.schemas.integration import IntegrationRequestOut, ProcessResultOut
from tests.api.utils.asserts import (
    assert_error_envelope,
    assert_pagination,
    assert_schema,
    assert_status,
)
from tests.api.utils.markers import req

pytestmark = pytest.mark.integration

CREATED = (200, 201)


# -- helpers ---------------------------------------------------------------------------------
def _new_client(admin_clients, **overrides) -> tuple[int, str]:
    response = admin_clients.create(factories.client_payload(**overrides))
    assert_status(response, *CREATED)
    return response.json["client_id"], response.json["api_key"]


def _request_id(submit_response, admin_integration, client_id) -> int:
    body = submit_response.json
    if isinstance(body, dict) and isinstance(body.get("id"), int):
        return body["id"]
    listing = admin_integration.list(client_id=client_id, limit=100)
    assert_status(listing, 200)
    items = extract_items(listing.json)
    assert items, "ожидался хотя бы один сохранённый интеграционный запрос"
    return max(item["id"] for item in items)


# -- submit: positive / persistence ----------------------------------------------------------
@req("FR-I4", "FR-I10")
@pytest.mark.positive
def test_submit_request_accepted(admin_clients, integration):
    _, api_key = _new_client(admin_clients)
    response = integration.submit(factories.employee_sync_payload(), api_key=api_key)
    assert_status(response, *CREATED)


@req("FR-I10", "FR-I13")
@pytest.mark.positive
def test_submit_persists_and_is_listed(admin_clients, integration, admin_integration):
    client_id, api_key = _new_client(admin_clients)
    assert_status(integration.submit(factories.employee_sync_payload(), api_key=api_key), *CREATED)
    listing = admin_integration.list(client_id=client_id, limit=100)
    assert_status(listing, 200)
    items = assert_pagination(listing.json, limit=100)
    assert items, "сохранённый запрос должен попадать в список"


@req("FR-I19")
@pytest.mark.contract
def test_request_status_enum_contract(admin_clients, integration, admin_integration):
    client_id, api_key = _new_client(admin_clients)
    assert_status(integration.submit(factories.employee_sync_payload(), api_key=api_key), *CREATED)
    listing = admin_integration.list(client_id=client_id, limit=100)
    assert_status(listing, 200)
    items = extract_items(listing.json)
    item = assert_schema(items[0], IntegrationRequestOut)
    assert item.status in {"accepted", "rejected", "processed", "failed"}


# -- submit: auth / negative -----------------------------------------------------------------
@req("FR-I5", "INV-P9")
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.contract
def test_submit_without_api_key_401(integration):
    response = integration.submit(factories.employee_sync_payload())  # no X-API-Key
    assert_status(response, 401)
    assert_error_envelope(response, "UNAUTHORIZED")


@req("FR-I6", "INV-P9")
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.contract
def test_submit_invalid_api_key_401(integration):
    response = integration.submit(factories.employee_sync_payload(), api_key="company_live_invalid_key")
    assert_status(response, 401)
    assert_error_envelope(response, "UNAUTHORIZED")


@req("FR-I7", "INV-P9")
@pytest.mark.negative
@pytest.mark.auth
@pytest.mark.contract
def test_submit_deactivated_client_403(admin_clients, integration):
    client_id, api_key = _new_client(admin_clients)
    assert_status(admin_clients.deactivate(client_id), 200)
    response = integration.submit(factories.employee_sync_payload(), api_key=api_key)
    assert_status(response, 403)
    assert_error_envelope(response, "FORBIDDEN")


@req("FR-I9")
@pytest.mark.negative
@pytest.mark.contract
def test_submit_empty_request_type_422(admin_clients, integration):
    _, api_key = _new_client(admin_clients)
    response = integration.submit({"request_type": "", "payload": {}}, api_key=api_key)
    assert_status(response, 422)
    assert_error_envelope(response, "VALIDATION_ERROR")


@req("FR-I8", "INV-P9")
@pytest.mark.negative
@pytest.mark.boundary
@pytest.mark.contract
def test_submit_rate_limit_429(admin_clients, integration, settings):
    limit = 2
    _, api_key = _new_client(admin_clients, requests_limit_per_minute=limit)
    extra = max(3, settings.rate_limit_probe_count)
    statuses = [
        integration.submit(factories.employee_sync_payload(), api_key=api_key).status_code
        for _ in range(limit + extra)
    ]
    assert 429 in statuses, f"ожидался 429 при превышении лимита {limit}/мин, получено: {statuses}"


# -- listing filters -------------------------------------------------------------------------
@req("FR-I13")
@pytest.mark.positive
def test_list_requests_filter_by_client(admin_clients, integration, admin_integration):
    client_id, api_key = _new_client(admin_clients)
    assert_status(integration.submit(factories.employee_sync_payload(), api_key=api_key), *CREATED)
    response = admin_integration.list(client_id=client_id, limit=100)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=100)
    assert all(item.get("client_id") == client_id for item in items)


# -- processing ------------------------------------------------------------------------------
@req("FR-I14", "FR-I15", "INV-P12")
@pytest.mark.positive
@pytest.mark.contract
def test_process_employee_sync_creates_employee(admin_clients, integration, admin_integration, employees):
    client_id, api_key = _new_client(admin_clients)
    sync = factories.employee_sync_payload()
    email = sync.payload["email"]
    submit = integration.submit(sync, api_key=api_key)
    assert_status(submit, *CREATED)
    request_id = _request_id(submit, admin_integration, client_id)
    # Act: process
    result = admin_integration.process(request_id)
    assert_status(result, 200)
    assert_schema(result.json, ProcessResultOut)
    assert result.json.get("status") == "processed"
    # Assert: employee was created/updated in the directory (INV-P12).
    found = employees.list(search=email, limit=50)
    assert_status(found, 200)
    items = extract_items(found.json)
    assert any(item.get("email") == email for item in items), "employee_sync должен создать сотрудника"


@req("FR-I17", "INV-P11")
@pytest.mark.negative
@pytest.mark.contract
def test_process_already_processed_409(admin_clients, integration, admin_integration):
    client_id, api_key = _new_client(admin_clients)
    submit = integration.submit(factories.employee_sync_payload(), api_key=api_key)
    assert_status(submit, *CREATED)
    request_id = _request_id(submit, admin_integration, client_id)
    assert_status(admin_integration.process(request_id), 200)
    # Re-processing a processed request must be rejected (idempotency).
    response = admin_integration.process(request_id)
    assert_status(response, 409)
    assert_error_envelope(response, "ALREADY_PROCESSED")


@req("FR-I16")
@pytest.mark.negative
def test_process_failure_sets_failed_status(admin_clients, integration, admin_integration):
    client_id, api_key = _new_client(admin_clients)
    # Payload that cannot be synced (no external_id and no email → no match key, cannot create).
    bad = factories.employee_sync_payload()
    bad.payload.pop("external_id", None)
    bad.payload.pop("email", None)
    submit = integration.submit(bad, api_key=api_key)
    assert_status(submit, *CREATED)
    request_id = _request_id(submit, admin_integration, client_id)
    admin_integration.process(request_id)  # processing is expected to fail
    # Assert via listing: the request ended in 'failed' with an error_message (FR-I16).
    listing = admin_integration.list(client_id=client_id, limit=100)
    assert_status(listing, 200)
    item = next(i for i in extract_items(listing.json) if i.get("id") == request_id)
    assert item.get("status") == "failed", f"ожидался статус failed, получено {item.get('status')!r}"
    assert item.get("error_message"), "error_message должен быть заполнен при ошибке обработки"
