import asyncio
import signal
from typing import Optional, Callable, Dict, Any, List
from ..gateway.shard import GatewayShard
from ..api.rest import RestClient
from .cache import Cache
from .dispatch import EventDispatcher
from ..spoof import PlatformSpoofer


class Session:
    def __init__(self, token: str, *, message_cache_limit: int = 1000, platform: str = "desktop"):
        self.token = token
        self.cache = Cache(message_limit=message_cache_limit)
        self.dispatcher = EventDispatcher()
        self.spoofer = PlatformSpoofer(platform)
        self.rest = RestClient(token, spoofer=self.spoofer)
        self.gateway: Optional[GatewayShard] = None
        self.user: Optional[Any] = None
        self._closed = False
        self._ready = asyncio.Event()
        self.platform = platform

    def event(self, coro: Callable) -> Callable:
        event_name = coro.__name__
        if not event_name.startswith('on_'):
            raise ValueError('Event callback must start with "on_"')
        self.dispatcher.register(event_name, coro)
        return coro

    async def start(self) -> None:
        self.gateway = GatewayShard(self.token, self)
        await self.gateway.connect()
        await self._ready.wait()

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self.gateway:
            await self.gateway.close()
        await self.rest.close()

    async def run(self) -> None:
        async def runner():
            try:
                await self.start()
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                await self.close()
            except Exception:
                await self.close()
                raise
            finally:
                await self.close()

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            pass

    def get_guild(self, guild_id: int):
        return self.cache.get_guild(str(guild_id))

    def get_channel(self, channel_id: int):
        return self.cache.get_channel(str(channel_id))

    def get_user(self, user_id: int):
        return self.cache.get_user(str(user_id))

    async def wait_for(self, event: str, *, check: Callable = None, timeout: float = None):
        return await self.dispatcher.wait_for(event, check, timeout)

    @property
    def guilds(self) -> List[Any]:
        return list(self.cache.guilds.values())

    @property
    def users(self) -> List[Any]:
        return list(self.cache.users.values())

    @property
    def latency(self) -> float:
        if self.gateway and self.gateway.heartbeat:
            return self.gateway.heartbeat.latency
        return float('inf')

    async def change_presence(self, status: str = None, activity=None, afk: bool = False):
        if not self.gateway:
            return
        
        from ..gateway import opcodes
        activities = []
        if activity:
            activities.append(activity.to_dict())
        
        await self.gateway.send_json({
            'op': opcodes.PRESENCE_UPDATE,
            'd': {
                'status': status or 'online',
                'activities': activities,
                'afk': afk,
                'since': 0
            }
        })
    
    async def request_guild_members(self, guild_id: int, query: str = '', limit: int = 0, presences: bool = False, user_ids: List[int] = None, nonce: str = None):
        if not self.gateway:
            return
        
        from ..gateway import opcodes
        payload = {
            'guild_id': str(guild_id),
            'query': query,
            'limit': limit,
            'presences': presences
        }
        
        if user_ids:
            payload['user_ids'] = [str(uid) for uid in user_ids]
        if nonce:
            payload['nonce'] = nonce
        
        await self.gateway.send_json({
            'op': opcodes.REQUEST_GUILD_MEMBERS,
            'd': payload
        })
    
    async def update_voice_state(self, guild_id: int, channel_id: int = None, self_mute: bool = False, self_deaf: bool = False):
        if not self.gateway:
            return
        
        from ..gateway import opcodes
        await self.gateway.send_json({
            'op': opcodes.VOICE_STATE_UPDATE,
            'd': {
                'guild_id': str(guild_id) if guild_id else None,
                'channel_id': str(channel_id) if channel_id else None,
                'self_mute': self_mute,
                'self_deaf': self_deaf
            }
        })

    def set_platform(self, platform: str):
        self.platform = platform
        self.spoofer.set_platform(platform)
        self.rest.spoofer = self.spoofer
        if self.gateway:
            self.gateway.spoofer = self.spoofer
    
    def get_platform_info(self) -> Dict[str, str]:
        return self.spoofer.get_platform_info()
    
    @staticmethod
    def list_platforms() -> List[str]:
        return PlatformSpoofer.list_platforms()

    async def fetch_relationships(self) -> List[Any]:
        from ..entities.relationship import Relationship
        data = await self.rest.get_relationships()
        return [Relationship(r, self) for r in data]

    async def fetch_friends(self) -> List[Any]:
        from ..entities.relationship import Relationship, RelationshipType
        data = await self.rest.get_relationships()
        return [Relationship(r, self) for r in data if r.get('type') == RelationshipType.FRIEND]

    async def fetch_blocked(self) -> List[Any]:
        from ..entities.relationship import Relationship, RelationshipType
        data = await self.rest.get_relationships()
        return [Relationship(r, self) for r in data if r.get('type') == RelationshipType.BLOCKED]

    async def send_friend_request(self, username: str) -> None:
        await self.rest.send_friend_request(username)

    async def fetch_teams(self) -> List[Any]:
        from ..entities.team import Team
        data = await self.rest.get_my_teams()
        return [Team(t, self) for t in data]

    async def create_team(self, name: str) -> Any:
        from ..entities.team import Team
        data = await self.rest.create_team(name)
        return Team(data, self)

    async def fetch_team(self, team_id: int) -> Any:
        from ..entities.team import Team
        data = await self.rest.get_team(team_id)
        return Team(data, self)

    async def fetch_my_applications(self) -> List[Any]:
        from ..entities.application import Application
        data = await self.rest.get_my_applications()
        return [Application(a, self) for a in data]

    async def fetch_application(self, application_id: int) -> Any:
        from ..entities.application import Application
        data = await self.rest.get_application(application_id)
        return Application(data, self)
