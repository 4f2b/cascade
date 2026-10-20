from typing import TypedDict, Optional, List, Any


class UserPayload(TypedDict, total=False):
    id: str
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: Optional[str]
    accent_color: Optional[int]
    locale: str
    verified: bool
    email: Optional[str]
    flags: int
    premium_type: int
    public_flags: int


class MessagePayload(TypedDict, total=False):
    id: str
    channel_id: str
    author: UserPayload
    content: str
    timestamp: str
    edited_timestamp: Optional[str]
    tts: bool
    mention_everyone: bool
    mentions: List[UserPayload]
    mention_roles: List[str]
    attachments: List[Any]
    embeds: List[Any]
    reactions: List[Any]
    nonce: Optional[str]
    pinned: bool
    webhook_id: Optional[str]
    type: int
    activity: Optional[Any]
    application: Optional[Any]
    message_reference: Optional[Any]
    flags: int
    referenced_message: Optional[Any]
    interaction: Optional[Any]


class ChannelPayload(TypedDict, total=False):
    id: str
    type: int
    guild_id: Optional[str]
    position: Optional[int]
    permission_overwrites: List[Any]
    name: Optional[str]
    topic: Optional[str]
    nsfw: Optional[bool]
    last_message_id: Optional[str]
    bitrate: Optional[int]
    user_limit: Optional[int]
    rate_limit_per_user: Optional[int]
    recipients: Optional[List[UserPayload]]
    icon: Optional[str]
    owner_id: Optional[str]
    application_id: Optional[str]
    parent_id: Optional[str]
    last_pin_timestamp: Optional[str]


class GuildPayload(TypedDict, total=False):
    id: str
    name: str
    icon: Optional[str]
    icon_hash: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    owner: Optional[bool]
    owner_id: str
    permissions: Optional[str]
    region: Optional[str]
    afk_channel_id: Optional[str]
    afk_timeout: int
    widget_enabled: Optional[bool]
    widget_channel_id: Optional[str]
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    roles: List[Any]
    emojis: List[Any]
    features: List[str]
    mfa_level: int
    application_id: Optional[str]
    system_channel_id: Optional[str]
    system_channel_flags: int
    rules_channel_id: Optional[str]
    max_presences: Optional[int]
    max_members: Optional[int]
    vanity_url_code: Optional[str]
    description: Optional[str]
    banner: Optional[str]
    premium_tier: int
    premium_subscription_count: Optional[int]
    preferred_locale: str
    public_updates_channel_id: Optional[str]
    max_video_channel_users: Optional[int]
    approximate_member_count: Optional[int]
    approximate_presence_count: Optional[int]
