import json
from typing import Any

import jwt
from jwt import InvalidTokenError
from jwt.algorithms import RSAAlgorithm

from app.auth.exceptions import authentication_error
from app.auth.jwks import JwksProvider
from app.auth.models import IdentityContext
from app.core.config import Settings
from app.rbac.policies import permissions_for_roles
from app.tenant.context import resolve_tenant_context


class JwtValidator:
    def __init__(self, settings: Settings, jwks_provider: JwksProvider) -> None:
        self._settings = settings
        self._jwks_provider = jwks_provider

    async def validate(self, token: str) -> IdentityContext:
        try:
            unverified_header = jwt.get_unverified_header(token)
        except InvalidTokenError as exc:
            raise authentication_error("Malformed bearer token.") from exc

        jwks = await self._jwks_provider.get_jwks()
        key = self._find_key(jwks, unverified_header.get("kid"))
        if key is None:
            raise authentication_error("Token signing key is not trusted.")

        try:
            public_key = RSAAlgorithm.from_jwk(json.dumps(key))
            claims = jwt.decode(
                token,
                public_key,
                algorithms=[self._settings.auth_algorithm],
                audience=self._settings.keycloak_audience,
                issuer=self._settings.keycloak_issuer_url,
            )
        except InvalidTokenError as exc:
            raise authentication_error("Bearer token validation failed.") from exc

        return self._identity_from_claims(claims)

    @staticmethod
    def _find_key(jwks: dict, kid: str | None) -> dict | None:
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        return None

    def _identity_from_claims(self, claims: dict[str, Any]) -> IdentityContext:
        user_id = claims.get("user_id") or claims.get("sub")
        tenant_id = claims.get("tenant_id")
        roles = self._extract_roles(claims)

        if not user_id:
            raise authentication_error("Token does not contain a user identity.")
        if not tenant_id and self._settings.auth_jwks_json:
            raise authentication_error("Token does not contain a tenant identity.")
        if not roles:
            raise authentication_error("Token does not contain RBAC roles.")

        return IdentityContext(
            user_id=user_id,
            email=claims.get("email") or claims.get("preferred_username"),
            tenant=resolve_tenant_context(tenant_id or "__unresolved__"),
            roles=roles,
            permissions=permissions_for_roles(roles),
        )

    def _extract_roles(self, claims: dict[str, Any]) -> set[str]:
        roles = set(claims.get("roles", []))
        roles.update(claims.get("realm_access", {}).get("roles", []))
        resource_access = claims.get("resource_access", {})
        audience_access = resource_access.get(self._settings.keycloak_audience, {})
        roles.update(audience_access.get("roles", []))
        return roles
