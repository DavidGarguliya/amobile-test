"""API key entity (ADR-004). Separate table to support rotation: many keys per client.

Stores only ``secret_hash`` (HMAC-SHA256 of the secret with a server pepper) plus the plaintext
``key_id`` for O(1) lookup and a safe-to-display ``prefix``.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utcnow


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("api_clients.id"), index=True)
    key_id: Mapped[str] = mapped_column(unique=True, index=True)
    secret_hash: Mapped[str]
    prefix: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )
