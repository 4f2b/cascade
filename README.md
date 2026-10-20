# Cascade

High-performance Discord selfbot library for Python. Built for speed, stealth, and reliability.

## Features

- **Blazing Fast**: Optimized for maximum performance with async/await
- **Stealthy**: Mimics official Discord client behavior to avoid detection
- **Full-Featured**: Complete gateway, REST API, and event system
- **Smart Caching**: Intelligent caching system for optimal memory usage
- **Type-Safe**: Full type hints throughout the codebase
- **Extensible**: Plugin system for custom commands and features

## Quick Start

```python
import asyncio
import cascade

async def main():
    session = cascade.Session('YOUR_TOKEN')
    
    @session.event
    async def on_ready(user):
        print(f'Logged in as {user.username}')
    
    @session.event
    async def on_message(message):
        if message.content == '!ping':
            await session.rest.send_message(message.channel_id, 'Pong!')
    
    await session.start()

asyncio.run(main())
```

## Advanced Usage

### Commands Framework

```python
from cascade.ext.commands import Bot

bot = Bot(command_prefix='!', self_bot=True)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {bot.session.gateway.latency:.2f}ms')

await bot.start('YOUR_TOKEN')
```

### Smart Features

```python
async with cascade.TypingIndicator(session.rest, channel_id):
    await process_long_task()
    await session.rest.send_message(channel_id, 'Done!')

results = await session.rest.search_channel_messages(
    channel_id,
    query='keyword',
    author_id=user_id
)

profile = await session.rest.get_user_profile(user_id)
connections = await session.rest.get_user_connections()
settings = await session.rest.get_user_settings()
```

### Permissions & Safety

```python
from cascade import Permission, Permissions

perms = Permissions()
perms.add(Permission.SEND_MESSAGES, Permission.READ_MESSAGE_HISTORY)

if perms.has(Permission.ADMINISTRATOR):
    print('User has admin')
```

## Installation

```bash
pip install cascade
```

## Performance

- **Gateway**: Sub-millisecond message handling
- **REST**: Smart rate limiting with automatic retry
- **Cache**: LRU caching with TTL support
- **Memory**: Optimized for low memory footprint

## Architecture

```
cascade/
├── core/           # Core session, cache, events
├── gateway/        # WebSocket gateway handling
├── api/            # REST API client
├── entities/       # Discord entities (User, Guild, Message, etc.)
├── types/          # Enums and type definitions
├── utils/          # Utilities (permissions, formatting, validation)
└── ext/            # Extensions (commands framework)
```

## Capabilities

- Full gateway connection with auto-reconnect
- Complete REST API coverage (100+ endpoints)
- User account features (notes, relationships, settings)
- Guild management (roles, channels, members)
- Message handling (send, edit, delete, search, reactions)
- Thread support (create, join, manage)
- Voice state updates
- Stage instances and scheduled events
- Webhooks and integrations
- Rich presence and activities
- Advanced search and filtering
- Bulk operations
- Smart markdown processing
- Permission calculations

## Examples

Check the `examples/` directory for:
- `basic.py` - Simple bot setup
- `commands.py` - Command framework usage  
- `advanced.py` - Advanced features
- `moderation.py` - Moderation utilities

## Warning

Selfbots are against Discord's Terms of Service. Use at your own risk.

## License

MIT.

## ⚠️ Warning

**Automating user accounts violates Discord's Terms of Service and can result in account termination.** This library is for educational purposes only. Use at your own risk.

## Features

- Async/await with aiohttp and websockets
- Full gateway connection with automatic reconnection
- Event-driven architecture
- REST API with intelligent rate limiting
- Built-in caching system
- Complete entity models (User, Guild, Channel, Message, etc.)
- Command framework
- Type hints throughout
- Zero comments, clean professional code

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import cascade

client = cascade.Session('your_token_here')

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message):
    if message.content == '!ping':
        await message.channel.send('Pong!')

client.run()
```

## Command Framework

```python
from cascade.ext.commands import Bot

bot = Bot('your_token_here', command_prefix='!')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')

@bot.command()
async def say(ctx, *args):
    await ctx.send(' '.join(args))

bot.run()
```

## Examples

### Change Presence

```python
from cascade import Activity, ActivityType

activity = Activity.playing('with Python')
await client.change_presence(status='dnd', activity=activity)
```

### Message Formatting

```python
from cascade.utils.formatting import bold, code, codeblock

await channel.send(bold('Bold text'))
await channel.send(code('inline code'))
await channel.send(codeblock('print("hello")', 'python'))
```

## License

MIT
