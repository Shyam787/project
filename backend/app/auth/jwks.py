import json
from time import monotonic

import httpx

from app.core.config import Settings


class JwksProvider:
    def __init__(self, settings: Settings, cache_seconds: int = 300) -> None:
        self._settings = settings
        self._cache_seconds = cache_seconds
        self._cached_jwks: dict | None = None
        self._cached_at = 0.0

    async def get_jwks(self) -> dict:
        if self._settings.auth_jwks_json:
            return json.loads(self._settings.auth_jwks_json)

        now = monotonic()
        if self._cached_jwks and now - self._cached_at < self._cache_seconds:
            return self._cached_jwks

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(self._settings.keycloak_jwks_url)
            response.raise_for_status()
            self._cached_jwks = response.json()
            self._cached_at = now
            return self._cached_jwks
