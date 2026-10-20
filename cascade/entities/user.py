from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class User:
    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self._update(data)

    def _update(self, data: dict) -> None:
        self.id = data['id']
        self.username = data['username']
        self.discriminator = data.get('discriminator', '0')
        self.global_name = data.get('global_name')
        self.avatar = data.get('avatar')
        self.avatar_decoration_data = data.get('avatar_decoration_data')
        self.collectibles = data.get('collectibles')
        self.display_name_styles = data.get('display_name_styles')
        self.primary_guild = data.get('primary_guild')
        self.linked_users = data.get('linked_users', [])
        self.bot = data.get('bot', False)
        self.system = data.get('system', False)
        self.mfa_enabled = data.get('mfa_enabled', False)
        self.nsfw_allowed = data.get('nsfw_allowed')
        self.age_verification_status = data.get('age_verification_status', 0)
        self.pronouns = data.get('pronouns', '')
        self.bio = data.get('bio', '')
        self.banner = data.get('banner')
        self.accent_color = data.get('accent_color')
        self.public_flags = data.get('public_flags', 0)
        self.flags = data.get('flags', 0)
        self.purchased_flags = data.get('purchased_flags', 0)
        self.premium_usage_flags = data.get('premium_usage_flags', 0)

    @property
    def name(self) -> str:
        return self.global_name or self.username

    @property
    def mention(self) -> str:
        return f'<@{self.id}>'

    @property
    def avatar_url(self) -> Optional[str]:
        if not self.avatar:
            return None
        ext = 'gif' if self.avatar.startswith('a_') else 'png'
        return f'https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.{ext}'

    @property
    def default_avatar_url(self) -> str:
        if self.discriminator == '0':
            index = (int(self.id) >> 22) % 6
        else:
            index = int(self.discriminator) % 5
        return f'https://cdn.discordapp.com/embed/avatars/{index}.png'

    @property
    def display_avatar(self) -> str:
        return self.avatar_url or self.default_avatar_url

    async def create_dm(self):
        data = await self._session.rest.create_dm(self.id)
        from .channel import create_channel
        return create_channel(data, self._session)

    async def send(self, content: str = None, **kwargs):
        dm = await self.create_dm()
        return await dm.send(content, **kwargs)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<User id={self.id} name={self.name}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, User) and self.id == other.id

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return int(self.id)


class ClientUser(User):
    def _update(self, data: dict) -> None:
        super()._update(data)
        self.verified = data.get('verified', False)
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.premium = data.get('premium', False)
        self.premium_type = data.get('premium_type', 0)
        self.premium_state = data.get('premium_state')
        self.personal_connection_id = data.get('personal_connection_id')
        self.locale = data.get('locale', 'en-US')
        self.desktop = data.get('desktop', False)
        self.mobile = data.get('mobile', False)
        self.has_bounced_email = data.get('has_bounced_email', False)
        self.authenticator_types = data.get('authenticator_types', [])
        self.analytics_token = data.get('analytics_token', '')

    def __repr__(self) -> str:
        return f'<ClientUser id={self.id} name={self.name}>'
