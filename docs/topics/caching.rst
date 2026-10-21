Caching
=======

cascade provides an advanced caching system with multiple strategies.

Basic Usage
-----------

The default cache is used internally by the session:

.. code-block:: python

   guild = session.get_guild(guild_id)
   channel = session.get_channel(channel_id)
   user = session.get_user(user_id)

Advanced Cache
--------------

For custom use cases, use :class:`~cascade.core.advanced_cache.AdvancedCache` directly:

.. code-block:: python

   from cascade.core.advanced_cache import AdvancedCache, CacheStrategy

   cache = AdvancedCache(
       max_size=1000,
       ttl=300,
       strategy=CacheStrategy.LRU
   )

   cache.set('key', value)
   data = cache.get('key', default=None)
   cache.delete('key')

   stats = cache.get_stats()

Strategies
----------

- ``LRU`` - evicts the least recently used entry
- ``LFU`` - evicts the least frequently used entry
- ``FIFO`` - evicts the oldest entry
- ``TTL`` - evicts expired entries on access

Layered Cache
-------------

:class:`~cascade.core.advanced_cache.LayeredCache` provides a 3-tier cache that promotes hot entries automatically:

.. code-block:: python

   from cascade.core.advanced_cache import LayeredCache

   cache = LayeredCache()
   cache.set('user:123', user_data)
   data = cache.get('user:123')
   stats = cache.get_stats()
