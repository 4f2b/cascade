import asyncio
import cascade
from cascade.ext.commands import Bot, Context

bot = Bot(command_prefix='!', self_bot=True)

@bot.event
async def on_ready(user):
    print(f'{user.username} is ready')

@bot.command()
async def ping(ctx: Context):
    latency = bot.session.gateway.latency
    await ctx.send(f'Pong! Latency: {latency:.2f}ms')

@bot.command()
async def purge(ctx: Context, amount: int):
    if amount > 100:
        await ctx.send('Cannot purge more than 100 messages')
        return
    
    messages = await bot.rest.get_channel_messages(ctx.channel_id, limit=amount)
    my_messages = [m['id'] for m in messages if int(m['author']['id']) == ctx.author.id]
    
    for msg_id in my_messages:
        await bot.rest.delete_message(ctx.channel_id, msg_id)
    
    await ctx.send(f'Purged {len(my_messages)} messages')

@bot.command()
async def afk(ctx: Context, *, status: str = 'AFK'):
    await bot.rest.modify_current_user(custom_status={'text': status})
    await ctx.send(f'Set AFK status: {status}')

@bot.command()
async def snipe(ctx: Context):
    cache = bot.session.cache
    deleted = cache.get('last_deleted_message')
    
    if not deleted:
        await ctx.send('No recently deleted messages')
        return
    
    author = deleted.get('author', {})
    content = deleted.get('content', 'No content')
    await ctx.send(f'**{author.get("username")}**: {content}')

@bot.event
async def on_message_delete(message_id, channel_id, cached_message):
    if cached_message:
        bot.session.cache.set('last_deleted_message', cached_message, ttl=60)

async def main():
    await bot.start('YOUR_TOKEN_HERE')

if __name__ == '__main__':
    asyncio.run(main())
