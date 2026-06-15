"""Employee request/response schemas (FR-E*)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeCreate(BaseModel):
    full_name: str = Field(min_length=1)
    position: str = Field(min_length=1)
    department: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    email: EmailStr
    external_id: str | None = None


class EmployeeUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1)
    position: str | None = Field(default=None, min_length=1)
    department: str | None = Field(default=None, min_length=1)
    phone: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    is_active: bool | None = None


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    position: str
    department: str
    phone: str | None = None
    email: str
    is_active: bool
    external_id: str | None = None
    created_at: datetime
    updated_at: datetime
