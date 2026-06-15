"""API client administration router (EP-12, EP-13)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.integration import ClientCreate, ClientCreatedOut, ClientOut
from app.services import clients as service

router = APIRouter(prefix="/api/admin/clients", tags=["admin:clients"])


@router.post("", response_model=ClientCreatedOut, status_code=201)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)) -> ClientCreatedOut:
    client, api_key = service.create_client(db, payload)
    # The plaintext key is returned exactly once here (INV-P8).
    return ClientCreatedOut(client_id=client.id, api_key=api_key)


@router.patch("/{client_id}/deactivate", response_model=ClientOut)
def deactivate_client(client_id: int, db: Session = Depends(get_db)) -> ClientOut:
    return service.deactivate_client(db, client_id)
