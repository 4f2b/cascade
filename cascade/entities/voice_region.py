from __future__ import annotations


class VoiceRegion:
    __slots__ = ('id', 'name', 'optimal', 'deprecated', 'custom')

    def __init__(self, data: dict):
        self.id: str = data['id']
        self.name: str = data['name']
        self.optimal: bool = data.get('optimal', False)
        self.deprecated: bool = data.get('deprecated', False)
        self.custom: bool = data.get('custom', False)

    def __repr__(self) -> str:
        return f'<VoiceRegion id={self.id!r} name={self.name!r} optimal={self.optimal}>'

    def __str__(self) -> str:
        return self.name
