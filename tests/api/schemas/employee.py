"""Response contract schema for the Employees resource (entity §2.2)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmployeeOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    full_name: str
    position: str
    department: str
    phone: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
