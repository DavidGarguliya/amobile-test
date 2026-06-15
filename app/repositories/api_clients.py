"""Data access for API clients."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.api_client import ApiClient


def create(db: Session, *, name: str, requests_limit_per_minute: int) -> ApiClient:
    client = ApiClient(name=name, requests_limit_per_minute=requests_limit_per_minute)
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
