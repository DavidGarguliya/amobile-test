"""Engine, session factory and FastAPI dependency (single source of truth for state, INV-D*)."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables for local/dev runs (SQLite). Production uses Alembic migrations (NFR-1/NFR-9)."""
    from app import models  # noqa: F401  (ensure models are imported/registered)
    from app.db.base import Base

    Base.metadata.create_all(bind=engine)
