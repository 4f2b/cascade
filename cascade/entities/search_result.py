from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session
    from .message import Message


class MessageSearchResult:
    __slots__ = ('messages', 'total_results', 'analytics_id', 'doing_deep_index')

    def __init__(self, data: dict, session: 'Session'):
        from .message import Message
        self.total_results: int = data.get('total_results', 0)
        self.analytics_id: Optional[str] = data.get('analytics_id')
        self.doing_deep_index: bool = data.get('doing_deep_index', False)
        self.messages: List[Message] = []
        for group in data.get('messages', []):
            for msg_data in (group if isinstance(group, list) else [group]):
                try:
                    self.messages.append(Message(msg_data, session))
                except Exception:
                    pass

    def __repr__(self) -> str:
        return f'<MessageSearchResult total={self.total_results} loaded={len(self.messages)}>'

    def __len__(self) -> int:
        return self.total_results

    def __iter__(self):
        return iter(self.messages)
