"""Data access for integration requests."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.integration_request import IntegrationRequest


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
    client_id: int,
    request_type: str,
    payload: dict[str, Any] | None,
    status: str,
    error_message: str | None = None,
) -> IntegrationRequest:
    request = IntegrationRequest(
        client_id=client_id,
        request_type=request_type,
        payload=payload,
        status=status,
        error_message=error_message,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def save(db: Session, request: IntegrationRequest) -> IntegrationRequest:
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def get(db: Session, request_id: int) -> IntegrationRequest | None:
    return db.get(IntegrationRequest, request_id)


def list_requests(
    db: Session,
    *,
    client_id: int | None = None,
    status: str | None = None,
    request_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[IntegrationRequest], int]:
    stmt = select(IntegrationRequest)
    if client_id is not None:
        stmt = stmt.where(IntegrationRequest.client_id == client_id)
    if status is not None:
        stmt = stmt.where(IntegrationRequest.status == status)
    if request_type is not None:
        stmt = stmt.where(IntegrationRequest.request_type == request_type)
    if (parsed := _parse(date_from)) is not None:
        stmt = stmt.where(IntegrationRequest.created_at >= parsed)
    if (parsed := _parse(date_to)) is not None:
        stmt = stmt.where(IntegrationRequest.created_at <= parsed)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(IntegrationRequest.id).offset((page - 1) * limit).limit(limit)).all()
    return list(rows), total
