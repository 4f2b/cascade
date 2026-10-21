from typing import Optional, Dict, Any, List


class SoundboardSound:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.sound_id: int = int(data['sound_id'])
        self.name: str = data['name']
        self.volume: float = data.get('volume', 1.0)
        self.emoji_id: Optional[int] = int(data['emoji_id']) if data.get('emoji_id') else None
        self.emoji_name: Optional[str] = data.get('emoji_name')
        self.guild_id: Optional[int] = int(data['guild_id']) if data.get('guild_id') else None
        self.available: bool = data.get('available', True)

        user = data.get('user')
        self.creator_id: Optional[int] = int(user['id']) if user else None

    @property
    def is_default(self) -> bool:
        return self.guild_id is None

    async def send(self, channel_id: int) -> None:
        await self._session.rest.send_soundboard_sound(channel_id, self.sound_id, self.guild_id)

    async def edit(self, name: str = None, volume: float = None, emoji_id: int = None, emoji_name: str = None) -> 'SoundboardSound':
        if not self.guild_id:
            raise ValueError('Cannot edit a default sound')
        kwargs = {}
        if name is not None:
            kwargs['name'] = name
        if volume is not None:
            kwargs['volume'] = volume
        if emoji_id is not None:
            kwargs['emoji_id'] = str(emoji_id)
        if emoji_name is not None:
            kwargs['emoji_name'] = emoji_name
        data = await self._session.rest.modify_guild_soundboard_sound(self.guild_id, self.sound_id, **kwargs)
        self._update(data)
        return self

    async def delete(self) -> None:
        if not self.guild_id:
            raise ValueError('Cannot delete a default sound')
        await self._session.rest.delete_guild_soundboard_sound(self.guild_id, self.sound_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sound_id': str(self.sound_id),
            'name': self.name,
            'volume': self.volume,
            'emoji_id': str(self.emoji_id) if self.emoji_id else None,
            'emoji_name': self.emoji_name,
            'guild_id': str(self.guild_id) if self.guild_id else None,
            'available': self.available
        }
