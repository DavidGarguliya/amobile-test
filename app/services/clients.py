"""API client administration: key generation/hash, deactivation (ADR-004, INV-P8)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import not_found
from app.core.security import generate_api_key, hash_api_key
from app.models.api_client import ApiClient
from app.repositories import api_clients as repo
from app.schemas.integration import ClientCreate


def create_client(db: Session, data: ClientCreate) -> tuple[ApiClient, str]:
    """Create a client; return it together with the plaintext key (shown once)."""
    api_key = generate_api_key()
    client = repo.create(
        db,
        name=data.name,
        api_key_hash=hash_api_key(api_key),
        requests_limit_per_minute=data.requests_limit_per_minute,
    )
    return client, api_key


def deactivate_client(db: Session, client_id: int) -> ApiClient:
    client = repo.get(db, client_id)
    if client is None:
        raise not_found("API client not found", id=client_id)
    client.is_active = False
    return repo.save(db, client)
