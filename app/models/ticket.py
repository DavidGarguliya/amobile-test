"""Ticket entity (brief §3.2)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Ticket(Base, TimestampMixin):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    title: Mapped[str]
    description: Mapped[str]
    priority: Mapped[str] = mapped_column(index=True)  # low | medium | high | critical
    status: Mapped[str] = mapped_column(default="new", index=True)  # new | in_progress | resolved | rejected
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), nullable=True, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
