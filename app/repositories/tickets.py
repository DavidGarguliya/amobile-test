"""Data access for tickets."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket


def create(db: Session, data: dict[str, Any]) -> Ticket:
    ticket = Ticket(**data)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def save(db: Session, ticket: Ticket) -> Ticket:
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get(db: Session, ticket_id: int) -> Ticket | None:
    return db.get(Ticket, ticket_id)


def list_tickets(
    db: Session,
    *,
    status: str | None = None,
    priority: str | None = None,
    employee_id: int | None = None,
    assigned_to: int | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Ticket], int]:
    stmt = select(Ticket)
    if status is not None:
        stmt = stmt.where(Ticket.status == status)
    if priority is not None:
        stmt = stmt.where(Ticket.priority == priority)
    if employee_id is not None:
        stmt = stmt.where(Ticket.employee_id == employee_id)
    if assigned_to is not None:
        stmt = stmt.where(Ticket.assigned_to == assigned_to)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(Ticket.id).offset((page - 1) * limit).limit(limit)).all()
    return list(rows), total


def stats(db: Session) -> dict[str, int]:
    total = db.scalar(select(func.count()).select_from(Ticket)) or 0
    by_status = dict(db.execute(select(Ticket.status, func.count()).group_by(Ticket.status)).all())
    critical_opened = (
        db.scalar(
            select(func.count())
            .select_from(Ticket)
            .where(Ticket.priority == "critical", Ticket.status.in_(["new", "in_progress"]))
        )
        or 0
    )
    return {
        "total": total,
        "new": int(by_status.get("new", 0)),
        "in_progress": int(by_status.get("in_progress", 0)),
        "resolved": int(by_status.get("resolved", 0)),
        "rejected": int(by_status.get("rejected", 0)),
        "critical_opened": critical_opened,
    }
