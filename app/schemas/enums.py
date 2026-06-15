"""Enumerations from the brief (§3.3, §3.4, §4.3)."""

from __future__ import annotations

from enum import Enum


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TicketStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"


class RequestStatus(str, Enum):
    accepted = "accepted"
    rejected = "rejected"
    processed = "processed"
    failed = "failed"
