Invites
=======

Fetching an Invite
------------------

.. code-block:: python

   invite = await session.fetch_invite('discord-invite-code')
   print(invite.guild_name, invite.approximate_member_count)
   print(invite.url)

   invite = await session.fetch_invite('https://discord.gg/abc123')

Accepting an Invite
-------------------

.. code-block:: python

   await session.accept_invite('abc123')

   await invite.accept()

Deleting an Invite
------------------

Requires ``MANAGE_CHANNELS`` or ``MANAGE_GUILD``:

.. code-block:: python

   await invite.delete()

   await session.rest.delete_invite('abc123')

Creating Invites
----------------

.. code-block:: python

   invite_data = await channel.create_invite(
       max_age=86400,
       max_uses=10,
       temporary=False,
       unique=True,
   )

Listing Channel Invites
-----------------------

.. code-block:: python

   invites = await channel.invites()

Gateway Events
--------------

.. code-block:: python

   @session.event
   async def on_invite_create(invite):
       print(f'New invite {invite.code} created for {invite.guild_name}')

   @session.event
   async def on_invite_delete(code, guild_id, channel_id):
       print(f'Invite {code} deleted')

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``code``
     - Invite code string
   * - ``url``
     - Full ``https://discord.gg/...`` URL
   * - ``guild_id``
     - Guild ID or ``None``
   * - ``guild_name``
     - Guild name
   * - ``guild_icon_url``
     - Guild icon CDN URL
   * - ``guild_description``
     - Guild description
   * - ``guild_features``
     - List of guild feature strings
   * - ``guild_verification_level``
     - Verification level integer
   * - ``channel_id``
     - Channel ID
   * - ``channel_name``
     - Channel name
   * - ``channel_type``
     - Channel type integer
   * - ``inviter_id``
     - Inviter user ID
   * - ``inviter_username``
     - Inviter username
   * - ``approximate_member_count``
     - Total member count
   * - ``approximate_presence_count``
     - Online member count
   * - ``expires_at``
     - Expiry timestamp or ``None``
