from typing import Optional, Dict, Any, List
from enum import IntEnum


class ScheduledEventPrivacyLevel(IntEnum):
    GUILD_ONLY = 2


class ScheduledEventEntityType(IntEnum):
    STAGE_INSTANCE = 1
    VOICE = 2
    EXTERNAL = 3


class ScheduledEventStatus(IntEnum):
    SCHEDULED = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELED = 4


class ScheduledEvent:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.id: int = int(data['id'])
        self.guild_id: int = int(data['guild_id'])
        self.name: str = data['name']
        self.description: Optional[str] = data.get('description')
        self.scheduled_start_time: str = data['scheduled_start_time']
        self.scheduled_end_time: Optional[str] = data.get('scheduled_end_time')
        self.privacy_level: ScheduledEventPrivacyLevel = ScheduledEventPrivacyLevel(data['privacy_level'])
        self.status: ScheduledEventStatus = ScheduledEventStatus(data['status'])
        self.entity_type: ScheduledEventEntityType = ScheduledEventEntityType(data['entity_type'])
        self.entity_id: Optional[int] = int(data['entity_id']) if data.get('entity_id') else None
        self.channel_id: Optional[int] = int(data['channel_id']) if data.get('channel_id') else None
        self.creator_id: Optional[int] = int(data['creator_id']) if data.get('creator_id') else None
        self.user_count: Optional[int] = data.get('user_count')
        self.image: Optional[str] = data.get('image')
        self.entity_metadata: Optional[Dict] = data.get('entity_metadata')

    @property
    def cover_url(self) -> Optional[str]:
        if self.image:
            return f'https://cdn.discordapp.com/guild-events/{self.id}/{self.image}.png'
        return None

    @property
    def location(self) -> Optional[str]:
        if self.entity_metadata:
            return self.entity_metadata.get('location')
        return None

    async def edit(self, **kwargs) -> 'ScheduledEvent':
        data = await self._session.rest.modify_guild_scheduled_event(self.guild_id, self.id, **kwargs)
        self._update(data)
        return self

    async def delete(self) -> None:
        await self._session.rest.delete_guild_scheduled_event(self.guild_id, self.id)

    async def start(self) -> 'ScheduledEvent':
        return await self.edit(status=int(ScheduledEventStatus.ACTIVE))

    async def complete(self) -> 'ScheduledEvent':
        return await self.edit(status=int(ScheduledEventStatus.COMPLETED))

    async def cancel(self) -> 'ScheduledEvent':
        return await self.edit(status=int(ScheduledEventStatus.CANCELED))

    async def fetch_users(self, limit: int = 100, with_member: bool = False) -> List[Dict]:
        return await self._session.rest.get_guild_scheduled_event_users(
            self.guild_id, self.id, limit=limit, with_member=with_member
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'guild_id': str(self.guild_id),
            'name': self.name,
            'description': self.description,
            'scheduled_start_time': self.scheduled_start_time,
            'scheduled_end_time': self.scheduled_end_time,
            'status': int(self.status),
            'entity_type': int(self.entity_type),
            'user_count': self.user_count
        }
