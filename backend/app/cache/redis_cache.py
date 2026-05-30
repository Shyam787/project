import hashlib
import json
from collections.abc import Mapping
from typing import Any

import redis.asyncio as redis

from app.auth.models import IdentityContext
from app.core.config import Settings

QUERY_RESPONSE_TTL_SECONDS = 600


def create_redis_client(settings: Settings) -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def rbac_fingerprint(identity: IdentityContext) -> str:
    payload = {
        "tenant_id": identity.tenant.tenant_id,
        "roles": sorted(identity.roles),
        "permissions": sorted(identity.permissions),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def tenant_cache_key(
    *,
    identity: IdentityContext,
    category: str,
    parts: Mapping[str, Any],
) -> str:
    encoded_parts = json.dumps(parts, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded_parts.encode("utf-8")).hexdigest()
    return (
        f"tenant:{identity.tenant.tenant_id}:"
        f"rbac:{rbac_fingerprint(identity)}:"
        f"{category}:{digest}"
    )
