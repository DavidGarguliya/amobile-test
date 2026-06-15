"""Specs for Module 1 — Employees (EP-01..EP-05). Traceability: FR-E1..FR-E10.

Structure: Arrange-Act-Assert. HTTP is reached only through the EmployeesClient service object.
"""

from __future__ import annotations

import pytest

from tests.api.fixtures import factories
from tests.api.schemas.employee import EmployeeOut
from tests.api.utils.asserts import (
    assert_error_envelope,
    assert_not_success,
    assert_pagination,
    assert_schema,
    assert_status,
)
from tests.api.utils.markers import req

pytestmark = pytest.mark.employees

CREATED = (200, 201)
REQUIRED_FIELDS = ["full_name", "position", "department", "phone", "email"]


# -- positive / contract ---------------------------------------------------------------------
@req("FR-E1", "FR-E10", "INV-D1")
@pytest.mark.positive
@pytest.mark.contract
def test_create_employee_returns_created(employees):
    # Arrange
    payload = factories.employee_payload()
    # Act
    response = employees.create(payload)
    # Assert
    assert_status(response, *CREATED)
    body = assert_schema(response.json, EmployeeOut)
    assert body.is_active is True
    assert body.email == payload.email


@req("FR-E10")
@pytest.mark.positive
def test_create_employee_has_timestamps(employees):
    response = employees.create(factories.employee_payload())
    assert_status(response, *CREATED)
    assert response.json.get("created_at"), "created_at must be set on creation"
    assert response.json.get("updated_at"), "updated_at must be set on creation"


# -- negative: validation --------------------------------------------------------------------
@req("FR-E2", "NFR-2")
@pytest.mark.negative
@pytest.mark.contract
@pytest.mark.parametrize("missing", REQUIRED_FIELDS)
def test_create_employee_missing_required_field(employees, missing):
    payload = factories.employee_payload().model_dump()
    payload.pop(missing)
    response = employees.create(payload)
    assert_status(response, 422)
    assert_error_envelope(response, "VALIDATION_ERROR")


@req("FR-E3", "INV-P2")
@pytest.mark.negative
@pytest.mark.contract
def test_create_employee_duplicate_email(employees):
    first = factories.employee_payload()
    assert_status(employees.create(first), *CREATED)
    # Arrange: a second employee reusing the same email
    duplicate = factories.employee_payload().model_dump()
    duplicate["email"] = first.email
    # Act
    response = employees.create(duplicate)
    # Assert: uniqueness violation (409 or 422 — Q-7), unified envelope.
    assert_not_success(response)
    assert_error_envelope(response)


@req("FR-E2")
@pytest.mark.negative
def test_create_employee_invalid_email_format(employees):
    payload = factories.employee_payload().model_dump()
    payload["email"] = "not-an-email"
    response = employees.create(payload)
    assert_status(response, 422)
    assert_error_envelope(response, "VALIDATION_ERROR")


# -- list / filter / search / pagination -----------------------------------------------------
@req("FR-E5")
@pytest.mark.positive
@pytest.mark.boundary
def test_list_employees_pagination(employees):
    for _ in range(2):
        assert_status(employees.create(factories.employee_payload()), *CREATED)
    response = employees.list(page=1, limit=1)
    assert_status(response, 200)
    assert_pagination(response.json, limit=1)


@req("FR-E4")
@pytest.mark.positive
def test_list_employees_filter_department(employees):
    department = f"DEPT-{factories.unique_suffix()}"
    created = employees.create(factories.employee_payload(department=department))
    assert_status(created, *CREATED)
    response = employees.list(department=department, limit=50)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=50)
    assert any(item.get("department") == department for item in items)


@req("FR-E4")
@pytest.mark.positive
def test_list_employees_filter_is_active_excludes_deactivated(employees):
    created = employees.create(factories.employee_payload())
    assert_status(created, *CREATED)
    employee_id = created.json["id"]
    assert_status(employees.deactivate(employee_id), 200)
    response = employees.list(is_active=True, limit=100)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=100)
    assert all(item.get("id") != employee_id for item in items), "deactivated employee must be filtered out"


@req("FR-E6")
@pytest.mark.positive
@pytest.mark.parametrize("field", ["full_name", "email", "position"])
def test_search_employees_by_field(employees, field):
    token = factories.unique_suffix()
    overrides = {field: f"Searchable {token}" if field != "email" else f"search.{token}@example.com"}
    created = employees.create(factories.employee_payload(**overrides))
    assert_status(created, *CREATED)
    response = employees.list(search=token, limit=50)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=50)
    assert any(item.get("id") == created.json["id"] for item in items), f"search by {field} must match"


# -- get by id -------------------------------------------------------------------------------
@req("FR-E7")
@pytest.mark.positive
@pytest.mark.contract
def test_get_employee_by_id(employees, created_employee):
    response = employees.get(created_employee["id"])
    assert_status(response, 200)
    assert_schema(response.json, EmployeeOut)


@req("FR-E7", "NFR-2")
@pytest.mark.negative
@pytest.mark.contract
def test_get_employee_not_found(employees):
    response = employees.get(999_999_999)
    assert_status(response, 404)
    assert_error_envelope(response, "NOT_FOUND")


# -- update ----------------------------------------------------------------------------------
@req("FR-E8", "INV-D1")
@pytest.mark.positive
@pytest.mark.contract
def test_update_employee_changes_fields(employees, created_employee):
    new_position = f"Lead {factories.unique_suffix()}"
    response = employees.update(created_employee["id"], {"position": new_position})
    assert_status(response, 200)
    body = assert_schema(response.json, EmployeeOut)
    assert body.position == new_position


# -- deactivate (soft delete) ----------------------------------------------------------------
@req("FR-E9", "INV-P1")
@pytest.mark.positive
@pytest.mark.contract
def test_deactivate_employee_keeps_record(employees, created_employee):
    employee_id = created_employee["id"]
    # Act: deactivate
    deactivated = employees.deactivate(employee_id)
    assert_status(deactivated, 200)
    assert deactivated.json.get("is_active") is False
    # Assert: record is NOT physically deleted — still readable.
    fetched = employees.get(employee_id)
    assert_status(fetched, 200)
    assert fetched.json.get("is_active") is False
