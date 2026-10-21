from typing import Optional, Dict, Any
from enum import IntEnum


class StagePrivacyLevel(IntEnum):
    PUBLIC = 1
    GUILD_ONLY = 2


class StageInstance:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.id: int = int(data['id'])
        self.guild_id: int = int(data['guild_id'])
        self.channel_id: int = int(data['channel_id'])
        self.topic: str = data['topic']
        self.privacy_level: StagePrivacyLevel = StagePrivacyLevel(data['privacy_level'])
        self.discoverable_disabled: bool = data.get('discoverable_disabled', False)
        self.guild_scheduled_event_id: Optional[int] = int(data['guild_scheduled_event_id']) if data.get('guild_scheduled_event_id') else None

    async def edit(self, topic: str = None, privacy_level: StagePrivacyLevel = None) -> 'StageInstance':
        kwargs = {}
        if topic is not None:
            kwargs['topic'] = topic
        if privacy_level is not None:
            kwargs['privacy_level'] = int(privacy_level)
        data = await self._session.rest.modify_stage_instance(self.channel_id, **kwargs)
        self._update(data)
        return self

    async def delete(self) -> None:
        await self._session.rest.delete_stage_instance(self.channel_id)

    async def request_to_speak(self) -> None:
        await self._session.rest.modify_current_user_voice_state(
            self.guild_id,
            channel_id=self.channel_id,
            request_to_speak_timestamp=__import__('datetime').datetime.utcnow().isoformat()
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'guild_id': str(self.guild_id),
            'channel_id': str(self.channel_id),
            'topic': self.topic,
            'privacy_level': int(self.privacy_level)
        }
