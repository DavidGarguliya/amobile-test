"""Specs for Module 3 — API client administration (EP-12, EP-13). Traceability: FR-I1..FR-I3."""

from __future__ import annotations

import pytest

from tests.api.fixtures import factories
from tests.api.schemas.integration import ClientCreatedOut
from tests.api.utils.asserts import assert_schema, assert_status
from tests.api.utils.markers import req

pytestmark = pytest.mark.integration

CREATED = (200, 201)


@req("FR-I1", "FR-I2", "INV-P8")
@pytest.mark.positive
@pytest.mark.contract
def test_create_client_returns_key_once(admin_clients):
    response = admin_clients.create(factories.client_payload())
    assert_status(response, *CREATED)
    body = assert_schema(response.json, ClientCreatedOut)
    assert body.api_key, "plaintext api_key must be returned exactly once on creation"
    assert body.client_id


@req("FR-I2", "NFR-7")
@pytest.mark.positive
@pytest.mark.boundary
def test_create_client_key_looks_like_token(admin_clients):
    response = admin_clients.create(factories.client_payload())
    assert_status(response, *CREATED)
    api_key = response.json["api_key"]
    assert isinstance(api_key, str) and len(api_key) >= 16, "api_key должен быть непрозрачным токеном"


@req("FR-I2", "INV-P8")
@pytest.mark.positive
def test_create_two_clients_keys_are_distinct(admin_clients):
    first = admin_clients.create(factories.client_payload())
    second = admin_clients.create(factories.client_payload())
    assert_status(first, *CREATED)
    assert_status(second, *CREATED)
    assert first.json["api_key"] != second.json["api_key"], "ключи разных клиентов должны отличаться"
    assert first.json["client_id"] != second.json["client_id"]


@req("FR-I3")
@pytest.mark.positive
def test_deactivate_client(admin_clients, active_client_key):
    response = admin_clients.deactivate(active_client_key["client_id"])
    assert_status(response, 200)
