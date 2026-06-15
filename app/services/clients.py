"""API client administration: client + key lifecycle, rotation (ADR-004, INV-P8)."""

from __future__ import annotations

from app.core.errors import not_found
from app.core.security import generate_api_key, hash_secret
from app.models.api_client import ApiClient
from app.repositories import api_clients as repo
from app.repositories import api_keys as keys_repo
from app.schemas.integration import ClientCreate
from sqlalchemy.orm import Session


def create_client(db: Session, data: ClientCreate) -> tuple[ApiClient, str]:
    """Create a client with its first API key; return the client and the plaintext key (shown once)."""
    client = repo.create(db, name=data.name, requests_limit_per_minute=data.requests_limit_per_minute)
    plaintext = _issue_key(db, client.id)
    return client, plaintext


def rotate_key(db: Session, client_id: int) -> str:
    """Issue a new key for an existing client (rotation). Old keys remain valid until revoked."""
    client = repo.get(db, client_id)
    if client is None:
        raise not_found("API client not found", id=client_id)
    return _issue_key(db, client.id)


def deactivate_client(db: Session, client_id: int) -> ApiClient:
    client = repo.get(db, client_id)
    if client is None:
        raise not_found("API client not found", id=client_id)
    client.is_active = False
    return repo.save(db, client)


def _issue_key(db: Session, client_id: int) -> str:
    generated = generate_api_key()
    keys_repo.create(
        db,
        client_id=client_id,
        key_id=generated.key_id,
        secret_hash=hash_secret(generated.secret),
        prefix=generated.prefix,
    )
    return generated.plaintext
