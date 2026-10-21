from typing import List, Dict, Any
from .components import ActionRow, TextInput


class Modal:
    def __init__(
        self,
        *,
        custom_id: str,
        title: str,
        components: List[ActionRow]
    ):
        self.custom_id = custom_id
        self.title = title
        self.components = components

    def to_dict(self) -> Dict[str, Any]:
        return {
            'custom_id': self.custom_id,
            'title': self.title,
            'components': [c.to_dict() for c in self.components]
        }

    @classmethod
    def create(cls, custom_id: str, title: str, *inputs: TextInput) -> 'Modal':
        components = [ActionRow(input_field) for input_field in inputs]
        return cls(custom_id=custom_id, title=title, components=components)
