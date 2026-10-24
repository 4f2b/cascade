Changelog
=========

.. note::
   Versions follow `semantic versioning <https://semver.org>`_.
   Pre-release suffixes: ``a`` alpha, ``b`` beta, ``rc`` release candidate.

----

v0.4.0
------

*Unreleased*

Added
~~~~~

- :class:`~cascade.entities.attachment.Attachment` entity with ``is_image``, ``is_video``, ``is_audio``, ``spoiler`` properties. Messages now parse attachments automatically.
- :class:`~cascade.entities.forum.ForumChannel`, :class:`~cascade.entities.forum.ForumPost`, :class:`~cascade.entities.forum.ForumTag` — full forum channel support
- :class:`~cascade.entities.note.Note` entity with ``edit()`` and ``delete()`` methods
- :class:`~cascade.entities.integration.Integration`, :class:`~cascade.entities.integration.IntegrationAccount`, :class:`~cascade.entities.integration.IntegrationApplication`
- :class:`~cascade.entities.guild_preview.GuildPreview`
- :class:`~cascade.entities.voice_region.VoiceRegion`
- :class:`~cascade.entities.search_result.MessageSearchResult` — wraps message search results
- :class:`~cascade.utils.message_builder.MessageBuilder` — fluent message builder. Accepts embeds, components, reply, mentions, tts, flags. ``send_message()`` accepts it directly.
- :class:`~cascade.utils.message_builder.AllowedMentions` — ``.none()``, ``.all()``, ``.to_dict()``
- **Quests module** (``cascade.quests``): :class:`~cascade.quests.QuestClient`, :class:`~cascade.quests.Quest`, :class:`~cascade.quests.QuestConfig`, :class:`~cascade.quests.QuestUserStatus`, :class:`~cascade.quests.QuestTaskProgress`, :class:`~cascade.quests.QuestReward`, :class:`~cascade.quests.ClaimedQuest`, :class:`~cascade.quests.QuestTaskHeartbeat`
- ``session.quests`` property — lazy ``QuestClient`` instance
- ``QuestClient.run_heartbeat_loop()`` — safe heartbeat loop (55-65s intervals with jitter)
- ``QuestClient.run_video_quest()`` — safe video progress loop
- Rich methods on :class:`~cascade.entities.guild.Guild`: ``fetch_bans()``, ``fetch_ban()``, ``fetch_audit_log()``, ``fetch_templates()``, ``fetch_onboarding()``, ``fetch_welcome_screen()``, ``fetch_scheduled_events()``, ``fetch_invites()``, ``fetch_webhooks()``, ``fetch_stickers()``, ``fetch_emojis()``, ``fetch_roles()``, ``edit()``
- Rich methods on :class:`~cascade.entities.member.Member`: ``edit()``, ``set_nickname()``, ``add_role()``, ``remove_role()``, ``kick()``, ``ban()``, ``timeout()``, ``remove_timeout()``, ``send()``, ``fetch_profile()``
- New session methods: ``fetch_guild_preview()``, ``fetch_integrations()``, ``fetch_voice_regions()``, ``fetch_guild_voice_regions()``, ``search_messages()`` (returns ``MessageSearchResult``), ``fetch_note()``, ``set_note()``, ``fetch_pinned_messages()``, ``fetch_forum_posts()``, ``set_voice_channel_status()``
- 30+ new REST endpoints: bulk ban, recent mentions, all notes, hypesquad, proto settings, join requests, member verification, greet, channel affinities, guild profile, recent avatars, accept/decline message requests, relationship nickname, mutual friends
- New gateway events: ``on_ban_add``, ``on_ban_remove``, ``on_emojis_update``, ``on_integrations_update``, ``on_pins_update``, ``on_members_chunk``, ``on_thread_list_sync``, ``on_thread_members_update``, ``on_sessions_replace``, ``on_voice_channel_status``, ``on_reaction_remove_emoji``
- Read states now cached from READY payload

Changed
~~~~~~~

