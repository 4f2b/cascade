from typing import Optional, List, Dict, Any
from enum import IntEnum


class StickerType(IntEnum):
    STANDARD = 1
    GUILD = 2


class StickerFormatType(IntEnum):
    PNG = 1
    APNG = 2
    LOTTIE = 3
    GIF = 4


class Sticker:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.id: int = int(data['id'])
        self.pack_id: Optional[int] = int(data['pack_id']) if data.get('pack_id') else None
        self.name: str = data['name']
        self.description: Optional[str] = data.get('description')
        self.tags: str = data.get('tags', '')
        self.type: StickerType = StickerType(data['type'])
        self.format_type: StickerFormatType = StickerFormatType(data['format_type'])
        self.available: bool = data.get('available', True)
        self.guild_id: Optional[int] = int(data['guild_id']) if data.get('guild_id') else None
        self.sort_value: Optional[int] = data.get('sort_value')

        user = data.get('user')
        self.creator_id: Optional[int] = int(user['id']) if user else None

    @property
    def url(self) -> str:
        if self.format_type == StickerFormatType.LOTTIE:
            return f'https://cdn.discordapp.com/stickers/{self.id}.json'
        ext = 'gif' if self.format_type == StickerFormatType.GIF else 'png'
        return f'https://cdn.discordapp.com/stickers/{self.id}.{ext}'

    @property
    def is_guild_sticker(self) -> bool:
        return self.type == StickerType.GUILD

    async def edit(self, name: str = None, description: str = None, tags: str = None) -> 'Sticker':
        if not self.guild_id:
            raise ValueError('Cannot edit a standard sticker')
        kwargs = {}
        if name is not None:
            kwargs['name'] = name
        if description is not None:
            kwargs['description'] = description
        if tags is not None:
            kwargs['tags'] = tags
        data = await self._session.rest.modify_guild_sticker(self.guild_id, self.id, **kwargs)
        self._update(data)
        return self

    async def delete(self) -> None:
        if not self.guild_id:
            raise ValueError('Cannot delete a standard sticker')
        await self._session.rest.delete_guild_sticker(self.guild_id, self.id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
            'type': int(self.type),
            'format_type': int(self.format_type)
        }
