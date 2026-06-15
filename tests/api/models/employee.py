"""Request DTOs for the Employees resource (EP-01, EP-04)."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    full_name: str
    position: str
    department: str
    phone: str
    email: EmailStr


class EmployeeUpdate(BaseModel):
    full_name: str | None = None
    position: str | None = None
    department: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