- Version strings updated: Electron 42, Chrome 136, build number 635180
- ``on_presence_update`` now dispatches a :class:`~cascade.entities.presence.Presence` entity (was raw dict)
- ``on_user_update`` now dispatches :class:`~cascade.entities.user.ClientUser` (was raw dict)
- ``on_reaction_add`` / ``on_reaction_remove`` now dispatch :class:`~cascade.entities.reaction.Reaction` (was raw dict)
- ``on_audit_log_entry`` now dispatches :class:`~cascade.entities.audit_log.AuditLogEntry` (was raw dict)
- ``on_ban_add`` / ``on_ban_remove`` dispatch :class:`~cascade.entities.ban.Ban`
- ``accept-encoding`` header no longer includes ``br`` (Brotli not installed, caused 400 errors)
- ``fetch_read_states()`` now uses READY payload cache, falls back to REST

Fixed
~~~~~

- Read states REST endpoint updated to correct path
- Duplicate ``fetch_note``/``set_note`` methods removed from session
- ``Message.clear_reactions()`` broken import path fixed
- Missing ``datetime`` import in ``message.py``

----

v0.3.1
------

*Released 2026-10-20*

Fixed
~~~~~

- Gateway send queue serialises all outgoing messages — none drop during reconnect
- Proper WebSocket close code handling — 4004/4014 are fatal and stop immediately, others resume or re-identify as appropriate
- Guild stubs from the READY payload (``unavailable: true``) now cache correctly without throwing ``KeyError``
- ``GUILD_CREATE`` events after READY update unavailable stubs and fire :func:`on_guild_available` instead of :func:`on_guild_join`
- Zombie connection detection — 2 missed heartbeat acks triggers a full reconnect
- Exponential backoff on reconnect capped at 60s, resets on successful heartbeat ack
- Heartbeat task cancels cleanly when a reconnect begins

Added
~~~~~

- :func:`on_guild_available` — fires when a previously unavailable guild becomes available
- :func:`on_guild_update` — fires when guild settings change
- Thread events: :func:`on_thread_create`, :func:`on_thread_update`, :func:`on_thread_delete`
- Member events: :func:`on_member_join`, :func:`on_member_remove`, :func:`on_member_update`
- Role events: :func:`on_role_create`, :func:`on_role_update`, :func:`on_role_delete`
- Reaction events: :func:`on_reaction_add`, :func:`on_reaction_remove`, :func:`on_reaction_clear`
- :func:`on_webhooks_update`, :func:`on_audit_log_entry`, :func:`on_voice_server_update`
- :meth:`~cascade.gateway.shard.GatewayShard.update_presence` method on the shard

----

v0.3.0
------

*Released 2026-10-20*

Added
~~~~~

- :class:`~cascade.entities.polls.PollBuilder` — fluent API for building polls
- :class:`~cascade.entities.scheduled_event.ScheduledEvent` entity
- :class:`~cascade.entities.stage.StageInstance` entity
- :class:`~cascade.entities.sticker.Sticker` entity
- :class:`~cascade.entities.invite.Invite` entity with ``.url`` property
- :class:`~cascade.entities.gift_code.GiftCode` entity
- :class:`~cascade.entities.voice_state_entity.VoiceStateEntity` entity
- :class:`~cascade.entities.read_state.ReadState` entity
- :class:`~cascade.entities.soundboard.SoundboardSound` entity
- Poll gateway events: :func:`on_poll_vote_add`, :func:`on_poll_vote_remove`
- Soundboard gateway event: :func:`on_soundboard_update`
- Sticker gateway event: :func:`on_stickers_update`

----



*Released 2026-10-20*

Changed
~~~~~~~

- ``pyproject.toml`` modernised to SPDX license, ``setuptools>=77``, optional extras (``voice``, ``security``), docs and changelog URLs added, examples excluded from installed package
- Docs switched from sphinx-rtd-theme to Furo with Discord-branded dark mode colours
- README rewritten to be minimal

Added
~~~~~

- Changelog page in documentation
- ``Documentation`` and ``Changelog`` links on PyPI project page

----

v0.2.0
------

*Released 2026-10-20*

Added
~~~~~

- **Device spoofing** via :class:`~cascade.spoof.platforms.PlatformSpoofer`

  14 presets: ``desktop``, ``macos``, ``linux``, ``web``, ``mobile``, ``android``, ``ios``,
  ``iphone``, ``ipad``, ``vr``, ``quest``, ``xbox``, ``playstation``.
  Automatic ``X-Super-Properties`` and ``User-Agent`` injection.
  Switch platforms at runtime with :meth:`~cascade.core.session.Session.set_platform`.

