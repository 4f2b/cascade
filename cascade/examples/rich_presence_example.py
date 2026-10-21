import asyncio
import time
import cascade
from cascade.utils.activity_builder import RichActivity


async def main():
    session = cascade.Session(token)
    
    @session.event
    async def on_ready(user):
        print(f'Connected as {user.username}')
        
        activity = RichActivity.playing('Epic Game')
        activity.set_state('In a match')
        activity.set_details('Level 50 | Rank Diamond')
        
        activity.assets.set_large_image('game_logo', 'Epic Game')
        activity.assets.set_small_image('rank_diamond', 'Diamond Rank')
        
        start_time = int(time.time())
        activity.timestamps.set_start(start_time)
        
        activity.party.set_id('party123')
        activity.party.set_size(2, 4)
        
        activity.add_button('View Profile', 'https://example.com/profile')
        activity.add_button('Join Server', 'https://example.com/invite')
        
        await session.gateway.update_presence(
            status='dnd',
            activities=[activity.to_dict()]
        )
        
        streaming = RichActivity.streaming('Coding Stream', 'https://twitch.tv/username')
        streaming.set_details('Building Discord Bot')
        streaming.set_state('Python Development')
        
        listening = RichActivity.listening('Spotify')
        listening.set_details('Song Name')
        listening.set_state('Artist Name')
        
        watching = RichActivity.watching('YouTube')
        watching.set_details('Tutorial Video')
        
        custom = RichActivity.custom('Custom status text')
        custom.assets.set_large_image('emoji_id', 'Emoji Text')
        
        await asyncio.sleep(30)
        await session.gateway.update_presence(
            status='online',
            activities=[streaming.to_dict()]
        )
    
    await session.start()


if __name__ == '__main__':
    asyncio.run(main())
