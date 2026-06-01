from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import authentication_error, authorization_error
from app.auth.jwks import JwksProvider
from app.auth.jwt_validator import JwtValidator
from app.auth.models import IdentityContext
from app.core.config import Settings, get_settings
from app.db.dependencies import get_session
from app.db.schema import users
from app.rbac.policies import Permission, has_permission
from app.tenant.context import resolve_tenant_context

bearer_scheme = HTTPBearer(auto_error=False)


def get_jwks_provider(
    settings: Annotated[Settings, Depends(get_settings)],
) -> JwksProvider:
    return JwksProvider(settings)


def get_jwt_validator(
    settings: Annotated[Settings, Depends(get_settings)],
    jwks_provider: Annotated[JwksProvider, Depends(get_jwks_provider)],
) -> JwtValidator:
    return JwtValidator(settings, jwks_provider)


async def require_identity(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    validator: Annotated[JwtValidator, Depends(get_jwt_validator)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> IdentityContext:
    if credentials is None:
        raise authentication_error("Bearer token is required.")
    if credentials.scheme.lower() != "bearer":
        raise authentication_error("Bearer token is required.")
    identity = await validator.validate(credentials.credentials)
    if identity.tenant.tenant_id != "__unresolved__":
        try:
            row = (
                await session.execute(
                    select(users.c.is_active, users.c.display_name).where(
                        users.c.tenant_id == identity.tenant.tenant_id,
                        (
                            (users.c.external_subject == identity.user_id)
                            | (users.c.id == identity.user_id)
                            | (users.c.email == (identity.email or ""))
                        ),
                    )
                )
            ).first()
            if row is not None and not row.is_active:
                raise authentication_error("Your account is inactive. Contact your organization administrator to regain access.")
            if row is not None:
                identity.full_name = row.display_name
        except HTTPException:
            raise
        except (SQLAlchemyError, OSError):
            pass
        return identity
    row = (
        await session.execute(
            select(users.c.tenant_id, users.c.is_active, users.c.display_name).where(
                (users.c.external_subject == identity.user_id)
                | (users.c.id == identity.user_id)
                | (users.c.email == (identity.email or ""))
            )
        )
    ).first()
    if row is None:
        raise authentication_error("Token does not contain a tenant identity.")
    if not row.is_active:
        raise authentication_error("Your account is inactive. Contact your organization administrator to regain access.")
    return IdentityContext(
        user_id=identity.user_id,
        email=identity.email,
        full_name=row.display_name,
        tenant=resolve_tenant_context(row.tenant_id),
        roles=identity.roles,
        permissions=identity.permissions,
    )


def require_permission(permission: Permission):
    async def dependency(
        identity: Annotated[IdentityContext, Depends(require_identity)]
    ) -> IdentityContext:
        if not has_permission(identity.roles, permission):
            raise authorization_error("Identity does not have required permission.")
        return identity

    return dependency
