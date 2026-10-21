Security
========

TokenManager
------------

Utilities for safe token handling. Encryption requires ``pip install cascade-discord[security]``.

.. code-block:: python

   from cascade.security import TokenManager

   tm = TokenManager()

   masked = tm.mask_token(token, visible_chars=4)

   user_id = tm.extract_user_id(token)

   is_valid = tm.validate_token_format(token)

   hashed = tm.hash_token(token)

   are_equal = tm.constant_time_compare(token_a, token_b)

   session_token = tm.generate_session_token()

With encryption (requires ``cryptography`` package):

.. code-block:: python

   tm = TokenManager(master_password='your_password')
   encrypted = tm.encrypt_token(token)
   recovered = tm.decrypt_token(encrypted)

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Method
     - Description
   * - ``mask_token(token, visible_chars=4)``
     - Returns ``abc.****...6789`` style masked string
   * - ``validate_token_format(token)``
     - Returns ``True`` if token has valid 3-part structure
   * - ``extract_user_id(token)``
     - Decodes the user ID from the first token segment
   * - ``hash_token(token)``
     - SHA-256 hex digest
   * - ``constant_time_compare(a, b)``
     - Timing-attack resistant comparison
   * - ``generate_session_token()``
     - Generates a random URL-safe 32-byte token
   * - ``encrypt_token(token)``
     - AES-256 via Fernet (requires ``cryptography``)
   * - ``decrypt_token(encrypted)``
     - Decrypts a Fernet-encrypted token

FingerprintRandomizer
---------------------

Generates realistic browser fingerprint values to avoid pattern detection.

.. code-block:: python

   from cascade.security import FingerprintRandomizer

   fp = FingerprintRandomizer()

   res     = fp.get_random_screen_resolution()
   tz      = fp.get_random_timezone()
   locale  = fp.get_random_locale()
   noise   = fp.generate_canvas_noise()
   delay   = fp.randomize_timing(base_delay=0.5)
   mouse   = fp.generate_mouse_movement(steps=10)
   typing  = fp.generate_typing_pattern(text_length=30)
   headers = fp.get_realistic_headers()

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Returns
   * - ``get_random_screen_resolution()``
     - ``(width, height)`` tuple from common resolutions
   * - ``get_random_timezone()``
     - Timezone string e.g. ``'America/New_York'``
   * - ``get_random_locale()``
     - Locale string e.g. ``'en-US'``
   * - ``generate_canvas_noise()``
     - SHA-256 hex string
   * - ``randomize_timing(base_delay)``
     - Float with gaussian jitter applied
   * - ``generate_mouse_movement(steps)``
     - List of ``(x, y, timestamp)`` tuples
   * - ``generate_typing_pattern(text_length)``
     - Dict with ``keystrokes``, ``wpm``, ``total_time``
   * - ``get_realistic_headers()``
     - Dict of extra browser-like headers

SmartRateLimiter
----------------

Adaptive rate limiter with human-like delays on top of the built-in bucket limiter.

.. code-block:: python

   from cascade.security import SmartRateLimiter

   limiter = SmartRateLimiter()

   await limiter.wait_if_needed('/api/channels/123/messages')

   limiter.update_bucket('/api/channels/123/messages', response_headers)

   delay = limiter.get_adaptive_delay('/api/channels/123/messages')

Delay behaviour scales with bucket usage:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Usage ratio
     - Delay range
   * - > 90%
     - 2.0 -- 4.0s
   * - > 70%
     - 1.0 -- 2.0s
   * - > 50%
     - 0.5 -- 1.0s
   * - < 50%
     - 0.1 -- 0.5s
