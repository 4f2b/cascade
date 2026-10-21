Entities
========

User
----

.. code-block:: python

   user = session.get_user(user_id)
   print(user.name, user.avatar_url, user.mention)

   dm = await user.create_dm()
   await user.send('hello')

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id``
     - User snowflake ID (string)
   * - ``username``
     - Raw username
   * - ``global_name``
     - Display name (``None`` if not set)
   * - ``name``
     - ``global_name`` if set, else ``username``
   * - ``discriminator``
     - Legacy discriminator, ``'0'`` for new usernames
   * - ``avatar`` / ``avatar_url``
     - Hash / full CDN URL (animated if applicable)
   * - ``default_avatar_url``
     - Fallback CDN URL
   * - ``display_avatar``
     - ``avatar_url`` or ``default_avatar_url``
   * - ``mention``
     - ``<@id>`` string
   * - ``banner``
     - Banner hash or ``None``
   * - ``accent_color``
     - Profile accent colour integer
   * - ``bio``
     - User bio string
   * - ``pronouns``
     - Pronouns string
   * - ``bot``
     - Whether this is a bot account
   * - ``public_flags``
     - Public badge flags bitfield

ClientUser
----------

Subclass of :class:`User` representing the logged-in account.
Available as ``session.user`` after ``on_ready``.

Extra attributes: ``email``, ``phone``, ``verified``, ``premium``,
``premium_type`` (0 none / 1 classic / 2 full / 3 basic), ``locale``,
``mfa_enabled``, ``desktop``, ``mobile``.

Guild
-----

.. code-block:: python

   guild = session.get_guild(guild_id)
   print(guild.name, guild.icon_url)

   await guild.leave()
   channels  = await guild.fetch_channels()
   member    = await guild.fetch_member(user_id)
   texts     = guild.text_channels
   voices    = guild.voice_channels
   ch        = guild.get_channel(channel_id)

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id`` / ``name``
     - Guild snowflake ID / name
   * - ``icon`` / ``icon_url``
     - Icon hash / CDN URL (animated if applicable)
   * - ``banner`` / ``banner_url``
     - Banner hash / CDN URL
   * - ``splash`` / ``splash_url``
     - Splash hash / CDN URL
   * - ``owner_id``
     - Owner user ID
   * - ``description``
     - Guild description
   * - ``member_count``
     - Approximate member count
   * - ``premium_tier``
     - Boost tier 0-3
   * - ``premium_subscription_count``
     - Active boost count
   * - ``features``
     - List of feature strings
   * - ``nsfw_level``
     - NSFW level integer
   * - ``verification_level``
     - Verification level integer
   * - ``preferred_locale``
     - Locale string
   * - ``channels``
     - All cached channels for this guild
   * - ``text_channels``
     - Cached text channels
   * - ``voice_channels``
     - Cached voice channels

Channels
--------

**TextChannel**

.. code-block:: python

   msg      = await channel.send('hello')
   msg      = await channel.fetch_message(message_id)
   messages = await channel.fetch_messages(limit=50, before=message_id)
   await channel.trigger_typing()
   deleted  = await channel.purge(limit=100, check=lambda m: m.author.id == my_id)
   invite   = await channel.create_invite(max_age=86400, max_uses=10)
   invites  = await channel.invites()

Attributes: ``topic``, ``nsfw``, ``rate_limit_per_user`` (slowmode),
``last_message_id``, ``parent_id`` (category).

**VoiceChannel**

Attributes: ``bitrate``, ``user_limit`` (0 = unlimited), ``rtc_region``.

**DMChannel**

.. code-block:: python

   await dm.send('hey')
   await dm.trigger_typing()

Attribute: ``recipient`` -- the other :class:`User`.

**GroupChannel**

.. code-block:: python

   await group.send('hey everyone')

Attributes: ``recipients`` (list of :class:`User`), ``owner_id``, ``icon``.

Message
-------

.. code-block:: python

   await message.reply('pong')
   await message.edit('new content')
   await message.delete()
   await message.delete(delay=5.0)
   await message.pin()
   await message.unpin()
   await message.add_reaction('👍')
   await message.remove_reaction('👍')
   await message.ack()

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id``
     - Message snowflake ID
   * - ``channel_id``
     - Channel ID string
   * - ``guild_id``
     - Guild ID or ``None`` for DMs
   * - ``content``
     - Message text content
   * - ``author``
     - :class:`User` who sent it
   * - ``timestamp``
     - ``datetime`` of creation
   * - ``edited_timestamp``
     - ``datetime`` of last edit or ``None``
   * - ``tts``
     - Whether TTS message
   * - ``pinned``
     - Whether pinned
   * - ``mentions``
     - List of mentioned :class:`User` objects
   * - ``attachments``
     - List of attachment dicts
   * - ``reactions``
     - List of reaction dicts
   * - ``components``
     - List of component dicts
   * - ``sticker_items``
     - List of sticker item dicts
   * - ``jump_url``
     - Direct link to the message
   * - ``channel``
     - Cached channel or ``None``
   * - ``guild``
     - Cached guild or ``None``

