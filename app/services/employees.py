"""Employee business logic and invariants (INV-P1, INV-P2)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import not_found, validation_error
from app.models.employee import Employee
from app.repositories import employees as repo
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    if repo.get_by_email(db, data.email):
        raise validation_error("Employee with this email already exists", field="email")
    if data.external_id and repo.get_by_external_id(db, data.external_id):
        raise validation_error("Employee with this external_id already exists", field="external_id")
    return repo.create(db, {**data.model_dump(), "email": str(data.email)})


def get_employee(db: Session, employee_id: int) -> Employee:
    employee = repo.get(db, employee_id)
    if employee is None:
        raise not_found("Employee not found", id=employee_id)
    return employee


def list_employees(db: Session, **filters) -> tuple[list[Employee], int]:
    return repo.list_employees(db, **filters)


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> Employee:
    employee = get_employee(db, employee_id)
    payload = data.model_dump(exclude_unset=True)
    if "email" in payload and payload["email"]:
        new_email = str(payload["email"])
        existing = repo.get_by_email(db, new_email)
        if existing and existing.id != employee.id:
            raise validation_error("Employee with this email already exists", field="email")
        payload["email"] = new_email
    for key, value in payload.items():
        setattr(employee, key, value)
    return repo.save(db, employee)


def deactivate_employee(db: Session, employee_id: int) -> Employee:
    employee = get_employee(db, employee_id)
    employee.is_active = False  # soft delete only (INV-P1)
    return repo.save(db, employee)
