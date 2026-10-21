Event Reference
===============

Register event handlers with the ``@session.event`` decorator or on a ``Bot`` instance:

.. code-block:: python

   @session.event
   async def on_ready(user):
       print(f'Connected as {user.username}')

All event names must start with ``on_``.

on_ready
--------

Called when the READY payload is received and the session is established.

.. code-block:: python

   @session.event
   async def on_ready(user):
       ...

:param user: :class:`~cascade.entities.user.ClientUser`

on_resumed
----------

Called after a successful RESUME (reconnect without full re-identify).

.. code-block:: python

   @session.event
   async def on_resumed():
       ...

on_message
----------

Called when a message is created in any visible channel. Own messages are excluded.

.. code-block:: python

   @session.event
   async def on_message(message):
       if message.content == '!ping':
           await session.rest.send_message(message.channel_id, 'Pong!')

:param message: :class:`~cascade.entities.message.Message`

on_message_edit
---------------

Called when a visible message is edited.

.. code-block:: python

   @session.event
   async def on_message_edit(before, after):
       print(before.content, '->', after.content)

:param before: :class:`~cascade.entities.message.Message` (cached, may be ``None``)
:param after: :class:`~cascade.entities.message.Message`

on_message_delete
-----------------

Called when a visible message is deleted.

.. code-block:: python

   @session.event
   async def on_message_delete(message):
       ...

:param message: :class:`~cascade.entities.message.Message` (cached, may be ``None``)

on_guild_join
-------------

Called when GUILD_CREATE is dispatched (initial load and actual join).

.. code-block:: python

   @session.event
   async def on_guild_join(guild):
       print(f'In guild: {guild.name}')

:param guild: :class:`~cascade.entities.guild.Guild`

on_guild_remove
---------------

Called when the user leaves or is removed from a guild.

.. code-block:: python

   @session.event
   async def on_guild_remove(guild):
       ...

:param guild: :class:`~cascade.entities.guild.Guild` (cached, may be ``None``)

on_channel_create
-----------------

:param channel: :class:`~cascade.entities.channel.Channel`

on_channel_update
-----------------

:param channel: :class:`~cascade.entities.channel.Channel`

on_channel_delete
-----------------

:param channel: :class:`~cascade.entities.channel.Channel`

on_typing
---------

Called when a user starts typing.

.. code-block:: python

   @session.event
   async def on_typing(channel, user, timestamp):
       ...

:param channel: Cached channel or ``None``
:param user: Cached :class:`~cascade.entities.user.User` or ``None``
:param timestamp: Unix timestamp integer

on_presence_update
------------------

Called when any visible user's presence changes.

.. code-block:: python

   @session.event
   async def on_presence_update(data):
       print(data['user']['id'], data.get('status'))

:param data: Raw presence update dict

on_user_update
--------------

Called when the logged-in user's account data changes.

.. code-block:: python

   @session.event
   async def on_user_update(data):
       ...

:param data: Raw user dict

on_relationship_add
-------------------

Called when a relationship is added (friend request sent/received, user blocked).

.. code-block:: python

   @session.event
   async def on_relationship_add(data):
       print(data['type'], data['user']['username'])

:param data: Raw relationship dict

on_relationship_remove
----------------------

Called when a relationship is removed.

.. code-block:: python

   @session.event
   async def on_relationship_remove(data):
       ...

:param data: Raw relationship dict

wait_for
--------

Wait for a specific event that satisfies a condition:

.. code-block:: python

   msg = await session.wait_for(
       'on_message',
       check=lambda m: m.author.id == target_id and m.channel_id == channel_id,
       timeout=60.0,
   )

Raises ``asyncio.TimeoutError`` if timeout expires without a matching event.
