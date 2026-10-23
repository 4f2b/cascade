from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class AuditLogChange:
    __slots__ = ('key', 'before', 'after')

    def __init__(self, data: dict):
        self.key: str = data['key']
        self.before: Any = data.get('old_value')
        self.after: Any = data.get('new_value')

    def __repr__(self) -> str:
        return f'<AuditLogChange key={self.key!r} before={self.before!r} after={self.after!r}>'


class AuditLogEntry:
    __slots__ = (
        'id', 'guild_id', 'action_type', 'user_id', 'target_id',
        'reason', 'changes', 'options', 'extra',
    )

    ACTIONS = {
        1: 'guild_update',
        10: 'channel_create',
        11: 'channel_update',
        12: 'channel_delete',
        13: 'channel_overwrite_create',
        14: 'channel_overwrite_update',
        15: 'channel_overwrite_delete',
        20: 'member_kick',
        21: 'member_prune',
        22: 'member_ban_add',
        23: 'member_ban_remove',
        24: 'member_update',
        25: 'member_role_update',
        26: 'member_move',
        27: 'member_disconnect',
        28: 'bot_add',
        30: 'role_create',
        31: 'role_update',
        32: 'role_delete',
        40: 'invite_create',
        41: 'invite_update',
        42: 'invite_delete',
        50: 'webhook_create',
        51: 'webhook_update',
        52: 'webhook_delete',
        60: 'emoji_create',
        61: 'emoji_update',
        62: 'emoji_delete',
        72: 'message_delete',
        73: 'message_bulk_delete',
        74: 'message_pin',
        75: 'message_unpin',
        80: 'integration_create',
        81: 'integration_update',
        82: 'integration_delete',
        83: 'stage_instance_create',
        84: 'stage_instance_update',
        85: 'stage_instance_delete',
        90: 'sticker_create',
        91: 'sticker_update',
        92: 'sticker_delete',
        100: 'guild_scheduled_event_create',
        101: 'guild_scheduled_event_update',
        102: 'guild_scheduled_event_delete',
        110: 'thread_create',
        111: 'thread_update',
        112: 'thread_delete',
        121: 'application_command_permission_update',
        140: 'auto_moderation_rule_create',
        141: 'auto_moderation_rule_update',
        142: 'auto_moderation_rule_delete',
        143: 'auto_moderation_block_message',
        144: 'auto_moderation_flag_to_channel',
        145: 'auto_moderation_user_communication_disabled',
        150: 'creator_monetization_request_created',
        151: 'creator_monetization_terms_accepted',
        163: 'voice_channel_status_update',
        192: 'home_settings_create',
        193: 'home_settings_update',
    }

    def __init__(self, data: dict, guild_id: str = None):
        self.id: str = data['id']
        self.guild_id: Optional[str] = data.get('guild_id') or guild_id
        self.action_type: int = data['action_type']
        self.user_id: Optional[str] = data.get('user_id')
        self.target_id: Optional[str] = data.get('target_id')
        self.reason: Optional[str] = data.get('reason')
        self.changes: List[AuditLogChange] = [AuditLogChange(c) for c in data.get('changes', [])]
        self.options: Dict[str, Any] = data.get('options', {})
        self.extra: Dict[str, Any] = data

    def __repr__(self) -> str:
        return f'<AuditLogEntry id={self.id!r} action={self.action_name!r} user_id={self.user_id!r}>'

    @property
    def action_name(self) -> str:
        return self.ACTIONS.get(self.action_type, f'unknown_{self.action_type}')

    def get_change(self, key: str) -> Optional[AuditLogChange]:
        for c in self.changes:
            if c.key == key:
                return c
        return None


class AuditLog:
    __slots__ = ('entries', 'users', 'guild_id')

    def __init__(self, data: dict, guild_id: str):
        self.guild_id: str = guild_id
        self.entries: List[AuditLogEntry] = [
            AuditLogEntry(e, guild_id=guild_id) for e in data.get('audit_log_entries', [])
        ]
        self.users: List[dict] = data.get('users', [])

    def __repr__(self) -> str:
        return f'<AuditLog guild_id={self.guild_id!r} entries={len(self.entries)}>'

    def __iter__(self):
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def filter(self, action_type: int) -> List[AuditLogEntry]:
        return [e for e in self.entries if e.action_type == action_type]
