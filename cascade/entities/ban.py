from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class Ban:
    __slots__ = ('guild_id', 'user_id', 'username', 'discriminator', 'avatar', 'reason', '_raw_user')

    def __init__(self, data: dict, guild_id: str):
        self.guild_id: str = guild_id
        self.reason: Optional[str] = data.get('reason')
        user = data.get('user', data)
        self._raw_user = user
        self.user_id: str = user.get('id', '')
        self.username: str = user.get('username', '')
        self.discriminator: str = user.get('discriminator', '0')
        self.avatar: Optional[str] = user.get('avatar')

    def __repr__(self) -> str:
        return f'<Ban user_id={self.user_id!r} username={self.username!r} reason={self.reason!r}>'

    def __str__(self) -> str:
        return self.username

    @property
    def avatar_url(self) -> Optional[str]:
        if not self.avatar:
            return None
        ext = 'gif' if self.avatar.startswith('a_') else 'png'
        return f'https://cdn.discordapp.com/avatars/{self.user_id}/{self.avatar}.{ext}'
