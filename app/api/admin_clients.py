"""API client administration router (EP-12, EP-13). Admin-only (ADR-009)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.schemas.integration import ClientCreate, ClientCreatedOut, ClientOut
from app.services import clients as service

router = APIRouter(
    prefix="/api/admin/clients", tags=["admin:clients"], dependencies=[Depends(require_roles("admin"))]
)


@router.post("", response_model=ClientCreatedOut, status_code=201)
def create_client(payload: ClientCreate, response: Response, db: Session = Depends(get_db)) -> ClientCreatedOut:
    client, api_key = service.create_client(db, payload)
    response.headers["Location"] = f"/api/admin/clients/{client.id}"
    # The plaintext key is returned exactly once here (INV-P8).
    return ClientCreatedOut(client_id=client.id, api_key=api_key)


@router.post("/{client_id}/keys", response_model=ClientCreatedOut, status_code=201)
def rotate_key(client_id: int, db: Session = Depends(get_db)) -> ClientCreatedOut:
    """Issue a new key for the client (rotation). The plaintext is shown once."""
    api_key = service.rotate_key(db, client_id)
    return ClientCreatedOut(client_id=client_id, api_key=api_key)


@router.patch("/{client_id}/deactivate", response_model=ClientOut)
def deactivate_client(client_id: int, db: Session = Depends(get_db)) -> ClientOut:
    return service.deactivate_client(db, client_id)
