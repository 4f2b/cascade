from typing import Optional, List, Dict, Any
from enum import IntFlag


class ApplicationFlags(IntFlag):
    GATEWAY_PRESENCE = 1 << 12
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    GATEWAY_GUILD_MEMBERS = 1 << 14
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    EMBEDDED = 1 << 17
    GATEWAY_MESSAGE_CONTENT = 1 << 18
    GATEWAY_MESSAGE_CONTENT_LIMITED = 1 << 19
    APPLICATION_COMMAND_BADGE = 1 << 23


class Application:
    def __init__(self, data: Dict[str, Any], session=None):
        self._session = session
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.id: int = int(data['id'])
        self.name: str = data['name']
        self.icon: Optional[str] = data.get('icon')
        self.description: str = data.get('description', '')
        self.summary: str = data.get('summary', '')
        self.bot_public: bool = data.get('bot_public', False)
        self.bot_require_code_grant: bool = data.get('bot_require_code_grant', False)
        self.verify_key: str = data.get('verify_key', '')
        self.flags: int = data.get('flags', 0)
        self.redirect_uris: List[str] = data.get('redirect_uris', [])
        self.rpc_origins: List[str] = data.get('rpc_origins') or []
        self.terms_of_service_url: Optional[str] = data.get('terms_of_service_url')
        self.privacy_policy_url: Optional[str] = data.get('privacy_policy_url')
        self.custom_install_url: Optional[str] = data.get('custom_install_url')
        self.install_params: Optional[Dict] = data.get('install_params')
        self.tags: List[str] = data.get('tags') or []
        self.role_connections_verification_url: Optional[str] = data.get('role_connections_verification_url')
        self.interactions_endpoint_url: Optional[str] = data.get('interactions_endpoint_url')

        owner = data.get('owner')
        self.owner_id: Optional[int] = int(owner['id']) if owner else None

        team = data.get('team')
        self.team_id: Optional[int] = int(team['id']) if team else None
        self.team_name: Optional[str] = team['name'] if team else None

    @property
    def icon_url(self) -> Optional[str]:
        if self.icon:
            return f'https://cdn.discordapp.com/app-icons/{self.id}/{self.icon}.png'
        return None

    @property
    def has_flag(self) -> callable:
        return lambda flag: bool(self.flags & flag)

    async def edit(
        self,
        name: str = None,
        description: str = None,
        icon: str = None,
        bot_public: bool = None,
        redirect_uris: List[str] = None,
        rpc_origins: List[str] = None,
        terms_of_service_url: str = None,
        privacy_policy_url: str = None,
        tags: List[str] = None,
        interactions_endpoint_url: str = None,
        role_connections_verification_url: str = None,
        custom_install_url: str = None,
    ) -> 'Application':
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        if icon is not None:
            data['icon'] = icon
        if bot_public is not None:
            data['bot_public'] = bot_public
        if redirect_uris is not None:
            data['redirect_uris'] = redirect_uris
        if rpc_origins is not None:
            data['rpc_origins'] = rpc_origins
        if terms_of_service_url is not None:
            data['terms_of_service_url'] = terms_of_service_url
        if privacy_policy_url is not None:
            data['privacy_policy_url'] = privacy_policy_url
        if tags is not None:
            data['tags'] = tags
        if interactions_endpoint_url is not None:
            data['interactions_endpoint_url'] = interactions_endpoint_url
        if role_connections_verification_url is not None:
            data['role_connections_verification_url'] = role_connections_verification_url
        if custom_install_url is not None:
            data['custom_install_url'] = custom_install_url

        result = await self._session.rest.edit_application(self.id, **data)
        self._update(result)
        return self

    async def delete(self) -> None:
        await self._session.rest.delete_application(self.id)

    async def transfer(self, team_id: int) -> None:
        await self._session.rest.transfer_application(self.id, team_id)

    async def get_assets(self) -> List[Dict[str, Any]]:
        return await self._session.rest.get_application_assets(self.id)

    async def upload_asset(self, name: str, image: str) -> Dict[str, Any]:
        return await self._session.rest.create_application_asset(self.id, name, image)

    async def delete_asset(self, asset_id: int) -> None:
        await self._session.rest.delete_application_asset(self.id, asset_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'flags': self.flags,
            'bot_public': self.bot_public,
            'tags': self.tags,
            'owner_id': str(self.owner_id) if self.owner_id else None,
            'team_id': str(self.team_id) if self.team_id else None
        }
