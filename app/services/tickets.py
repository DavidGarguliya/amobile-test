"""Ticket business logic: ownership, assignment, status state machine (INV-P3..P7, ADR-005)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import invalid_transition, not_found
from app.db.base import utcnow
from app.models.ticket import Ticket
from app.repositories import employees as employees_repo
from app.repositories import tickets as repo
from app.schemas.ticket import TicketAssign, TicketCreate, TicketStatusUpdate

# Allowed status transitions (brief §3.6). resolved/rejected are terminal.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "new": {"in_progress", "rejected"},
    "in_progress": {"resolved", "rejected"},
    "resolved": set(),
    "rejected": set(),
}


def create_ticket(db: Session, data: TicketCreate) -> Ticket:
    if employees_repo.get(db, data.employee_id) is None:
        raise not_found("Employee (author) not found", field="employee_id", id=data.employee_id)
    return repo.create(
        db,
        {
            "employee_id": data.employee_id,
            "title": data.title,
            "description": data.description,
            "priority": data.priority.value,
            "status": "new",  # INV-P3
        },
    )


def get_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = repo.get(db, ticket_id)
    if ticket is None:
        raise not_found("Ticket not found", id=ticket_id)
    return ticket


def list_tickets(db: Session, **filters) -> tuple[list[Ticket], int]:
    return repo.list_tickets(db, **filters)


def assign_ticket(db: Session, ticket_id: int, data: TicketAssign) -> Ticket:
    ticket = get_ticket(db, ticket_id)
    if employees_repo.get(db, data.assigned_to) is None:
        raise not_found("Assignee not found", field="assigned_to", id=data.assigned_to)
    ticket.assigned_to = data.assigned_to
    if ticket.status == "new":  # assignment moves new -> in_progress (INV-P6)
        ticket.status = "in_progress"
    return repo.save(db, ticket)


def change_status(db: Session, ticket_id: int, data: TicketStatusUpdate) -> Ticket:
    ticket = get_ticket(db, ticket_id)
    target = data.status.value
    if target not in ALLOWED_TRANSITIONS[ticket.status]:
        raise invalid_transition(
            f"Cannot transition ticket from {ticket.status} to {target}",
            **{"from": ticket.status, "to": target},
        )
    ticket.status = target
    if target == "resolved":
        ticket.resolved_at = utcnow()  # INV-P7
    return repo.save(db, ticket)


def stats(db: Session) -> dict[str, int]:
    return repo.stats(db)
