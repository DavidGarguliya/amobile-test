"""External integration ingress router (EP-14)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, get_db, user_agent
from app.core.config import settings
from app.schemas.integration import IntegrationRequestIn, IntegrationRequestOut
from app.services import integration as service

router = APIRouter(prefix="/api/integration", tags=["integration"])


@router.post("/requests", response_model=IntegrationRequestOut, status_code=201)
def submit_request(
    request: Request,
    payload: IntegrationRequestIn,
    db: Session = Depends(get_db),
) -> IntegrationRequestOut:
    api_key = request.headers.get(settings.api_key_header)
    created = service.submit_request(
        db,
        api_key,
        payload,
        ip_address=client_ip(request),
        user_agent=user_agent(request),
    )
    return created
