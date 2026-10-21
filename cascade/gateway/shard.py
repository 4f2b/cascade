import asyncio
import base64
import json
import platform
import random
import sys
import time
import websockets
from typing import Optional, Any, Dict
from .heartbeat import Heartbeat
from . import opcodes


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
        self._last_heartbeat_ack = time.time()
        self._identify_lock = asyncio.Lock()
        self._ready_timeout = 15.0

    async def connect(self, resume: bool = False) -> None:
        url = self.resume_url if resume and self.resume_url else self.GATEWAY_URL
        
        extra_headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        
        self.ws = await websockets.connect(
            url,
            user_agent_header='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            compression=None,
            max_size=None,
            max_queue=512
        )
        asyncio.create_task(self._receive_loop())

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self.heartbeat:
            await self.heartbeat.stop()
        if self.ws:
            await self.ws.close()

    async def send_json(self, data: Dict) -> None:
        if self.ws:
            await self.ws.send(json.dumps(data))

    async def send_heartbeat(self) -> None:
        await self.send_json({
            'op': opcodes.HEARTBEAT,
            'd': self.sequence
        })

    def _build_client_properties(self) -> Dict:
        if self.spoofer:
            return self.spoofer.get_identify_properties()
        
        return {
            'os': 'Windows',
            'browser': 'Chrome',
            'device': '',
            'system_locale': 'en-US',
            'browser_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'browser_version': '131.0.0.0',
            'os_version': '10',
            'referrer': '',
            'referring_domain': '',
            'referrer_current': '',
            'referring_domain_current': '',
            'release_channel': 'stable',
            'client_build_number': 331288,
            'client_event_source': None,
        }

    def _calculate_capabilities(self) -> int:
        capabilities = 0
        capabilities |= (1 << 0)
        capabilities |= (1 << 1)
        capabilities |= (1 << 2)
        capabilities |= (1 << 3)
        capabilities |= (1 << 4)
        capabilities |= (1 << 5)
        capabilities |= (1 << 6)
        capabilities |= (1 << 7)
        capabilities |= (1 << 8)
        capabilities |= (1 << 9)
        capabilities |= (1 << 10)
        capabilities |= (1 << 11)
        capabilities |= (1 << 12)
        capabilities |= (1 << 13)
        return capabilities

    def _calculate_intents(self) -> int:
        intents = 0
        intents |= (1 << 0)   # GUILDS
        intents |= (1 << 1)   # GUILD_MEMBERS  
        intents |= (1 << 2)   # GUILD_MODERATION
        intents |= (1 << 9)   # GUILD_MESSAGES
        intents |= (1 << 12)  # DIRECT_MESSAGES
        intents |= (1 << 15)  # MESSAGE_CONTENT
        return intents

    async def send_identify(self) -> None:
        async with self._identify_lock:
            await asyncio.sleep(random.uniform(0.5, 2.5))
            await self.send_json({
                'op': opcodes.IDENTIFY,
                'd': {
                    'token': self.token,
                    'capabilities': self._calculate_capabilities(),
                    'properties': self._build_client_properties(),
                    'presence': {
                        'status': 'online',
                        'since': 0,
                        'activities': [],
                        'afk': False
                    },
                    'compress': False,
                    'client_state': {
                        'guild_versions': {},
                        'highest_last_message_id': '0',
                        'read_state_version': 0,
                        'user_guild_settings_version': -1,
                        'user_settings_version': -1,
                        'private_channels_version': '0',
                        'api_code_version': 0
                    },
                    'intents': self._calculate_intents()
                }
            })

    async def send_resume(self) -> None:
        await asyncio.sleep(random.uniform(0.5, 1.5))
        await self.send_json({
            'op': opcodes.RESUME,
            'd': {
                'token': self.token,
                'session_id': self.session_id,
                'seq': self.sequence
            }
        })

    async def _receive_loop(self) -> None:
        try:
            async for message in self.ws:
                try:
                    await self._handle_message(message)
                except Exception:
                    pass
        except websockets.exceptions.ConnectionClosed as e:
            if not self._closed:
                if e.code == 4004:
                    raise Exception('Authentication failed')
                elif e.code == 4014:
                    raise Exception('Privileged intents required')
                await self._handle_disconnect()
        except Exception as e:
            if not self._closed:
                await asyncio.sleep(random.uniform(1, 3))
                await self._handle_disconnect()

    async def _handle_message(self, message: str) -> None:
        try:
            data = json.loads(message)
            op = data['op']
            d = data.get('d')
            s = data.get('s')
            t = data.get('t')

            if s is not None:
                self.sequence = s

            if op == opcodes.HELLO:
                heartbeat_interval = d['heartbeat_interval']
                jitter = random.random()
                initial_delay = heartbeat_interval * jitter / 1000.0
                await asyncio.sleep(initial_delay)
                
                self.heartbeat = Heartbeat(self, heartbeat_interval)
                await self.heartbeat.start()
                
                if self.session_id and self.sequence:
                    await self.send_resume()
                else:
                    await self.send_identify()
            
            elif op == opcodes.HEARTBEAT_ACK:
                self._last_heartbeat_ack = time.time()
                if self.heartbeat:
                    self.heartbeat.ack()
            
            elif op == opcodes.HEARTBEAT:
                await self.send_heartbeat()
            
            elif op == opcodes.RECONNECT:
                await self._handle_reconnect()
            
            elif op == opcodes.INVALID_SESSION:
                resumable = d if isinstance(d, bool) else False
                if resumable and self.session_id and self.sequence:
                    await asyncio.sleep(random.uniform(1, 5))
                    await self._handle_reconnect()
                else:
                    self.session_id = None
                    self.sequence = None
                    await asyncio.sleep(random.uniform(1, 5))
                    await self.send_identify()
            
            elif op == opcodes.DISPATCH:
                await self._handle_dispatch(t, d)

        except Exception:
            pass

    async def _handle_dispatch(self, event: str, data: Dict) -> None:
        if event == 'READY':
            self.session_id = data['session_id']
            self.resume_url = data.get('resume_gateway_url')
            from ..entities.user import ClientUser
            self.session.user = ClientUser(data['user'], self.session)
            self.session._ready.set()
            self.session.dispatcher.dispatch('on_ready', self.session.user)
        
        elif event == 'RESUMED':
            self.session._ready.set()
            self.session.dispatcher.dispatch('on_resumed')
        
        elif event == 'MESSAGE_CREATE':
            from ..entities.message import Message
            message = Message(data, self.session)
            self.session.cache.add_message(message)
            
            if message.author and message.author.id != self.session.user.id:
                self.session.dispatcher.dispatch('on_message', message)
        
        elif event == 'MESSAGE_UPDATE':
            from ..entities.message import Message
            old_message = self.session.cache.get_message(data['id'])
            message = Message(data, self.session)
            self.session.cache.add_message(message)
            self.session.dispatcher.dispatch('on_message_edit', old_message, message)
        
        elif event == 'MESSAGE_DELETE':
            message_id = data['id']
            cached = self.session.cache.get_message(message_id)
            self.session.cache.remove_message(message_id)
            self.session.dispatcher.dispatch('on_message_delete', cached)
        
        elif event == 'GUILD_CREATE':
            from ..entities.guild import Guild
            guild = Guild(data, self.session)
            self.session.cache.add_guild(guild)
            self.session.dispatcher.dispatch('on_guild_join', guild)
        
        elif event == 'GUILD_DELETE':
            guild_id = data['id']
            guild = self.session.cache.get_guild(guild_id)
            self.session.cache.remove_guild(guild_id)
            self.session.dispatcher.dispatch('on_guild_remove', guild)
        
        elif event == 'CHANNEL_CREATE':
            from ..entities.channel import create_channel
            channel = create_channel(data, self.session)
            if channel:
                self.session.cache.add_channel(channel)
                self.session.dispatcher.dispatch('on_channel_create', channel)
        
        elif event == 'CHANNEL_UPDATE':
            from ..entities.channel import create_channel
            channel = create_channel(data, self.session)
            if channel:
                self.session.cache.add_channel(channel)
                self.session.dispatcher.dispatch('on_channel_update', channel)
        
        elif event == 'CHANNEL_DELETE':
            from ..entities.channel import create_channel
            channel = create_channel(data, self.session)
            if channel:
                self.session.cache.remove_channel(channel.id)
                self.session.dispatcher.dispatch('on_channel_delete', channel)
        
        elif event == 'TYPING_START':
            channel_id = data['channel_id']
            user_id = data['user_id']
            timestamp = data['timestamp']
            
            channel = self.session.get_channel(int(channel_id))
            user = self.session.get_user(int(user_id))
            
            self.session.dispatcher.dispatch('on_typing', channel, user, timestamp)
        
        elif event == 'PRESENCE_UPDATE':
            from ..entities.user import User
            user_data = data.get('user', {})
            if user_data:
                user_id = user_data.get('id')
                cached_user = self.session.cache.get_user(user_id)
                if cached_user:
                    cached_user._update(user_data)
            
            self.session.dispatcher.dispatch('on_presence_update', data)
        
        elif event == 'USER_UPDATE':
            from ..entities.user import User
            if self.session.user and data.get('id') == self.session.user.id:
                self.session.user._update(data)
            self.session.dispatcher.dispatch('on_user_update', data)
        
        elif event == 'RELATIONSHIP_ADD':
            from ..entities.relationship import Relationship
            rel = Relationship(data, self.session)
            self.session.dispatcher.dispatch('on_relationship_add', rel)

        elif event == 'RELATIONSHIP_REMOVE':
            from ..entities.relationship import Relationship
            rel = Relationship(data, self.session)
            self.session.dispatcher.dispatch('on_relationship_remove', rel)

        elif event == 'GUILD_SCHEDULED_EVENT_CREATE':
            from ..entities.scheduled_event import ScheduledEvent
            event_obj = ScheduledEvent(data, self.session)
            self.session.dispatcher.dispatch('on_scheduled_event_create', event_obj)

        elif event == 'GUILD_SCHEDULED_EVENT_UPDATE':
            from ..entities.scheduled_event import ScheduledEvent
            event_obj = ScheduledEvent(data, self.session)
            self.session.dispatcher.dispatch('on_scheduled_event_update', event_obj)

        elif event == 'GUILD_SCHEDULED_EVENT_DELETE':
            from ..entities.scheduled_event import ScheduledEvent
            event_obj = ScheduledEvent(data, self.session)
            self.session.dispatcher.dispatch('on_scheduled_event_delete', event_obj)

        elif event == 'STAGE_INSTANCE_CREATE':
            from ..entities.stage import StageInstance
            stage = StageInstance(data, self.session)
            self.session.dispatcher.dispatch('on_stage_create', stage)

        elif event == 'STAGE_INSTANCE_UPDATE':
            from ..entities.stage import StageInstance
            stage = StageInstance(data, self.session)
            self.session.dispatcher.dispatch('on_stage_update', stage)

        elif event == 'STAGE_INSTANCE_DELETE':
            from ..entities.stage import StageInstance
            stage = StageInstance(data, self.session)
            self.session.dispatcher.dispatch('on_stage_delete', stage)

        elif event == 'GUILD_STICKERS_UPDATE':
            guild_id = data.get('guild_id')
            stickers = data.get('stickers', [])
            self.session.dispatcher.dispatch('on_stickers_update', guild_id, stickers)

        elif event == 'GUILD_SOUNDBOARD_SOUNDS_UPDATE':
            guild_id = data.get('guild_id')
            sounds = data.get('soundboard_sounds', [])
            self.session.dispatcher.dispatch('on_soundboard_update', guild_id, sounds)

        elif event == 'MESSAGE_POLL_VOTE_ADD':
            self.session.dispatcher.dispatch('on_poll_vote_add', data)

        elif event == 'MESSAGE_POLL_VOTE_REMOVE':
            self.session.dispatcher.dispatch('on_poll_vote_remove', data)

        elif event == 'VOICE_STATE_UPDATE':
            from ..entities.voice_state_entity import VoiceStateEntity
            state = VoiceStateEntity(data, self.session)
            self.session.dispatcher.dispatch('on_voice_state_update', state)

        elif event == 'INVITE_CREATE':
            from ..entities.invite import Invite
            invite = Invite(data, self.session)
            self.session.dispatcher.dispatch('on_invite_create', invite)

        elif event == 'INVITE_DELETE':
            self.session.dispatcher.dispatch('on_invite_delete', data.get('code'), data.get('guild_id'), data.get('channel_id'))

    async def _handle_reconnect(self) -> None:
        if self._closed:
            return
        await self.close()
        await asyncio.sleep(random.uniform(2, 5))
        try:
            await self.connect(resume=True)
            if self.session_id and self.sequence:
                await self.send_resume()
            else:
                await self.send_identify()
        except Exception:
            await asyncio.sleep(random.uniform(3, 7))
            await self.connect()

    async def _handle_disconnect(self) -> None:
        if self._closed:
            return
        
        await asyncio.sleep(random.uniform(1, 3))
        
        if self.session_id and self.sequence:
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    await self.connect(resume=True)
                    await self.send_resume()
                    return
                except Exception:
                    if attempt < max_retries - 1:
                        backoff = min(300, (2 ** attempt) + random.uniform(0, 1))
                        await asyncio.sleep(backoff)
                    else:
                        self.session_id = None
                        self.sequence = None
        
        await self.connect()

    async def _handle_zombie(self) -> None:
        if self._closed:
            return
        await self.close()
        await asyncio.sleep(random.uniform(1, 3))
        
        if self.session_id and self.sequence:
            try:
                await self.connect(resume=True)
                await self.send_resume()
            except Exception:
                await asyncio.sleep(random.uniform(2, 4))
                await self.connect()
        else:
            await self.connect()