Member
------

A guild member. Inherits all :class:`User` attributes plus:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``nick``
     - Server nickname or ``None``
   * - ``roles``
     - List of role ID strings
   * - ``joined_at``
     - Join timestamp string
   * - ``premium_since``
     - Boosting since or ``None``
   * - ``deaf``
     - Server-deafened
   * - ``mute``
     - Server-muted
   * - ``pending``
     - Pending membership screening

Role
----

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id`` / ``name``
     - Role ID / name
   * - ``color``
     - Colour integer
   * - ``hoist``
     - Displayed separately in member list
   * - ``position``
     - Position in role hierarchy
   * - ``permissions``
     - Permissions bitfield integer
   * - ``managed``
     - Managed by integration
   * - ``mentionable``
     - Whether mentionable by everyone

Emoji / PartialEmoji
--------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id``
     - Emoji ID or ``None`` for unicode
   * - ``name``
     - Emoji name
   * - ``animated``
     - Whether animated
   * - ``url``
     - CDN URL for custom emoji

Presence & Activity
-------------------

.. code-block:: python

   from cascade.entities.presence import Activity
   from cascade.types.enums import ActivityType

   activity = Activity.playing('My Game')
   activity = Activity.streaming('Live', url='https://twitch.tv/user')
   activity = Activity.listening('Spotify')
   activity = Activity.watching('YouTube')
   activity = Activity.competing('Tournament')

   await session.change_presence(status='online', activity=activity)

For richer control (assets, timestamps, party, buttons) see :doc:`/topics/presence`.

Webhook
-------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id``
     - Webhook ID
   * - ``type``
     - :class:`~cascade.types.enums.WebhookType`
   * - ``guild_id``
     - Guild ID
   * - ``channel_id``
     - Channel ID
   * - ``name``
     - Webhook name
   * - ``avatar``
     - Avatar hash
   * - ``token``
     - Webhook token (if incoming)
   * - ``url``
     - Webhook execution URL

Relationship
------------

.. code-block:: python

   friends = await session.fetch_friends()
   for r in friends:
       print(r.display_name, r.since)
       await r.set_nickname('nickname')
       dm = await r.open_dm()

   incoming = [r for r in await session.fetch_relationships() if r.is_incoming_request]
   await incoming[0].accept()

   await some_relationship.block()
   await some_relationship.remove()

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``user_id``
     - User snowflake ID
   * - ``username``
     - Username
   * - ``global_name``
     - Display name
   * - ``display_name``
     - Nickname if set, else global_name, else username
   * - ``type``
     - :class:`~cascade.entities.relationship.RelationshipType`
   * - ``nickname``
     - Your private nickname for this person
   * - ``since``
     - ISO timestamp of when relationship was created
   * - ``avatar_url``
     - CDN URL
   * - ``is_friend``
     - ``True`` if mutual friend
   * - ``is_blocked``
     - ``True`` if blocked
   * - ``is_incoming_request``
     - ``True`` if they sent you a request
   * - ``is_outgoing_request``
     - ``True`` if you sent them a request

Application
-----------

.. code-block:: python

   apps = await session.fetch_my_applications()
   app  = await session.fetch_application(app_id)

   await app.edit(name='New Name', description='Updated', bot_public=False)
   await app.transfer(team_id)
   await app.delete()

   assets = await app.get_assets()
   asset  = await app.upload_asset('name', base64_data)
   await app.delete_asset(asset_id)

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id`` / ``name``
     - App ID / name
   * - ``description``
     - App description
   * - ``icon`` / ``icon_url``
     - Icon hash / CDN URL
   * - ``flags``
     - App flags bitfield
   * - ``bot_public``
     - Whether bot can be invited by anyone
   * - ``owner_id``
     - Owner user ID
   * - ``team_id``
     - Team ID if owned by a team
   * - ``tags``
     - List of tag strings
   * - ``redirect_uris``
     - OAuth2 redirect URIs
   * - ``terms_of_service_url``
     - ToS URL
   * - ``privacy_policy_url``
     - Privacy policy URL

Team
----

.. code-block:: python

   teams = await session.fetch_teams()
   team  = await session.create_team('Name')
   team  = await session.fetch_team(team_id)

   await team.edit(name='New Name')
   await team.invite_member('username')
   await team.remove_member(user_id)
   await team.transfer_ownership(user_id)
   await team.delete()

   for member in team.members:
       print(member.username, member.role, member.accepted)

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id`` / ``name``
     - Team ID / name
   * - ``icon`` / ``icon_url``
     - Icon hash / CDN URL
   * - ``owner_user_id``
     - Owner's user ID
   * - ``members``
     - List of :class:`~cascade.entities.team.TeamMember`
   * - ``owner``
     - The owner as a ``TeamMember``
