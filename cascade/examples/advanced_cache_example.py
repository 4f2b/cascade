import asyncio
import cascade
from cascade.core.advanced_cache import AdvancedCache, LayeredCache, CacheStrategy


async def main():
    lru_cache = AdvancedCache(
        max_size=100,
        ttl=300,
        strategy=CacheStrategy.LRU
    )
    
    lru_cache.set('user:123', {'id': 123, 'name': 'John'})
    lru_cache.set('user:456', {'id': 456, 'name': 'Jane'})
    
    user = lru_cache.get('user:123')
    print(f'Retrieved user: {user}')
    
    lru_cache.set('temp:data', 'value', ttl=60)
    
    stats = lru_cache.get_stats()
    print(f'Cache stats: {stats}')
    
    lfu_cache = AdvancedCache(
        max_size=500,
        strategy=CacheStrategy.LFU,
        on_evict=lambda k, v: print(f'Evicted {k}')
    )
    
    for i in range(10):
        lfu_cache.set(f'item:{i}', {'data': i})
    
    for _ in range(5):
        lfu_cache.get('item:0')
    
    layered = LayeredCache()
    
    layered.set('hot:data', 'frequently accessed')
    layered.set('warm:data', 'occasionally accessed')
    layered.set('cold:data', 'rarely accessed')
    
    value = layered.get('hot:data')
    print(f'Layered cache value: {value}')
    
    all_stats = layered.get_stats()
    print(f'L1 Cache: {all_stats["l1"]}')
    print(f'L2 Cache: {all_stats["l2"]}')
    print(f'L3 Cache: {all_stats["l3"]}')
    
    session = cascade.Session(token)
    
    guild_cache = AdvancedCache(max_size=1000, ttl=3600)
    
    @session.event
    async def on_ready(user):
        print(f'Connected as {user.username}')
        
        guilds = await session.rest.get_guilds()
        for guild in guilds:
            guild_cache.set(f'guild:{guild["id"]}', guild)
        
        guild_cache.cleanup_expired()
    
    await session.start()


if __name__ == '__main__':
    asyncio.run(main())
