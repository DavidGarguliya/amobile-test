"""Data access for the audit log."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def _parse(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt)
    except ValueError:
        return None


def create(
    db: Session,
    *,
    client_id: int | None,
    action: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    record = AuditLog(
        client_id=client_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        details=details,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_audit(
    db: Session,
    *,
    client_id: int | None = None,
    success: bool | None = None,
    action: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[AuditLog], int]:
    stmt = select(AuditLog)
    if client_id is not None:
        stmt = stmt.where(AuditLog.client_id == client_id)
    if success is not None:
        stmt = stmt.where(AuditLog.success == success)
    if action is not None:
        stmt = stmt.where(AuditLog.action == action)
    if (parsed := _parse(date_from)) is not None:
        stmt = stmt.where(AuditLog.created_at >= parsed)
    if (parsed := _parse(date_to)) is not None:
        stmt = stmt.where(AuditLog.created_at <= parsed)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(AuditLog.id.desc()).offset((page - 1) * limit).limit(limit)).all()
    return list(rows), total
