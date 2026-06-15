"""Audit read service (thin wrapper over the audit repository)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories import audit as repo


def list_audit(db: Session, **filters) -> tuple[list[AuditLog], int]:
    return repo.list_audit(db, **filters)
