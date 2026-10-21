import time
from typing import Optional, Dict, Any, Callable, TypeVar, Generic
from collections import OrderedDict
from enum import Enum


T = TypeVar('T')


class CacheStrategy(Enum):
    LRU = 'lru'
    LFU = 'lfu'
    TTL = 'ttl'
    FIFO = 'fifo'


class CacheEntry(Generic[T]):
    def __init__(self, value: T, ttl: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
        self.ttl = ttl

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def access(self):
        self.last_accessed = time.time()
        self.access_count += 1


class AdvancedCache(Generic[T]):
    def __init__(
        self,
        max_size: int = 1000,
        ttl: Optional[int] = None,
        strategy: CacheStrategy = CacheStrategy.LRU,
        on_evict: Optional[Callable[[Any, T], None]] = None
    ):
        self.max_size = max_size
        self.ttl = ttl
        self.strategy = strategy
        self.on_evict = on_evict
        self._cache: OrderedDict[Any, CacheEntry[T]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: Any, default: Optional[T] = None) -> Optional[T]:
        if key not in self._cache:
            self._misses += 1
            return default

        entry = self._cache[key]
        
        if entry.is_expired():
            self._evict(key)
            self._misses += 1
            return default

        entry.access()
        self._hits += 1

        if self.strategy == CacheStrategy.LRU:
            self._cache.move_to_end(key)

        return entry.value

    def set(self, key: Any, value: T, ttl: Optional[int] = None):
        if key in self._cache:
            entry = self._cache[key]
            entry.value = value
            entry.created_at = time.time()
            if ttl is not None:
                entry.ttl = ttl
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)
            return

        if len(self._cache) >= self.max_size:
            self._evict_one()

        entry_ttl = ttl if ttl is not None else self.ttl
        self._cache[key] = CacheEntry(value, entry_ttl)

    def delete(self, key: Any) -> bool:
        if key in self._cache:
            self._evict(key)
            return True
        return False

    def clear(self):
        keys = list(self._cache.keys())
        for key in keys:
            self._evict(key)

    def _evict(self, key: Any):
        entry = self._cache.pop(key)
        if self.on_evict:
            self.on_evict(key, entry.value)

    def _evict_one(self):
        if not self._cache:
            return

        if self.strategy == CacheStrategy.LRU:
            key = next(iter(self._cache))
        elif self.strategy == CacheStrategy.LFU:
            key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
        elif self.strategy == CacheStrategy.FIFO:
            key = next(iter(self._cache))
        else:
            key = next(iter(self._cache))

        self._evict(key)

    def cleanup_expired(self):
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            self._evict(key)

    def get_stats(self) -> Dict[str, Any]:
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': hit_rate,
            'strategy': self.strategy.value
        }

    def __contains__(self, key: Any) -> bool:
        return key in self._cache and not self._cache[key].is_expired()

    def __len__(self) -> int:
        return len(self._cache)


class LayeredCache:
    def __init__(self):
        self.l1 = AdvancedCache(max_size=100, ttl=60, strategy=CacheStrategy.LRU)
        self.l2 = AdvancedCache(max_size=1000, ttl=300, strategy=CacheStrategy.LFU)
        self.l3 = AdvancedCache(max_size=10000, ttl=3600, strategy=CacheStrategy.FIFO)

    def get(self, key: Any) -> Optional[Any]:
        value = self.l1.get(key)
        if value is not None:
            return value

        value = self.l2.get(key)
        if value is not None:
            self.l1.set(key, value)
            return value

        value = self.l3.get(key)
        if value is not None:
            self.l2.set(key, value)
            self.l1.set(key, value)
            return value

        return None

    def set(self, key: Any, value: Any):
        self.l1.set(key, value)
        self.l2.set(key, value)
        self.l3.set(key, value)

    def delete(self, key: Any):
        self.l1.delete(key)
        self.l2.delete(key)
        self.l3.delete(key)

    def clear(self):
        self.l1.clear()
        self.l2.clear()
        self.l3.clear()

    def get_stats(self) -> Dict[str, Any]:
        return {
            'l1': self.l1.get_stats(),
            'l2': self.l2.get_stats(),
            'l3': self.l3.get_stats()
        }
