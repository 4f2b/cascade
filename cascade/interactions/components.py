from typing import Optional, List, Dict, Any, Union
from enum import IntEnum


class ComponentType(IntEnum):
    ACTION_ROW = 1
    BUTTON = 2
    SELECT_MENU = 3
    TEXT_INPUT = 4


class ButtonStyle(IntEnum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class TextInputStyle(IntEnum):
    SHORT = 1
    PARAGRAPH = 2


class Component:
    def __init__(self, type: ComponentType):
        self.type = type

    def to_dict(self) -> Dict[str, Any]:
        return {'type': int(self.type)}


class ActionRow(Component):
    def __init__(self, *components: Union['Button', 'SelectMenu', 'TextInput']):
        super().__init__(ComponentType.ACTION_ROW)
        self.components = list(components)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': int(self.type),
            'components': [c.to_dict() for c in self.components]
        }


class Button(Component):
    def __init__(
        self,
        *,
        style: ButtonStyle = ButtonStyle.PRIMARY,
        label: Optional[str] = None,
        emoji: Optional[Union[str, Dict[str, Any]]] = None,
        custom_id: Optional[str] = None,
        url: Optional[str] = None,
        disabled: bool = False
    ):
        super().__init__(ComponentType.BUTTON)
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'type': int(self.type),
            'style': int(self.style)
        }
        
        if self.label:
            data['label'] = self.label
        if self.emoji:
            if isinstance(self.emoji, str):
                data['emoji'] = {'name': self.emoji}
            else:
                data['emoji'] = self.emoji
        if self.custom_id:
            data['custom_id'] = self.custom_id
        if self.url:
            data['url'] = self.url
        if self.disabled:
            data['disabled'] = self.disabled
        
        return data

    @classmethod
    def primary(cls, label: str, custom_id: str, **kwargs) -> 'Button':
        return cls(style=ButtonStyle.PRIMARY, label=label, custom_id=custom_id, **kwargs)

    @classmethod
    def secondary(cls, label: str, custom_id: str, **kwargs) -> 'Button':
        return cls(style=ButtonStyle.SECONDARY, label=label, custom_id=custom_id, **kwargs)

    @classmethod
    def success(cls, label: str, custom_id: str, **kwargs) -> 'Button':
        return cls(style=ButtonStyle.SUCCESS, label=label, custom_id=custom_id, **kwargs)

    @classmethod
    def danger(cls, label: str, custom_id: str, **kwargs) -> 'Button':
        return cls(style=ButtonStyle.DANGER, label=label, custom_id=custom_id, **kwargs)

    @classmethod
    def link(cls, label: str, url: str, **kwargs) -> 'Button':
        return cls(style=ButtonStyle.LINK, label=label, url=url, **kwargs)


class SelectOption:
    def __init__(
        self,
        label: str,
        value: str,
        *,
        description: Optional[str] = None,
        emoji: Optional[Union[str, Dict[str, Any]]] = None,
        default: bool = False
    ):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'label': self.label,
            'value': self.value
        }
        
        if self.description:
            data['description'] = self.description
        if self.emoji:
            if isinstance(self.emoji, str):
                data['emoji'] = {'name': self.emoji}
            else:
                data['emoji'] = self.emoji
        if self.default:
            data['default'] = self.default
        
        return data


class SelectMenu(Component):
    def __init__(
        self,
        *,
        custom_id: str,
        options: List[SelectOption],
        placeholder: Optional[str] = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False
    ):
        super().__init__(ComponentType.SELECT_MENU)
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'type': int(self.type),
            'custom_id': self.custom_id,
            'options': [opt.to_dict() for opt in self.options]
        }
        
        if self.placeholder:
            data['placeholder'] = self.placeholder
        if self.min_values != 1:
            data['min_values'] = self.min_values
        if self.max_values != 1:
            data['max_values'] = self.max_values
        if self.disabled:
            data['disabled'] = self.disabled
        
        return data


class TextInput(Component):
    def __init__(
        self,
        *,
        custom_id: str,
        label: str,
        style: TextInputStyle = TextInputStyle.SHORT,
        placeholder: Optional[str] = None,
        value: Optional[str] = None,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ):
        super().__init__(ComponentType.TEXT_INPUT)
        self.custom_id = custom_id
        self.label = label
        self.style = style
        self.placeholder = placeholder
        self.value = value
        self.required = required
        self.min_length = min_length
        self.max_length = max_length

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'type': int(self.type),
            'custom_id': self.custom_id,
            'label': self.label,
            'style': int(self.style),
            'required': self.required
        }
        
        if self.placeholder:
            data['placeholder'] = self.placeholder
        if self.value:
            data['value'] = self.value
        if self.min_length is not None:
            data['min_length'] = self.min_length
        if self.max_length is not None:
            data['max_length'] = self.max_length
        
        return data
