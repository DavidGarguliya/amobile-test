"""Data access for external identity mappings (ADR-007, Q-8)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.external_identity import ExternalIdentity


def get(db: Session, source_system: str, external_id: str) -> ExternalIdentity | None:
    return db.scalar(
        select(ExternalIdentity).where(
            ExternalIdentity.source_system == source_system,
            ExternalIdentity.external_id == external_id,
        )
    )


def create(
    db: Session, *, source_system: str, external_id: str, employee_id: int, commit: bool = True
) -> ExternalIdentity:
    identity = ExternalIdentity(
        source_system=source_system, external_id=external_id, employee_id=employee_id
    )
    db.add(identity)
    db.commit() if commit else db.flush()
    db.refresh(identity)
    return identity