- **Voice** (:mod:`cascade.voice`)

  :class:`~cascade.voice.client.VoiceClient`,
  :class:`~cascade.voice.state.VoiceState`,
  :class:`~cascade.voice.audio.PCMAudio`,
  :class:`~cascade.voice.audio.FFmpegAudio`,
  :class:`~cascade.voice.opus.OpusEncoder`

- **Interactions** (:mod:`cascade.interactions`)

  :class:`~cascade.interactions.components.Button`,
  :class:`~cascade.interactions.components.SelectMenu`,
  :class:`~cascade.interactions.components.TextInput`,
  :class:`~cascade.interactions.components.ActionRow`,
  :class:`~cascade.interactions.modal.Modal`,
  full :class:`~cascade.interactions.interaction.Interaction` response handling

- **Auto-moderation** (:mod:`cascade.automod`)

  :class:`~cascade.automod.rule.AutoModRule` with keyword, regex, preset, and mention-spam triggers.
  Action types: block message, send alert, timeout.

- **Advanced caching** (:mod:`cascade.core.advanced_cache`)

  LRU, LFU, FIFO, TTL strategies via :class:`~cascade.core.advanced_cache.AdvancedCache`.
  Three-tier :class:`~cascade.core.advanced_cache.LayeredCache`.
  Per-entry TTL, eviction callbacks, cache stats.

- **Rich presence builder** (:mod:`cascade.utils.activity_builder`)

  :class:`~cascade.utils.activity_builder.RichActivity` fluent API.
  Assets, timestamps, party, secrets, buttons.

- **Security module** (:mod:`cascade.security`)

  :class:`~cascade.security.token_protection.TokenManager` -- masking, validation, user ID extraction, optional AES-256 encryption.
  :class:`~cascade.security.fingerprint.FingerprintRandomizer` -- canvas noise, resolution, timezone, typing and mouse patterns.
  :class:`~cascade.security.ratelimit_evasion.SmartRateLimiter` -- adaptive delays, bucket tracking.

- Sphinx documentation with Furo dark-mode theme, full API reference, and topic guides

Changed
~~~~~~~

- Desktop Chrome updated to **136**, Electron to **42**, build number to **635180**
- Android client updated to **350.6**, iOS to **350.0**
- Removed duplicate platform presets (``quest2``, ``quest3``, ``ps5``)
- :class:`~cascade.api.rest.RestClient` now accepts a ``spoofer`` parameter and rebuilds headers from it
- :class:`~cascade.gateway.shard.GatewayShard` reads the spoofer from the session on init
- README rewritten to be minimal

----

v0.1.0
------

*Released 2026-01-18*

Initial release.

Added
~~~~~

- Full Discord Gateway v10 -- connect, heartbeat, resume, reconnect, ``INVALID_SESSION`` handling
- 120+ REST API endpoints covering users, guilds, channels, messages, roles, webhooks, threads, voice, search, connections, settings, billing, and relationships
- Rate limiter with per-bucket tracking and automatic 429 retry
- Entity models: :class:`~cascade.entities.user.User`, :class:`~cascade.entities.guild.Guild`, :class:`~cascade.entities.channel.Channel`, :class:`~cascade.entities.message.Message`, :class:`~cascade.entities.member.Member`, :class:`~cascade.entities.role.Role`, :class:`~cascade.entities.emoji.Emoji`, :class:`~cascade.entities.presence.Presence`, :class:`~cascade.entities.webhook.Webhook`
- Event dispatcher with ``@session.event`` decorator and :meth:`~cascade.core.session.Session.wait_for`
- Cache system for guilds, channels, users, and messages
- Command framework: :class:`~cascade.ext.commands.bot.Bot`, :class:`~cascade.ext.commands.context.Context`, ``@command`` decorator
- Utilities: :class:`~cascade.utils.permissions.Permissions`, :class:`~cascade.utils.intents.Intents`, :class:`~cascade.utils.snowflake.Snowflake`, :class:`~cascade.utils.color.Color`, :class:`~cascade.api.typing.TypingIndicator`
- Examples: ``basic.py``, ``commands.py``, ``advanced.py``, ``moderation.py``
