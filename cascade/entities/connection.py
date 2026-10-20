from typing import Optional, List
from dataclasses import dataclass

@dataclass
class ConnectionIntegration:
    id: str
    name: str
    type: str
    enabled: bool
    syncing: bool
    role_id: Optional[int] = None
    enable_emoticons: bool = False
    expire_behavior: int = 0
    expire_grace_period: int = 0
    subscriber_count: int = 0
    revoked: bool = False

@dataclass
class Connection:
    id: str
    name: str
    type: str
    verified: bool
    friend_sync: bool
    show_activity: bool
    visibility: int
    revoked: bool = False
    integrations: List[ConnectionIntegration] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Connection':
        integrations = []
        if 'integrations' in data:
            for i in data['integrations']:
                integrations.append(ConnectionIntegration(
                    id=i['id'],
                    name=i['name'],
                    type=i['type'],
                    enabled=i['enabled'],
                    syncing=i.get('syncing', False),
                    role_id=int(i['role_id']) if i.get('role_id') else None,
                    enable_emoticons=i.get('enable_emoticons', False),
                    expire_behavior=i.get('expire_behavior', 0),
                    expire_grace_period=i.get('expire_grace_period', 0),
                    subscriber_count=i.get('subscriber_count', 0),
                    revoked=i.get('revoked', False)
                ))
        
        return cls(
            id=data['id'],
            name=data['name'],
            type=data['type'],
            verified=data.get('verified', False),
            friend_sync=data.get('friend_sync', False),
            show_activity=data.get('show_activity', True),
            visibility=data.get('visibility', 1),
            revoked=data.get('revoked', False),
            integrations=integrations if integrations else None
        )
