from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class Emoji:
    def __init__(self, data: dict, session: 'Session' = None):
        self._session = session
        self._update(data)

    def _update(self, data: dict) -> None:
        self.id = data.get('id')
        self.name = data.get('name')
        self.roles = data.get('roles', [])
        self.user = data.get('user')
        self.require_colons = data.get('require_colons', True)
        self.managed = data.get('managed', False)
        self.animated = data.get('animated', False)
        self.available = data.get('available', True)

    @property
    def url(self) -> Optional[str]:
        if not self.id:
            return None
        ext = 'gif' if self.animated else 'png'
        return f'https://cdn.discordapp.com/emojis/{self.id}.{ext}'

    @property
    def is_custom(self) -> bool:
        return self.id is not None

    @property
    def is_unicode(self) -> bool:
        return self.id is None

    def __str__(self) -> str:
        if self.is_unicode:
            return self.name
        return f'<{"a" if self.animated else ""}:{self.name}:{self.id}>'

    def __repr__(self) -> str:
        return f'<Emoji id={self.id} name={self.name} animated={self.animated}>'

    def __eq__(self, other) -> bool:
        if isinstance(other, Emoji):
            return self.id == other.id if self.id else self.name == other.name
        if isinstance(other, str):
            return str(self) == other
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id) if self.id else hash(self.name)


class PartialEmoji:
    def __init__(self, name: str, id: str = None, animated: bool = False):
        self.name = name
        self.id = id
        self.animated = animated

    @property
    def url(self) -> Optional[str]:
        if not self.id:
            return None
        ext = 'gif' if self.animated else 'png'
        return f'https://cdn.discordapp.com/emojis/{self.id}.{ext}'

    @property
    def is_custom(self) -> bool:
        return self.id is not None

    @property
    def is_unicode(self) -> bool:
        return self.id is None

    def __str__(self) -> str:
        if self.is_unicode:
            return self.name
        return f'<{"a" if self.animated else ""}:{self.name}:{self.id}>'

    def __repr__(self) -> str:
        return f'<PartialEmoji name={self.name} id={self.id}>'

    @classmethod
    def from_str(cls, emoji_str: str) -> 'PartialEmoji':
        if not emoji_str.startswith('<'):
            return cls(name=emoji_str)
        
        parts = emoji_str.strip('<>').split(':')
        if len(parts) == 3:
            animated = parts[0] == 'a'
            name = parts[1]
            emoji_id = parts[2]
            return cls(name=name, id=emoji_id, animated=animated)
        
        return cls(name=emoji_str)
