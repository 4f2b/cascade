import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict


class RateLimitBucket:
    def __init__(self):
        self.remaining: int = 1
        self.limit: int = 1
        self.reset_after: float = 0.0
        self.reset: float = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.time()
            
            if self.remaining == 0:
                wait_time = self.reset - now
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    self.remaining = self.limit
            
            self.remaining -= 1

    def update(self, headers: Dict[str, str]) -> None:
        self.limit = int(headers.get('X-RateLimit-Limit', 1))
        self.remaining = int(headers.get('X-RateLimit-Remaining', 1))
        self.reset = float(headers.get('X-RateLimit-Reset', 0))
        reset_after = headers.get('X-RateLimit-Reset-After')
        if reset_after:
            self.reset_after = float(reset_after)


class RateLimiter:
    def __init__(self):
        self.buckets: Dict[str, RateLimitBucket] = defaultdict(RateLimitBucket)
        self.global_lock = asyncio.Lock()
        self.global_reset: float = 0.0

    def get_bucket(self, route: str, method: str) -> RateLimitBucket:
        key = f'{method}:{route}'
        return self.buckets[key]

    async def acquire(self, route: str, method: str) -> None:
        if self.global_reset > 0:
            now = time.time()
            if now < self.global_reset:
                await asyncio.sleep(self.global_reset - now)
            self.global_reset = 0.0

        bucket = self.get_bucket(route, method)
        await bucket.acquire()

    def update_bucket(self, route: str, method: str, headers: Dict[str, str]) -> None:
        bucket = self.get_bucket(route, method)
        bucket.update(headers)

        if headers.get('X-RateLimit-Global'):
            retry_after = float(headers.get('Retry-After', 0))
            self.global_reset = time.time() + retry_after
