"""Integration / admin request/response schemas (FR-I*)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClientCreate(BaseModel):
    name: str = Field(min_length=1)
    requests_limit_per_minute: int = Field(default=60, ge=1)


class ClientCreatedOut(BaseModel):
    """Returned once on creation — the only place the plaintext key is exposed (INV-P8)."""

    client_id: int
    api_key: str


class ClientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    is_active: bool
    requests_limit_per_minute: int
    created_at: datetime


class IntegrationRequestIn(BaseModel):
    # Default "" (instead of min_length=1) so an empty/missing request_type reaches the handler and
    # is validated AFTER authentication — the attempt is then audited (FR-I9 + FR-I11/INV-P10).
    request_type: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class IntegrationRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    request_type: str
    payload: dict[str, Any] | None = None
    status: str
    error_message: str | None = None
    created_at: datetime
    processed_at: datetime | None = None


class ProcessResultOut(BaseModel):
    status: str
    message: str


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int | None = None
    action: str
    ip_address: str
    user_agent: str
    success: bool
    details: Any | None = None
    created_at: datetime
