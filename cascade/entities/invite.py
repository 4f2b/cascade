from typing import Optional, Dict, Any


class Invite:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.code: str = data['code']
        self.type: int = data.get('type', 0)
        self.approximate_member_count: int = data.get('approximate_member_count', 0)
        self.approximate_presence_count: int = data.get('approximate_presence_count', 0)
        self.expires_at: Optional[str] = data.get('expires_at')

        guild = data.get('guild')
        self.guild_id: Optional[int] = int(guild['id']) if guild else None
        self.guild_name: Optional[str] = guild['name'] if guild else None
        self.guild_icon: Optional[str] = guild.get('icon') if guild else None
        self.guild_description: Optional[str] = guild.get('description') if guild else None
        self.guild_features: list = guild.get('features', []) if guild else []
        self.guild_verification_level: Optional[int] = guild.get('verification_level') if guild else None
        self.guild_nsfw_level: Optional[int] = guild.get('nsfw_level') if guild else None
        self.guild_premium_subscription_count: Optional[int] = guild.get('premium_subscription_count') if guild else None

        channel = data.get('channel')
        self.channel_id: Optional[int] = int(channel['id']) if channel else None
        self.channel_name: Optional[str] = channel.get('name') if channel else None
        self.channel_type: Optional[int] = channel.get('type') if channel else None

        inviter = data.get('inviter')
        self.inviter_id: Optional[int] = int(inviter['id']) if inviter else None
        self.inviter_username: Optional[str] = inviter.get('username') if inviter else None

    @property
    def url(self) -> str:
        return f'https://discord.gg/{self.code}'

    @property
    def guild_icon_url(self) -> Optional[str]:
        if self.guild_id and self.guild_icon:
            return f'https://cdn.discordapp.com/icons/{self.guild_id}/{self.guild_icon}.png'
        return None

    async def accept(self) -> None:
        await self._session.rest.accept_invite(self.code)

    async def delete(self) -> None:
        await self._session.rest.delete_invite(self.code)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'approximate_member_count': self.approximate_member_count,
            'approximate_presence_count': self.approximate_presence_count,
            'expires_at': self.expires_at
        }
