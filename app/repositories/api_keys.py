"""Data access for API keys (rotation support, ADR-004)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.api_key import ApiKey


def create(
    db: Session,
    *,
    client_id: int,
    key_id: str,
    secret_hash: str,
    prefix: str,
    expires_at: datetime | None = None,
) -> ApiKey:
    key = ApiKey(
        client_id=client_id,
        key_id=key_id,
        secret_hash=secret_hash,
        prefix=prefix,
        expires_at=expires_at,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


def save(db: Session, key: ApiKey) -> ApiKey:
    db.add(key)
    db.commit()
    db.refresh(key)
    return key


def get_by_key_id(db: Session, key_id: str) -> ApiKey | None:
    return db.scalar(select(ApiKey).where(ApiKey.key_id == key_id))
