"""Shared schemas: generic pagination envelope and the documented error envelope."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int


class ErrorEnvelope(BaseModel):
    """Documented in OpenAPI; produced by the centralized handlers (ADR-003)."""

    error: bool = True
    code: str
    message: str
    details: dict[str, Any] | None = None
