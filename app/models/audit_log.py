"""Audit log entity (brief §4.4). Records every integration attempt (INV-P10)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utcnow


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("api_clients.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(index=True)
    ip_address: Mapped[str] = mapped_column(default="")
    user_agent: Mapped[str] = mapped_column(default="")
    success: Mapped[bool] = mapped_column(index=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now(), index=True
    )
