import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Awaitable, Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class CacheEntry(Generic[T]):
    value: T
    fresh_until: float
    stale_until: float


@dataclass(slots=True)
class LockEntry:
    lock: asyncio.Lock
    users: int = 0


class AsyncTTLCache(Generic[T]):
    """Small process-local cache with per-key request coalescing."""

    def __init__(self, ttl: int, stale_ttl: int, max_size: int = 512):
        self.ttl = ttl
        self.stale_ttl = stale_ttl
        self.max_size = max_size
        self._items: dict[str, CacheEntry[T]] = {}
        self._locks: dict[str, LockEntry] = {}
        self._locks_guard = asyncio.Lock()

    @asynccontextmanager
    async def _key_lock(self, key: str) -> AsyncIterator[None]:
        async with self._locks_guard:
            slot = self._locks.setdefault(key, LockEntry(asyncio.Lock()))
            slot.users += 1
        try:
            async with slot.lock:
                yield
        finally:
            async with self._locks_guard:
                slot.users -= 1
                if slot.users == 0 and self._locks.get(key) is slot:
                    self._locks.pop(key, None)

    async def get_or_set(self, key: str, loader: Callable[[], Awaitable[T]]) -> T:
        now = time.monotonic()
        entry = self._items.get(key)
        if entry and entry.fresh_until > now:
            return entry.value

        async with self._key_lock(key):
            now = time.monotonic()
            entry = self._items.get(key)
            if entry and entry.fresh_until > now:
                return entry.value
            try:
                value = await loader()
            except Exception:
                if entry and entry.stale_until > now:
                    return entry.value
                raise
            self._items[key] = CacheEntry(
                value=value,
                fresh_until=now + self.ttl,
                stale_until=now + self.ttl + self.stale_ttl,
            )
            if len(self._items) > self.max_size:
                oldest = min(self._items, key=lambda k: self._items[k].stale_until)
                self._items.pop(oldest, None)
            return value
