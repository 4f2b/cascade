# Changelog

All notable changes to this project will be documented here.

Format: `## [version] - YYYY-MM-DD`

---

## [0.2.0] - 2026-10-20

### Added
- **Device spoofing** — 14 platform presets (desktop, mobile, iOS, Android, VR, Xbox, PlayStation) with automatic X-Super-Properties and User-Agent injection
- **Platform switching at runtime** — `session.set_platform()` hot-swaps properties without reconnecting
- **Voice support** — `VoiceClient`, `VoiceState`, `PCMAudio`, `FFmpegAudio`, `OpusEncoder`
- **Interactions** — `Button`, `SelectMenu`, `TextInput`, `ActionRow`, `Modal`, full `Interaction` response handling
- **Auto-moderation** — `AutoModRule`, `AutoModAction`, `AutoModTriggerMetadata` with keyword/regex/preset/mention-spam triggers
- **Advanced caching** — LRU, LFU, FIFO, TTL strategies; `LayeredCache` (L1/L2/L3); per-entry TTL; eviction callbacks; cache stats
- **Rich presence builder** — `RichActivity` fluent API with assets, timestamps, party, secrets, buttons
- **Security module** — `TokenManager` (masking, validation, user ID extraction, optional AES-256 encryption), `FingerprintRandomizer` (canvas, resolution, timezone, typing/mouse patterns), `SmartRateLimiter` (adaptive delays, bucket tracking)
- **Docs** — Sphinx + Read the Docs setup with full API reference, quickstart, event reference, caching/presence/rate-limit guides

### Changed
- Updated desktop/web Chrome to **136**, Electron to **42**, build number to **635180**
- Updated Android Discord client to **350.6**, iOS to **350.0**
- Cleaned up platform presets — removed duplicates (`quest2`, `quest3`, `ps5`, `windows`, `iphone`, `ipad` kept as aliases only)
- Rewrote `README.md` to be minimal and focused

### Fixed
- `RestClient` now accepts `spoofer` parameter and rebuilds headers/super-properties from it
- `GatewayShard` now reads `spoofer` from session and uses it in `_build_client_properties`

---

## [0.1.0] - 2026-01-18

### Added
- Full Discord Gateway v10 — connect, heartbeat, resume, reconnect, INVALID_SESSION handling
- 120+ REST API endpoints covering users, guilds, channels, messages, roles, webhooks, threads, voice, search, connections, settings, billing, relationships, and more
- Rate limiter with per-bucket tracking and automatic retry
- Entity models — `User`, `ClientUser`, `Guild`, `Channel`, `TextChannel`, `DMChannel`, `VoiceChannel`, `GroupChannel`, `Message`, `Member`, `Role`, `Emoji`, `Presence`, `Webhook`, `Connection`, `UserSettings`, `Application`
- Event dispatcher with `@session.event` decorator and `wait_for` support
- Cache system for guilds, channels, users, messages
- Command framework — `Bot`, `Context`, `@command` decorator with prefix support
- Utilities — `Permission`, `Permissions`, `Intents`, `Snowflake`, `Color`, `MarkdownProcessor`, `TypingIndicator`, `BackoffStrategy`, `Chunker`, `Validator`
- Examples — `basic.py`, `commands.py`, `advanced.py`, `moderation.py`
- MIT license, `pyproject.toml`, `setup.py`, `MANIFEST.in`
