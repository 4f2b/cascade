Utilities
=========

Permissions
-----------

.. code-block:: python

   from cascade.utils.permissions import Permission, Permissions

   perms = Permissions()
   perms.add(Permission.SEND_MESSAGES, Permission.ATTACH_FILES)
   perms.remove(Permission.SEND_TTS_MESSAGES)

   perms.has(Permission.SEND_MESSAGES)
   perms.has(Permission.ADMINISTRATOR)
   perms.is_admin()

   text_perms  = Permissions.text()
   voice_perms = Permissions.voice()
   all_perms   = Permissions.all()
   no_perms    = Permissions.none()

   perms.is_subset(other)
   perms.is_superset(other)

Full list of :class:`~cascade.utils.permissions.Permission` flags:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Flag
     - Bit
   * - ``CREATE_INSTANT_INVITE``
     - 0
   * - ``KICK_MEMBERS``
     - 1
   * - ``BAN_MEMBERS``
     - 2
   * - ``ADMINISTRATOR``
     - 3
   * - ``MANAGE_CHANNELS``
     - 4
   * - ``MANAGE_GUILD``
     - 5
   * - ``ADD_REACTIONS``
     - 6
   * - ``VIEW_AUDIT_LOG``
     - 7
   * - ``PRIORITY_SPEAKER``
     - 8
   * - ``STREAM``
     - 9
   * - ``VIEW_CHANNEL``
     - 10
   * - ``SEND_MESSAGES``
     - 11
   * - ``MANAGE_MESSAGES``
     - 13
   * - ``EMBED_LINKS``
     - 14
   * - ``ATTACH_FILES``
     - 15
   * - ``READ_MESSAGE_HISTORY``
     - 16
   * - ``MENTION_EVERYONE``
     - 17
   * - ``USE_EXTERNAL_EMOJIS``
     - 18
   * - ``CONNECT``
     - 20
   * - ``SPEAK``
     - 21
   * - ``MUTE_MEMBERS``
     - 22
   * - ``DEAFEN_MEMBERS``
     - 23
   * - ``MOVE_MEMBERS``
     - 24
   * - ``MANAGE_ROLES``
     - 28
   * - ``MANAGE_WEBHOOKS``
     - 29
   * - ``MANAGE_GUILD_EXPRESSIONS``
     - 30
   * - ``USE_APPLICATION_COMMANDS``
     - 31
   * - ``MANAGE_EVENTS``
     - 33
   * - ``MANAGE_THREADS``
     - 34
   * - ``MODERATE_MEMBERS``
     - 40
   * - ``USE_SOUNDBOARD``
     - 42
   * - ``SEND_VOICE_MESSAGES``
     - 46

Intents
-------

.. code-block:: python

   from cascade.utils.intents import Intents

   intents = Intents()
   intents.guilds         = True
   intents.guild_messages = True
   intents.message_content = True

   value = intents.value

The gateway uses a calculated intents value automatically covering guilds, guild members, guild moderation, guild messages, direct messages, and message content.

Snowflake
---------

.. code-block:: python

   from cascade.utils.snowflake import Snowflake

   snow = Snowflake(1234567890123456789)
   print(snow.timestamp)
   print(snow.worker_id)
   print(snow.process_id)
   print(snow.increment)

Color
-----

.. code-block:: python

   from cascade.utils.color import Color

   red   = Color.red()
   blue  = Color.blue()
   green = Color.green()

   c = Color(0x5865F2)
   print(c.r, c.g, c.b)
   print(c.hex)

Rich Activity Builder
---------------------

For building full rich presence activities. See :doc:`/topics/presence` for the full guide.

.. code-block:: python

   from cascade.utils.activity_builder import RichActivity

   activity = RichActivity.playing('My Game')
   activity.set_state('In Match').set_details('Level 50')
   activity.assets.set_large_image('logo', 'My Game')
   activity.assets.set_small_image('rank', 'Diamond')
   activity.timestamps.set_start(int(time.time()))
   activity.party.set_size(2, 4)
   activity.add_button('Join', 'https://example.com/join')

   await session.gateway.update_presence(
       status='online',
       activities=[activity.to_dict()]
   )

Advanced Caching
----------------

For the full caching guide see :doc:`/topics/caching`.

.. code-block:: python

   from cascade.core.advanced_cache import AdvancedCache, LayeredCache, CacheStrategy

   cache = AdvancedCache(max_size=1000, ttl=300, strategy=CacheStrategy.LRU)
   cache.set('key', value)
   data  = cache.get('key', default=None)
   cache.delete('key')
   cache.cleanup_expired()
   stats = cache.get_stats()

   layered = LayeredCache()
   layered.set('key', value)
   data = layered.get('key')

Typing Indicator
----------------

.. code-block:: python

   from cascade.api.typing import TypingIndicator

   async with TypingIndicator(session.rest, channel_id):
       result = await slow_operation()
       await session.rest.send_message(channel_id, result)

Markdown
--------

.. code-block:: python

   from cascade.utils.markdown import bold, italic, underline, strikethrough, code, code_block, spoiler

   await channel.send(bold('hello'))
   await channel.send(italic('world'))
   await channel.send(code('print("hi")'))
   await channel.send(code_block('print("hi")', 'python'))
   await channel.send(spoiler('secret'))

Validator
---------

.. code-block:: python

   from cascade.utils.validator import is_valid_username, extract_invite_code, parse_message_link

   is_valid_username('john_doe')
   extract_invite_code('https://discord.gg/abc123')
   parse_message_link('https://discord.com/channels/123/456/789')
