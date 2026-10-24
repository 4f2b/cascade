import asyncio
import json
import random
import time
import websockets
import websockets.exceptions
from typing import Optional, Any, Dict
from .heartbeat import Heartbeat
from . import opcodes


_NO_RESUME_CODES = {4004, 4010, 4011, 4012, 4013, 4014}
_FATAL_CODES = {4004, 4014}
_FATAL_MESSAGES = {
    4004: 'Authentication failed - token is invalid',
    4014: 'Privileged intent not granted in developer portal',
}


class GatewayShard:
    GATEWAY_URL = 'wss://gateway.discord.gg/?v=10&encoding=json'

    def __init__(self, token: str, session):
        self.token = token
        self.session = session
        self.spoofer = getattr(session, 'spoofer', None)

        self.ws: Optional[Any] = None
        self.heartbeat: Optional[Heartbeat] = None
        self.sequence: Optional[int] = None
        self.session_id: Optional[str] = None
        self.resume_url: Optional[str] = None

        self._closed = False
        self._reconnecting = False
        self._recv_task: Optional[asyncio.Task] = None
        self._send_queue: asyncio.Queue = asyncio.Queue()
        self._send_task: Optional[asyncio.Task] = None
        self._identify_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()
        self._last_heartbeat_ack: float = time.monotonic()
        self._reconnect_attempts: int = 0
        self._max_reconnect_wait: float = 60.0

    async def connect(self, resume: bool = False) -> None:
        async with self._connect_lock:
            await self._do_connect(resume=resume)

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self._cancel_tasks()
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass

    async def send_json(self, data: Dict) -> None:
        await self._send_queue.put(json.dumps(data))

    async def send_heartbeat(self) -> None:
        await self.send_json({'op': opcodes.HEARTBEAT, 'd': self.sequence})

    async def update_presence(self, status: str = 'online', activities: list = None, afk: bool = False) -> None:
        await self.send_json({
            'op': opcodes.PRESENCE_UPDATE,
            'd': {
                'status': status,
                'activities': activities or [],
                'afk': afk,
                'since': 0,
            }
        })

    async def _do_connect(self, resume: bool = False) -> None:
        url = self.resume_url if resume and self.resume_url else self.GATEWAY_URL
        ua = self._get_user_agent()

        self.ws = await websockets.connect(
            url,
            compression=None,
            max_size=None,
            max_queue=512,
            open_timeout=20,
            close_timeout=5,
            ping_interval=None,
            ping_timeout=None,
            user_agent_header=ua,
            additional_headers={
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            }
        )

        self._send_queue = asyncio.Queue()
        self._send_task = asyncio.create_task(self._send_loop())
        self._recv_task = asyncio.create_task(self._receive_loop())
        self._recv_task.add_done_callback(self._on_recv_done)

    async def _cancel_tasks(self) -> None:
        for task in (self._send_task, self._recv_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except (asyncio.CancelledError, Exception):
                    pass
        if self.heartbeat:
            await self.heartbeat.stop()
            self.heartbeat = None

    def _on_recv_done(self, task: asyncio.Task) -> None:
        if task.cancelled() or self._closed:
            return
        exc = task.exception()
        if exc:
            asyncio.create_task(self._handle_disconnect(exc))

    def _get_user_agent(self) -> str:
        if self.spoofer:
            return self.spoofer.get_user_agent()
        return (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) discord/1.0.9262 Chrome/136.0.0.0 Electron/42.0.0 Safari/537.36'
        )

    async def _send_loop(self) -> None:
        while not self._closed:
            try:
                payload = await asyncio.wait_for(self._send_queue.get(), timeout=1.0)
                await self.ws.send(payload)
            except asyncio.TimeoutError:
                continue
            except (asyncio.CancelledError, websockets.exceptions.ConnectionClosed, Exception):
                break

    async def _receive_loop(self) -> None:
        try:
            async for raw in self.ws:
                try:
                    await self._handle_message(raw)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass
        except asyncio.CancelledError:
            raise
        except websockets.exceptions.ConnectionClosedOK:
            pass
        except websockets.exceptions.ConnectionClosedError as e:
            if not self._closed:
                raise RuntimeError(f'ws closed error code={e.code} reason={e.reason!r}') from e
        except Exception:
            if not self._closed:
                raise

    async def _handle_message(self, raw: str) -> None:
        data = json.loads(raw)
        op = data['op']
        d = data.get('d')
        s = data.get('s')
        t = data.get('t')

        if s is not None:
            self.sequence = s

        if op == opcodes.HELLO:
            interval = d['heartbeat_interval']
            if self.heartbeat:
                await self.heartbeat.stop()
            self.heartbeat = Heartbeat(self, interval)
            await self.heartbeat.start()
            await asyncio.sleep(interval / 1000.0 * random.random())
            if self.session_id and self.sequence:
                await self._send_resume()
            else:
                await self._send_identify()

        elif op == opcodes.HEARTBEAT_ACK:
            self._last_heartbeat_ack = time.monotonic()
            self._reconnect_attempts = 0
            if self.heartbeat:
                self.heartbeat.ack()

        elif op == opcodes.HEARTBEAT:
            await self.send_heartbeat()

        elif op == opcodes.RECONNECT:
            await self._handle_reconnect()

        elif op == opcodes.INVALID_SESSION:
            resumable = bool(d)
            if not resumable:
                self.session_id = None
                self.sequence = None
            await asyncio.sleep(random.uniform(1, 5))
            if resumable and self.session_id:
                await self._handle_reconnect()
            else:
                await self._send_identify()

        elif op == opcodes.DISPATCH:
            await self._handle_dispatch(t, d)

    async def _send_identify(self) -> None:
        async with self._identify_lock:
            await self.send_json({
                'op': opcodes.IDENTIFY,
                'd': {
                    'token': self.token,
                    'capabilities': 16381,
                    'properties': self._build_client_properties(),
                    'presence': {'status': 'online', 'since': 0, 'activities': [], 'afk': False},
                    'compress': False,
                    'client_state': {
                        'guild_versions': {},
                        'highest_last_message_id': '0',
                        'read_state_version': 0,
                        'user_guild_settings_version': -1,
                        'user_settings_version': -1,
                        'private_channels_version': '0',
                        'api_code_version': 0,
                    },
                    'intents': self._calculate_intents(),
                }
            })

    async def _send_resume(self) -> None:
        await self.send_json({
            'op': opcodes.RESUME,
            'd': {
                'token': self.token,
                'session_id': self.session_id,
                'seq': self.sequence,
            }
        })

    def _build_client_properties(self) -> Dict:
        if self.spoofer:
            return self.spoofer.get_identify_properties()
        return {
            'os': 'Windows',
            'browser': 'Discord Client',
            'device': '',
            'system_locale': 'en-US',
            'browser_user_agent': self._get_user_agent(),
            'browser_version': '1.0.9262',
            'os_version': '10.0.22631',
            'referrer': '',
            'referring_domain': '',
            'referrer_current': '',
            'referring_domain_current': '',
            'release_channel': 'stable',
            'client_build_number': 635180,
            'client_event_source': None,
            'has_client_mods': False,
        }

    def _calculate_intents(self) -> int:
        intents = 0
        intents |= (1 << 0)
        intents |= (1 << 1)
        intents |= (1 << 2)
        intents |= (1 << 9)
        intents |= (1 << 12)
        intents |= (1 << 15)
        return intents

    async def _handle_reconnect(self) -> None:
        if self._closed or self._reconnecting:
            return
        self._reconnecting = True
        try:
            await self._cancel_tasks()
            if self.ws:
                try:
                    await self.ws.close()
                except Exception:
                    pass
            await self._reconnect_loop(can_resume=bool(self.session_id and self.sequence))
        finally:
            self._reconnecting = False

    async def _handle_disconnect(self, exc: Exception) -> None:
        if self._closed or self._reconnecting:
            return

        can_resume = True
        if isinstance(exc, RuntimeError) and 'code=' in str(exc):
            try:
                code = int(str(exc).split('code=')[1].split(' ')[0])
                if code in _FATAL_CODES:
                    self._closed = True
                    self.session._ready.set()
                    raise RuntimeError(_FATAL_MESSAGES.get(code, f'Fatal gateway error code={code}'))
                can_resume = code not in _NO_RESUME_CODES
            except (IndexError, ValueError):
                pass

        self._reconnecting = True
        try:
            await self._cancel_tasks()
            if self.ws:
                try:
                    await self.ws.close()
                except Exception:
                    pass
            if not (can_resume and self.session_id and self.sequence):
                self.session_id = None
                self.sequence = None
            await self._reconnect_loop(can_resume=can_resume and bool(self.session_id))
        finally:
            self._reconnecting = False

    async def _reconnect_loop(self, can_resume: bool = True) -> None:
        self._reconnect_attempts = 0

        while not self._closed:
            attempt = self._reconnect_attempts
            if attempt > 0:
                await asyncio.sleep(min(self._max_reconnect_wait, (2 ** min(attempt, 7)) + random.uniform(0, 1)))

            try:
                async with self._connect_lock:
                    await self._do_connect(resume=can_resume)
                self._reconnect_attempts = 0
                return
            except asyncio.CancelledError:
                raise
            except Exception:
                self._reconnect_attempts += 1
                if self._reconnect_attempts >= 3:
                    self.session_id = None
                    self.sequence = None
                    can_resume = False

    async def _handle_zombie(self) -> None:
        if not self._closed:
            await self._handle_reconnect()

    async def _handle_dispatch(self, event: str, data: Dict) -> None:
        try:
            await self._dispatch(event, data)
        except asyncio.CancelledError:
            raise
        except Exception:
            pass

    async def _dispatch(self, event: str, data: Dict) -> None:
        session = self.session

        if event == 'READY':
            self.session_id = data['session_id']
            self.resume_url = data.get('resume_gateway_url')
            from ..entities.user import ClientUser
            from ..entities.guild import Guild
            session.user = ClientUser(data['user'], session)
            for g in data.get('guilds', []):
                try:
                    session.cache.add_guild(Guild(g, session))
                except Exception:
                    pass
            for rs in data.get('read_state', {}).get('entries', []):
                try:
                    from ..entities.read_state import ReadState
                    session.cache._read_states[rs['id']] = ReadState(rs, session)
                except Exception:
                    pass
            session._ready.set()
            session.dispatcher.dispatch('on_ready', session.user)

        elif event == 'RESUMED':
            session._ready.set()
            session.dispatcher.dispatch('on_resumed')

        elif event == 'MESSAGE_CREATE':
            from ..entities.message import Message
            msg = Message(data, session)
            session.cache.add_message(msg)
            if msg.author and msg.author.id != session.user.id:
                session.dispatcher.dispatch('on_message', msg)

        elif event == 'MESSAGE_UPDATE':
            from ..entities.message import Message
            old = session.cache.get_message(data['id'])
            msg = Message(data, session)
            session.cache.add_message(msg)
            session.dispatcher.dispatch('on_message_edit', old, msg)

        elif event == 'MESSAGE_DELETE':
            cached = session.cache.get_message(data['id'])
            session.cache.remove_message(data['id'])
            session.dispatcher.dispatch('on_message_delete', cached)

        elif event == 'GUILD_CREATE':
            from ..entities.guild import Guild
            guild = Guild(data, session)
            existing = session.cache.get_guild(guild.id)
            session.cache.add_guild(guild)
            if existing and getattr(existing, 'unavailable', False):
                session.dispatcher.dispatch('on_guild_available', guild)
            else:
                session.dispatcher.dispatch('on_guild_join', guild)

        elif event == 'GUILD_UPDATE':
            from ..entities.guild import Guild
            guild = Guild(data, session)
            session.cache.add_guild(guild)
            session.dispatcher.dispatch('on_guild_update', guild)

        elif event == 'GUILD_DELETE':
            guild = session.cache.get_guild(data['id'])
            session.cache.remove_guild(data['id'])
            session.dispatcher.dispatch('on_guild_remove', guild)

        elif event == 'CHANNEL_CREATE':
            from ..entities.channel import create_channel
            ch = create_channel(data, session)
            if ch:
                session.cache.add_channel(ch)
                session.dispatcher.dispatch('on_channel_create', ch)

        elif event == 'CHANNEL_UPDATE':
            from ..entities.channel import create_channel
            ch = create_channel(data, session)
            if ch:
                session.cache.add_channel(ch)
                session.dispatcher.dispatch('on_channel_update', ch)

        elif event == 'CHANNEL_DELETE':
            from ..entities.channel import create_channel
            ch = create_channel(data, session)
            if ch:
                session.cache.remove_channel(ch.id)
                session.dispatcher.dispatch('on_channel_delete', ch)

        elif event == 'TYPING_START':
            ch = session.get_channel(int(data['channel_id']))
            user = session.get_user(int(data['user_id']))
            session.dispatcher.dispatch('on_typing', ch, user, data['timestamp'])

        elif event == 'PRESENCE_UPDATE':
            user_data = data.get('user', {})
            if user_data:
                cached = session.cache.get_user(user_data.get('id'))
                if cached:
                    cached._update(user_data)
            from ..entities.presence import Presence
            session.dispatcher.dispatch('on_presence_update', Presence(data))

        elif event == 'USER_UPDATE':
            from ..entities.user import User
            if session.user and data.get('id') == session.user.id:
                session.user._update(data)
            session.dispatcher.dispatch('on_user_update', session.user or User(data, session))

        elif event == 'GUILD_MEMBER_ADD':
            from ..entities.member import Member
            session.dispatcher.dispatch('on_member_join', Member(data, session, data.get('guild_id')))

        elif event == 'GUILD_MEMBER_REMOVE':
            session.dispatcher.dispatch('on_member_remove', data.get('guild_id'), data.get('user', {}))

        elif event == 'GUILD_MEMBER_UPDATE':
            from ..entities.member import Member
            session.dispatcher.dispatch('on_member_update', Member(data, session, data.get('guild_id')))

        elif event == 'GUILD_ROLE_CREATE':
            from ..entities.role import Role
            session.dispatcher.dispatch('on_role_create', data.get('guild_id'), Role(data['role']))

        elif event == 'GUILD_ROLE_UPDATE':
            from ..entities.role import Role
            session.dispatcher.dispatch('on_role_update', data.get('guild_id'), Role(data['role']))

        elif event == 'GUILD_ROLE_DELETE':
            session.dispatcher.dispatch('on_role_delete', data.get('guild_id'), data.get('role_id'))

        elif event == 'MESSAGE_REACTION_ADD':
            from ..entities.reaction import Reaction
            session.dispatcher.dispatch('on_reaction_add', Reaction(data))

        elif event == 'MESSAGE_REACTION_REMOVE':
            from ..entities.reaction import Reaction
            session.dispatcher.dispatch('on_reaction_remove', Reaction(data))

        elif event == 'MESSAGE_REACTION_REMOVE_ALL':
            session.dispatcher.dispatch('on_reaction_clear', data.get('message_id'), data.get('channel_id'), data.get('guild_id'))

        elif event == 'MESSAGE_REACTION_REMOVE_EMOJI':
            from ..entities.reaction import ReactionEmoji
            session.dispatcher.dispatch('on_reaction_remove_emoji', data.get('message_id'), data.get('channel_id'), ReactionEmoji(data.get('emoji', {})))

        elif event == 'INTERACTION_CREATE':
            from ..interactions.interaction import Interaction
            session.dispatcher.dispatch('on_interaction', Interaction(data, session))

        elif event == 'RELATIONSHIP_ADD':
            from ..entities.relationship import Relationship
            session.dispatcher.dispatch('on_relationship_add', Relationship(data, session))

        elif event == 'RELATIONSHIP_REMOVE':
            from ..entities.relationship import Relationship
            session.dispatcher.dispatch('on_relationship_remove', Relationship(data, session))

        elif event == 'VOICE_STATE_UPDATE':
            from ..entities.voice_state_entity import VoiceStateEntity
            session.dispatcher.dispatch('on_voice_state_update', VoiceStateEntity(data, session))

        elif event == 'VOICE_SERVER_UPDATE':
            session.dispatcher.dispatch('on_voice_server_update', data)

        elif event == 'GUILD_SCHEDULED_EVENT_CREATE':
            from ..entities.scheduled_event import ScheduledEvent
            session.dispatcher.dispatch('on_scheduled_event_create', ScheduledEvent(data, session))

        elif event == 'GUILD_SCHEDULED_EVENT_UPDATE':
            from ..entities.scheduled_event import ScheduledEvent
            session.dispatcher.dispatch('on_scheduled_event_update', ScheduledEvent(data, session))

        elif event == 'GUILD_SCHEDULED_EVENT_DELETE':
            from ..entities.scheduled_event import ScheduledEvent
            session.dispatcher.dispatch('on_scheduled_event_delete', ScheduledEvent(data, session))

        elif event == 'STAGE_INSTANCE_CREATE':
            from ..entities.stage import StageInstance
            session.dispatcher.dispatch('on_stage_create', StageInstance(data, session))

        elif event == 'STAGE_INSTANCE_UPDATE':
            from ..entities.stage import StageInstance
            session.dispatcher.dispatch('on_stage_update', StageInstance(data, session))

        elif event == 'STAGE_INSTANCE_DELETE':
            from ..entities.stage import StageInstance
            session.dispatcher.dispatch('on_stage_delete', StageInstance(data, session))

        elif event == 'INVITE_CREATE':
            from ..entities.invite import Invite
            session.dispatcher.dispatch('on_invite_create', Invite(data, session))

        elif event == 'INVITE_DELETE':
            session.dispatcher.dispatch('on_invite_delete', data.get('code'), data.get('guild_id'), data.get('channel_id'))

        elif event == 'THREAD_CREATE':
            from ..entities.channel import create_channel
            thread = create_channel(data, session)
            if thread:
                session.cache.add_channel(thread)
                session.dispatcher.dispatch('on_thread_create', thread)

        elif event == 'THREAD_UPDATE':
            from ..entities.channel import create_channel
            thread = create_channel(data, session)
            if thread:
                session.cache.add_channel(thread)
                session.dispatcher.dispatch('on_thread_update', thread)

        elif event == 'THREAD_DELETE':
            session.cache.remove_channel(data.get('id', ''))
            session.dispatcher.dispatch('on_thread_delete', data)

        elif event == 'GUILD_STICKERS_UPDATE':
            session.dispatcher.dispatch('on_stickers_update', data.get('guild_id'), data.get('stickers', []))

        elif event == 'GUILD_SOUNDBOARD_SOUNDS_UPDATE':
            session.dispatcher.dispatch('on_soundboard_update', data.get('guild_id'), data.get('soundboard_sounds', []))

        elif event == 'MESSAGE_POLL_VOTE_ADD':
            session.dispatcher.dispatch('on_poll_vote_add', data.get('user_id'), data.get('message_id'), data.get('channel_id'), data.get('answer_id'), data.get('guild_id'))

        elif event == 'MESSAGE_POLL_VOTE_REMOVE':
            session.dispatcher.dispatch('on_poll_vote_remove', data.get('user_id'), data.get('message_id'), data.get('channel_id'), data.get('answer_id'), data.get('guild_id'))

        elif event == 'AUDIT_LOG_ENTRY_CREATE':
            from ..entities.audit_log import AuditLogEntry
            session.dispatcher.dispatch('on_audit_log_entry', AuditLogEntry(data))

        elif event == 'GUILD_BAN_ADD':
            from ..entities.ban import Ban
            session.dispatcher.dispatch('on_ban_add', Ban(data, data.get('guild_id', '')))

        elif event == 'GUILD_BAN_REMOVE':
            from ..entities.ban import Ban
            session.dispatcher.dispatch('on_ban_remove', Ban(data, data.get('guild_id', '')))

        elif event == 'GUILD_EMOJIS_UPDATE':
            session.dispatcher.dispatch('on_emojis_update', data.get('guild_id'), data.get('emojis', []))

        elif event == 'GUILD_INTEGRATIONS_UPDATE':
            session.dispatcher.dispatch('on_integrations_update', data.get('guild_id'))

        elif event == 'CHANNEL_PINS_UPDATE':
            session.dispatcher.dispatch('on_pins_update', data.get('channel_id'), data.get('guild_id'), data.get('last_pin_timestamp'))

        elif event == 'GUILD_MEMBERS_CHUNK':
            session.dispatcher.dispatch('on_members_chunk', data.get('guild_id'), data.get('members', []), data.get('chunk_index', 0), data.get('chunk_count', 1), data.get('nonce'))

        elif event == 'THREAD_MEMBERS_UPDATE':
            session.dispatcher.dispatch('on_thread_members_update', data.get('id'), data.get('guild_id'), data.get('member_count', 0), data.get('added_members', []), data.get('removed_member_ids', []))

        elif event == 'THREAD_LIST_SYNC':
            session.dispatcher.dispatch('on_thread_list_sync', data.get('guild_id'), data.get('channel_ids', []), data.get('threads', []))

        elif event == 'SESSIONS_REPLACE':
            session.dispatcher.dispatch('on_sessions_replace', data)

        elif event == 'VOICE_CHANNEL_STATUS_UPDATE':
            session.dispatcher.dispatch('on_voice_channel_status', data.get('id'), data.get('guild_id'), data.get('status'))

        elif event == 'WEBHOOKS_UPDATE':
            session.dispatcher.dispatch('on_webhooks_update', data.get('guild_id'), data.get('channel_id'))
