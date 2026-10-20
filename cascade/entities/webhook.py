from typing import Optional
from dataclasses import dataclass
from ..types.enums import WebhookType

@dataclass
class Webhook:
    id: int
    type: WebhookType
    guild_id: Optional[int]
    channel_id: int
    name: Optional[str]
    avatar: Optional[str]
    token: Optional[str] = None
    application_id: Optional[int] = None
    user_id: Optional[int] = None
    source_guild_id: Optional[int] = None
    source_channel_id: Optional[int] = None
    url: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Webhook':
        return cls(
            id=int(data['id']),
            type=WebhookType(data['type']),
            guild_id=int(data['guild_id']) if data.get('guild_id') else None,
            channel_id=int(data['channel_id']),
            name=data.get('name'),
            avatar=data.get('avatar'),
            token=data.get('token'),
            application_id=int(data['application_id']) if data.get('application_id') else None,
            user_id=int(data['user']['id']) if data.get('user') else None,
            source_guild_id=int(data['source_guild']['id']) if data.get('source_guild') else None,
            source_channel_id=int(data['source_channel']['id']) if data.get('source_channel') else None,
            url=data.get('url')
        )
    
    @property
    def avatar_url(self) -> Optional[str]:
        if self.avatar:
            return f'https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png'
        return None
    
    @property
    def default_avatar_url(self) -> str:
        return f'https://cdn.discordapp.com/embed/avatars/{int(self.id) % 5}.png'
