from typing import Optional, List, TYPE_CHECKING
import asyncio
from datetime import datetime

if TYPE_CHECKING:
    from ..core.session import Session
    from .user import User
    from .channel import TextChannel


class Message:
    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self._update(data)

    def _update(self, data: dict) -> None:
        self.id = data['id']
        self.channel_id = data['channel_id']
        self.lobby_id = data.get('lobby_id')
        self.content = data.get('content', '')
        self.timestamp = datetime.fromisoformat(data['timestamp'].rstrip('Z'))
        self.edited_timestamp = None
        if data.get('edited_timestamp'):
            self.edited_timestamp = datetime.fromisoformat(data['edited_timestamp'].rstrip('Z'))
        self.tts = data.get('tts', False)
        self.mention_everyone = data.get('mention_everyone', False)
        self.pinned = data.get('pinned', False)
        self.type = data.get('type', 0)
        self.flags = data.get('flags', 0)
        self.guild_id = data.get('guild_id')
        self.webhook_id = data.get('webhook_id')
        self.application_id = data.get('application_id')
        self.nonce = data.get('nonce')

        from .user import User
        author_data = data.get('author', {})
        self.author = User(author_data, self._session) if author_data else None

        self.mentions: List['User'] = []
        for user_data in data.get('mentions', []):
            self.mentions.append(User(user_data, self._session))

        self.mention_roles = data.get('mention_roles', [])
        self.mention_channels = data.get('mention_channels', [])
        from .attachment import Attachment
        self.attachments = [Attachment(a) for a in data.get('attachments', [])]
        self.embeds = data.get('embeds', [])
        self.reactions = data.get('reactions', [])
        self.activity = data.get('activity')
        self.application = data.get('application')
        self.message_reference = data.get('message_reference')
        self.referenced_message = data.get('referenced_message')
        self.message_snapshots = data.get('message_snapshots', [])
        self.call = data.get('call')
        self.interaction = data.get('interaction')
        self.interaction_metadata = data.get('interaction_metadata')
        self.resolved = data.get('resolved')
        self.thread = data.get('thread')
        self.role_subscription_data = data.get('role_subscription_data')
        self.purchase_notification = data.get('purchase_notification')
        self.gift_info = data.get('gift_info')
        self.components = data.get('components', [])
        self.sticker_items = data.get('sticker_items', [])
        self.stickers = data.get('stickers', [])
        self.poll = data.get('poll')
        self.changelog_id = data.get('changelog_id')
        self.soundboard_sounds = data.get('soundboard_sounds', [])
        self.potions = data.get('potions', [])
        self.shared_client_theme = data.get('shared_client_theme')

    @property
    def channel(self) -> Optional['TextChannel']:
        return self._session.get_channel(int(self.channel_id))

    @property
    def guild(self):
        if self.guild_id:
            return self._session.get_guild(int(self.guild_id))
        return None

    @property
    def jump_url(self) -> str:
        guild_id = self.guild_id or '@me'
        return f'https://discord.com/channels/{guild_id}/{self.channel_id}/{self.id}'
    
    @property
    def created_at(self) -> datetime:
        return self.timestamp

    async def reply(self, content: str = None, mention: bool = False, **kwargs):
        kwargs['message_reference'] = {'message_id': self.id}
        if not mention:
            kwargs['allowed_mentions'] = {'replied_user': False}
        return await self.channel.send(content, **kwargs)

    async def edit(self, content: str = None, **kwargs):
        data = await self._session.rest.edit_message(self.channel_id, self.id, content, **kwargs)
        self._update(data)
        return self

    async def delete(self, delay: float = None) -> None:
        if delay:
            await asyncio.sleep(delay)
        await self._session.rest.delete_message(self.channel_id, self.id)

    async def pin(self) -> None:
        await self._session.rest.pin_message(self.channel_id, self.id)

    async def unpin(self) -> None:
        await self._session.rest.unpin_message(self.channel_id, self.id)

    async def add_reaction(self, emoji: str) -> None:
        await self._session.rest.add_reaction(self.channel_id, self.id, emoji)

    async def remove_reaction(self, emoji: str) -> None:
        await self._session.rest.remove_reaction(self.channel_id, self.id, emoji)
    
    async def clear_reactions(self, emoji: str = None) -> None:
        base = f'https://discord.com/api/v10/channels/{self.channel_id}/messages/{self.id}/reactions'
        if emoji:
            await self._session.rest.delete(f'{base}/{emoji}')
        else:
            await self._session.rest.delete(base)
    
    async def ack(self) -> None:
        await self._session.rest.ack_message(self.channel_id, self.id)

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return f'<Message id={self.id} author={self.author}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Message) and self.id == other.id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return int(self.id)
