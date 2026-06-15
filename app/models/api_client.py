"""API client entity (brief §4.2). Only the key hash is stored (INV-P8)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utcnow


class ApiClient(Base):
    __tablename__ = "api_clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    requests_limit_per_minute: Mapped[int] = mapped_column(default=60)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )

    # Keys live in the separate ``api_keys`` table (rotation support, ADR-004).
