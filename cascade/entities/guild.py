from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session
    from .channel import Channel
    from .member import Member


class Guild:
    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self._update(data)

    def _update(self, data: dict) -> None:
        self.id = data['id']
        self.unavailable = data.get('unavailable', False)
        self.name = data.get('name', '')
        self.icon = data.get('icon')
        self.icon_hash = data.get('icon_hash')
        self.splash = data.get('splash')
        self.discovery_splash = data.get('discovery_splash')
        self.banner = data.get('banner')
        self.home_header = data.get('home_header')
        self.owner_id = data.get('owner_id', '')
        self.application_id = data.get('application_id')
        self.description = data.get('description')
        self.region = data.get('region')
        self.afk_channel_id = data.get('afk_channel_id')
        self.afk_timeout = data.get('afk_timeout', 300)
        self.widget_enabled = data.get('widget_enabled', False)
        self.widget_channel_id = data.get('widget_channel_id')
        self.verification_level = data.get('verification_level', 0)
        self.default_message_notifications = data.get('default_message_notifications', 0)
        self.explicit_content_filter = data.get('explicit_content_filter', 0)
        self.roles = data.get('roles', [])
        self.emojis = data.get('emojis', [])
        self.stickers = data.get('stickers', [])
        self.features = data.get('features', [])
        self.mfa_level = data.get('mfa_level', 0)
        self.system_channel_id = data.get('system_channel_id')
        self.system_channel_flags = data.get('system_channel_flags', 0)
        self.rules_channel_id = data.get('rules_channel_id')
        self.public_updates_channel_id = data.get('public_updates_channel_id')
        self.safety_alerts_channel_id = data.get('safety_alerts_channel_id')
        self.max_presences = data.get('max_presences')
        self.max_members = data.get('max_members')
        self.vanity_url_code = data.get('vanity_url_code')
        self.premium_tier = data.get('premium_tier', 0)
        self.premium_subscription_count = data.get('premium_subscription_count', 0)
        self.preferred_locale = data.get('preferred_locale', 'en-US')
        self.max_video_channel_users = data.get('max_video_channel_users')
        self.max_stage_video_channel_users = data.get('max_stage_video_channel_users')
        self.nsfw = data.get('nsfw', False)
        self.nsfw_level = data.get('nsfw_level', 0)
        self.owner_configured_content_level = data.get('owner_configured_content_level')
        self.hub_type = data.get('hub_type')
        self.premium_progress_bar_enabled = data.get('premium_progress_bar_enabled', False)
        self.latest_onboarding_question_id = data.get('latest_onboarding_question_id')
        self.incidents_data = data.get('incidents_data')
        self.approximate_member_count = data.get('approximate_member_count')
        self.approximate_presence_count = data.get('approximate_presence_count')
        self.member_count = data.get('member_count', 0)

    @property
    def icon_url(self) -> Optional[str]:
        if not self.icon:
            return None
        ext = 'gif' if self.icon.startswith('a_') else 'png'
        return f'https://cdn.discordapp.com/icons/{self.id}/{self.icon}.{ext}'

    @property
    def banner_url(self) -> Optional[str]:
        if not self.banner:
            return None
        return f'https://cdn.discordapp.com/banners/{self.id}/{self.banner}.png'

    @property
    def splash_url(self) -> Optional[str]:
        if not self.splash:
            return None
        return f'https://cdn.discordapp.com/splashes/{self.id}/{self.splash}.png'

    @property
    def channels(self) -> List['Channel']:
        return [ch for ch in self._session.cache.channels.values() if ch.guild_id == self.id]

    @property
    def text_channels(self):
        from .channel import TextChannel
        return [ch for ch in self.channels if isinstance(ch, TextChannel)]

    @property
    def voice_channels(self):
        from .channel import VoiceChannel
        return [ch for ch in self.channels if isinstance(ch, VoiceChannel)]

    def get_channel(self, channel_id: int) -> Optional['Channel']:
        channel = self._session.get_channel(channel_id)
        if channel and channel.guild_id == self.id:
            return channel
        return None

    async def leave(self) -> None:
        await self._session.rest.leave_guild(self.id)

    async def fetch_channels(self) -> List['Channel']:
        from .channel import create_channel
        channels_data = await self._session.rest.get_guild_channels(self.id)
        channels = []
        for data in channels_data:
            channel = create_channel(data, self._session)
            if channel:
                self._session.cache.add_channel(channel)
                channels.append(channel)
        return channels

    async def fetch_member(self, user_id: int) -> 'Member':
        from .member import Member
        data = await self._session.rest.get_guild_member(self.id, str(user_id))
        return Member(data, self._session, self.id)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Guild id={self.id} name={self.name}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Guild) and self.id == other.id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return int(self.id)
