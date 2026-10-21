Rate Limits
===========

cascade handles Discord's rate limits automatically at the REST layer.

Built-in Handling
-----------------

The :class:`~cascade.api.rest.RestClient` tracks per-route buckets and waits automatically when a bucket is exhausted. You do not need to handle 429s yourself.

Smart Rate Limiter
------------------

For additional evasion, use :class:`~cascade.security.ratelimit_evasion.SmartRateLimiter`:

.. code-block:: python

   from cascade.security import SmartRateLimiter

   limiter = SmartRateLimiter()

   await limiter.wait_if_needed('/api/channels/123/messages')

   limiter.update_bucket('/api/channels/123/messages', response.headers)

   delay = limiter.get_adaptive_delay('/api/channels/123/messages')

The smart limiter adds human-like jitter and adaptive delays based on bucket usage ratio to reduce detection risk.
