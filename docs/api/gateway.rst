Gateway
=======

The gateway shard manages the WebSocket connection to Discord. You normally never interact with it directly -- use ``session.change_presence()``, ``session.update_voice_state()``, and ``@session.event`` instead. It is available as ``session.gateway`` after ``start()`` is called.

Connection
----------

The shard connects automatically when you call ``await session.start()``. It handles:

- HELLO / IDENTIFY / RESUME handshake
- Heartbeat with jitter
- Auto-reconnect with exponential backoff
- INVALID_SESSION and RECONNECT op handling
- Zombie connection detection

Dispatched Events
-----------------

The gateway dispatches the following events. See :doc:`/topics/events` for the full event reference with parameter types.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Event
     - Trigger
   * - ``on_ready``
     - READY received, session established
   * - ``on_resumed``
     - RESUMED after reconnect
   * - ``on_message``
     - MESSAGE_CREATE (excluding own messages)
   * - ``on_message_edit``
     - MESSAGE_UPDATE
   * - ``on_message_delete``
     - MESSAGE_DELETE
   * - ``on_guild_join``
     - GUILD_CREATE
   * - ``on_guild_remove``
     - GUILD_DELETE
   * - ``on_channel_create``
     - CHANNEL_CREATE
   * - ``on_channel_update``
     - CHANNEL_UPDATE
   * - ``on_channel_delete``
     - CHANNEL_DELETE
   * - ``on_typing``
     - TYPING_START
   * - ``on_presence_update``
     - PRESENCE_UPDATE
   * - ``on_user_update``
     - USER_UPDATE
   * - ``on_relationship_add``
     - RELATIONSHIP_ADD
   * - ``on_relationship_remove``
     - RELATIONSHIP_REMOVE

Latency
-------

.. code-block:: python

   print(f'{session.latency * 1000:.0f}ms')

This is the heartbeat round-trip time in seconds. Returns ``float('inf')`` before the first heartbeat ACK.

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``session_id``
     - Active session ID (used for resume)
   * - ``sequence``
     - Last sequence number received
   * - ``resume_url``
     - Resume gateway URL from READY
   * - ``heartbeat.latency``
     - Heartbeat round-trip in seconds
