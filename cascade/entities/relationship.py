from typing import Optional, Dict, Any
from enum import IntEnum


class RelationshipType(IntEnum):
    FRIEND = 1
    BLOCKED = 2
    INCOMING_REQUEST = 3
    OUTGOING_REQUEST = 4
    IMPLICIT = 5


class Relationship:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.type: RelationshipType = RelationshipType(data['type'])
        self.nickname: Optional[str] = data.get('nickname')
        self.since: Optional[str] = data.get('since')

        user = data.get('user', {})
        self.user_id: int = int(user.get('id', data.get('id', 0)))
        self.username: str = user.get('username', '')
        self.discriminator: str = user.get('discriminator', '0')
        self.avatar: Optional[str] = user.get('avatar')
        self.global_name: Optional[str] = user.get('global_name')
        self.bot: bool = user.get('bot', False)

    @property
    def is_friend(self) -> bool:
        return self.type == RelationshipType.FRIEND

    @property
    def is_blocked(self) -> bool:
        return self.type == RelationshipType.BLOCKED

    @property
    def is_incoming_request(self) -> bool:
        return self.type == RelationshipType.INCOMING_REQUEST

    @property
    def is_outgoing_request(self) -> bool:
        return self.type == RelationshipType.OUTGOING_REQUEST

    @property
    def display_name(self) -> str:
        return self.nickname or self.global_name or self.username

    @property
    def avatar_url(self) -> Optional[str]:
        if self.avatar:
            ext = 'gif' if self.avatar.startswith('a_') else 'png'
            return f'https://cdn.discordapp.com/avatars/{self.user_id}/{self.avatar}.{ext}'
        return None

    async def accept(self) -> None:
        await self._session.rest.accept_friend_request(self.user_id)

    async def remove(self) -> None:
        await self._session.rest.remove_relationship(self.user_id)

    async def block(self) -> None:
        await self._session.rest.block_user(str(self.user_id))

    async def set_nickname(self, nickname: Optional[str]) -> None:
        await self._session.rest.set_relationship_nickname(self.user_id, nickname)
        self.nickname = nickname

    async def open_dm(self) -> Dict[str, Any]:
        return await self._session.rest.create_dm(self.user_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': int(self.type),
            'nickname': self.nickname,
            'since': self.since,
            'user': {
                'id': str(self.user_id),
                'username': self.username,
                'discriminator': self.discriminator,
                'avatar': self.avatar,
                'global_name': self.global_name,
                'bot': self.bot
            }
        }
