import asyncio

import pytest
from fastapi import HTTPException

from app.chat.router import _enforce_chat_rate_limit


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int] = {}
        self.expiry: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    async def expire(self, key: str, seconds: int) -> None:
        self.expiry[key] = seconds

    async def ttl(self, key: str) -> int:
        return self.expiry.get(key, 0)


def test_chat_rate_limit_blocks_after_configured_quota():
    async def run() -> None:
        cache = FakeRedis()

        await _enforce_chat_rate_limit(
            cache_client=cache,
            tenant_id="tenant-a",
            user_id="user-a",
            limit=2,
            window_seconds=60,
        )
        await _enforce_chat_rate_limit(
            cache_client=cache,
            tenant_id="tenant-a",
            user_id="user-a",
            limit=2,
            window_seconds=60,
        )

        with pytest.raises(HTTPException) as exc:
            await _enforce_chat_rate_limit(
                cache_client=cache,
                tenant_id="tenant-a",
                user_id="user-a",
                limit=2,
                window_seconds=60,
            )

        assert exc.value.status_code == 429
        assert exc.value.detail["code"] == "CHAT_RATE_LIMIT_EXCEEDED"

    asyncio.run(run())


def test_chat_rate_limit_can_be_disabled():
    async def run() -> None:
        cache = FakeRedis()

        await _enforce_chat_rate_limit(
            cache_client=cache,
            tenant_id="tenant-a",
            user_id="user-a",
            limit=0,
            window_seconds=60,
        )

        assert cache.values == {}

    asyncio.run(run())
