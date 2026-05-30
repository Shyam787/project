from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.exceptions import authentication_error, authorization_error
from app.auth.jwks import JwksProvider
from app.auth.jwt_validator import JwtValidator
from app.auth.models import IdentityContext
from app.core.config import Settings, get_settings
from app.rbac.policies import Permission, has_permission

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
) -> IdentityContext:
    if credentials is None:
        raise authentication_error("Bearer token is required.")
    if credentials.scheme.lower() != "bearer":
        raise authentication_error("Bearer token is required.")
    return await validator.validate(credentials.credentials)


def require_permission(permission: Permission):
    async def dependency(
        identity: Annotated[IdentityContext, Depends(require_identity)]
    ) -> IdentityContext:
        if not has_permission(identity.roles, permission):
            raise authorization_error("Identity does not have required permission.")
        return identity

    return dependency
