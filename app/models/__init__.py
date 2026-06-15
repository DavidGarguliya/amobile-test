"""ORM models registry — importing this package registers all tables on ``Base.metadata``."""

from app.models.api_client import ApiClient
from app.models.api_key import ApiKey
from app.models.audit_log import AuditLog
from app.models.employee import Employee
from app.models.external_identity import ExternalIdentity
from app.models.integration_request import IntegrationRequest
from app.models.ticket import Ticket
from app.models.user import User

__all__ = [
    "ApiClient",
    "ApiKey",
    "AuditLog",
    "Employee",
    "ExternalIdentity",
    "IntegrationRequest",
    "Ticket",
    "User",
]
