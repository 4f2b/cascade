Stickers
========

Stickers can be used in messages. cascade supports both standard (Discord-provided) and guild stickers.

Fetching Stickers
-----------------

.. code-block:: python

   stickers = await session.fetch_guild_stickers(guild_id)
   for sticker in stickers:
       print(sticker.name, sticker.url)

   sticker = await session.rest.get_guild_sticker(guild_id, sticker_id)

   sticker = await session.rest.get_sticker(sticker_id)

   packs = await session.rest.list_sticker_packs()

Creating a Guild Sticker
------------------------

Requires ``MANAGE_GUILD_EXPRESSIONS`` permission. File must be PNG, APNG, GIF, or Lottie JSON under 512KB.

.. code-block:: python

   with open('sticker.png', 'rb') as f:
       sticker = await session.rest.create_guild_sticker(
           guild_id,
           name='cool_sticker',
           description='A cool sticker',
           tags='cool',
           file_data=f.read(),
           filename='sticker.png',
       )

Editing a Sticker
-----------------

.. code-block:: python

   await sticker.edit(name='new_name', description='updated', tags='fun')

Deleting
--------

.. code-block:: python

   await sticker.delete()

Sending in a Message
--------------------

.. code-block:: python

   await session.rest.send_message(
       channel_id,
       sticker_ids=[sticker.id],
   )

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``id``
     - Sticker snowflake ID
   * - ``name``
     - Sticker name
   * - ``description``
     - Sticker description
   * - ``tags``
     - Autocomplete tags string
   * - ``type``
     - :class:`~cascade.entities.sticker.StickerType` (``STANDARD`` or ``GUILD``)
   * - ``format_type``
     - :class:`~cascade.entities.sticker.StickerFormatType`
   * - ``available``
     - Whether the sticker can be used
   * - ``guild_id``
     - Guild ID or ``None`` for standard stickers
   * - ``url``
     - CDN URL (PNG/GIF/JSON depending on format)
   * - ``is_guild_sticker``
     - ``True`` if type is ``GUILD``

**StickerFormatType**: ``PNG`` (1), ``APNG`` (2), ``LOTTIE`` (3), ``GIF`` (4)
