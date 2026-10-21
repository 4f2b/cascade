Changelog
=========

.. note::
   Versions follow `semantic versioning <https://semver.org>`_.
   Pre-release suffixes: ``a`` alpha, ``b`` beta, ``rc`` release candidate.

----

v0.2.0
------

*Released 2026-10-20*

Added
~~~~~

- **Device spoofing** — 14 platform presets (desktop, mobile, iOS, Android, VR, Xbox, PlayStation) with automatic ``X-Super-Properties`` and ``User-Agent`` injection. Switch platforms at runtime with :meth:`~cascade.core.session.Session.set_platform`.
- **Voice** — :class:`~cascade.voice.client.VoiceClient`, :class:`~cascade.voice.state.VoiceState`, :class:`~cascade.voice.audio.PCMAudio`, :class:`~cascade.voice.audio.FFmpegAudio`, :class:`~cascade.voice.opus.OpusEncoder`.
- **Interactions** — :class:`~cascade.interactions.components.Button`, :class:`~cascade.interactions.components.SelectMenu`, :class:`~cascade.interactions.components.TextInput`, :class:`~cascade.interactions.components.ActionRow`, :class:`~cascade.interactions.modal.Modal`, full :class:`~cascade.interactions.interaction.Interaction` response handling.
- **Auto-moderation** — :class:`~cascade.automod.rule.AutoModRule`, :class:`~cascade.automod.rule.AutoModAction`, :class:`~cascade.automod.rule.AutoModTriggerMetadata` with keyword, regex, preset, and mention-spam triggers.
- **Advanced caching** — LRU, LFU, FIFO, TTL strategies via :class:`~cascade.core.advanced_cache.AdvancedCache`; three-tier :class:`~cascade.core.advanced_cache.LayeredCache`; per-entry TTL; eviction callbacks; cache statistics.
- **Rich presence builder** — :class:`~cascade.utils.activity_builder.RichActivity` fluent API with assets, timestamps, party, secrets, and buttons.
- **Security module** — :class:`~cascade.security.token_protection.TokenManager` (masking, validation, user ID extraction, optional AES-256 encryption), :class:`~cascade.security.fingerprint.FingerprintRandomizer` (canvas noise, resolution, timezone, typing and mouse patterns), :class:`~cascade.security.ratelimit_evasion.SmartRateLimiter` (adaptive delays, bucket tracking).
- Sphinx documentation with Furo dark-mode theme, full API reference, and topic guides.

Changed
~~~~~~~

- Desktop Chrome updated to **136**, Electron to **42**, build number to **635180**.
- Android client updated to **350.6**, iOS to **350.0**.
- Removed duplicate platform presets (``quest2``, ``quest3``, ``ps5``).
- :class:`~cascade.api.rest.RestClient` now accepts a ``spoofer`` parameter and rebuilds headers from it.
- :class:`~cascade.gateway.shard.GatewayShard` reads the spoofer from session on init.
- README rewritten to be minimal — install command, two examples, links.

----

v0.1.0
------

*Released 2026-01-18*

Initial release.

Added
~~~~~

- Full Discord Gateway v10 — connect, heartbeat, resume, reconnect, ``INVALID_SESSION`` handling.
- 120+ REST API endpoints — users, guilds, channels, messages, roles, webhooks, threads, voice, search, connections, settings, billing, relationships.
- Rate limiter with per-bucket tracking and automatic 429 retry.
- Entity models — :class:`~cascade.entities.user.User`, :class:`~cascade.entities.user.ClientUser`, :class:`~cascade.entities.guild.Guild`, :class:`~cascade.entities.channel.Channel`, :class:`~cascade.entities.message.Message`, :class:`~cascade.entities.member.Member`, :class:`~cascade.entities.role.Role`, :class:`~cascade.entities.emoji.Emoji`, :class:`~cascade.entities.presence.Presence`, :class:`~cascade.entities.webhook.Webhook`, :class:`~cascade.entities.connection.Connection`, and more.
- Event dispatcher with ``@session.event`` decorator and :meth:`~cascade.core.session.Session.wait_for`.
- Cache system for guilds, channels, users, and messages.
- Command framework — :class:`~cascade.ext.commands.bot.Bot`, :class:`~cascade.ext.commands.context.Context`, ``@command`` decorator with prefix support.
- Utilities — :class:`~cascade.utils.permissions.Permissions`, :class:`~cascade.utils.intents.Intents`, :class:`~cascade.utils.snowflake.Snowflake`, :class:`~cascade.utils.color.Color`, :class:`~cascade.utils.markdown.MarkdownProcessor`, :class:`~cascade.api.typing.TypingIndicator`.
- Examples — ``basic.py``, ``commands.py``, ``advanced.py``, ``moderation.py``.
