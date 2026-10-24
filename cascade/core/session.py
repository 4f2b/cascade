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
        self._ready = asyncio.Event()
        self.gateway = GatewayShard(self.token, self)
        await self.gateway.connect()
        try:
            await asyncio.wait_for(self._ready.wait(), timeout=30.0)
        except asyncio.TimeoutError:
            await self.gateway.close()
            raise RuntimeError('Gateway did not become ready within 30 seconds')

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
        activities = []
        if activity:
            activities.append(activity.to_dict() if hasattr(activity, 'to_dict') else activity)
        await self.gateway.update_presence(
            status=status or 'online',
            activities=activities,
            afk=afk
        )
    
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

    async def fetch_scheduled_events(self, guild_id: int) -> List[Any]:
        from ..entities.scheduled_event import ScheduledEvent
        data = await self.rest.get_guild_scheduled_events(guild_id)
        return [ScheduledEvent(e, self) for e in data]

    async def create_scheduled_event(self, guild_id: int, **kwargs) -> Any:
        from ..entities.scheduled_event import ScheduledEvent
        data = await self.rest.create_guild_scheduled_event(guild_id, **kwargs)
        return ScheduledEvent(data, self)

    async def fetch_stage_instance(self, channel_id: int) -> Any:
        from ..entities.stage import StageInstance
        data = await self.rest.get_stage_instance(channel_id)
        return StageInstance(data, self)

    async def create_stage_instance(self, channel_id: int, topic: str, privacy_level: int = 2) -> Any:
        from ..entities.stage import StageInstance
        data = await self.rest.create_stage_instance(channel_id, topic, privacy_level)
        return StageInstance(data, self)

    async def fetch_read_states(self) -> List[Any]:
        from ..entities.read_state import ReadState
        if self.cache._read_states:
            return list(self.cache._read_states.values())
        try:
            data = await self.rest.get_read_states()
            if isinstance(data, dict):
                data = data.get('entries', [])
            return [ReadState(r, self) for r in (data or [])]
        except Exception:
            return []

    async def fetch_guild_stickers(self, guild_id: int) -> List[Any]:
        from ..entities.sticker import Sticker
        data = await self.rest.get_guild_stickers(guild_id)
        return [Sticker(s, self) for s in data]

    async def fetch_soundboard_sounds(self, guild_id: int = None) -> List[Any]:
        from ..entities.soundboard import SoundboardSound
        if guild_id:
            data = await self.rest.list_guild_soundboard_sounds(guild_id)
        else:
            data = await self.rest.list_default_soundboard_sounds()
        return [SoundboardSound(s, self) for s in data]

    async def fetch_nitro_status(self) -> Dict[str, Any]:
        return await self.rest.get_nitro_status()

    async def fetch_subscriptions(self) -> List[Any]:
        from ..entities.billing import Subscription
        data = await self.rest.get_billing_subscriptions()
        return [Subscription(s) for s in data]

    async def fetch_payment_sources(self) -> List[Any]:
        from ..entities.billing import PaymentSource
        data = await self.rest.get_billing_payment_sources()
        return [PaymentSource(s) for s in data]

    async def fetch_applied_boosts(self) -> List[Dict[str, Any]]:
        return await self.rest.get_applied_boosts()

    async def fetch_gift_code(self, code: str) -> Any:
        from ..entities.billing import GiftCode
        data = await self.rest.get_gift_code(code)
        return GiftCode(data)

    async def redeem_gift_code(self, code: str) -> Dict[str, Any]:
        return await self.rest.redeem_gift_code(code)

    async def set_profile_bio(self, bio: str) -> None:
        await self.rest.set_profile_bio(bio)
        if self.user:
            self.user.bio = bio

    async def set_profile_pronouns(self, pronouns: str) -> None:
        await self.rest.set_profile_pronouns(pronouns)
        if self.user:
            self.user.pronouns = pronouns

    async def set_profile_banner(self, banner_data: Optional[str]) -> None:
        await self.rest.set_profile_banner(banner_data)

    async def set_profile_theme_colors(self, primary: int, accent: int) -> None:
        await self.rest.set_profile_theme_colors(primary, accent)

    async def fetch_invite(self, code: str) -> Any:
        from ..entities.invite import Invite
        data = await self.rest.get_invite(code)
        return Invite(data, self)

    async def accept_invite(self, code: str) -> Dict[str, Any]:
        return await self.rest.accept_invite(code)

    async def fetch_oauth2_tokens(self) -> List[Any]:
        from ..oauth2 import OAuth2Token
        data = await self.rest.get_oauth2_tokens()
        return [OAuth2Token(t, self) for t in data]

    async def fetch_oauth2_authorization(
        self,
        client_id: str,
        scopes: List[str],
        response_type: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        code_challenge: Optional[str] = None,
        state: Optional[str] = None,
        nonce: Optional[str] = None,
    ) -> Any:
        from ..oauth2 import OAuth2Authorization
        data = await self.rest.get_oauth2_authorization(
            client_id=client_id,
            scopes=scopes,
            response_type=response_type,
            redirect_uri=redirect_uri,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
            state=state,
            nonce=nonce,
        )
        return OAuth2Authorization(
            data,
            self,
            scopes=scopes,
            response_type=response_type,
            original_redirect_uri=redirect_uri,
            code_challenge_method=code_challenge_method,
            code_challenge=code_challenge,
            state=state,
            nonce=nonce,
        )

    async def fetch_welcome_screen(self, guild_id: int) -> Any:
        from ..entities.onboarding import WelcomeScreen
        data = await self.rest.get_guild_welcome_screen(str(guild_id))
        return WelcomeScreen(data, self, str(guild_id))

    async def fetch_onboarding(self, guild_id: int) -> Any:
        from ..entities.onboarding import GuildOnboarding
        data = await self.rest.get_guild_onboarding(str(guild_id))
        return GuildOnboarding(data, self)

    async def fetch_guild(self, guild_id: int) -> Any:
        from ..entities.guild import Guild
        data = await self.rest.get_guild(str(guild_id))
        guild = Guild(data, self)
        self.cache.add_guild(guild)
        return guild

    async def fetch_channel(self, channel_id: int) -> Any:
        from ..entities.channel import create_channel
        data = await self.rest.get_channel(str(channel_id))
        ch = create_channel(data, self)
        if ch:
            self.cache.add_channel(ch)
        return ch

    async def fetch_user(self, user_id: int) -> Any:
        from ..entities.user import User
        data = await self.rest.get_user(str(user_id))
        return User(data, self)

    async def fetch_member(self, guild_id: int, user_id: int) -> Any:
        from ..entities.member import Member
        data = await self.rest.get_guild_member(str(guild_id), str(user_id))
        return Member(data, self, str(guild_id))

    async def fetch_ban(self, guild_id: int, user_id: int) -> Any:
        from ..entities.ban import Ban
        data = await self.rest.get_guild_ban(str(guild_id), str(user_id))
        return Ban(data, str(guild_id))

    async def fetch_bans(self, guild_id: int) -> List[Any]:
        from ..entities.ban import Ban
        data = await self.rest.get_guild_bans(str(guild_id))
        return [Ban(b, str(guild_id)) for b in data]

    async def fetch_audit_log(self, guild_id: int, **kwargs) -> Any:
        from ..entities.audit_log import AuditLog
        data = await self.rest.get_guild_audit_log(str(guild_id), **kwargs)
        return AuditLog(data, str(guild_id))

    async def fetch_guild_templates(self, guild_id: int) -> List[Any]:
        from ..entities.template import GuildTemplate
        data = await self.rest.get_guild_templates(str(guild_id))
        return [GuildTemplate(t, self) for t in data]

    async def create_guild_template(self, guild_id: int, name: str, description: str = None) -> Any:
        from ..entities.template import GuildTemplate
        data = await self.rest.create_guild_template(str(guild_id), name, description)
        return GuildTemplate(data, self)

    async def fetch_template(self, code: str) -> Any:
        from ..entities.template import GuildTemplate
        data = await self.rest.get_template(code)
        return GuildTemplate(data, self)

    async def fetch_user_profile(self, user_id: int, guild_id: int = None) -> Dict[str, Any]:
        return await self.rest.get_user_profile_full(str(user_id), str(guild_id) if guild_id else None)

    async def fetch_note(self, user_id: int) -> Any:
        from ..entities.note import Note
        data = await self.rest.get_user_notes(str(user_id))
        content = data.get('note', '') if isinstance(data, dict) else ''
        return Note(str(user_id), content, self)

    async def set_note(self, user_id: int, content: str) -> Any:
        from ..entities.note import Note
        await self.rest.set_user_note(str(user_id), content)
        return Note(str(user_id), content, self)

    async def fetch_messages(self, channel_id: int, limit: int = 50, **kwargs) -> List[Any]:
        from ..entities.message import Message
        data = await self.rest.get_messages(str(channel_id), limit=limit, **kwargs)
        return [Message(m, self) for m in data]

    async def fetch_message(self, channel_id: int, message_id: int) -> Any:
        from ..entities.message import Message
        data = await self.rest.get_message(str(channel_id), str(message_id))
        return Message(data, self)

    async def send_message(self, channel_id: int, content=None, **kwargs) -> Any:
        from ..entities.message import Message
        data = await self.rest.send_message(str(channel_id), content, **kwargs)
        return Message(data, self)

    async def ack_message(self, channel_id: int, message_id: int) -> None:
        await self.rest.ack_message(str(channel_id), str(message_id))

    async def fetch_pinned_messages(self, channel_id: int) -> List[Any]:
        from ..entities.message import Message
        data = await self.rest.get_pinned_messages(str(channel_id))
        return [Message(m, self) for m in data]

    async def search_messages(self, query: str, *, channel_id: int = None, guild_id: int = None, **kwargs) -> Any:
        from ..entities.search_result import MessageSearchResult
        if guild_id:
            data = await self.rest.search_guild_messages(str(guild_id), query, **kwargs)
        elif channel_id:
            data = await self.rest.search_channel_messages(str(channel_id), query, **kwargs)
        else:
            raise ValueError('Provide either channel_id or guild_id')
        return MessageSearchResult(data, self)

    async def fetch_guild_preview(self, guild_id: int) -> Any:
        from ..entities.guild_preview import GuildPreview
        data = await self.rest.get_guild_preview(str(guild_id))
        return GuildPreview(data)

    async def fetch_integrations(self, guild_id: int) -> List[Any]:
        from ..entities.integration import Integration
        data = await self.rest.get_guild_integrations(str(guild_id))
        return [Integration(i, self, str(guild_id)) for i in data]

    async def fetch_voice_regions(self) -> List[Any]:
        from ..entities.voice_region import VoiceRegion
        data = await self.rest.get_voice_regions()
        return [VoiceRegion(r) for r in data]

    async def fetch_guild_voice_regions(self, guild_id: int) -> List[Any]:
        from ..entities.voice_region import VoiceRegion
        data = await self.rest.get_guild_voice_regions(str(guild_id))
        return [VoiceRegion(r) for r in data]

    async def set_voice_channel_status(self, channel_id: int, status: str) -> None:
        await self.rest.set_voice_channel_status(str(channel_id), status)

    async def fetch_forum_posts(self, channel_id: int, archived: bool = False, limit: int = 50) -> List[Any]:
        from ..entities.forum import ForumPost
        if archived:
            data = await self.rest.list_public_archived_threads(str(channel_id), limit=limit)
        else:
            ch = await self.rest.get_channel(str(channel_id))
            guild_id = ch.get('guild_id', '')
            data = await self.rest.list_active_threads(guild_id)
        threads = data if isinstance(data, list) else data.get('threads', [])
        return [ForumPost(t, self) for t in threads if t.get('parent_id') == str(channel_id)]

    @property
    def quests(self):
        from ..quests.client import QuestClient
        if not hasattr(self, '_quest_client') or self._quest_client is None:
            self._quest_client = QuestClient(self)
        return self._quest_client