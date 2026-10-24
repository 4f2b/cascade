from __future__ import annotations

from typing import List, Optional


class GuildPreview:
    __slots__ = (
        'id', 'name', 'icon', 'splash', 'discovery_splash',
        'emojis', 'features', 'approximate_member_count',
        'approximate_presence_count', 'description', 'stickers',
    )

    def __init__(self, data: dict):
        self.id: str = data['id']
        self.name: str = data['name']
        self.icon: Optional[str] = data.get('icon')
        self.splash: Optional[str] = data.get('splash')
        self.discovery_splash: Optional[str] = data.get('discovery_splash')
        self.emojis: list = data.get('emojis', [])
        self.features: List[str] = data.get('features', [])
        self.approximate_member_count: int = data.get('approximate_member_count', 0)
        self.approximate_presence_count: int = data.get('approximate_presence_count', 0)
        self.description: Optional[str] = data.get('description')
        self.stickers: list = data.get('stickers', [])

    def __repr__(self) -> str:
        return f'<GuildPreview id={self.id!r} name={self.name!r} members={self.approximate_member_count}>'

    def __str__(self) -> str:
        return self.name

    @property
    def icon_url(self) -> Optional[str]:
        if not self.icon:
            return None
        ext = 'gif' if self.icon.startswith('a_') else 'png'
        return f'https://cdn.discordapp.com/icons/{self.id}/{self.icon}.{ext}'
