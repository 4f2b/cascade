from typing import Optional, List
from dataclasses import dataclass

@dataclass
class ApplicationAsset:
    id: str
    name: str
    type: int

@dataclass
class Application:
    id: int
    name: str
    icon: Optional[str]
    description: str
    summary: str
    bot_public: bool
    bot_require_code_grant: bool
    verify_key: str
    owner_id: Optional[int] = None
    flags: int = 0
    redirect_uris: List[str] = None
    rpc_origins: List[str] = None
    terms_of_service_url: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    custom_install_url: Optional[str] = None
    install_params: Optional[dict] = None
    tags: List[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Application':
        return cls(
            id=int(data['id']),
            name=data['name'],
            icon=data.get('icon'),
            description=data['description'],
            summary=data.get('summary', ''),
            bot_public=data.get('bot_public', False),
            bot_require_code_grant=data.get('bot_require_code_grant', False),
            verify_key=data['verify_key'],
            owner_id=int(data['owner']['id']) if 'owner' in data else None,
            flags=data.get('flags', 0),
            redirect_uris=data.get('redirect_uris', []),
            rpc_origins=data.get('rpc_origins', []),
            terms_of_service_url=data.get('terms_of_service_url'),
            privacy_policy_url=data.get('privacy_policy_url'),
            custom_install_url=data.get('custom_install_url'),
            install_params=data.get('install_params'),
            tags=data.get('tags', [])
        )
    
    @property
    def icon_url(self) -> Optional[str]:
        if self.icon:
            return f'https://cdn.discordapp.com/app-icons/{self.id}/{self.icon}.png'
        return None
