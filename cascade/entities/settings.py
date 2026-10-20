from typing import Optional, List
from dataclasses import dataclass
from ..types.enums import StatusType

@dataclass
class UserSettings:
    locale: str
    theme: str
    status: StatusType
    show_current_game: bool
    default_guilds_restricted: bool
    inline_attachment_media: bool
    inline_embed_media: bool
    gif_auto_play: bool
    render_embeds: bool
    render_reactions: bool
    animate_emoji: bool
    enable_tts_command: bool
    message_display_compact: bool
    convert_emoticons: bool
    explicit_content_filter: int
    disable_games_tab: bool
    developer_mode: bool
    detect_platform_accounts: bool
    stream_notifications_enabled: bool
    allow_accessibility_detection: bool
    native_phone_integration_enabled: bool
    timezone_offset: int
    friend_source_flags: Dict[str, bool]
    guild_positions: List[int]
    restricted_guilds: List[int]
    custom_status: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserSettings':
        return cls(
            locale=data.get('locale', 'en-US'),
            theme=data.get('theme', 'dark'),
            status=StatusType(data.get('status', 'online')),
            show_current_game=data.get('show_current_game', True),
            default_guilds_restricted=data.get('default_guilds_restricted', False),
            inline_attachment_media=data.get('inline_attachment_media', True),
            inline_embed_media=data.get('inline_embed_media', True),
            gif_auto_play=data.get('gif_auto_play', True),
            render_embeds=data.get('render_embeds', True),
            render_reactions=data.get('render_reactions', True),
            animate_emoji=data.get('animate_emoji', True),
            enable_tts_command=data.get('enable_tts_command', True),
            message_display_compact=data.get('message_display_compact', False),
            convert_emoticons=data.get('convert_emoticons', True),
            explicit_content_filter=data.get('explicit_content_filter', 1),
            disable_games_tab=data.get('disable_games_tab', False),
            developer_mode=data.get('developer_mode', False),
            detect_platform_accounts=data.get('detect_platform_accounts', True),
            stream_notifications_enabled=data.get('stream_notifications_enabled', True),
            allow_accessibility_detection=data.get('allow_accessibility_detection', True),
            native_phone_integration_enabled=data.get('native_phone_integration_enabled', True),
            timezone_offset=data.get('timezone_offset', 0),
            friend_source_flags=data.get('friend_source_flags', {}),
            guild_positions=[int(g) for g in data.get('guild_positions', [])],
            restricted_guilds=[int(g) for g in data.get('restricted_guilds', [])],
            custom_status=data.get('custom_status')
        )
