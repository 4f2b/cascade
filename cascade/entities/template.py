from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class GuildTemplate:
    __slots__ = (
        'code', 'name', 'description', 'usage_count',
        'creator_id', 'creator', 'created_at', 'updated_at',
        'source_guild_id', 'serialized_source_guild',
        'is_dirty', '_session',
    )

    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self.code: str = data['code']
        self.name: str = data['name']
        self.description: Optional[str] = data.get('description')
        self.usage_count: int = data.get('usage_count', 0)
        self.creator_id: Optional[str] = data.get('creator_id')
        self.creator: Optional[dict] = data.get('creator')
        self.created_at: Optional[str] = data.get('created_at')
        self.updated_at: Optional[str] = data.get('updated_at')
        self.source_guild_id: Optional[str] = data.get('source_guild_id')
        self.serialized_source_guild: Optional[dict] = data.get('serialized_source_guild')
        self.is_dirty: Optional[bool] = data.get('is_dirty')

    def __repr__(self) -> str:
        return f'<GuildTemplate code={self.code!r} name={self.name!r} guild_id={self.source_guild_id!r}>'

    def __str__(self) -> str:
        return self.name

    @property
    def url(self) -> str:
        return f'https://discord.new/{self.code}'

    async def sync(self) -> 'GuildTemplate':
        data = await self._session.rest.sync_guild_template(self.source_guild_id, self.code)
        return GuildTemplate(data, self._session)

    async def edit(self, *, name: str = None, description: str = None) -> 'GuildTemplate':
        kwargs = {}
        if name is not None:
            kwargs['name'] = name
        if description is not None:
            kwargs['description'] = description
        data = await self._session.rest.edit_guild_template(self.source_guild_id, self.code, **kwargs)
        return GuildTemplate(data, self._session)

    async def delete(self) -> None:
        await self._session.rest.delete_guild_template(self.source_guild_id, self.code)

    async def create_guild(self, name: str, icon: str = None) -> dict:
        return await self._session.rest.create_guild_from_template(self.code, name, icon)
