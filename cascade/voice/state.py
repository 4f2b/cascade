from typing import Optional, Dict, Any
from datetime import datetime


class VoiceState:
    def __init__(self, data: Dict[str, Any], session):
        self.session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.guild_id = int(data.get('guild_id', 0)) if data.get('guild_id') else None
        self.channel_id = int(data.get('channel_id', 0)) if data.get('channel_id') else None
        self.user_id = int(data['user_id'])
        self.member = data.get('member')
        self.session_id = data.get('session_id')
        self.deaf = data.get('deaf', False)
        self.mute = data.get('mute', False)
        self.self_deaf = data.get('self_deaf', False)
        self.self_mute = data.get('self_mute', False)
        self.self_stream = data.get('self_stream', False)
        self.self_video = data.get('self_video', False)
        self.suppress = data.get('suppress', False)
        self.request_to_speak_timestamp = data.get('request_to_speak_timestamp')

    @property
    def channel(self):
        return self.session.cache.get_channel(self.channel_id) if self.channel_id else None

    @property
    def guild(self):
        return self.session.cache.get_guild(self.guild_id) if self.guild_id else None

    async def move_to(self, channel_id: Optional[int]):
        if not self.guild_id:
            return
        
        await self.session.rest.modify_current_user_voice_state(
            self.guild_id,
            channel_id=channel_id
        )

    async def toggle_deaf(self):
        await self.session.gateway.send({
            'op': 4,
            'd': {
                'guild_id': str(self.guild_id) if self.guild_id else None,
                'channel_id': str(self.channel_id) if self.channel_id else None,
                'self_mute': self.self_mute,
                'self_deaf': not self.self_deaf
            }
        })

    async def toggle_mute(self):
        await self.session.gateway.send({
            'op': 4,
            'd': {
                'guild_id': str(self.guild_id) if self.guild_id else None,
                'channel_id': str(self.channel_id) if self.channel_id else None,
                'self_mute': not self.self_mute,
                'self_deaf': self.self_deaf
            }
        })

    async def disconnect(self):
        await self.move_to(None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'guild_id': str(self.guild_id) if self.guild_id else None,
            'channel_id': str(self.channel_id) if self.channel_id else None,
            'user_id': str(self.user_id),
            'session_id': self.session_id,
            'deaf': self.deaf,
            'mute': self.mute,
            'self_deaf': self.self_deaf,
            'self_mute': self.self_mute,
            'self_stream': self.self_stream,
            'self_video': self.self_video,
            'suppress': self.suppress,
            'request_to_speak_timestamp': self.request_to_speak_timestamp
        }
