from typing import Optional, List, Dict, Any
from enum import IntEnum


class AutoModTriggerType(IntEnum):
    KEYWORD = 1
    SPAM = 3
    KEYWORD_PRESET = 4
    MENTION_SPAM = 5


class AutoModEventType(IntEnum):
    MESSAGE_SEND = 1


class AutoModActionType(IntEnum):
    BLOCK_MESSAGE = 1
    SEND_ALERT_MESSAGE = 2
    TIMEOUT = 3


class KeywordPresetType(IntEnum):
    PROFANITY = 1
    SEXUAL_CONTENT = 2
    SLURS = 3


class AutoModAction:
    def __init__(self, data: Dict[str, Any]):
        self.type = AutoModActionType(data['type'])
        self.metadata = data.get('metadata', {})

    def to_dict(self) -> Dict[str, Any]:
        result = {'type': int(self.type)}
        if self.metadata:
            result['metadata'] = self.metadata
        return result

    @classmethod
    def block_message(cls) -> 'AutoModAction':
        return cls({'type': AutoModActionType.BLOCK_MESSAGE})

    @classmethod
    def send_alert(cls, channel_id: int) -> 'AutoModAction':
        return cls({
            'type': AutoModActionType.SEND_ALERT_MESSAGE,
            'metadata': {'channel_id': str(channel_id)}
        })

    @classmethod
    def timeout(cls, duration_seconds: int) -> 'AutoModAction':
        return cls({
            'type': AutoModActionType.TIMEOUT,
            'metadata': {'duration_seconds': duration_seconds}
        })


class AutoModTriggerMetadata:
    def __init__(self, data: Dict[str, Any]):
        self.keyword_filter = data.get('keyword_filter', [])
        self.regex_patterns = data.get('regex_patterns', [])
        self.presets = data.get('presets', [])
        self.allow_list = data.get('allow_list', [])
        self.mention_total_limit = data.get('mention_total_limit')
        self.mention_raid_protection_enabled = data.get('mention_raid_protection_enabled', False)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.keyword_filter:
            result['keyword_filter'] = self.keyword_filter
        if self.regex_patterns:
            result['regex_patterns'] = self.regex_patterns
        if self.presets:
            result['presets'] = self.presets
        if self.allow_list:
            result['allow_list'] = self.allow_list
        if self.mention_total_limit is not None:
            result['mention_total_limit'] = self.mention_total_limit
        if self.mention_raid_protection_enabled:
            result['mention_raid_protection_enabled'] = self.mention_raid_protection_enabled
        return result


class AutoModRule:
    def __init__(self, data: Dict[str, Any], session):
        self.session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.id = int(data['id'])
        self.guild_id = int(data['guild_id'])
        self.name = data['name']
        self.creator_id = int(data['creator_id'])
        self.event_type = AutoModEventType(data['event_type'])
        self.trigger_type = AutoModTriggerType(data['trigger_type'])
        self.trigger_metadata = AutoModTriggerMetadata(data.get('trigger_metadata', {}))
        self.actions = [AutoModAction(action) for action in data.get('actions', [])]
        self.enabled = data.get('enabled', True)
        self.exempt_roles = [int(rid) for rid in data.get('exempt_roles', [])]
        self.exempt_channels = [int(cid) for cid in data.get('exempt_channels', [])]

    async def edit(
        self,
        name: Optional[str] = None,
        event_type: Optional[AutoModEventType] = None,
        trigger_metadata: Optional[AutoModTriggerMetadata] = None,
        actions: Optional[List[AutoModAction]] = None,
        enabled: Optional[bool] = None,
        exempt_roles: Optional[List[int]] = None,
        exempt_channels: Optional[List[int]] = None
    ):
        data = {}
        if name is not None:
            data['name'] = name
        if event_type is not None:
            data['event_type'] = int(event_type)
        if trigger_metadata is not None:
            data['trigger_metadata'] = trigger_metadata.to_dict()
        if actions is not None:
            data['actions'] = [action.to_dict() for action in actions]
        if enabled is not None:
            data['enabled'] = enabled
        if exempt_roles is not None:
            data['exempt_roles'] = [str(rid) for rid in exempt_roles]
        if exempt_channels is not None:
            data['exempt_channels'] = [str(cid) for cid in exempt_channels]

        result = await self.session.rest.modify_automod_rule(
            self.guild_id,
            self.id,
            **data
        )
        self._update(result)

    async def delete(self):
        await self.session.rest.delete_automod_rule(self.guild_id, self.id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'guild_id': str(self.guild_id),
            'name': self.name,
            'creator_id': str(self.creator_id),
            'event_type': int(self.event_type),
            'trigger_type': int(self.trigger_type),
            'trigger_metadata': self.trigger_metadata.to_dict(),
            'actions': [action.to_dict() for action in self.actions],
            'enabled': self.enabled,
            'exempt_roles': [str(rid) for rid in self.exempt_roles],
            'exempt_channels': [str(cid) for cid in self.exempt_channels]
        }
