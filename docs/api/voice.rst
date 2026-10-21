Voice
=====

cascade provides voice channel connections with UDP audio streaming via :mod:`cascade.voice`.

Optional dependencies: ``PyNaCl`` for voice encryption, ``opuslib`` for Opus encoding.

Install with: ``pip install "cascade-discord[voice]"``

VoiceState
----------

Tracks a user's current voice state. The logged-in user's state is updated automatically from gateway events.

.. code-block:: python

   await session.update_voice_state(guild_id, channel_id=channel_id)

   await session.update_voice_state(guild_id, self_mute=True)

   await session.update_voice_state(guild_id, channel_id=None)

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``guild_id``
     - Guild ID or ``None``
   * - ``channel_id``
     - Voice channel ID or ``None``
   * - ``user_id``
     - User ID
   * - ``session_id``
     - Voice session ID
   * - ``self_deaf``
     - Self-deafened
   * - ``self_mute``
     - Self-muted
   * - ``self_stream``
     - Go Live active
   * - ``self_video``
     - Camera active
   * - ``deaf``
     - Server-deafened
   * - ``mute``
     - Server-muted
   * - ``suppress``
     - Suppressed in stage channel

Methods: ``move_to(channel_id)``, ``toggle_deaf()``, ``toggle_mute()``, ``disconnect()``.

VoiceClient
-----------

Low-level UDP voice connection.

.. code-block:: python

   from cascade.voice import VoiceClient, FFmpegAudio

   voice = VoiceClient(session, guild_id, channel_id)
   await voice.connect(voice_server_data)

   audio = FFmpegAudio('song.mp3', bitrate=128)
   voice.play_audio(audio)

   await voice.disconnect()
   voice.is_connected()

``voice_server_data`` is the payload from a ``VOICE_SERVER_UPDATE`` gateway event.

Audio Sources
-------------

**PCMAudio**

Reads raw 16-bit stereo PCM at 48kHz from any file-like object:

.. code-block:: python

   from cascade.voice import PCMAudio

   with open('audio.pcm', 'rb') as f:
       source = PCMAudio(f)
       voice.play_audio(source)

**FFmpegAudio**

Streams any format FFmpeg can decode. FFmpeg must be installed and on ``PATH``:

.. code-block:: python

   from cascade.voice import FFmpegAudio

   source = FFmpegAudio('song.mp3', bitrate=128)
   source = FFmpegAudio('https://example.com/stream.mp3')

**YTDLSource**

Streams directly from YouTube (requires ``yt-dlp``):

.. code-block:: python

   from cascade.voice.audio import YTDLSource

   source = YTDLSource('https://youtube.com/watch?v=...')
   print(source.title, source.duration)
   voice.play_audio(source)

OpusEncoder
-----------

Wraps ``opuslib`` for Opus encoding. Used internally by ``VoiceClient``.

.. code-block:: python

   from cascade.voice import OpusEncoder

   encoder = OpusEncoder(bitrate=128000)
   encoder.set_bitrate(96000)
   encoder.set_fec(True)
   encoder.set_packet_loss_percent(5)
