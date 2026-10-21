from typing import Optional, Dict, Any
from ..types.enums import ActivityType


class ActivityAssets:
    def __init__(self):
        self.large_image: Optional[str] = None
        self.large_text: Optional[str] = None
        self.small_image: Optional[str] = None
        self.small_text: Optional[str] = None

    def set_large_image(self, image: str, text: Optional[str] = None) -> 'ActivityAssets':
        self.large_image = image
        self.large_text = text
        return self

    def set_small_image(self, image: str, text: Optional[str] = None) -> 'ActivityAssets':
        self.small_image = image
        self.small_text = text
        return self

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.large_image:
            data['large_image'] = self.large_image
        if self.large_text:
            data['large_text'] = self.large_text
        if self.small_image:
            data['small_image'] = self.small_image
        if self.small_text:
            data['small_text'] = self.small_text
        return data


class ActivityTimestamps:
    def __init__(self):
        self.start: Optional[int] = None
        self.end: Optional[int] = None

    def set_start(self, timestamp: int) -> 'ActivityTimestamps':
        self.start = timestamp
        return self

    def set_end(self, timestamp: int) -> 'ActivityTimestamps':
        self.end = timestamp
        return self

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.start:
            data['start'] = self.start
        if self.end:
            data['end'] = self.end
        return data


class ActivityParty:
    def __init__(self):
        self.party_id: Optional[str] = None
        self.current_size: Optional[int] = None
        self.max_size: Optional[int] = None

    def set_id(self, party_id: str) -> 'ActivityParty':
        self.party_id = party_id
        return self

    def set_size(self, current: int, maximum: int) -> 'ActivityParty':
        self.current_size = current
        self.max_size = maximum
        return self

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.party_id:
            data['id'] = self.party_id
        if self.current_size is not None and self.max_size is not None:
            data['size'] = [self.current_size, self.max_size]
        return data


class ActivitySecrets:
    def __init__(self):
        self.join: Optional[str] = None
        self.spectate: Optional[str] = None
        self.match: Optional[str] = None

    def set_join(self, secret: str) -> 'ActivitySecrets':
        self.join = secret
        return self

    def set_spectate(self, secret: str) -> 'ActivitySecrets':
        self.spectate = secret
        return self

    def set_match(self, secret: str) -> 'ActivitySecrets':
        self.match = secret
        return self

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.join:
            data['join'] = self.join
        if self.spectate:
            data['spectate'] = self.spectate
        if self.match:
            data['match'] = self.match
        return data


class ActivityButton:
    def __init__(self, label: str, url: str):
        self.label = label
        self.url = url

    def to_dict(self) -> Dict[str, Any]:
        return {
            'label': self.label,
            'url': self.url
        }


class RichActivity:
    def __init__(self, name: str, type: ActivityType = ActivityType.PLAYING):
        self.name = name
        self.type = type
        self.url: Optional[str] = None
        self.state: Optional[str] = None
        self.details: Optional[str] = None
        self.application_id: Optional[int] = None
        self.assets = ActivityAssets()
        self.timestamps = ActivityTimestamps()
        self.party = ActivityParty()
        self.secrets = ActivitySecrets()
        self.buttons: list[ActivityButton] = []
        self.instance: bool = False

    def set_state(self, state: str) -> 'RichActivity':
        self.state = state
        return self

    def set_details(self, details: str) -> 'RichActivity':
        self.details = details
        return self

    def set_url(self, url: str) -> 'RichActivity':
        self.url = url
        return self

    def set_application_id(self, app_id: int) -> 'RichActivity':
        self.application_id = app_id
        return self

    def set_instance(self, instance: bool) -> 'RichActivity':
        self.instance = instance
        return self

    def add_button(self, label: str, url: str) -> 'RichActivity':
        self.buttons.append(ActivityButton(label, url))
        return self

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'name': self.name,
            'type': int(self.type)
        }

        if self.url:
            data['url'] = self.url
        if self.state:
            data['state'] = self.state
        if self.details:
            data['details'] = self.details
        if self.application_id:
            data['application_id'] = str(self.application_id)
        
        assets = self.assets.to_dict()
        if assets:
            data['assets'] = assets
        
        timestamps = self.timestamps.to_dict()
        if timestamps:
            data['timestamps'] = timestamps
        
        party = self.party.to_dict()
        if party:
            data['party'] = party
        
        secrets = self.secrets.to_dict()
        if secrets:
            data['secrets'] = secrets
        
        if self.buttons:
            data['buttons'] = [btn.to_dict() for btn in self.buttons]
        
        data['instance'] = self.instance
        
        return data

    @classmethod
    def playing(cls, name: str) -> 'RichActivity':
        return cls(name, ActivityType.PLAYING)

    @classmethod
    def streaming(cls, name: str, url: str) -> 'RichActivity':
        activity = cls(name, ActivityType.STREAMING)
        activity.url = url
        return activity

    @classmethod
    def listening(cls, name: str) -> 'RichActivity':
        return cls(name, ActivityType.LISTENING)

    @classmethod
    def watching(cls, name: str) -> 'RichActivity':
        return cls(name, ActivityType.WATCHING)

    @classmethod
    def competing(cls, name: str) -> 'RichActivity':
        return cls(name, ActivityType.COMPETING)

    @classmethod
    def custom(cls, state: str) -> 'RichActivity':
        activity = cls('Custom Status', ActivityType.CUSTOM)
        activity.state = state
        return activity
