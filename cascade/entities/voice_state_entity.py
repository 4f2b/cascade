from typing import Optional, Dict, Any


class VoiceStateEntity:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.guild_id: Optional[int] = int(data['guild_id']) if data.get('guild_id') else None
        self.channel_id: Optional[int] = int(data['channel_id']) if data.get('channel_id') else None
        self.user_id: int = int(data['user_id'])
        self.session_id: str = data.get('session_id', '')
        self.deaf: bool = data.get('deaf', False)
        self.mute: bool = data.get('mute', False)
        self.self_deaf: bool = data.get('self_deaf', False)
        self.self_mute: bool = data.get('self_mute', False)
        self.self_stream: bool = data.get('self_stream', False)
        self.self_video: bool = data.get('self_video', False)
        self.suppress: bool = data.get('suppress', False)
        self.request_to_speak_timestamp: Optional[str] = data.get('request_to_speak_timestamp')
        self.member = data.get('member')

    @property
    def connected(self) -> bool:
        return self.channel_id is not None

    @property
    def guild(self):
        return self._session.cache.get_guild(str(self.guild_id)) if self.guild_id and self._session else None

    @property
    def channel(self):
        return self._session.cache.get_channel(str(self.channel_id)) if self.channel_id and self._session else None

    async def move_to(self, channel_id: Optional[int]) -> None:
        if self._session and self.guild_id:
            await self._session.update_voice_state(self.guild_id, channel_id=channel_id)

    async def disconnect(self) -> None:
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
            'suppress': self.suppress
        }
