"""Audit log router (EP-17)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_db, page_params
from app.schemas.common import Page
from app.schemas.integration import AuditOut
from app.services import audit as service

router = APIRouter(prefix="/api/admin/audit", tags=["admin:audit"])


@router.get("", response_model=Page[AuditOut])
def list_audit(
    client_id: int | None = None,
    success: bool | None = None,
    action: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    pagination: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> Page[AuditOut]:
    items, total = service.list_audit(
        db,
        client_id=client_id,
        success=success,
        action=action,
        date_from=date_from,
        date_to=date_to,
        page=pagination.page,
        limit=pagination.limit,
    )
    return Page(items=items, total=total, page=pagination.page, limit=pagination.limit)
