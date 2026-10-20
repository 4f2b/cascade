import asyncio
import cascade

async def advanced_features():
    session = cascade.Session('YOUR_TOKEN_HERE')
    
    @session.event
    async def on_ready(user):
        print(f'Logged in as {user.username}')
        
        settings = await session.rest.get_user_settings()
        print(f'Theme: {settings.get("theme")}')
        print(f'Status: {settings.get("status")}')
        
        connections = await session.rest.get_user_connections()
        print(f'Connected accounts: {len(connections)}')
        
        affinities = await session.rest.get_user_affinities()
        print(f'User affinities: {len(affinities.get("user_affinities", []))}')
    
    @session.event
    async def on_message(message):
        if message.content.startswith('!search'):
            query = message.content[8:]
            results = await session.rest.search_channel_messages(
                message.channel_id,
                query=query,
                limit=10
            )
            
            total = results.get('total_results', 0)
            await session.rest.send_message(
                message.channel_id,
                f'Found {total} messages matching "{query}"'
            )
        
        elif message.content.startswith('!profile'):
            parts = message.content.split()
            if len(parts) < 2:
                return
            
            user_id = parts[1].strip('<@!>')
            profile = await session.rest.get_user_profile(user_id)
            
            user_data = profile.get('user', {})
            await session.rest.send_message(
                message.channel_id,
                f'**Profile for {user_data.get("username")}**\n'
                f'Bio: {profile.get("bio", "No bio")}\n'
                f'Banner: {"Yes" if profile.get("banner") else "No"}'
            )
        
        elif message.content.startswith('!typing'):
            async with cascade.TypingIndicator(session.rest, message.channel_id):
                await asyncio.sleep(5)
                await session.rest.send_message(
                    message.channel_id,
                    'Done typing!'
                )
    
    @session.event
    async def on_guild_member_add(guild_id, member):
        print(f'New member joined {guild_id}: {member.get("user", {}).get("username")}')
        
        welcome_channel = await find_welcome_channel(guild_id)
        if welcome_channel:
            await session.rest.send_message(
                welcome_channel,
                f'Welcome <@{member["user"]["id"]}> to the server!'
            )
    
    @session.event
    async def on_presence_update(presence):
        if presence.status == cascade.Status.ONLINE:
            user = session.cache.get_user(presence.user_id)
            if user:
                print(f'{user.username} came online')
    
    async def find_welcome_channel(guild_id):
        channels = await session.rest.get_guild_channels(guild_id)
        for channel in channels:
            if 'welcome' in channel['name'].lower():
                return channel['id']
        return None
    
    await session.start()

if __name__ == '__main__':
    asyncio.run(advanced_features())
