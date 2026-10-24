from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.embed import Embed


class AllowedMentions:
    __slots__ = ('everyone', 'users', 'roles', 'replied_user', '_user_ids', '_role_ids')

    def __init__(
        self,
        *,
        everyone: bool = False,
        users: bool = True,
        roles: bool = True,
        replied_user: bool = True,
        user_ids: List[str] = None,
        role_ids: List[str] = None,
    ):
        self.everyone = everyone
        self.users = users
        self.roles = roles
        self.replied_user = replied_user
        self._user_ids: Optional[List[str]] = user_ids
        self._role_ids: Optional[List[str]] = role_ids

    def to_dict(self) -> dict:
        parse = []
        if self.everyone:
            parse.append('everyone')
        if self.users and not self._user_ids:
            parse.append('users')
        if self.roles and not self._role_ids:
            parse.append('roles')

        data: dict = {'parse': parse, 'replied_user': self.replied_user}
        if self._user_ids is not None:
            data['users'] = self._user_ids
        if self._role_ids is not None:
            data['roles'] = self._role_ids
        return data

    @classmethod
    def none(cls) -> 'AllowedMentions':
        return cls(everyone=False, users=False, roles=False, replied_user=False)

    @classmethod
    def all(cls) -> 'AllowedMentions':
        return cls(everyone=True, users=True, roles=True, replied_user=True)


class MessageBuilder:
    __slots__ = (
        '_content', '_embeds', '_components', '_allowed_mentions',
        '_reply_to', '_tts', '_flags', '_nonce', '_sticker_ids',
    )

    def __init__(self, content: str = None):
        self._content: Optional[str] = content
        self._embeds: List[dict] = []
        self._components: List[dict] = []
        self._allowed_mentions: Optional[AllowedMentions] = None
        self._reply_to: Optional[str] = None
        self._tts: bool = False
        self._flags: int = 0
        self._nonce: Optional[str] = None
        self._sticker_ids: List[str] = []

    def content(self, text: str) -> 'MessageBuilder':
        self._content = text
        return self

    def embed(self, embed: 'Embed') -> 'MessageBuilder':
        self._embeds.append(embed.to_dict() if hasattr(embed, 'to_dict') else embed)
        return self

    def embeds(self, *embeds: 'Embed') -> 'MessageBuilder':
        for e in embeds:
            self.embed(e)
        return self

    def component(self, row) -> 'MessageBuilder':
        self._components.append(row.to_dict() if hasattr(row, 'to_dict') else row)
        return self

    def components(self, *rows) -> 'MessageBuilder':
        for r in rows:
            self.component(r)
        return self

    def reply(self, message_id: str, mention: bool = False) -> 'MessageBuilder':
        self._reply_to = message_id
        if not mention:
            if self._allowed_mentions is None:
                self._allowed_mentions = AllowedMentions(replied_user=False)
            else:
                self._allowed_mentions.replied_user = False
        return self

    def mention(self, *, everyone: bool = False, users: bool = True, roles: bool = True, replied_user: bool = True) -> 'MessageBuilder':
        self._allowed_mentions = AllowedMentions(everyone=everyone, users=users, roles=roles, replied_user=replied_user)
        return self

    def suppress_mentions(self) -> 'MessageBuilder':
        self._allowed_mentions = AllowedMentions.none()
        return self

    def tts(self, value: bool = True) -> 'MessageBuilder':
        self._tts = value
        return self

    def suppress_embeds(self) -> 'MessageBuilder':
        self._flags |= 1 << 2
        return self

    def ephemeral(self) -> 'MessageBuilder':
        self._flags |= 1 << 6
        return self

    def nonce(self, value: str) -> 'MessageBuilder':
        self._nonce = value
        return self

    def sticker(self, sticker_id: str) -> 'MessageBuilder':
        self._sticker_ids.append(sticker_id)
        return self

    def build(self) -> dict:
        payload: dict = {}

        if self._content is not None:
            payload['content'] = self._content
        if self._embeds:
            payload['embeds'] = self._embeds
        if self._components:
            payload['components'] = self._components
        if self._tts:
            payload['tts'] = True
        if self._flags:
            payload['flags'] = self._flags
        if self._nonce is not None:
            payload['nonce'] = self._nonce
        if self._sticker_ids:
            payload['sticker_ids'] = self._sticker_ids
        if self._allowed_mentions is not None:
            payload['allowed_mentions'] = self._allowed_mentions.to_dict()
        if self._reply_to is not None:
            payload['message_reference'] = {'message_id': self._reply_to}

        return payload

    def __repr__(self) -> str:
        return f'<MessageBuilder content={self._content!r} embeds={len(self._embeds)} components={len(self._components)}>'
