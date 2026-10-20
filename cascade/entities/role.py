from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class Role:
    def __init__(self, data: dict, session: 'Session', guild_id: str):
        self._session = session
        self.guild_id = guild_id
        self._update(data)

    def _update(self, data: dict) -> None:
        self.id = data['id']
        self.name = data['name']
        self.color = data.get('color', 0)
        self.hoist = data.get('hoist', False)
        self.icon = data.get('icon')
        self.unicode_emoji = data.get('unicode_emoji')
        self.position = data.get('position', 0)
        self.permissions = data.get('permissions', '0')
        self.managed = data.get('managed', False)
        self.mentionable = data.get('mentionable', False)
        self.tags = data.get('tags', {})

    @property
    def mention(self) -> str:
        return f'<@&{self.id}>'

    @property
    def is_default(self) -> bool:
        return self.id == self.guild_id

    @property
    def is_bot_managed(self) -> bool:
        return 'bot_id' in self.tags

    @property
    def is_integration(self) -> bool:
        return 'integration_id' in self.tags

    @property
    def is_premium_subscriber(self) -> bool:
        return 'premium_subscriber' in self.tags

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Role id={self.id} name={self.name}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Role) and self.id == other.id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return int(self.id)

    def __lt__(self, other) -> bool:
        if not isinstance(other, Role):
            return NotImplemented
        if self.position < other.position:
            return True
        if self.position == other.position:
            return int(self.id) > int(other.id)
        return False

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __gt__(self, other) -> bool:
        return not self <= other

    def __ge__(self, other) -> bool:
        return not self < other
