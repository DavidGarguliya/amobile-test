"""Specs for admin authn/authz (ADR-009). Traceability: NFR-7, Q-4."""

from __future__ import annotations

import pytest

from tests.api.fixtures import factories
from tests.api.utils.asserts import assert_error_envelope, assert_status
from tests.api.utils.markers import req

pytestmark = pytest.mark.auth


@req("NFR-7")
@pytest.mark.positive
def test_login_success(auth, settings):
    response = auth.login(settings.admin_email, settings.admin_password)
    assert_status(response, 200)
    assert response.json.get("access_token"), "login must return an access token"
    assert response.json.get("role") == "admin"


@req("NFR-7")
@pytest.mark.negative
@pytest.mark.contract
def test_login_wrong_password(auth, settings):
    response = auth.login(settings.admin_email, "definitely-wrong-password")
    assert_status(response, 401)
    assert_error_envelope(response, "UNAUTHORIZED")


@req("NFR-7", "Q-4")
@pytest.mark.negative
@pytest.mark.contract
def test_protected_endpoint_requires_token(anon_client):
    response = anon_client.get("/api/employees")
    assert_status(response, 401)
    assert_error_envelope(response, "UNAUTHORIZED")


@req("NFR-7", "Q-4")
@pytest.mark.negative
@pytest.mark.contract
def test_insufficient_role_forbidden(auth, admin_token, anon_client):
    # Arrange: an admin creates a viewer; viewers may read but not write.
    email = factories.unique_email("viewer")
    created = auth.create_user(
        {"email": email, "password": "viewerpass123", "role": "viewer"}, token=admin_token
    )
    assert_status(created, 201)
    login = auth.login(email, "viewerpass123")
    assert_status(login, 200)
    viewer_token = login.json["access_token"]
    # Act: viewer attempts a write.
    response = anon_client.post(
        "/api/employees",
        json=factories.employee_payload().model_dump(),
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    # Assert: forbidden by role (not unauthorized).
    assert_status(response, 403)
    assert_error_envelope(response, "FORBIDDEN")
