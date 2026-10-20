import asyncio
import cascade
from cascade.ext.commands import Bot, Context
from cascade.utils import Permissions

bot = Bot(command_prefix='!', self_bot=True)

@bot.event
async def on_ready(user):
    print(f'Moderation bot ready: {user.username}')

@bot.command()
async def clean(ctx: Context, limit: int = 10):
    if limit > 100:
        await ctx.send('Cannot clean more than 100 messages')
        return
    
    messages = await bot.rest.get_channel_messages(ctx.channel_id, limit=limit)
    my_id = str(bot.session.user.id)
    
    to_delete = [m['id'] for m in messages if m['author']['id'] == my_id]
    
    for msg_id in to_delete:
        await bot.rest.delete_message(ctx.channel_id, msg_id)
        await asyncio.sleep(0.5)
    
    response = await ctx.send(f'Cleaned {len(to_delete)} messages')
    await asyncio.sleep(3)
    await bot.rest.delete_message(ctx.channel_id, response['id'])

@bot.command()
async def nuke(ctx: Context, amount: int):
    if amount > 100:
        await ctx.send('Cannot nuke more than 100 messages')
        return
    
    messages = await bot.rest.get_channel_messages(ctx.channel_id, limit=amount)
    message_ids = [m['id'] for m in messages]
    
    if len(message_ids) > 1:
        await bot.rest.bulk_delete_messages(ctx.channel_id, message_ids)
        await ctx.send(f'Nuked {len(message_ids)} messages')

@bot.command()
async def slowmode(ctx: Context, seconds: int):
    if seconds < 0 or seconds > 21600:
        await ctx.send('Slowmode must be between 0 and 21600 seconds')
        return
    
    await bot.rest.edit_channel(ctx.channel_id, rate_limit_per_user=seconds)
    await ctx.send(f'Set slowmode to {seconds}s')

@bot.command()
async def lockdown(ctx: Context):
    roles = await bot.rest.get_guild_roles(ctx.guild_id)
    everyone_role = next(r for r in roles if r['name'] == '@everyone')
    
    perms = Permissions(int(everyone_role['permissions']))
    perms.remove(cascade.Permission.SEND_MESSAGES)
    
    await bot.rest.edit_guild_role(
        ctx.guild_id,
        everyone_role['id'],
        permissions=str(perms.value)
    )
    await ctx.send('🔒 Channel locked down')

@bot.command()
async def unlock(ctx: Context):
    roles = await bot.rest.get_guild_roles(ctx.guild_id)
    everyone_role = next(r for r in roles if r['name'] == '@everyone')
    
    perms = Permissions(int(everyone_role['permissions']))
    perms.add(cascade.Permission.SEND_MESSAGES)
    
    await bot.rest.edit_guild_role(
        ctx.guild_id,
        everyone_role['id'],
        permissions=str(perms.value)
    )
    await ctx.send('🔓 Channel unlocked')

@bot.command()
async def raid(ctx: Context):
    await ctx.send('⚠️ Raid mode activated')
    
    guild = await bot.rest.get_guild(ctx.guild_id)
    
    await bot.rest.edit_guild(
        ctx.guild_id,
        verification_level=4,
        default_message_notifications=1
    )
    
    await ctx.send('✅ Guild security maximized')

@bot.command()
async def massban(ctx: Context, *user_ids):
    if len(user_ids) > 10:
        await ctx.send('Cannot ban more than 10 users at once')
        return
    
    banned = 0
    for user_id in user_ids:
        try:
            await bot.rest.ban_guild_member(ctx.guild_id, user_id.strip('<@!>'))
            banned += 1
        except Exception as e:
            print(f'Failed to ban {user_id}: {e}')
    
    await ctx.send(f'Banned {banned}/{len(user_ids)} users')

async def main():
    await bot.start('YOUR_TOKEN_HERE')

if __name__ == '__main__':
    asyncio.run(main())
