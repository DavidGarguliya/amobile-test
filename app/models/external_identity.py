"""External identity mapping (ADR-007, Q-8). Links an employee to an id in an external system.

A dedicated table (instead of a single column) supports multiple source systems (1C, AD, ...)
mapping to the same employee.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, utcnow


class ExternalIdentity(Base):
    __tablename__ = "external_identities"
    __table_args__ = (UniqueConstraint("source_system", "external_id", name="uq_external_identity"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_system: Mapped[str] = mapped_column(index=True)
    external_id: Mapped[str] = mapped_column(index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )
