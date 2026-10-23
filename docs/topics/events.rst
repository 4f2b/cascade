Event Reference
===============

Register event handlers using the ``@session.event`` decorator:

.. code-block:: python

   @session.event
   async def on_ready(user):
       print(f'Connected as {user.username}')

All handler names must start with ``on_``. You can also use :meth:`~cascade.core.session.Session.wait_for` to wait for a one-off event inline.

.. code-block:: python

   msg = await session.wait_for(
       'on_message',
       check=lambda m: m.channel_id == '123' and 'hello' in m.content,
       timeout=30.0,
   )

Raises :exc:`asyncio.TimeoutError` if the timeout expires before a matching event fires.

----

Connection Events
-----------------

on_ready
~~~~~~~~

Fired once when the READY payload arrives and the session is fully established. Guilds are cached and ``session.user`` is populated before this fires.

.. code-block:: python

   @session.event
   async def on_ready(user):
       print(f'Logged in as {user.username}')
       print(f'In {len(session.guilds)} guilds')

:param user: :class:`~cascade.entities.user.ClientUser`

on_resumed
~~~~~~~~~~

Fired after a successful RESUME — the connection was re-established without a full re-identify. The session sequence and session ID were preserved.

.. code-block:: python

   @session.event
   async def on_resumed():
       print('Reconnected (resumed)')

----

Message Events
--------------

on_message
~~~~~~~~~~

Fired when a message is created in any visible channel or DM. The user's own messages are excluded — use ``on_message_sent`` patterns or listen to the REST response instead.

.. code-block:: python

   @session.event
   async def on_message(message):
       if message.content.startswith('!ping'):
           await session.rest.send_message(message.channel_id, 'Pong!')

:param message: :class:`~cascade.entities.message.Message`

on_message_edit
~~~~~~~~~~~~~~~

Fired when a visible message is edited.

.. code-block:: python

   @session.event
   async def on_message_edit(before, after):
       if before:
           print(f'Edited: {before.content!r} -> {after.content!r}')

:param before: :class:`~cascade.entities.message.Message` — cached version before the edit, may be ``None`` if not cached
:param after: :class:`~cascade.entities.message.Message` — updated message

on_message_delete
~~~~~~~~~~~~~~~~~

Fired when a visible message is deleted.

.. code-block:: python

   @session.event
   async def on_message_delete(message):
       if message:
           print(f'Deleted: {message.content!r}')

:param message: :class:`~cascade.entities.message.Message` — cached message, may be ``None`` if not cached

----

Reaction Events
---------------

on_reaction_add
~~~~~~~~~~~~~~~

Fired when a reaction is added to a message.

.. code-block:: python

   @session.event
   async def on_reaction_add(reaction):
       print(f'{reaction.user_id} reacted {reaction.emoji} on {reaction.message_id}')

:param reaction: :class:`~cascade.entities.reaction.Reaction`

on_reaction_remove
~~~~~~~~~~~~~~~~~~

Fired when a specific reaction is removed from a message.

.. code-block:: python

   @session.event
   async def on_reaction_remove(reaction):
       ...

:param reaction: :class:`~cascade.entities.reaction.Reaction`

on_reaction_clear
~~~~~~~~~~~~~~~~~

Fired when all reactions are removed from a message at once.

.. code-block:: python

   @session.event
   async def on_reaction_clear(message_id, channel_id, guild_id):
       print(f'All reactions cleared on message {message_id}')

:param message_id: Message ID string
:param channel_id: Channel ID string
:param guild_id: Guild ID string or ``None`` for DMs

on_reaction_remove_emoji
~~~~~~~~~~~~~~~~~~~~~~~~

Fired when all reactions for a specific emoji are removed from a message.

.. code-block:: python

   @session.event
   async def on_reaction_remove_emoji(message_id, channel_id, emoji):
       print(f'{emoji} reactions cleared on {message_id}')

:param message_id: Message ID string
:param channel_id: Channel ID string
:param emoji: :class:`~cascade.entities.reaction.ReactionEmoji`

----

Guild Events
------------

on_guild_join
~~~~~~~~~~~~~

Fired when the user joins a new guild.

.. code-block:: python

   @session.event
   async def on_guild_join(guild):
       print(f'Joined: {guild.name}')

:param guild: :class:`~cascade.entities.guild.Guild`

on_guild_available
~~~~~~~~~~~~~~~~~~

Fired when a guild that was marked unavailable in the READY payload becomes fully available. This is distinct from ``on_guild_join`` which fires for actual new joins.

.. code-block:: python

   @session.event
   async def on_guild_available(guild):
       print(f'Available: {guild.name}')

:param guild: :class:`~cascade.entities.guild.Guild`

on_guild_update
~~~~~~~~~~~~~~~

Fired when a guild's settings change (name, icon, features, etc.).

.. code-block:: python

   @session.event
   async def on_guild_update(guild):
       ...

:param guild: :class:`~cascade.entities.guild.Guild`

on_guild_remove
~~~~~~~~~~~~~~~

Fired when the user leaves, is kicked from, or is banned from a guild.

.. code-block:: python

   @session.event
   async def on_guild_remove(guild):
       if guild:
           print(f'Left: {guild.name}')

:param guild: :class:`~cascade.entities.guild.Guild` — cached guild, may be ``None``

on_ban_add
~~~~~~~~~~

Fired when a user is banned from a guild.

.. code-block:: python

   @session.event
   async def on_ban_add(ban):
       print(f'{ban.username} was banned from guild {ban.guild_id}')

:param ban: :class:`~cascade.entities.ban.Ban`

on_ban_remove
~~~~~~~~~~~~~

Fired when a user's ban is revoked.

.. code-block:: python

   @session.event
   async def on_ban_remove(ban):
       print(f'{ban.username} was unbanned from guild {ban.guild_id}')

:param ban: :class:`~cascade.entities.ban.Ban`

on_emojis_update
~~~~~~~~~~~~~~~~

Fired when a guild's emoji list changes.

.. code-block:: python

   @session.event
   async def on_emojis_update(guild_id, emojis):
       print(f'{guild_id} now has {len(emojis)} emojis')

:param guild_id: Guild ID string
:param emojis: List of raw emoji dicts

on_stickers_update
~~~~~~~~~~~~~~~~~~

Fired when a guild's sticker list changes.

.. code-block:: python

   @session.event
   async def on_stickers_update(guild_id, stickers):
       ...

:param guild_id: Guild ID string
:param stickers: List of raw sticker dicts

on_integrations_update
~~~~~~~~~~~~~~~~~~~~~~

Fired when a guild's integrations change (bots added/removed, etc.).

.. code-block:: python

   @session.event
   async def on_integrations_update(guild_id):
       ...

:param guild_id: Guild ID string

----

Member Events
-------------

on_member_join
~~~~~~~~~~~~~~

Fired when a user joins a guild.

.. code-block:: python

   @session.event
   async def on_member_join(member):
       print(f'{member.user_id} joined {member.guild_id}')

:param member: :class:`~cascade.entities.member.Member`

on_member_remove
~~~~~~~~~~~~~~~~

Fired when a user leaves or is removed from a guild.

.. code-block:: python

   @session.event
   async def on_member_remove(guild_id, user):
       print(f'{user.get("username")} left {guild_id}')

:param guild_id: Guild ID string
:param user: Raw user dict

on_member_update
~~~~~~~~~~~~~~~~

Fired when a member's data changes — roles added/removed, nickname changed, timeout, etc.

.. code-block:: python

   @session.event
   async def on_member_update(member):
       ...

:param member: :class:`~cascade.entities.member.Member`

on_members_chunk
~~~~~~~~~~~~~~~~

Fired in response to a ``REQUEST_GUILD_MEMBERS`` gateway op. Contains a chunk of guild members.

.. code-block:: python

   @session.event
   async def on_members_chunk(guild_id, members, chunk_index, chunk_count, nonce):
       print(f'Chunk {chunk_index+1}/{chunk_count}: {len(members)} members')

:param guild_id: Guild ID string
:param members: List of raw member dicts
:param chunk_index: Zero-based index of this chunk
:param chunk_count: Total number of chunks
:param nonce: Optional nonce string passed to the original request

----

Role Events
-----------

on_role_create
~~~~~~~~~~~~~~

:param guild_id: Guild ID string
:param role: :class:`~cascade.entities.role.Role`

on_role_update
~~~~~~~~~~~~~~

:param guild_id: Guild ID string
:param role: :class:`~cascade.entities.role.Role`

on_role_delete
~~~~~~~~~~~~~~

:param guild_id: Guild ID string
:param role_id: Role ID string

----

Channel Events
--------------

on_channel_create
~~~~~~~~~~~~~~~~~

Fired when a channel is created in a guild the user is in, or when a DM is opened.

.. code-block:: python

   @session.event
   async def on_channel_create(channel):
       print(f'New channel: #{channel.name}')

:param channel: :class:`~cascade.entities.channel.Channel` subclass

on_channel_update
~~~~~~~~~~~~~~~~~

Fired when a channel's settings change.

:param channel: :class:`~cascade.entities.channel.Channel` subclass

on_channel_delete
~~~~~~~~~~~~~~~~~

Fired when a channel is deleted.

:param channel: :class:`~cascade.entities.channel.Channel` subclass

on_pins_update
~~~~~~~~~~~~~~

Fired when a message is pinned or unpinned in a channel.

.. code-block:: python

   @session.event
   async def on_pins_update(channel_id, guild_id, last_pin_timestamp):
       ...

:param channel_id: Channel ID string
:param guild_id: Guild ID string or ``None`` for DMs
:param last_pin_timestamp: ISO8601 timestamp string of the most recent pin, or ``None``

on_typing
~~~~~~~~~

Fired when a user starts typing in a channel.

.. code-block:: python

   @session.event
   async def on_typing(channel, user, timestamp):
       if user:
           print(f'{user.username} is typing in #{channel.name if channel else channel_id}')

:param channel: Cached :class:`~cascade.entities.channel.Channel` or ``None``
:param user: Cached :class:`~cascade.entities.user.User` or ``None``
:param timestamp: Unix timestamp integer

on_webhooks_update
~~~~~~~~~~~~~~~~~~

Fired when a channel's webhooks are created or deleted.

:param guild_id: Guild ID string
:param channel_id: Channel ID string

----

Thread Events
-------------

on_thread_create
~~~~~~~~~~~~~~~~

Fired when a thread is created.

.. code-block:: python

   @session.event
   async def on_thread_create(thread):
       print(f'Thread created: {thread.name}')

:param thread: Thread channel object

on_thread_update
~~~~~~~~~~~~~~~~

Fired when a thread's settings change.

:param thread: Thread channel object

on_thread_delete
~~~~~~~~~~~~~~~~

Fired when a thread is deleted.

:param data: Raw dict with ``id``, ``guild_id``, ``parent_id``, ``type``

on_thread_list_sync
~~~~~~~~~~~~~~~~~~~

Fired when the client gains access to a channel and receives its thread list.

:param guild_id: Guild ID string
:param channel_ids: List of channel ID strings that were synced
:param threads: List of raw thread dicts

on_thread_members_update
~~~~~~~~~~~~~~~~~~~~~~~~

Fired when members are added to or removed from a thread.

:param thread_id: Thread ID string
:param guild_id: Guild ID string
:param member_count: Approximate member count
:param added_members: List of raw thread member dicts
:param removed_member_ids: List of removed user ID strings

----

Voice Events
------------

on_voice_state_update
~~~~~~~~~~~~~~~~~~~~~

Fired when any user's voice state changes — joining, leaving, muting, deafening, etc.

.. code-block:: python

   @session.event
   async def on_voice_state_update(state):
       if state.channel_id:
           print(f'{state.user_id} joined voice channel {state.channel_id}')
       else:
           print(f'{state.user_id} disconnected from voice')

:param state: :class:`~cascade.entities.voice_state_entity.VoiceStateEntity`

on_voice_server_update
~~~~~~~~~~~~~~~~~~~~~~

Fired when the voice server endpoint for a guild changes. Used internally for voice connections.

:param data: Raw dict with ``token``, ``guild_id``, ``endpoint``

on_soundboard_update
~~~~~~~~~~~~~~~~~~~~

Fired when a guild's soundboard sounds change.

:param guild_id: Guild ID string
:param sounds: List of raw soundboard sound dicts

----

Stage Events
------------

on_stage_create
~~~~~~~~~~~~~~~

Fired when a Stage instance is created.

:param stage: :class:`~cascade.entities.stage.StageInstance`

on_stage_update
~~~~~~~~~~~~~~~

Fired when a Stage instance is updated.

:param stage: :class:`~cascade.entities.stage.StageInstance`

on_stage_delete
~~~~~~~~~~~~~~~

Fired when a Stage instance ends.

:param stage: :class:`~cascade.entities.stage.StageInstance`

----

Scheduled Event Events
----------------------

on_scheduled_event_create
~~~~~~~~~~~~~~~~~~~~~~~~~

Fired when a scheduled event is created in a guild.

:param event: :class:`~cascade.entities.scheduled_event.ScheduledEvent`

on_scheduled_event_update
~~~~~~~~~~~~~~~~~~~~~~~~~

