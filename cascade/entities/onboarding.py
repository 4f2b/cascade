from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.session import Session


class OnboardingPromptOption:
    __slots__ = (
        'id', 'title', 'description', 'emoji_id', 'emoji_name',
        'emoji_animated', 'channel_ids', 'role_ids',
    )

    def __init__(self, data: dict):
        self.id: str = data['id']
        self.title: str = data['title']
        self.description: Optional[str] = data.get('description')
        self.channel_ids: List[str] = data.get('channel_ids', [])
        self.role_ids: List[str] = data.get('role_ids', [])

        emoji = data.get('emoji') or {}
        self.emoji_id: Optional[str] = emoji.get('id')
        self.emoji_name: Optional[str] = emoji.get('name')
        self.emoji_animated: bool = emoji.get('animated', False)

    def __repr__(self) -> str:
        return f'<OnboardingPromptOption id={self.id!r} title={self.title!r}>'

    @property
    def emoji(self) -> Optional[str]:
        if self.emoji_name and not self.emoji_id:
            return self.emoji_name
        if self.emoji_id:
            animated = 'a' if self.emoji_animated else ''
            return f'<{animated}:{self.emoji_name}:{self.emoji_id}>'
        return None

    def to_dict(self) -> dict:
        d: dict = {
            'id': self.id,
            'title': self.title,
            'channel_ids': self.channel_ids,
            'role_ids': self.role_ids,
        }
        if self.description is not None:
            d['description'] = self.description
        d['emoji'] = {
            'id': self.emoji_id,
            'name': self.emoji_name,
            'animated': self.emoji_animated,
        }
        return d


class OnboardingPrompt:
    __slots__ = (
        'id', 'type', 'title', 'options', 'single_select',
        'required', 'in_onboarding',
    )

    MULTIPLE_CHOICE = 0
    DROPDOWN = 1

    def __init__(self, data: dict):
        self.id: str = data['id']
        self.type: int = data.get('type', 0)
        self.title: str = data['title']
        self.single_select: bool = data.get('single_select', False)
        self.required: bool = data.get('required', False)
        self.in_onboarding: bool = data.get('in_onboarding', True)
        self.options: List[OnboardingPromptOption] = [
            OnboardingPromptOption(o) for o in data.get('options', [])
        ]

    def __repr__(self) -> str:
        return f'<OnboardingPrompt id={self.id!r} title={self.title!r} options={len(self.options)}>'

    @property
    def is_multiple_choice(self) -> bool:
        return self.type == self.MULTIPLE_CHOICE

    @property
    def is_dropdown(self) -> bool:
        return self.type == self.DROPDOWN

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'single_select': self.single_select,
            'required': self.required,
            'in_onboarding': self.in_onboarding,
            'options': [o.to_dict() for o in self.options],
        }


class WelcomeChannel:
    __slots__ = ('channel_id', 'description', 'emoji_id', 'emoji_name')

    def __init__(self, data: dict):
        self.channel_id: str = data['channel_id']
        self.description: str = data.get('description', '')
        self.emoji_id: Optional[str] = data.get('emoji_id')
        self.emoji_name: Optional[str] = data.get('emoji_name')

    def __repr__(self) -> str:
        return f'<WelcomeChannel channel_id={self.channel_id!r} description={self.description!r}>'

    @property
    def emoji(self) -> Optional[str]:
        if self.emoji_name and not self.emoji_id:
            return self.emoji_name
        if self.emoji_id:
            return f'<:{self.emoji_name}:{self.emoji_id}>'
        return None

    def to_dict(self) -> dict:
        return {
            'channel_id': self.channel_id,
            'description': self.description,
            'emoji_id': self.emoji_id,
            'emoji_name': self.emoji_name,
        }

    @classmethod
    def new(cls, channel_id: str, description: str, emoji: Optional[str] = None) -> 'WelcomeChannel':
        data: dict = {
            'channel_id': channel_id,
            'description': description,
            'emoji_id': None,
            'emoji_name': emoji,
        }
        return cls(data)


class WelcomeScreen:
    __slots__ = ('guild_id', 'description', 'channels', 'enabled', '_session')

    def __init__(self, data: dict, session: 'Session', guild_id: str):
        self._session = session
        self.guild_id: str = guild_id
        self.description: Optional[str] = data.get('description')
        self.channels: List[WelcomeChannel] = [
            WelcomeChannel(c) for c in data.get('welcome_channels', [])
        ]
        guild = session.cache.get_guild(guild_id)
        features = getattr(guild, 'features', []) if guild else []
        self.enabled: bool = 'WELCOME_SCREEN_ENABLED' in features

    def __repr__(self) -> str:
        return f'<WelcomeScreen guild_id={self.guild_id!r} enabled={self.enabled} channels={len(self.channels)}>'

    def __bool__(self) -> bool:
        return self.enabled

    async def edit(
        self,
        *,
        enabled: Optional[bool] = None,
        description: Optional[str] = None,
        channels: Optional[List[WelcomeChannel]] = None,
    ) -> 'WelcomeScreen':
        payload: dict = {}
        if enabled is not None:
            payload['enabled'] = enabled
        if description is not None:
            payload['description'] = description
        if channels is not None:
            payload['welcome_channels'] = [c.to_dict() for c in channels]
        data = await self._session.rest.edit_welcome_screen(self.guild_id, payload)
        return WelcomeScreen(data, self._session, self.guild_id)


class GuildOnboarding:
    __slots__ = (
        'guild_id', 'prompts', 'default_channel_ids',
        'enabled', 'mode', '_session',
    )

    DEFAULT = 0
    ADVANCED = 1

    def __init__(self, data: dict, session: 'Session'):
        self._session = session
        self.guild_id: str = data['guild_id']
        self.enabled: bool = data.get('enabled', False)
        self.mode: int = data.get('mode', 0)
        self.default_channel_ids: List[str] = data.get('below_requirements_channel_ids', [])
        self.prompts: List[OnboardingPrompt] = [
            OnboardingPrompt(p) for p in data.get('prompts', [])
        ]

    def __repr__(self) -> str:
        return (
            f'<GuildOnboarding guild_id={self.guild_id!r} '
            f'enabled={self.enabled} prompts={len(self.prompts)}>'
        )

    def __bool__(self) -> bool:
        return self.enabled

    @property
    def is_advanced(self) -> bool:
        return self.mode == self.ADVANCED

    @property
    def required_prompts(self) -> List[OnboardingPrompt]:
        return [p for p in self.prompts if p.required]

    @property
    def optional_prompts(self) -> List[OnboardingPrompt]:
        return [p for p in self.prompts if not p.required]

    async def edit(
        self,
        *,
        enabled: Optional[bool] = None,
        mode: Optional[int] = None,
        prompts: Optional[List[OnboardingPrompt]] = None,
        default_channel_ids: Optional[List[str]] = None,
    ) -> 'GuildOnboarding':
        payload: dict = {}
        if enabled is not None:
            payload['enabled'] = enabled
        if mode is not None:
            payload['mode'] = mode
        if prompts is not None:
            payload['prompts'] = [p.to_dict() for p in prompts]
        if default_channel_ids is not None:
            payload['below_requirements_channel_ids'] = default_channel_ids
        data = await self._session.rest.edit_guild_onboarding(self.guild_id, payload)
        return GuildOnboarding(data, self._session)
