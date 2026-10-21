# Changelog

All notable changes to this project will be documented here.

Format: `## [version] - YYYY-MM-DD`

---

## [0.3.0] - 2026-10-20

### Added
- **Scheduled events** - `ScheduledEvent` entity with create/edit/delete/start/complete/cancel/fetch users. Gateway events `on_scheduled_event_create/update/delete`
- **Stage instances** - `StageInstance` with create/edit/delete/request_to_speak. Gateway `on_stage_create/update/delete`
- **Polls** - `Poll`, `PollBuilder`, `PollAnswer`. Vote, remove vote, end poll, fetch voters. Gateway `on_poll_vote_add/remove`
- **Stickers** - `Sticker` entity with edit/delete. Full guild sticker management endpoints + standard packs
- **Soundboard** - `SoundboardSound` with send/edit/delete. Default sounds + guild sounds. `on_soundboard_update`
- **Read states** - `ReadState` entity, `session.fetch_read_states()`, per-channel and guild-wide ack
- **Billing & Nitro** - `Subscription`, `PaymentSource`, `GiftCode`, `PremiumType`. Fetch subscriptions, payment sources, payments, applied boosts, Nitro status, redeem/fetch gift codes, promotions
- **Profile customisation** - `session.set_profile_bio/pronouns/banner/theme_colors()`. Set avatar decoration, theme colors (primary + accent)
- **Invites** - `Invite` entity with full guild/channel metadata. `session.fetch_invite()`, `session.accept_invite()`
- **VoiceStateEntity** - proper typed entity for voice state updates (replaces raw dict dispatch)
- **Expanded gateway events** - `on_relationship_add/remove` now pass `Relationship` entities. Added `on_voice_state_update`, `on_invite_create/delete`, `on_stickers_update`
- **Expanded enums** - `StagePrivacyLevel`, `ScheduledEventStatus/EntityType/PrivacyLevel`, `StickerType/FormatType`, `PremiumType`, `RelationshipType`, `InteractionType` all added to `cascade.types.enums`
- 20+ new REST endpoints across scheduled events, stage instances, polls, stickers, soundboard, billing, profile

### Changed
- `on_relationship_add/remove` now dispatch `Relationship` objects instead of raw dicts
- `on_voice_state_update` now dispatches `VoiceStateEntity` instead of raw dict
- Version bump: `cascade.__version__` is now `'0.3.0'`

---



### Changed
- `pyproject.toml` modernised - SPDX license string, `setuptools>=77`, optional extras (`voice`, `security`), docs/changelog URLs, examples excluded from package
- README rewritten to be minimal - matches discord.py-self style
- Docs switched to Furo theme with Discord-branded dark mode colours

### Added
- Changelog page in documentation
- `Documentation` and `Changelog` links on PyPI

---

## [0.2.0] - 2026-10-20

### Added
- **Device spoofing** - 14 platform presets (desktop, mobile, iOS, Android, VR, Xbox, PlayStation) with automatic X-Super-Properties and User-Agent injection
- **Platform switching at runtime** - `session.set_platform()` hot-swaps properties without reconnecting
- **Voice support** - `VoiceClient`, `VoiceState`, `PCMAudio`, `FFmpegAudio`, `OpusEncoder`
- **Interactions** - `Button`, `SelectMenu`, `TextInput`, `ActionRow`, `Modal`, full `Interaction` response handling
- **Auto-moderation** - `AutoModRule`, `AutoModAction`, `AutoModTriggerMetadata` with keyword/regex/preset/mention-spam triggers
- **Advanced caching** - LRU, LFU, FIFO, TTL strategies; `LayeredCache` (L1/L2/L3); per-entry TTL; eviction callbacks; cache stats
- **Rich presence builder** - `RichActivity` fluent API with assets, timestamps, party, secrets, buttons
- **Security module** - `TokenManager` (masking, validation, user ID extraction, optional AES-256 encryption), `FingerprintRandomizer` (canvas, resolution, timezone, typing/mouse patterns), `SmartRateLimiter` (adaptive delays, bucket tracking)
- **Docs** - Sphinx + Read the Docs setup with full API reference, quickstart, event reference, caching/presence/rate-limit guides

### Changed
- Updated desktop/web Chrome to **136**, Electron to **42**, build number to **635180**
- Updated Android Discord client to **350.6**, iOS to **350.0**
- Cleaned up platform presets - removed duplicates (`quest2`, `quest3`, `ps5`, `windows`, `iphone`, `ipad` kept as aliases only)
- Rewrote `README.md` to be minimal and focused

### Fixed
- `RestClient` now accepts `spoofer` parameter and rebuilds headers/super-properties from it
- `GatewayShard` now reads `spoofer` from session and uses it in `_build_client_properties`

---

## [0.1.0] - 2026-01-18

### Added
- Full Discord Gateway v10 - connect, heartbeat, resume, reconnect, INVALID_SESSION handling
- 120+ REST API endpoints covering users, guilds, channels, messages, roles, webhooks, threads, voice, search, connections, settings, billing, relationships, and more
- Rate limiter with per-bucket tracking and automatic retry
- Entity models - `User`, `ClientUser`, `Guild`, `Channel`, `TextChannel`, `DMChannel`, `VoiceChannel`, `GroupChannel`, `Message`, `Member`, `Role`, `Emoji`, `Presence`, `Webhook`, `Connection`, `UserSettings`, `Application`
- Event dispatcher with `@session.event` decorator and `wait_for` support
- Cache system for guilds, channels, users, messages
- Command framework - `Bot`, `Context`, `@command` decorator with prefix support
- Utilities - `Permission`, `Permissions`, `Intents`, `Snowflake`, `Color`, `MarkdownProcessor`, `TypingIndicator`, `BackoffStrategy`, `Chunker`, `Validator`
- Examples - `basic.py`, `commands.py`, `advanced.py`, `moderation.py`
- MIT license, `pyproject.toml`, `setup.py`, `MANIFEST.in`
