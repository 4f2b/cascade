from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class Note:
    __slots__ = ('user_id', 'content', '_session')

    def __init__(self, user_id: str, content: str, session: 'Session'):
        self.user_id: str = user_id
        self.content: str = content
        self._session = session

    def __repr__(self) -> str:
        return f'<Note user_id={self.user_id!r} content={self.content!r}>'

    def __str__(self) -> str:
        return self.content

    def __bool__(self) -> bool:
        return bool(self.content)

    async def edit(self, content: str) -> 'Note':
        await self._session.rest.set_user_note(self.user_id, content)
        self.content = content
        return self

    async def delete(self) -> None:
        await self._session.rest.set_user_note(self.user_id, '')
        self.content = ''
