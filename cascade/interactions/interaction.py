from typing import Optional, Dict, Any, List
from enum import IntEnum


class InteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionResponseType(IntEnum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class Interaction:
    def __init__(self, data: Dict[str, Any], session):
        self.session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.id = int(data['id'])
        self.application_id = int(data['application_id'])
        self.type = InteractionType(data['type'])
        self.token = data['token']
        self.version = data['version']
        
        self.guild_id = int(data['guild_id']) if 'guild_id' in data else None
        self.channel_id = int(data['channel_id']) if 'channel_id' in data else None
        self.user_id = int(data['user']['id']) if 'user' in data else None
        self.member = data.get('member')
        self.message = data.get('message')
        self.data_payload = data.get('data', {})
        
        self.custom_id = self.data_payload.get('custom_id')
        self.component_type = self.data_payload.get('component_type')
        self.values = self.data_payload.get('values', [])
        self.components = self.data_payload.get('components', [])

    async def respond(
        self,
        type: InteractionResponseType,
        *,
        content: Optional[str] = None,
        components: Optional[List] = None,
        flags: Optional[int] = None
    ):
        data = {}
        if content:
            data['content'] = content
        if components:
            data['components'] = [c.to_dict() for c in components]
        if flags:
            data['flags'] = flags

        await self.session.rest.create_interaction_response(
            self.id,
            self.token,
            type=int(type),
            data=data
        )

    async def send_message(self, content: str, **kwargs):
        await self.respond(
            InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            content=content,
            **kwargs
        )

    async def defer(self):
        await self.respond(InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE)

    async def update(self, content: str, **kwargs):
        await self.respond(
            InteractionResponseType.UPDATE_MESSAGE,
            content=content,
            **kwargs
        )

    async def send_modal(self, modal: 'Modal'):
        await self.session.rest.create_interaction_response(
            self.id,
            self.token,
            type=int(InteractionResponseType.MODAL),
            data=modal.to_dict()
        )

    async def followup(self, content: str, **kwargs):
        return await self.session.rest.create_followup_message(
            self.application_id,
            self.token,
            content=content,
            **kwargs
        )

    async def edit_original(self, content: str, **kwargs):
        return await self.session.rest.edit_original_interaction_response(
            self.application_id,
            self.token,
            content=content,
            **kwargs
        )

    async def delete_original(self):
        await self.session.rest.delete_original_interaction_response(
            self.application_id,
            self.token
        )
