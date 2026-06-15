"""Admin-side integration request management router (EP-15, EP-16)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import PageParams, get_db, page_params, require_roles
from app.schemas.common import Page
from app.schemas.enums import RequestStatus
from app.schemas.integration import IntegrationRequestOut, ProcessResultOut
from app.services import integration as service
from app.services import processing

router = APIRouter(
    prefix="/api/admin/integration/requests",
    tags=["admin:integration"],
    dependencies=[Depends(require_roles("admin"))],
)


@router.get("", response_model=Page[IntegrationRequestOut])
def list_requests(
    client_id: int | None = None,
    status: RequestStatus | None = None,
    request_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    pagination: PageParams = Depends(page_params),
    db: Session = Depends(get_db),
) -> Page[IntegrationRequestOut]:
    items, total = service.list_requests(
        db,
        client_id=client_id,
        status=status.value if status else None,
        request_type=request_type,
        date_from=date_from,
        date_to=date_to,
        page=pagination.page,
        limit=pagination.limit,
    )
    return Page(items=items, total=total, page=pagination.page, limit=pagination.limit)


@router.post("/{request_id}/process", response_model=ProcessResultOut)
def process_request(request_id: int, db: Session = Depends(get_db)) -> ProcessResultOut:
    request, message = processing.process_request(db, request_id)
    return ProcessResultOut(status=request.status, message=message)
