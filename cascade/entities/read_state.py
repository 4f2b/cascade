from typing import Optional, Dict, Any, List


class ReadState:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.channel_id: int = int(data['id'])
        self.last_message_id: Optional[int] = int(data['last_message_id']) if data.get('last_message_id') else None
        self.last_pin_timestamp: Optional[str] = data.get('last_pin_timestamp')
        self.mention_count: int = data.get('mention_count', 0)
        self.badge_count: int = data.get('badge_count', 0)
        self.flags: int = data.get('flags', 0)

    @property
    def unread(self) -> bool:
        return self.mention_count > 0

    async def ack(self) -> None:
        if self.last_message_id:
            await self._session.rest.ack_message(str(self.channel_id), str(self.last_message_id))

    async def ack_all(self) -> None:
        await self._session.rest.ack_channel(self.channel_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.channel_id),
            'last_message_id': str(self.last_message_id) if self.last_message_id else None,
            'mention_count': self.mention_count,
            'flags': self.flags
        }
