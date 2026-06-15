"""Response contract schemas for the Integration / Admin resources (§4.2–4.5)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ClientCreatedOut(BaseModel):
    """Response of ``POST /api/admin/clients`` — the only place the plaintext key appears (INV-P8)."""

    model_config = ConfigDict(extra="ignore")

    client_id: int
    api_key: str


class ClientOut(BaseModel):
    """Client as returned by listings/reads — must NOT expose the plaintext api_key (AC-I2)."""

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    is_active: bool
    requests_limit_per_minute: int
    created_at: datetime


class IntegrationRequestOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    client_id: int
    request_type: str
    payload: dict[str, Any] | None = None
    status: str  # accepted | rejected | processed | failed (FR-I19)
    error_message: str | None = None
    created_at: datetime
    processed_at: datetime | None = None


class ProcessResultOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str
    message: str | None = None


class AuditOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    client_id: int | None = None
    action: str
    ip_address: str
    user_agent: str
    success: bool
    details: Any | None = None
    created_at: datetime
