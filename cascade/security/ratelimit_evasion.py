import asyncio
import time
import random
from collections import defaultdict
from typing import Dict, Optional


class SmartRateLimiter:
    def __init__(self):
        self.buckets: Dict[str, Dict] = defaultdict(lambda: {
            'remaining': 0,
            'reset': 0,
            'limit': 0,
            'last_request': 0
        })
        self.global_rate_limit = False
        self.global_reset = 0
        self.request_count = 0
        self.start_time = time.time()
        
    async def wait_if_needed(self, route: str):
        await self._check_global_limit()
        await self._check_bucket_limit(route)
        await self._add_human_delay()
    
    async def _check_global_limit(self):
        if self.global_rate_limit:
            wait_time = self.global_reset - time.time()
            if wait_time > 0:
                jitter = random.uniform(0.5, 1.5)
                await asyncio.sleep(wait_time + jitter)
                self.global_rate_limit = False
    
    async def _check_bucket_limit(self, route: str):
        bucket = self.buckets[route]
        
        if bucket['remaining'] == 0 and bucket['reset'] > time.time():
            wait_time = bucket['reset'] - time.time()
            jitter = random.uniform(0.1, 0.5)
            await asyncio.sleep(wait_time + jitter)
    
    async def _add_human_delay(self):
        elapsed = time.time() - self.start_time
        requests_per_second = self.request_count / max(elapsed, 1)
        
        if requests_per_second > 10:
            await asyncio.sleep(random.uniform(0.5, 1.5))
        elif requests_per_second > 5:
            await asyncio.sleep(random.uniform(0.2, 0.8))
        else:
            await asyncio.sleep(random.uniform(0.05, 0.3))
        
        self.request_count += 1
    
    def update_bucket(self, route: str, headers: Dict):
        bucket = self.buckets[route]
        
        if 'X-RateLimit-Remaining' in headers:
            bucket['remaining'] = int(headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in headers:
            bucket['reset'] = float(headers['X-RateLimit-Reset'])
        
        if 'X-RateLimit-Limit' in headers:
            bucket['limit'] = int(headers['X-RateLimit-Limit'])
        
        bucket['last_request'] = time.time()
        
        if 'X-RateLimit-Global' in headers:
            self.global_rate_limit = True
            if 'Retry-After' in headers:
                self.global_reset = time.time() + float(headers['Retry-After'])
    
    def get_adaptive_delay(self, route: str) -> float:
        bucket = self.buckets[route]
        
        if bucket['limit'] == 0:
            return random.uniform(0.5, 1.5)
        
        usage_ratio = 1 - (bucket['remaining'] / bucket['limit'])
        
        if usage_ratio > 0.9:
            return random.uniform(2.0, 4.0)
        elif usage_ratio > 0.7:
            return random.uniform(1.0, 2.0)
        elif usage_ratio > 0.5:
            return random.uniform(0.5, 1.0)
        else:
            return random.uniform(0.1, 0.5)
