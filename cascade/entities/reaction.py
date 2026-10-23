from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class ReactionEmoji:
    __slots__ = ('id', 'name', 'animated')

    def __init__(self, data: dict):
        self.id: Optional[str] = data.get('id')
        self.name: Optional[str] = data.get('name')
        self.animated: bool = data.get('animated', False)

    def __repr__(self) -> str:
        if self.id:
            return f'<ReactionEmoji id={self.id!r} name={self.name!r}>'
        return f'<ReactionEmoji name={self.name!r}>'

    def __str__(self) -> str:
        if self.id:
            prefix = 'a' if self.animated else ''
            return f'<{prefix}:{self.name}:{self.id}>'
        return self.name or ''

    @property
    def is_custom(self) -> bool:
        return self.id is not None

    @property
    def url(self) -> Optional[str]:
        if not self.id:
            return None
        ext = 'gif' if self.animated else 'png'
        return f'https://cdn.discordapp.com/emojis/{self.id}.{ext}'


class Reaction:
    __slots__ = (
        'message_id', 'channel_id', 'guild_id',
        'user_id', 'emoji', 'burst', 'type',
    )

    def __init__(self, data: dict):
        self.message_id: str = data['message_id']
        self.channel_id: str = data['channel_id']
        self.guild_id: Optional[str] = data.get('guild_id')
        self.user_id: str = data['user_id']
        self.emoji: ReactionEmoji = ReactionEmoji(data.get('emoji', {}))
        self.burst: bool = data.get('burst', False)
        self.type: int = data.get('type', 0)

    def __repr__(self) -> str:
        return (
            f'<Reaction user_id={self.user_id!r} '
            f'emoji={self.emoji!r} message_id={self.message_id!r}>'
        )
