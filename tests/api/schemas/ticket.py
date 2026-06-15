"""Response contract schemas for the Tickets resource (entity §3.2, stats §3.5)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

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


class TicketStatsOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total: int
    new: int
    in_progress: int
    resolved: int
    rejected: int
    critical_opened: int