Fired when a scheduled event is updated.

:param event: :class:`~cascade.entities.scheduled_event.ScheduledEvent`

on_scheduled_event_delete
~~~~~~~~~~~~~~~~~~~~~~~~~

Fired when a scheduled event is cancelled or ends.

:param event: :class:`~cascade.entities.scheduled_event.ScheduledEvent`

----

Invite Events
-------------

on_invite_create
~~~~~~~~~~~~~~~~

Fired when an invite is created in a guild channel.

:param invite: :class:`~cascade.entities.invite.Invite`

on_invite_delete
~~~~~~~~~~~~~~~~

Fired when an invite is deleted or expires.

:param code: Invite code string
:param guild_id: Guild ID string
:param channel_id: Channel ID string

----

Relationship Events
-------------------

on_relationship_add
~~~~~~~~~~~~~~~~~~~

Fired when a relationship is added — friend request sent or received, or a user is blocked.

.. code-block:: python

   @session.event
   async def on_relationship_add(relationship):
       from cascade import RelationshipType
       if relationship.type == RelationshipType.INCOMING_REQUEST:
           print(f'Friend request from {relationship.user_id}')

:param relationship: :class:`~cascade.entities.relationship.Relationship`

on_relationship_remove
~~~~~~~~~~~~~~~~~~~~~~

Fired when a relationship is removed — unfriended or unblocked.

:param relationship: :class:`~cascade.entities.relationship.Relationship`

----

Presence / User Events
----------------------

on_presence_update
~~~~~~~~~~~~~~~~~~

Fired when any visible user's presence changes (status, activity, etc.).

.. code-block:: python

   @session.event
   async def on_presence_update(presence):
       print(presence.status, presence.activities)

:param presence: :class:`~cascade.entities.presence.Presence`

on_user_update
~~~~~~~~~~~~~~

Fired when the logged-in user's account data changes (username, avatar, etc.).

.. code-block:: python

   @session.event
   async def on_user_update(user):
       print(f'Account updated: {user.username}')

:param user: :class:`~cascade.entities.user.ClientUser`

on_sessions_replace
~~~~~~~~~~~~~~~~~~~

Fired when Discord replaces the list of active sessions (e.g. another client connects or disconnects). Selfbot-specific event.

:param data: List of raw session dicts

----

Poll Events
-----------

on_poll_vote_add
~~~~~~~~~~~~~~~~

Fired when a user votes on a poll.

.. code-block:: python

   @session.event
   async def on_poll_vote_add(user_id, message_id, channel_id, answer_id, guild_id):
       print(f'{user_id} voted answer {answer_id} on poll {message_id}')

:param user_id: Voter's user ID string
:param message_id: Poll message ID string
:param channel_id: Channel ID string
:param answer_id: The answer ID that was voted on
:param guild_id: Guild ID string or ``None``

on_poll_vote_remove
~~~~~~~~~~~~~~~~~~~

Fired when a user removes their vote from a poll.

:param user_id: Voter's user ID string
:param message_id: Poll message ID string
:param channel_id: Channel ID string
:param answer_id: The answer ID that was unvoted
:param guild_id: Guild ID string or ``None``

----

Audit Log Events
----------------

on_audit_log_entry
~~~~~~~~~~~~~~~~~~

Fired when an audit log entry is created in a guild the user has access to.

.. code-block:: python

   @session.event
   async def on_audit_log_entry(entry):
       print(f'{entry.action_name} by {entry.user_id} -> target {entry.target_id}')
       for change in entry.changes:
           print(f'  {change.key}: {change.before!r} -> {change.after!r}')

:param entry: :class:`~cascade.entities.audit_log.AuditLogEntry`

Common ``action_name`` values: ``guild_update``, ``channel_create``, ``channel_delete``, ``member_kick``, ``member_ban_add``, ``member_ban_remove``, ``member_role_update``, ``role_create``, ``role_delete``, ``invite_create``, ``webhook_create``, ``emoji_create``, ``message_delete``, ``message_bulk_delete``, ``thread_create``, ``auto_moderation_block_message``.

----

Interaction Events
------------------

on_interaction
~~~~~~~~~~~~~~

Fired when an interaction is created (button click, slash command, select menu, modal submit).

.. code-block:: python

   @session.event
   async def on_interaction(interaction):
       if interaction.type == 2:
           print(f'Slash command: {interaction.data.get("name")}')

:param interaction: :class:`~cascade.interactions.interaction.Interaction`
