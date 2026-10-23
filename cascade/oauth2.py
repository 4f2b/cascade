from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .core.session import Session
    from .entities.guild import Guild


class OAuth2Token:
    __slots__ = ('id', 'scopes', 'application', '_session')

    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self.id: int = int(data['id'])
        self.scopes: List[str] = data.get('scopes', [])
        self.application: OAuth2Application = OAuth2Application(data['application'])

    def __repr__(self) -> str:
        return f'<OAuth2Token id={self.id} application={self.application!r} scopes={self.scopes!r}>'

    def __str__(self) -> str:
        return self.application.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, OAuth2Token) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    async def revoke(self) -> None:
        await self._session.rest.revoke_oauth2_token(self.id)


class OAuth2Application:
    __slots__ = ('id', 'name', 'description', 'icon', 'flags', 'is_monetized', 'privacy_policy_url', 'terms_of_service_url', 'verify_key')

    def __init__(self, data: dict):
        self.id: int = int(data['id'])
        self.name: str = data['name']
        self.description: str = data.get('description', '')
        self.icon: Optional[str] = data.get('icon')
        self.flags: int = data.get('flags', 0)
        self.is_monetized: bool = data.get('is_monetized', False)
        self.privacy_policy_url: Optional[str] = data.get('privacy_policy_url')
        self.terms_of_service_url: Optional[str] = data.get('hook')
        self.verify_key: Optional[str] = data.get('verify_key')

    def __repr__(self) -> str:
        return f'<OAuth2Application id={self.id} name={self.name!r}>'

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, OAuth2Application) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def icon_url(self) -> Optional[str]:
        if not self.icon:
            return None
        return f'https://cdn.discordapp.com/app-icons/{self.id}/{self.icon}.png'


class OAuth2Authorization:
    __slots__ = (
        'authorized',
        'application',
        'scopes',
        'response_type',
        'redirect_uri',
        'code_challenge_method',
        'code_challenge',
        'state',
        'nonce',
        'bot',
        'approximate_guild_count',
        'guilds',
        '_original_redirect_uri',
        '_session',
    )

    def __init__(
        self,
        data: dict,
        session: 'Session',
        scopes: List[str],
        response_type: Optional[str] = None,
        original_redirect_uri: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        code_challenge: Optional[str] = None,
        state: Optional[str] = None,
        nonce: Optional[str] = None,
    ):
        self._session = session
        self.scopes: List[str] = scopes
        self.response_type: Optional[str] = response_type
        self._original_redirect_uri: Optional[str] = original_redirect_uri
        self.code_challenge_method: Optional[str] = code_challenge_method
        self.code_challenge: Optional[str] = code_challenge
        self.state: Optional[str] = state
        self.nonce: Optional[str] = nonce
        self.authorized: bool = data.get('authorized', False)
        self.application: OAuth2Application = OAuth2Application(data['application'])
        self.redirect_uri: Optional[str] = data.get('redirect_uri')
        self.bot: Optional[dict] = data.get('bot')
        self.approximate_guild_count: Optional[int] = data.get('bot', {}).get('approximate_guild_count') if 'bot' in data else None
        self.guilds: List[dict] = data.get('guilds', [])

    def __repr__(self) -> str:
        return (
            f'<OAuth2Authorization authorized={self.authorized} '
            f'application={self.application!r} scopes={self.scopes!r} '
            f'response_type={self.response_type!r} redirect_uri={self.redirect_uri!r}>'
        )

    async def authorize(
        self,
        guild_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        permissions: Optional[int] = None,
    ) -> str:
        data = await self._session.rest.authorize_oauth2(
            application_id=self.application.id,
            scopes=self.scopes,
            response_type=self.response_type,
            redirect_uri=self._original_redirect_uri,
            code_challenge_method=self.code_challenge_method,
            code_challenge=self.code_challenge,
            state=self.state,
            nonce=self.nonce,
            guild_id=guild_id,
            webhook_channel_id=channel_id,
            permissions=permissions,
        )
        return data.get('location', '')
