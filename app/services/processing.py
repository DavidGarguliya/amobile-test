"""Processing of integration requests, incl. employee_sync (ADR-007, INV-P11, INV-P12)."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.errors import already_processed, not_found
from app.db.base import utcnow
from app.models.integration_request import IntegrationRequest
from app.repositories import employees as employees_repo
from app.repositories import integration_requests as requests_repo

logger = logging.getLogger("app.processing")

_SYNC_FIELDS = ("full_name", "position", "department", "phone", "email", "external_id")


class ProcessingError(Exception):
    """Recoverable processing failure → request ends in 'failed' with error_message (FR-I16)."""


def process_request(db: Session, request_id: int) -> tuple[IntegrationRequest, str]:
    request = requests_repo.get(db, request_id)
    if request is None:
        raise not_found("Integration request not found", id=request_id)
    if request.status == "processed":  # idempotency (INV-P11)
        raise already_processed("Request has already been processed")

    try:
        message = _dispatch(db, request)
    except ProcessingError as exc:
        request.status = "failed"
        request.processed_at = utcnow()
        request.error_message = str(exc)
        requests_repo.save(db, request)
        logger.info("integration request %s failed: %s", request.id, exc)
        return request, str(exc)

    request.status = "processed"
    request.processed_at = utcnow()
    request.error_message = None
    requests_repo.save(db, request)
    logger.info("integration request %s processed", request.id)
    return request, message


def _dispatch(db: Session, request: IntegrationRequest) -> str:
    if request.request_type == "employee_sync":
        _sync_employee(db, request.payload or {})
        return "Employee synchronized successfully"
    # Unknown types are accepted and marked processed (extension point, ADR-007).
    return "Processed"


def _sync_employee(db: Session, payload: dict) -> None:
    external_id = payload.get("external_id")
    email = payload.get("email")
    if not external_id and not email:
        raise ProcessingError("employee_sync requires external_id or email for matching")

    employee = None
    if external_id:
        employee = employees_repo.get_by_external_id(db, external_id)
    if employee is None and email:
        employee = employees_repo.get_by_email(db, email)

    fields = {key: payload[key] for key in _SYNC_FIELDS if payload.get(key) is not None}

    if employee is not None:
        for key, value in fields.items():
            setattr(employee, key, value)
        employees_repo.save(db, employee)
        return

    data = {
        "full_name": payload.get("full_name") or "Unknown",
        "position": payload.get("position") or "Unknown",
        "department": payload.get("department") or "Unknown",
        "phone": payload.get("phone"),
        "email": email or (f"{external_id}@imported.local" if external_id else None),
        "external_id": external_id,
    }
    employees_repo.create(db, data)
