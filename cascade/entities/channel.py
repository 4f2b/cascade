from typing import Optional, List, Union, TYPE_CHECKING, Dict
from ..types.enums import ChannelType

if TYPE_CHECKING:
    from ..core.session import Session
    from .message import Message
    from .user import User

class Channel:
    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self._update(data)

    def _update(self, data: dict) -> None:
        self.id = data['id']
        self.type = ChannelType(data['type'])
        self.name = data.get('name')
        self.guild_id = data.get('guild_id')

    @property
    def mention(self) -> str:
        return f'<#{self.id}>'

    def __str__(self) -> str:
        return self.name or ''

    def __repr__(self) -> str:
        return f'<Channel id={self.id} name={self.name}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Channel) and self.id == other.id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return int(self.id)


class TextChannel(Channel):
    def _update(self, data: dict) -> None:
        super()._update(data)
        self.position = data.get('position', 0)
        self.permission_overwrites = data.get('permission_overwrites', [])
        self.topic = data.get('topic')
        self.nsfw = data.get('nsfw', False)
        self.last_message_id = data.get('last_message_id')
        self.last_pin_timestamp = data.get('last_pin_timestamp')
        self.rate_limit_per_user = data.get('rate_limit_per_user', 0)
        self.parent_id = data.get('parent_id')
        self.default_auto_archive_duration = data.get('default_auto_archive_duration')
        self.default_thread_rate_limit_per_user = data.get('default_thread_rate_limit_per_user')
        self.permissions = data.get('permissions')
        self.flags = data.get('flags', 0)
        self.default_reaction_emoji = data.get('default_reaction_emoji')
        self.default_forum_layout = data.get('default_forum_layout')
        self.default_sort_order = data.get('default_sort_order')
        self.available_tags = data.get('available_tags', [])
        self.applied_tags = data.get('applied_tags', [])

    async def send(self, content: str = None, **kwargs) -> 'Message':
        data = await self._session.rest.send_message(self.id, content, **kwargs)
        from .message import Message
        message = Message(data, self._session)
        self._session.cache.add_message(message)
        return message

    async def fetch_message(self, message_id: int) -> 'Message':
        data = await self._session.rest.get_message(self.id, str(message_id))
        from .message import Message
        return Message(data, self._session)

    async def fetch_messages(self, limit: int = 50, before: int = None, after: int = None, around: int = None) -> List['Message']:
        params = {}
        if before:
            params['before'] = str(before)
        if after:
            params['after'] = str(after)
        if around:
            params['around'] = str(around)
        
        messages_data = await self._session.rest.get_messages(self.id, limit, **params)
        from .message import Message
        messages = [Message(data, self._session) for data in messages_data]
        for message in messages:
            self._session.cache.add_message(message)
        return messages

    async def trigger_typing(self) -> None:
        await self._session.rest.trigger_typing(self.id)

    async def purge(self, limit: int = 100, check=None, bulk: bool = True) -> List['Message']:
        messages = await self.fetch_messages(limit=limit)
        to_delete = []
        
        for message in messages:
            if check is None or check(message):
                to_delete.append(message)
        
        if bulk and len(to_delete) > 1:
            message_ids = [m.id for m in to_delete]
            for i in range(0, len(message_ids), 100):
                chunk = message_ids[i:i+100]
                if len(chunk) > 1:
                    await self._session.rest.bulk_delete_messages(self.id, chunk)
                elif len(chunk) == 1:
                    await self._session.rest.delete_message(self.id, chunk[0])
        else:
            for message in to_delete:
                await message.delete()
        
        return to_delete
    
    async def create_invite(self, **kwargs) -> Dict:
        return await self._session.rest.create_channel_invite(self.id, **kwargs)
    
    async def invites(self) -> List[Dict]:
        return await self._session.rest.get_channel_invites(self.id)

    def __repr__(self) -> str:
        return f'<TextChannel id={self.id} name={self.name}>'


class VoiceChannel(Channel):
    def _update(self, data: dict) -> None:
        super()._update(data)
        self.position = data.get('position', 0)
        self.permission_overwrites = data.get('permission_overwrites', [])
        self.bitrate = data.get('bitrate', 64000)
        self.user_limit = data.get('user_limit', 0)
        self.parent_id = data.get('parent_id')
        self.rtc_region = data.get('rtc_region')
        self.video_quality_mode = data.get('video_quality_mode', 1)

    def __repr__(self) -> str:
        return f'<VoiceChannel id={self.id} name={self.name}>'


class CategoryChannel(Channel):
    def _update(self, data: dict) -> None:
        super()._update(data)
        self.position = data.get('position', 0)

    def __repr__(self) -> str:
        return f'<CategoryChannel id={self.id} name={self.name}>'


class DMChannel(Channel):
    def _update(self, data: dict) -> None:
        super()._update(data)
        self.last_message_id = data.get('last_message_id')
        
        from .user import User
        recipients = data.get('recipients', [])
        self.recipient = User(recipients[0], self._session) if recipients else None

    async def send(self, content: str = None, **kwargs) -> 'Message':
        data = await self._session.rest.send_message(self.id, content, **kwargs)
        from .message import Message
        message = Message(data, self._session)
        self._session.cache.add_message(message)
        return message

    async def trigger_typing(self) -> None:
        await self._session.rest.trigger_typing(self.id)

    def __repr__(self) -> str:
        return f'<DMChannel id={self.id} recipient={self.recipient}>'


class GroupChannel(Channel):
    def _update(self, data: dict) -> None:
        super()._update(data)
        self.icon = data.get('icon')
        self.owner_id = data.get('owner_id')
        self.last_message_id = data.get('last_message_id')
        
        from .user import User
        self.recipients = [User(user_data, self._session) for user_data in data.get('recipients', [])]

    async def send(self, content: str = None, **kwargs) -> 'Message':
        data = await self._session.rest.send_message(self.id, content, **kwargs)
        from .message import Message
        message = Message(data, self._session)
        self._session.cache.add_message(message)
        return message

    async def trigger_typing(self) -> None:
        await self._session.rest.trigger_typing(self.id)

    def __repr__(self) -> str:
        return f'<GroupChannel id={self.id} name={self.name}>'


def create_channel(data: dict, session: 'Session') -> Optional[Channel]:
    channel_type = ChannelType(data['type'])

    if channel_type == ChannelType.GUILD_TEXT:
        return TextChannel(data, session)
    elif channel_type == ChannelType.DM:
        return DMChannel(data, session)
    elif channel_type == ChannelType.GUILD_VOICE:
        return VoiceChannel(data, session)
    elif channel_type == ChannelType.GROUP_DM:
        return GroupChannel(data, session)
    elif channel_type == ChannelType.GUILD_CATEGORY:
        return CategoryChannel(data, session)
    elif channel_type == ChannelType.GUILD_NEWS:
        return TextChannel(data, session)
    elif channel_type == ChannelType.GUILD_FORUM:
        from .forum import ForumChannel
        return ForumChannel(data, session)
    elif channel_type in (
        ChannelType.GUILD_PUBLIC_THREAD,
        ChannelType.GUILD_PRIVATE_THREAD,
        ChannelType.GUILD_NEWS_THREAD,
    ):
        return TextChannel(data, session)
    elif channel_type == ChannelType.GUILD_STAGE_VOICE:
        return VoiceChannel(data, session)
    else:
        return Channel(data, session)
