import asyncio

import pytest

from src.cache import AsyncTTLCache


@pytest.mark.asyncio
async def test_cache_coalesces_requests_and_releases_key_lock():
    cache: AsyncTTLCache[int] = AsyncTTLCache(ttl=60, stale_ttl=60)
    calls = 0

    async def loader() -> int:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0)
        return 42

    results = await asyncio.gather(*(cache.get_or_set("same", loader) for _ in range(10)))

    assert results == [42] * 10
    assert calls == 1
    assert cache._locks == {}

