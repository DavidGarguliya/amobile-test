"""User entity for admin authn/authz (ADR-009). Roles: admin | operator | viewer."""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(default="viewer", index=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
