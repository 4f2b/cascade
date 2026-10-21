# cascade

High-performance Discord selfbot library for Python. Built for speed, reliability, and production use.

## Installation

```bash
pip install cascade-discord
```

## Quick Start

```python
import asyncio
import cascade

async def main():
    session = cascade.Session(token)
    
    @session.event
    async def on_ready(user):
        print(f'Connected as {user.username}')
    
    @session.event
    async def on_message(message):
        if message.content == '!ping':
            await session.rest.send_message(message.channel_id, 'Pong!')
    
    await session.start()

asyncio.run(main())
```

## Command Framework

```python
from cascade.ext.commands import Bot

bot = Bot(command_prefix='!', self_bot=True)

@bot.command()
async def ping(ctx):
    latency = bot.session.gateway.latency
    await ctx.send(f'Pong! {latency:.0f}ms')

@bot.command()
async def purge(ctx, limit: int):
    messages = await ctx.channel.history(limit=limit)
    for msg in messages:
        if msg.author.id == ctx.author.id:
            await msg.delete()

bot.run(token)
```

## Features

### Gateway & Events
- Full Discord Gateway v10 implementation
- Automatic reconnection with exponential backoff
- Event dispatching with type-safe handlers
- WebSocket compression and ETF encoding support
- Real-time latency tracking

### REST API
- 120+ endpoints covering all Discord operations
- Smart rate limit handling with bucket detection
- Automatic retry with exponential backoff
- Proper User-Agent and client property spoofing
- Session connection pooling

### Voice & Audio
- Voice state management and control
- WebSocket voice connection with UDP
- Opus audio encoding
- FFmpeg audio streaming
- YouTube-DL integration support
- PCM audio playback

### Interactions
- Button components with multiple styles
- Select menus with customizable options
- Modal forms with text inputs
- Action rows for component layouts
- Full interaction response handling
- Followup messages and edits

### Auto-Moderation
- Keyword filtering with regex support
- Preset filters (profanity, slurs, etc.)
- Mention spam detection
- Custom trigger rules
- Multiple action types (block, alert, timeout)
- Channel and role exemptions

### Advanced Caching
- Multiple cache strategies (LRU, LFU, FIFO, TTL)
- Layered cache system (L1/L2/L3)
- Automatic expiration handling
- Cache statistics and metrics
- Custom eviction callbacks
- Memory-efficient storage

### Rich Presence
- Activity builder with fluent API
- Asset configuration (large/small images)
- Timestamps and duration tracking
- Party information
- Custom buttons with URLs
- All activity types (playing, streaming, listening, watching, competing, custom)

### User Account Features
- User settings management
- Connections and integrations
- Friend relationships and notes
- User profiles and affinities
- Guild folders and positions

### Guild Management
- Full role and permission system
- Channel creation and management
- Member management and moderation
- Webhooks and integrations
- Scheduled events and stage instances

### Messaging
- Send, edit, delete messages
- Message search with advanced filters
- Reactions and message components
- Thread creation and management
- Bulk operations

### Utilities
- Permission calculator
- Intent builder
- Snowflake parsing
- Markdown processor
- Color utilities
- Request chunking and backoff

## Advanced Usage

### Voice Connections
```python
from cascade.voice import VoiceClient, FFmpegAudio

voice = VoiceClient(session, guild_id, channel_id)
await voice.connect(voice_server_data)

audio = FFmpegAudio('song.mp3', bitrate=128)
voice.play_audio(audio)

await voice.disconnect()
```

### Interactive Components
```python
from cascade.interactions import Button, ActionRow, SelectMenu, SelectOption

buttons = ActionRow(
    Button.primary('Accept', 'btn_accept'),
    Button.danger('Decline', 'btn_decline')
)

options = [SelectOption('Option 1', 'opt1'), SelectOption('Option 2', 'opt2')]
select = SelectMenu(custom_id='menu', options=options)

await session.rest.send_message(channel_id, 'Choose:', components=[buttons.to_dict()])
```

### Auto-Moderation Rules
```python
from cascade.automod import AutoModAction, AutoModTriggerMetadata

metadata = AutoModTriggerMetadata({
    'keyword_filter': ['spam', 'scam'],
    'allow_list': ['legitimate']
})

actions = [
    AutoModAction.block_message(),
    AutoModAction.send_alert(alert_channel_id),
    AutoModAction.timeout(300)
]

await session.rest.create_automod_rule(guild_id, name='Filter', ...)
```

### Rich Presence Activities
```python
from cascade.utils.activity_builder import RichActivity

activity = RichActivity.playing('My Game')
activity.set_state('In Match').set_details('Level 50')
activity.assets.set_large_image('game_logo', 'Game Title')
activity.timestamps.set_start(start_time)
activity.add_button('Join', 'https://example.com')

await session.gateway.update_presence(status='dnd', activities=[activity.to_dict()])
```

### Advanced Caching
```python
from cascade.core.advanced_cache import AdvancedCache, CacheStrategy

cache = AdvancedCache(max_size=1000, ttl=300, strategy=CacheStrategy.LRU)
cache.set('key', value)
data = cache.get('key')

stats = cache.get_stats()
print(f'Hit rate: {stats["hit_rate"]:.2%}')
```

### Typing Indicators
```python
from cascade.api.typing import TypingIndicator

async with TypingIndicator(session.rest, channel_id):
    result = await heavy_processing()
    await session.rest.send_message(channel_id, result)
```

### Permission Checks
```python
from cascade.utils.permissions import Permission, Permissions

perms = Permissions()
perms.add(Permission.SEND_MESSAGES, Permission.ATTACH_FILES)

if perms.has(Permission.ADMINISTRATOR):
    await dangerous_operation()
```

## Performance

- Zero overhead event dispatching
- Optimized JSON parsing with orjson fallback
- Connection pooling for HTTP requests
- LRU caching with TTL support
- Memory-efficient entity storage

## Architecture

```
cascade/
├── api/            REST client, rate limiting, routes
├── core/           Session management, caching, event dispatch
├── entities/       User, Guild, Channel, Message, Role, etc.
├── gateway/        WebSocket handling, heartbeat, sharding
├── types/          Enums, payloads, type definitions
├── utils/          Permissions, intents, formatting, validation
└── ext/commands/   Command framework with decorators
```

## Examples

See `examples/` for complete implementations:
- `basic.py` - Session setup and event handling
- `commands.py` - Command framework with error handling
- `advanced.py` - Advanced features and utilities
- `moderation.py` - Moderation and bulk operations
- `voice_example.py` - Voice connections and audio streaming
- `interactions_example.py` - Buttons, select menus, and modals
- `rich_presence_example.py` - Custom rich presence activities
- `automod_example.py` - Auto-moderation rule management
- `advanced_cache_example.py` - Advanced caching strategies

## Warning

User account automation violates Discord Terms of Service. This library is for educational purposes. Account termination may occur.

## License

MIT
