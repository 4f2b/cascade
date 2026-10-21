from typing import Optional, List, Dict, Any
from enum import IntEnum


class TeamMemberRole(IntEnum):
    OWNER = 1
    ADMIN = 2
    DEVELOPER = 3
    READ_ONLY = 4


class TeamMember:
    def __init__(self, data: Dict[str, Any]):
        self.membership_state: int = data['membership_state']
        self.team_id: int = int(data['team_id'])
        self.role: str = data.get('role', 'developer')
        user = data.get('user', {})
        self.user_id: int = int(user.get('id', 0))
        self.username: str = user.get('username', '')
        self.discriminator: str = user.get('discriminator', '0')
        self.avatar: Optional[str] = user.get('avatar')

    @property
    def pending(self) -> bool:
        return self.membership_state == 1

    @property
    def accepted(self) -> bool:
        return self.membership_state == 2

    @property
    def avatar_url(self) -> Optional[str]:
        if self.avatar:
            return f'https://cdn.discordapp.com/avatars/{self.user_id}/{self.avatar}.png'
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'membership_state': self.membership_state,
            'team_id': str(self.team_id),
            'role': self.role,
            'user': {
                'id': str(self.user_id),
                'username': self.username,
                'discriminator': self.discriminator,
                'avatar': self.avatar
            }
        }


class Team:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self.id: int = int(data['id'])
        self.name: str = data['name']
        self.icon: Optional[str] = data.get('icon')
        self.owner_user_id: int = int(data['owner_user_id'])
        self.members: List[TeamMember] = [
            TeamMember(m) for m in data.get('members', [])
        ]
        self.payout_account_status: Optional[int] = data.get('payout_account_status')

    @property
    def icon_url(self) -> Optional[str]:
        if self.icon:
            return f'https://cdn.discordapp.com/team-icons/{self.id}/{self.icon}.png'
        return None

    @property
    def owner(self) -> Optional[TeamMember]:
        for m in self.members:
            if m.user_id == self.owner_user_id:
                return m
        return None

    async def edit(self, name: str = None, icon: str = None) -> 'Team':
        data = {}
        if name is not None:
            data['name'] = name
        if icon is not None:
            data['icon'] = icon
        result = await self._session.rest.modify_team(self.id, **data)
        self._update(result)
        return self

    async def invite_member(self, username: str, discriminator: str = None) -> None:
        await self._session.rest.invite_team_member(self.id, username, discriminator)

    async def remove_member(self, user_id: int) -> None:
        await self._session.rest.remove_team_member(self.id, user_id)

    async def transfer_ownership(self, user_id: int) -> None:
        await self._session.rest.transfer_team_ownership(self.id, user_id)

    async def delete(self) -> None:
        await self._session.rest.delete_team(self.id)

    def _update(self, data: Dict[str, Any]):
        self.name = data.get('name', self.name)
        self.icon = data.get('icon', self.icon)
        self.members = [TeamMember(m) for m in data.get('members', [])]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'name': self.name,
            'icon': self.icon,
            'owner_user_id': str(self.owner_user_id),
            'members': [m.to_dict() for m in self.members]
        }
