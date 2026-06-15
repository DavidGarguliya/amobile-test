"""Specs for Module 2 — Tickets (EP-06..EP-11). Traceability: FR-T1..FR-T14, INV-P3..P7."""

from __future__ import annotations

import pytest

from tests.api.fixtures import factories
from tests.api.schemas.ticket import TicketOut, TicketStatsOut
from tests.api.utils.asserts import (
    assert_error_envelope,
    assert_not_success,
    assert_pagination,
    assert_schema,
    assert_status,
)
from tests.api.utils.markers import req

pytestmark = pytest.mark.tickets

CREATED = (200, 201)


def _make_employee(employees) -> int:
    response = employees.create(factories.employee_payload())
    assert_status(response, *CREATED)
    return response.json["id"]


def _move_to_in_progress(tickets, employees, ticket_id) -> int:
    assignee = _make_employee(employees)
    response = tickets.assign(ticket_id, {"assigned_to": assignee})
    assert_status(response, 200)
    return assignee


# -- create ----------------------------------------------------------------------------------
@req("FR-T1", "FR-T2", "INV-P3")
@pytest.mark.positive
@pytest.mark.contract
def test_create_ticket_status_is_new(tickets, created_employee):
    response = tickets.create(factories.ticket_payload(employee_id=created_employee["id"]))
    assert_status(response, *CREATED)
    body = assert_schema(response.json, TicketOut)
    assert body.status == "new"
    assert body.resolved_at is None


@req("FR-T5", "INV-P4")
@pytest.mark.negative
@pytest.mark.contract
def test_create_ticket_nonexistent_employee(tickets):
    response = tickets.create(factories.ticket_payload(employee_id=999_999_999))
    assert_not_success(response)
    assert_error_envelope(response, "NOT_FOUND", "VALIDATION_ERROR")


@req("FR-T3")
@pytest.mark.negative
def test_create_ticket_invalid_priority(tickets, created_employee):
    payload = factories.ticket_payload(employee_id=created_employee["id"]).model_dump()
    payload["priority"] = "urgent"  # not in {low, medium, high, critical}
    response = tickets.create(payload)
    assert_status(response, 422)
    assert_error_envelope(response, "VALIDATION_ERROR")


# -- get -------------------------------------------------------------------------------------
@req("FR-T7")
@pytest.mark.positive
@pytest.mark.contract
def test_get_ticket_by_id(tickets, new_ticket):
    response = tickets.get(new_ticket["id"])
    assert_status(response, 200)
    assert_schema(response.json, TicketOut)


@req("FR-T7", "NFR-2")
@pytest.mark.negative
@pytest.mark.contract
def test_get_ticket_not_found(tickets):
    response = tickets.get(999_999_999)
    assert_status(response, 404)
    assert_error_envelope(response, "NOT_FOUND")


# -- assign ----------------------------------------------------------------------------------
@req("FR-T8", "FR-T9", "INV-P6")
@pytest.mark.positive
@pytest.mark.contract
def test_assign_sets_in_progress(tickets, employees, new_ticket):
    assignee = _make_employee(employees)
    response = tickets.assign(new_ticket["id"], {"assigned_to": assignee})
    assert_status(response, 200)
    body = assert_schema(response.json, TicketOut)
    assert body.assigned_to == assignee
    assert body.status == "in_progress"


@req("FR-T8", "INV-P4")
@pytest.mark.negative
@pytest.mark.contract
def test_assign_nonexistent_assignee(tickets, new_ticket):
    response = tickets.assign(new_ticket["id"], {"assigned_to": 999_999_999})
    assert_not_success(response)
    assert_error_envelope(response, "NOT_FOUND", "VALIDATION_ERROR")


# -- status transitions ----------------------------------------------------------------------
@req("FR-T10", "FR-T11", "INV-P5")
@pytest.mark.positive
def test_status_transition_new_to_rejected(tickets, new_ticket):
    response = tickets.set_status(new_ticket["id"], {"status": "rejected"})
    assert_status(response, 200)
    assert response.json.get("status") == "rejected"


@req("FR-T11", "FR-T12", "INV-P7")
@pytest.mark.positive
@pytest.mark.contract
def test_resolve_sets_resolved_at(tickets, employees, new_ticket):
    _move_to_in_progress(tickets, employees, new_ticket["id"])
    response = tickets.set_status(new_ticket["id"], {"status": "resolved"})
    assert_status(response, 200)
    body = assert_schema(response.json, TicketOut)
    assert body.status == "resolved"
    assert body.resolved_at is not None, "resolved_at must be filled on resolve (INV-P7)"


@req("FR-T11", "INV-P5")
@pytest.mark.negative
@pytest.mark.contract
def test_status_transition_forbidden_new_to_resolved(tickets, new_ticket):
    response = tickets.set_status(new_ticket["id"], {"status": "resolved"})
    assert_status(response, 409)
    assert_error_envelope(response, "INVALID_STATUS_TRANSITION")


@req("FR-T11", "INV-P5")
@pytest.mark.negative
@pytest.mark.contract
def test_terminal_status_cannot_change(tickets, employees, new_ticket):
    _move_to_in_progress(tickets, employees, new_ticket["id"])
    assert_status(tickets.set_status(new_ticket["id"], {"status": "resolved"}), 200)
    # resolved is terminal — any further transition is rejected.
    response = tickets.set_status(new_ticket["id"], {"status": "in_progress"})
    assert_status(response, 409)
    assert_error_envelope(response, "INVALID_STATUS_TRANSITION")


@req("FR-T4")
@pytest.mark.negative
def test_status_transition_invalid_value(tickets, new_ticket):
    response = tickets.set_status(new_ticket["id"], {"status": "done"})
    assert_status(response, 422)
    assert_error_envelope(response, "VALIDATION_ERROR")


# -- list / filter / pagination --------------------------------------------------------------
@req("FR-T6")
@pytest.mark.positive
def test_list_tickets_filter_status_new(tickets, new_ticket):
    response = tickets.list(status="new", limit=100)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=100)
    assert all(item.get("status") == "new" for item in items)


@req("FR-T6")
@pytest.mark.positive
def test_list_tickets_filter_priority(tickets, created_employee):
    payload = factories.ticket_payload(employee_id=created_employee["id"], priority="critical")
    assert_status(tickets.create(payload), *CREATED)
    response = tickets.list(priority="critical", limit=100)
    assert_status(response, 200)
    items = assert_pagination(response.json, limit=100)
    assert all(item.get("priority") == "critical" for item in items)


@req("FR-T14")
@pytest.mark.positive
@pytest.mark.boundary
def test_list_tickets_pagination(tickets, created_employee):
    for _ in range(2):
        assert_status(tickets.create(factories.ticket_payload(employee_id=created_employee["id"])), *CREATED)
    response = tickets.list(page=1, limit=1)
    assert_status(response, 200)
    assert_pagination(response.json, limit=1)


# -- stats -----------------------------------------------------------------------------------
@req("FR-T13")
@pytest.mark.positive
@pytest.mark.contract
def test_tickets_stats_contract(tickets):
    response = tickets.stats()
    assert_status(response, 200)
    stats = assert_schema(response.json, TicketStatsOut)
    assert stats.new + stats.in_progress + stats.resolved + stats.rejected == stats.total, (
        "sum of per-status counts must equal total"
    )
    assert stats.critical_opened >= 0
