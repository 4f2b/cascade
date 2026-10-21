import asyncio
import cascade


async def main():
    session = cascade.Session(token, platform='mobile')
    
    @session.event
    async def on_ready(user):
        print(f'Connected as {user.username}')
        print(f'Platform: {session.get_platform_info()}')
        
        await asyncio.sleep(5)
        
        session.set_platform('vr')
        print('Switched to VR platform')
        print(f'Platform: {session.get_platform_info()}')
        
        await asyncio.sleep(5)
        
        session.set_platform('desktop')
        print('Switched to desktop')
        print(f'Platform: {session.get_platform_info()}')
    
    await session.start()


if __name__ == '__main__':
    print(f'Available platforms: {cascade.Session.list_platforms()}')
    asyncio.run(main())
