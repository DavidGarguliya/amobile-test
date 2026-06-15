"""Request DTOs for the Tickets resource (EP-06, EP-09, EP-10)."""

from __future__ import annotations

from pydantic import BaseModel


class TicketCreate(BaseModel):
    employee_id: int
    title: str
    description: str
    priority: str  # low | medium | high | critical (validated by the service, FR-T3)


class TicketAssign(BaseModel):
    assigned_to: int


class TicketStatusUpdate(BaseModel):
    status: str  # new | in_progress | resolved | rejected (FR-T4)
