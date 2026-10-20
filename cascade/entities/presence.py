from typing import Optional, List, Dict, Any
from ..types.enums import ActivityType, StatusType


class Activity:
    def __init__(
        self,
        name: str,
        type: ActivityType = ActivityType.PLAYING,
        url: str = None,
        state: str = None,
        details: str = None
    ):
        self.name = name
        self.type = type
        self.url = url
        self.state = state
        self.details = details
        self.timestamps = {}
        self.application_id = None
        self.assets = {}
        self.party = {}
        self.flags = 0

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
        return data

    @classmethod
    def playing(cls, name: str) -> 'Activity':
        return cls(name=name, type=ActivityType.PLAYING)

    @classmethod
    def streaming(cls, name: str, url: str) -> 'Activity':
        return cls(name=name, type=ActivityType.STREAMING, url=url)

    @classmethod
    def listening(cls, name: str) -> 'Activity':
        return cls(name=name, type=ActivityType.LISTENING)

    @classmethod
    def watching(cls, name: str) -> 'Activity':
        return cls(name=name, type=ActivityType.WATCHING)

    @classmethod
    def competing(cls, name: str) -> 'Activity':
        return cls(name=name, type=ActivityType.COMPETING)


class Presence:
    def __init__(
        self,
        status: str = StatusType.ONLINE,
        activities: List[Activity] = None,
        afk: bool = False
    ):
        self.status = status
        self.activities = activities or []
        self.afk = afk
        self.since = 0 if not afk else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'activities': [activity.to_dict() for activity in self.activities],
            'afk': self.afk,
            'since': self.since
        }
