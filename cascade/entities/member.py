from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..core.session import Session
    from .guild import Guild


class Member:
    def __init__(self, data: dict, session: 'Session', guild_id: str):
        self._session = session
        self.guild_id = guild_id
        self._update(data)

    def _update(self, data: dict) -> None:
        from .user import User
        user_data = data.get('user', {})
        self.user = User(user_data, self._session) if user_data else None
        
        self.nick = data.get('nick')
        self.avatar = data.get('avatar')
        self.roles = data.get('roles', [])
        self.joined_at = None
        if data.get('joined_at'):
            self.joined_at = datetime.fromisoformat(data['joined_at'].rstrip('Z'))
        self.premium_since = None
        if data.get('premium_since'):
            self.premium_since = datetime.fromisoformat(data['premium_since'].rstrip('Z'))
        self.deaf = data.get('deaf', False)
        self.mute = data.get('mute', False)
        self.pending = data.get('pending', False)
        self.communication_disabled_until = data.get('communication_disabled_until')

    @property
    def id(self) -> str:
        return self.user.id if self.user else None

    @property
    def name(self) -> str:
        return self.nick or (self.user.name if self.user else '')

    @property
    def display_name(self) -> str:
        return self.nick or (self.user.global_name if self.user and self.user.global_name else (self.user.username if self.user else ''))

    @property
    def mention(self) -> str:
        return f'<@!{self.id}>' if self.nick else f'<@{self.id}>'

    @property
    def guild(self) -> Optional['Guild']:
        return self._session.get_guild(int(self.guild_id))

    @property
    def avatar_url(self) -> Optional[str]:
        if self.avatar:
            ext = 'gif' if self.avatar.startswith('a_') else 'png'
            return f'https://cdn.discordapp.com/guilds/{self.guild_id}/users/{self.id}/avatars/{self.avatar}.{ext}'
        return self.user.avatar_url if self.user else None

    @property
    def display_avatar(self) -> str:
        return self.avatar_url or (self.user.display_avatar if self.user else '')

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f'<Member id={self.id} name={self.display_name} guild={self.guild_id}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Member) and self.id == other.id and self.guild_id == other.guild_id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.id, self.guild_id))
