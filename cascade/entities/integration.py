from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class IntegrationAccount:
    __slots__ = ('id', 'name')

    def __init__(self, data: dict):
        self.id: str = data.get('id', '')
        self.name: str = data.get('name', '')

    def __repr__(self) -> str:
        return f'<IntegrationAccount id={self.id!r} name={self.name!r}>'


class IntegrationApplication:
    __slots__ = ('id', 'name', 'icon', 'description', 'bot')

    def __init__(self, data: dict):
        self.id: str = data.get('id', '')
        self.name: str = data.get('name', '')
        self.icon: Optional[str] = data.get('icon')
        self.description: str = data.get('description', '')
        self.bot: Optional[dict] = data.get('bot')

    def __repr__(self) -> str:
        return f'<IntegrationApplication id={self.id!r} name={self.name!r}>'

    @property
    def icon_url(self) -> Optional[str]:
        if not self.icon:
            return None
        return f'https://cdn.discordapp.com/app-icons/{self.id}/{self.icon}.png'


class Integration:
    __slots__ = (
        'id', 'name', 'type', 'enabled', 'syncing',
        'role_id', 'enable_emoticons', 'expire_behavior',
        'expire_grace_period', 'user', 'account', 'synced_at',
        'subscriber_count', 'revoked', 'application', 'scopes',
        'guild_id', '_session',
    )

    def __init__(self, data: dict, session: 'Session', guild_id: str = None):
        self._session = session
        self.id: str = data['id']
        self.name: str = data['name']
        self.type: str = data['type']
        self.enabled: bool = data.get('enabled', False)
        self.syncing: bool = data.get('syncing', False)
        self.role_id: Optional[str] = data.get('role_id')
        self.enable_emoticons: bool = data.get('enable_emoticons', False)
        self.expire_behavior: Optional[int] = data.get('expire_behavior')
        self.expire_grace_period: Optional[int] = data.get('expire_grace_period')
        self.user: Optional[dict] = data.get('user')
        self.synced_at: Optional[str] = data.get('synced_at')
        self.subscriber_count: Optional[int] = data.get('subscriber_count')
        self.revoked: bool = data.get('revoked', False)
        self.scopes: list = data.get('scopes', [])
        self.guild_id: Optional[str] = data.get('guild_id') or guild_id

        account_data = data.get('account')
        self.account: Optional[IntegrationAccount] = IntegrationAccount(account_data) if account_data else None

        app_data = data.get('application')
        self.application: Optional[IntegrationApplication] = IntegrationApplication(app_data) if app_data else None

    def __repr__(self) -> str:
        return f'<Integration id={self.id!r} name={self.name!r} type={self.type!r}>'

    def __str__(self) -> str:
        return self.name

    async def delete(self) -> None:
        if self.guild_id:
            await self._session.rest.delete_guild_integration(self.guild_id, self.id)
