Session
=======

The :class:`~cascade.core.session.Session` is the main entry point. It holds the REST client, gateway shard, cache, and event dispatcher.

.. code-block:: python

   import asyncio
   import cascade

   async def main():
       session = cascade.Session(token, platform='desktop')

       @session.event
       async def on_ready(user):
           print(f'Logged in as {user.username}')

       await session.start()

   asyncio.run(main())

Constructor
-----------

.. code-block:: python

   session = cascade.Session(
       token,
       message_cache_limit=1000,
       platform='desktop'
   )

- **token** -- your Discord user token
- **message_cache_limit** -- max messages kept in the cache (default ``1000``)
- **platform** -- initial platform preset for device spoofing (default ``'desktop'``)

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Attribute
     - Description
   * - ``session.user``
     - :class:`~cascade.entities.user.ClientUser` after ``on_ready``
   * - ``session.rest``
     - :class:`~cascade.api.rest.RestClient` for raw API calls
   * - ``session.gateway``
     - :class:`~cascade.gateway.shard.GatewayShard` (available after ``start()``)
   * - ``session.cache``
     - :class:`~cascade.core.cache.Cache` -- guilds, channels, users, messages
   * - ``session.guilds``
     - list of cached :class:`~cascade.entities.guild.Guild` objects
   * - ``session.users``
     - list of cached :class:`~cascade.entities.user.User` objects
   * - ``session.latency``
     - gateway heartbeat latency in seconds (``float('inf')`` before ready)
   * - ``session.platform``
     - current platform preset string

Methods
-------

Lifecycle
~~~~~~~~~

.. code-block:: python

   await session.start()

   await session.close()

Registering Events
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @session.event
   async def on_ready(user):
       ...

   @session.event
   async def on_message(message):
       ...

Waiting for Events
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   msg = await session.wait_for(
       'on_message',
       check=lambda m: m.author.id == target_id,
       timeout=30.0
   )

Raises ``asyncio.TimeoutError`` if the timeout expires.

Cache Lookups
~~~~~~~~~~~~~

.. code-block:: python

   guild = session.get_guild(guild_id)
   channel = session.get_channel(channel_id)
   user = session.get_user(user_id)

Returns ``None`` if not cached.

Presence
~~~~~~~~

.. code-block:: python

   await session.change_presence(status='dnd', activity=activity, afk=False)

- **status** -- ``'online'``, ``'idle'``, ``'dnd'``, ``'invisible'``
- **activity** -- an :class:`~cascade.entities.presence.Activity` instance
- **afk** -- mark as AFK

Voice
~~~~~

.. code-block:: python

   await session.update_voice_state(
       guild_id,
       channel_id=channel_id,
       self_mute=False,
       self_deaf=False
   )

Pass ``channel_id=None`` to disconnect from voice.

Guild Members
~~~~~~~~~~~~~

.. code-block:: python

   await session.request_guild_members(
       guild_id,
       query='',
       limit=0,
       presences=True,
       user_ids=[user_id1, user_id2],
       nonce='optional_nonce'
   )

Platform Spoofing
~~~~~~~~~~~~~~~~~

.. code-block:: python

   session.set_platform('mobile')

   info = session.get_platform_info()

   platforms = cascade.Session.list_platforms()

Relationships
~~~~~~~~~~~~~

.. code-block:: python

   relationships = await session.fetch_relationships()

   friends = await session.fetch_friends()

   blocked = await session.fetch_blocked()

   await session.send_friend_request('username')

Applications & Teams
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   apps = await session.fetch_my_applications()

   app = await session.fetch_application(application_id)

   teams = await session.fetch_teams()

   team = await session.create_team('My Team')

   team = await session.fetch_team(team_id)
