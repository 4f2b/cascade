from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class ForumTag:
    __slots__ = ('id', 'name', 'moderated', 'emoji_id', 'emoji_name')

    def __init__(self, data: dict):
        self.id: str = data['id']
        self.name: str = data['name']
        self.moderated: bool = data.get('moderated', False)
        self.emoji_id: Optional[str] = data.get('emoji_id')
        self.emoji_name: Optional[str] = data.get('emoji_name')

    def __repr__(self) -> str:
        return f'<ForumTag id={self.id!r} name={self.name!r}>'

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'moderated': self.moderated,
            'emoji_id': self.emoji_id,
            'emoji_name': self.emoji_name,
        }


class ForumChannel:
    __slots__ = (
        'id', 'guild_id', 'name', 'topic', 'position',
        'nsfw', 'parent_id', 'rate_limit_per_user',
        'default_auto_archive_duration', 'default_thread_rate_limit_per_user',
        'default_sort_order', 'default_forum_layout', 'default_reaction_emoji',
        'available_tags', 'flags', 'permission_overwrites',
        '_session',
    )

    SORT_LATEST = 0
    SORT_CREATION = 1

    LAYOUT_DEFAULT = 0
    LAYOUT_LIST = 1
    LAYOUT_GALLERY = 2

    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self.id: str = data['id']
        self.guild_id: Optional[str] = data.get('guild_id')
        self.name: str = data.get('name', '')
        self.topic: Optional[str] = data.get('topic')
        self.position: int = data.get('position', 0)
        self.nsfw: bool = data.get('nsfw', False)
        self.parent_id: Optional[str] = data.get('parent_id')
        self.rate_limit_per_user: int = data.get('rate_limit_per_user', 0)
        self.default_auto_archive_duration: Optional[int] = data.get('default_auto_archive_duration')
        self.default_thread_rate_limit_per_user: int = data.get('default_thread_rate_limit_per_user', 0)
        self.default_sort_order: Optional[int] = data.get('default_sort_order')
        self.default_forum_layout: int = data.get('default_forum_layout', 0)
        self.default_reaction_emoji: Optional[dict] = data.get('default_reaction_emoji')
        self.available_tags: List[ForumTag] = [ForumTag(t) for t in data.get('available_tags', [])]
        self.flags: int = data.get('flags', 0)
        self.permission_overwrites: list = data.get('permission_overwrites', [])

    def __repr__(self) -> str:
        return f'<ForumChannel id={self.id!r} name={self.name!r}>'

    def __str__(self) -> str:
        return self.name

    @property
    def mention(self) -> str:
        return f'<#{self.id}>'

    def get_tag(self, name: str) -> Optional[ForumTag]:
        name_lower = name.lower()
        for tag in self.available_tags:
            if tag.name.lower() == name_lower:
                return tag
        return None

    async def create_post(
        self,
        name: str,
        content: str = None,
        *,
        auto_archive_duration: int = 4320,
        rate_limit_per_user: int = 0,
        applied_tags: List[str] = None,
        embeds: list = None,
        components: list = None,
    ) -> 'ForumPost':
        message: dict = {}
        if content:
            message['content'] = content
        if embeds:
            message['embeds'] = [e.to_dict() if hasattr(e, 'to_dict') else e for e in embeds]
        if components:
            message['components'] = [c.to_dict() if hasattr(c, 'to_dict') else c for c in components]

        payload: dict = {
            'name': name,
            'auto_archive_duration': auto_archive_duration,
            'rate_limit_per_user': rate_limit_per_user,
            'message': message,
        }
        if applied_tags:
            payload['applied_tags'] = applied_tags

        data = await self._session.rest.create_forum_post(self.id, payload)
        return ForumPost(data, self._session)

    async def fetch_posts(self, archived: bool = False, limit: int = 50) -> List['ForumPost']:
        if archived:
            data = await self._session.rest.list_public_archived_threads(self.id, limit=limit)
        else:
            data = await self._session.rest.list_active_threads(self.guild_id)
        threads = data if isinstance(data, list) else data.get('threads', [])
        return [ForumPost(t, self._session) for t in threads if t.get('parent_id') == self.id]


class ForumPost:
    __slots__ = (
        'id', 'name', 'guild_id', 'parent_id', 'owner_id',
        'message_count', 'member_count', 'applied_tags',
        'archived', 'auto_archive_duration', 'locked',
        'rate_limit_per_user', 'flags', '_session',
    )

    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self.id: str = data['id']
        self.name: str = data.get('name', '')
        self.guild_id: Optional[str] = data.get('guild_id')
        self.parent_id: Optional[str] = data.get('parent_id')
        self.owner_id: Optional[str] = data.get('owner_id')
        self.message_count: int = data.get('message_count', 0)
        self.member_count: int = data.get('member_count', 0)
        self.applied_tags: List[str] = data.get('applied_tags', [])
        self.flags: int = data.get('flags', 0)
        self.rate_limit_per_user: int = data.get('rate_limit_per_user', 0)

        meta = data.get('thread_metadata', {})
        self.archived: bool = meta.get('archived', False)
        self.auto_archive_duration: int = meta.get('auto_archive_duration', 4320)
        self.locked: bool = meta.get('locked', False)

    def __repr__(self) -> str:
        return f'<ForumPost id={self.id!r} name={self.name!r} archived={self.archived}>'

    def __str__(self) -> str:
        return self.name

    @property
    def mention(self) -> str:
        return f'<#{self.id}>'

    @property
    def jump_url(self) -> str:
        return f'https://discord.com/channels/{self.guild_id}/{self.id}'

    async def send(self, content: str = None, **kwargs):
        from ..entities.message import Message
        data = await self._session.rest.send_message(self.id, content, **kwargs)
        return Message(data, self._session)

    async def edit(self, **kwargs) -> 'ForumPost':
        data = await self._session.rest.edit_channel(self.id, **kwargs)
        return ForumPost(data, self._session)

    async def close(self) -> None:
        await self._session.rest.edit_channel(self.id, archived=True, locked=True)

    async def reopen(self) -> None:
        await self._session.rest.edit_channel(self.id, archived=False, locked=False)

    async def pin(self) -> None:
        await self._session.rest.edit_channel(self.id, flags=self.flags | 2)

    async def unpin(self) -> None:
        await self._session.rest.edit_channel(self.id, flags=self.flags & ~2)

    async def delete(self) -> None:
        await self._session.rest.delete_channel(self.id)

    async def join(self) -> None:
        await self._session.rest.join_thread(self.id)

    async def leave(self) -> None:
        await self._session.rest.leave_thread(self.id)

    async def fetch_messages(self, limit: int = 50, **kwargs):
        from ..entities.message import Message
        data = await self._session.rest.get_messages(self.id, limit=limit, **kwargs)
        return [Message(m, self._session) for m in data]
