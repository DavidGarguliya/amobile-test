"""Ticket request/response schemas (FR-T*)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import Priority, TicketStatus


class TicketCreate(BaseModel):
    employee_id: int
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: Priority


class TicketAssign(BaseModel):
    assigned_to: int


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    title: str
    description: str
    priority: str
    status: str
    assigned_to: int | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None


class TicketStats(BaseModel):
    total: int
    new: int
    in_progress: int
    resolved: int
    rejected: int
    critical_opened: int
