from __future__ import annotations

from typing import Optional


class Attachment:
    __slots__ = (
        'id', 'filename', 'description', 'content_type',
        'size', 'url', 'proxy_url', 'height', 'width',
        'ephemeral', 'duration_secs', 'waveform', 'flags',
    )

    def __init__(self, data: dict):
        self.id: str = data['id']
        self.filename: str = data['filename']
        self.description: Optional[str] = data.get('description')
        self.content_type: Optional[str] = data.get('content_type')
        self.size: int = data.get('size', 0)
        self.url: str = data['url']
        self.proxy_url: str = data.get('proxy_url', '')
        self.height: Optional[int] = data.get('height')
        self.width: Optional[int] = data.get('width')
        self.ephemeral: bool = data.get('ephemeral', False)
        self.duration_secs: Optional[float] = data.get('duration_secs')
        self.waveform: Optional[str] = data.get('waveform')
        self.flags: int = data.get('flags', 0)

    def __repr__(self) -> str:
        return f'<Attachment id={self.id!r} filename={self.filename!r} size={self.size}>'

    def __str__(self) -> str:
        return self.url

    @property
    def is_image(self) -> bool:
        if self.content_type:
            return self.content_type.startswith('image/')
        ext = self.filename.rsplit('.', 1)[-1].lower()
        return ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    @property
    def is_video(self) -> bool:
        if self.content_type:
            return self.content_type.startswith('video/')
        ext = self.filename.rsplit('.', 1)[-1].lower()
        return ext in {'mp4', 'mov', 'webm', 'avi'}

    @property
    def is_audio(self) -> bool:
        if self.content_type:
            return self.content_type.startswith('audio/')
        ext = self.filename.rsplit('.', 1)[-1].lower()
        return ext in {'mp3', 'ogg', 'wav', 'flac', 'aac'}

    @property
    def spoiler(self) -> bool:
        return self.filename.startswith('SPOILER_')
