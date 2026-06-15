"""Data access for employees. Thin SQLAlchemy CRUD; no business rules (those live in services)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.employee import Employee


def create(db: Session, data: dict[str, Any], *, commit: bool = True) -> Employee:
    employee = Employee(**data)
    db.add(employee)
    db.commit() if commit else db.flush()
    db.refresh(employee)
    return employee


def save(db: Session, employee: Employee, *, commit: bool = True) -> Employee:
    db.add(employee)
    db.commit() if commit else db.flush()
    db.refresh(employee)
    return employee


def get(db: Session, employee_id: int) -> Employee | None:
    return db.get(Employee, employee_id)


def get_by_email(db: Session, email: str) -> Employee | None:
    return db.scalar(select(Employee).where(Employee.email == email))


def get_by_external_id(db: Session, external_id: str) -> Employee | None:
    return db.scalar(select(Employee).where(Employee.external_id == external_id))


def list_employees(
    db: Session,
    *,
    department: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Employee], int]:
    stmt = select(Employee)
    if department is not None:
        stmt = stmt.where(Employee.department == department)
    if is_active is not None:
        stmt = stmt.where(Employee.is_active == is_active)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(
                Employee.full_name.ilike(like),
                Employee.email.ilike(like),
                Employee.position.ilike(like),
            )
        )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(Employee.id).offset((page - 1) * limit).limit(limit)).all()
    return list(rows), total
