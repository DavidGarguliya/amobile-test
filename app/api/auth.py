"""Auth router: login, current user, admin-only user management (ADR-009)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User
from app.schemas.auth import LoginIn, TokenOut, UserCreate, UserOut
from app.services import auth as service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = service.authenticate(db, str(payload.email), payload.password)
    return TokenOut(access_token=service.issue_token(user), role=user.role)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return user


@router.post("/users", response_model=UserOut, status_code=201, dependencies=[Depends(require_roles("admin"))])
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    return service.create_user(db, email=str(payload.email), password=payload.password, role=payload.role.value)
