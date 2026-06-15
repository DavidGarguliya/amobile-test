"""Auth business logic: authentication, user creation, token issuance (ADR-009)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.auth import create_access_token, hash_password, verify_password
from app.core.config import settings
from app.core.errors import conflict, unauthorized
from app.models.user import User
from app.repositories import users as repo


def authenticate(db: Session, email: str, password: str) -> User:
    user = repo.get_by_email(db, email)
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        raise unauthorized("Invalid email or password")
    return user


def create_user(db: Session, *, email: str, password: str, role: str) -> User:
    if repo.get_by_email(db, email):
        raise conflict("User with this email already exists", field="email")
    return repo.create(db, email=email, password_hash=hash_password(password), role=role)


def issue_token(user: User) -> str:
    return create_access_token(subject=str(user.id), role=user.role)


def seed_admin(db: Session) -> None:
    """Create the bootstrap admin user if it does not exist (idempotent)."""
    if repo.get_by_email(db, settings.admin_email) is None:
        repo.create(
            db,
            email=settings.admin_email,
            password_hash=hash_password(settings.admin_password),
            role="admin",
        )
