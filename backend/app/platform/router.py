from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.audit.service import list_recent_activity
from app.auth.dependencies import require_permission
from app.auth.models import IdentityContext
from app.core.config import get_settings
from app.db.dependencies import SessionDep
from app.platform.keycloak_admin import KeycloakAdminClient
from app.platform.service import (
    create_organization,
    create_tenant_user,
    disable_tenant_user,
    list_users,
)
from app.rbac.policies import Permission

router = APIRouter(tags=["platform"])


class OrganizationSignupRequest(BaseModel):
    organization_name: str = Field(min_length=3, max_length=100)
    organization_id: str = Field(min_length=2, max_length=80)
    admin_full_name: str = Field(min_length=2, max_length=120)
    admin_email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str
    confirm_password: str


class CreateUserRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    role: str


@router.post("/organizations/signup")
async def signup_organization(
    request: Request,
    body: OrganizationSignupRequest,
    session: SessionDep,
) -> dict:
    try:
        payload = await create_organization(
            session=session,
            keycloak=KeycloakAdminClient(get_settings()),
            organization_name=body.organization_name,
            organization_id=body.organization_id,
            admin_full_name=body.admin_full_name,
            admin_email=body.admin_email,
            password=body.password,
            confirm_password=body.confirm_password,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.get("/users")
async def users_index(
    request: Request,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.ADMIN_MANAGEMENT))],
) -> dict:
    try:
        payload = await list_users(session=session, identity=identity)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": {"users": payload},
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.post("/users")
async def create_user(
    request: Request,
    body: CreateUserRequest,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.ADMIN_MANAGEMENT))],
) -> dict:
    try:
        payload = await create_tenant_user(
            session=session,
            keycloak=KeycloakAdminClient(get_settings()),
            identity=identity,
            full_name=body.full_name,
            email=body.email,
            role=body.role,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.post("/users/{user_id}/disable")
async def disable_user(
    request: Request,
    user_id: str,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.ADMIN_MANAGEMENT))],
) -> dict:
    try:
        payload = await disable_tenant_user(
            session=session,
            identity=identity,
            user_id=user_id,
            request_id=getattr(request.state, "request_id", "unknown"),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": payload,
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }


@router.get("/activity")
async def recent_activity(
    request: Request,
    session: SessionDep,
    identity: Annotated[IdentityContext, Depends(require_permission(Permission.ADMIN_MANAGEMENT))],
) -> dict:
    try:
        payload = await list_recent_activity(session=session, identity=identity)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "success": True,
        "payload": {"events": payload},
        "metadata": {"request_id": getattr(request.state, "request_id", "unknown")},
        "error": None,
    }
