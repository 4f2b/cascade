import asyncio
import cascade

async def main():
    session = cascade.Session('YOUR_TOKEN_HERE')
    
    @session.event
    async def on_ready(user):
        print(f'Logged in as {user.username}#{user.discriminator}')
        print(f'User ID: {user.id}')
    
    @session.event
    async def on_message(message):
        if message.author.id == session.user.id:
            return
        
        if message.content.startswith('!ping'):
            await session.rest.send_message(message.channel_id, 'Pong!')
        
        elif message.content.startswith('!info'):
            await session.rest.send_message(
                message.channel_id,
                f'**User Info**\n'
                f'ID: {message.author.id}\n'
                f'Username: {message.author.username}\n'
                f'Created: {cascade.Snowflake.creation_time(message.author.id)}'
            )
    
    @session.event
    async def on_message_delete(message_id, channel_id):
        print(f'Message {message_id} deleted in channel {channel_id}')
    
    @session.event
    async def on_typing_start(channel_id, user_id, timestamp):
        print(f'User {user_id} started typing in {channel_id}')
    
    await session.start()

if __name__ == '__main__':
    asyncio.run(main())
