"""Employee entity (brief §2.2). external_id added to support employee_sync matching (Q-8)."""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(index=True)
    position: Mapped[str] = mapped_column(index=True)
    department: Mapped[str] = mapped_column(index=True)
    phone: Mapped[str | None] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    # Not in the original entity (§2.2); added for integration sync matching (ADR-007, Q-8).
    external_id: Mapped[str | None] = mapped_column(unique=True, index=True, nullable=True)
