"""Employees router (EP-01..EP-05)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_db, page_params
from app.schemas.common import Page
from app.schemas.employee import EmployeeCreate, EmployeeOut, EmployeeUpdate
from app.services import employees as service

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)) -> EmployeeOut:
    return service.create_employee(db, payload)


@router.get("", response_model=Page[EmployeeOut])
def list_employees(
    department: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    pagination: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> Page[EmployeeOut]:
    items, total = service.list_employees(
        db,
        department=department,
        is_active=is_active,
        search=search,
        page=pagination.page,
        limit=pagination.limit,
    )
    return Page(items=items, total=total, page=pagination.page, limit=pagination.limit)


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)) -> EmployeeOut:
    return service.get_employee(db, employee_id)


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)
) -> EmployeeOut:
    return service.update_employee(db, employee_id, payload)


@router.patch("/{employee_id}/deactivate", response_model=EmployeeOut)
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)) -> EmployeeOut:
    return service.deactivate_employee(db, employee_id)
