import asyncio
import cascade


async def main():
    session = cascade.Session(token)
    
    @session.event
    async def on_ready(user):
        print(f'Connected as {user.username}')
        
        guild_id = 123456789
        voice_channel_id = 987654321
        
        voice_state = cascade.VoiceState({
            'guild_id': str(guild_id),
            'channel_id': str(voice_channel_id),
            'user_id': str(user.id),
            'session_id': 'session',
            'deaf': False,
            'mute': False,
            'self_deaf': False,
            'self_mute': False
        }, session)
        
        await voice_state.move_to(voice_channel_id)
        
        voice_client = cascade.VoiceClient(session, guild_id, voice_channel_id)
        
        audio = cascade.FFmpegAudio('song.mp3', bitrate=128)
        voice_client.play_audio(audio)
        
        await asyncio.sleep(10)
        await voice_state.disconnect()
    
    await session.start()


if __name__ == '__main__':
    asyncio.run(main())
