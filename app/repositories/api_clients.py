"""Data access for API clients."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_client import ApiClient


def create(db: Session, *, name: str, api_key_hash: str, requests_limit_per_minute: int) -> ApiClient:
    client = ApiClient(
        name=name,
        api_key_hash=api_key_hash,
        requests_limit_per_minute=requests_limit_per_minute,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def save(db: Session, client: ApiClient) -> ApiClient:
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get(db: Session, client_id: int) -> ApiClient | None:
    return db.get(ApiClient, client_id)


def get_by_hash(db: Session, api_key_hash: str) -> ApiClient | None:
    return db.scalar(select(ApiClient).where(ApiClient.api_key_hash == api_key_hash))
