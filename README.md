# cascade

A modern, high-performance, async-ready API wrapper for Discord's user API written in Python.

> **Note:** Automating user accounts is against the Discord ToS. This library is for educational purposes only. Use at your own risk.

## Key Features

- Async/await throughout with `aiohttp` and `websockets`
- Full Discord Gateway v10 with auto-reconnect and resume
- 120+ REST API endpoints
- Smart rate limit handling with per-bucket tracking
- Device and platform spoofing (desktop, mobile, VR, console)
- Rich presence and activity builder
- Voice connections with FFmpeg and Opus support
- Interactions — buttons, select menus, modals
- Auto-moderation rule management
- Advanced layered caching (LRU/LFU/FIFO/TTL)
- Token protection and fingerprint randomization
- Command framework with prefix support

## Installing

Python 3.10 or higher is required.

```bash
pip install cascade-discord
```

For voice support:

```bash
pip install "cascade-discord[voice]"
```

## Quick Example

```python
import asyncio
import cascade

async def main():
    session = cascade.Session(token)

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

## Bot Example

```python
from cascade.ext.commands import Bot

bot = Bot(command_prefix='!', self_bot=True)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {bot.session.gateway.latency:.0f}ms')

bot.run(token)
```

## Links

- [Documentation](https://cascade-discord.readthedocs.io)
- [PyPI](https://pypi.org/project/cascade-discord)
- [GitHub](https://github.com/4f2b/cascade)

## Warning

User account automation violates Discord's Terms of Service. Account termination may occur.

## License

MIT
