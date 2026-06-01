from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import require_identity
from app.auth.models import IdentityContext

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def current_user(
    request: Request,
    identity: Annotated[IdentityContext, Depends(require_identity)],
) -> dict:
    return {
        "success": True,
        "payload": {
            "user_id": identity.user_id,
            "display_name": identity.full_name,
            "email": identity.email,
            "tenant_id": identity.tenant.tenant_id,
            "tenant_namespace": identity.tenant.namespace,
            "roles": sorted(identity.roles),
            "permissions": sorted(identity.permissions),
        },
        "metadata": {
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
        "error": None,
    }
