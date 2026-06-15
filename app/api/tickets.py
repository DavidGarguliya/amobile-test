"""Tickets router (EP-06..EP-11)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_db, page_params
from app.schemas.common import Page
from app.schemas.enums import Priority, TicketStatus
from app.schemas.ticket import (
    TicketAssign,
    TicketCreate,
    TicketOut,
    TicketStats,
    TicketStatusUpdate,
)
from app.services import tickets as service

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> TicketOut:
    return service.create_ticket(db, payload)


@router.get("", response_model=Page[TicketOut])
def list_tickets(
    status: TicketStatus | None = None,
    priority: Priority | None = None,
    employee_id: int | None = None,
    assigned_to: int | None = None,
    pagination: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> Page[TicketOut]:
    items, total = service.list_tickets(
        db,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        employee_id=employee_id,
        assigned_to=assigned_to,
        page=pagination.page,
        limit=pagination.limit,
    )
    return Page(items=items, total=total, page=pagination.page, limit=pagination.limit)


# Declared before /{ticket_id} so "stats" is not parsed as an id.
@router.get("/stats", response_model=TicketStats)
def ticket_stats(db: Session = Depends(get_db)) -> TicketStats:
    return TicketStats(**service.stats(db))


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)) -> TicketOut:
    return service.get_ticket(db, ticket_id)


@router.patch("/{ticket_id}/assign", response_model=TicketOut)
def assign_ticket(ticket_id: int, payload: TicketAssign, db: Session = Depends(get_db)) -> TicketOut:
    return service.assign_ticket(db, ticket_id, payload)


@router.patch("/{ticket_id}/status", response_model=TicketOut)
def change_status(ticket_id: int, payload: TicketStatusUpdate, db: Session = Depends(get_db)) -> TicketOut:
    return service.change_status(db, ticket_id, payload)
