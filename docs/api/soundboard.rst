Soundboard
==========

The soundboard lets users play short audio sounds in voice channels.

Fetching Sounds
---------------

.. code-block:: python

   defaults = await session.fetch_soundboard_sounds()

   guild_sounds = await session.fetch_soundboard_sounds(guild_id)
   for sound in guild_sounds:
       print(sound.name, sound.volume)

Playing a Sound
---------------

.. code-block:: python

   await sound.send(voice_channel_id)

   await session.rest.send_soundboard_sound(channel_id, sound_id, source_guild_id)

Creating a Guild Sound
----------------------

Requires ``MANAGE_GUILD_EXPRESSIONS`` permission. File must be an MP3 or OGG under 512KB.

.. code-block:: python

   with open('sound.mp3', 'rb') as f:
       sound_data = f.read()
       import base64
       encoded = f'data:audio/mpeg;base64,{base64.b64encode(sound_data).decode()}'

   sound = await session.rest.create_guild_soundboard_sound(
       guild_id,
       name='tada',
       sound=encoded,
       volume=1.0,
   )

Editing
-------

.. code-block:: python

   await sound.edit(name='new_name', volume=0.5, emoji_name='🎉')

Deleting
--------

.. code-block:: python

   await sound.delete()

Gateway Event
-------------

.. code-block:: python

   @session.event
   async def on_soundboard_update(guild_id, sounds):
       print(f'Guild {guild_id} sounds updated: {len(sounds)} sounds')

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``sound_id``
     - Sound snowflake ID
   * - ``name``
     - Sound name
   * - ``volume``
     - Volume float (0.0 to 1.0)
   * - ``emoji_id``
     - Custom emoji ID or ``None``
   * - ``emoji_name``
     - Unicode emoji or ``None``
   * - ``guild_id``
     - Guild ID or ``None`` for default sounds
   * - ``available``
     - Whether the sound can be used
   * - ``is_default``
     - ``True`` if this is a Discord default sound
