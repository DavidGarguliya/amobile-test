"""Processing of integration requests, incl. employee_sync (ADR-007, INV-P11, INV-P12).

Concurrency (brief §45): the request row is claimed with ``SELECT ... FOR UPDATE`` on databases
that support it (PostgreSQL), so two admins cannot process the same request in parallel — the second
waits and then sees ``processed`` → 409. On SQLite (single-process dev/tests) the lock is a no-op.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import already_processed, not_found
from app.db.base import utcnow
from app.models.integration_request import IntegrationRequest
from app.repositories import employees as employees_repo
from app.repositories import external_identities as identities_repo
from app.schemas.enums import RequestStatus

logger = logging.getLogger("app.processing")

SOURCE_SYSTEM = "integration"
_SYNC_FIELDS = ("full_name", "position", "department", "phone", "email", "external_id")


class ProcessingError(Exception):
    """Recoverable processing failure → request ends in 'failed' with error_message (FR-I16)."""


def process_request(db: Session, request_id: int) -> tuple[IntegrationRequest, str]:
    request = _claim(db, request_id)
    if request is None:
        raise not_found("Integration request not found", id=request_id)
    if request.status == RequestStatus.processed.value:  # idempotency (INV-P11)
        raise already_processed("Request has already been processed")

    try:
        message = _dispatch(db, request)
    except ProcessingError as exc:
        request.status = RequestStatus.failed.value
        request.processed_at = utcnow()
        request.error_message = str(exc)
        db.add(request)
        db.commit()
        db.refresh(request)
        logger.info("integration request %s failed: %s", request.id, exc)
        return request, str(exc)

    request.status = RequestStatus.processed.value
    request.processed_at = utcnow()
    request.error_message = None
    db.add(request)
    db.commit()
    db.refresh(request)
    logger.info("integration request %s processed", request.id)
    return request, message


def _claim(db: Session, request_id: int) -> IntegrationRequest | None:
    stmt = select(IntegrationRequest).where(IntegrationRequest.id == request_id)
    dialect = db.bind.dialect.name if db.bind is not None else ""
    if dialect not in ("sqlite",):
        stmt = stmt.with_for_update()
    return db.scalar(stmt)


def _dispatch(db: Session, request: IntegrationRequest) -> str:
    if request.request_type == "employee_sync":
        _sync_employee(db, request.payload or {})
        return "Employee synchronized successfully"
    return "Processed"  # unknown types accepted as a no-op extension point (ADR-007)


def _sync_employee(db: Session, payload: dict) -> None:
    external_id = payload.get("external_id")
    email = payload.get("email")
    if not external_id and not email:
        raise ProcessingError("employee_sync requires external_id or email for matching")

    employee = _match_employee(db, external_id, email)
    fields = {key: payload[key] for key in _SYNC_FIELDS if payload.get(key) is not None}

    if employee is not None:
        for key, value in fields.items():
            setattr(employee, key, value)
        employees_repo.save(db, employee)
    else:
        employee = employees_repo.create(
            db,
            {
                "full_name": payload.get("full_name") or "Unknown",
                "position": payload.get("position") or "Unknown",
                "department": payload.get("department") or "Unknown",
                "phone": payload.get("phone"),
                "email": email or (f"{external_id}@imported.local" if external_id else None),
                "external_id": external_id,
            },
        )

    # Maintain the external identity mapping (INV-P12).
    if external_id and identities_repo.get(db, SOURCE_SYSTEM, external_id) is None:
        identities_repo.create(db, source_system=SOURCE_SYSTEM, external_id=external_id, employee_id=employee.id)


def _match_employee(db: Session, external_id: str | None, email: str | None):
    if external_id:
        identity = identities_repo.get(db, SOURCE_SYSTEM, external_id)
        if identity is not None:
            found = employees_repo.get(db, identity.employee_id)
            if found is not None:
                return found
        legacy = employees_repo.get_by_external_id(db, external_id)
        if legacy is not None:
            return legacy
    if email:
        return employees_repo.get_by_email(db, email)
    return None
