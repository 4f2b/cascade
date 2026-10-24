from __future__ import annotations

from typing import Dict, List, Optional, Any


class QuestTaskHeartbeat:
    __slots__ = ('last_beat_at', 'expires_at')

    def __init__(self, data: dict):
        self.last_beat_at: Optional[str] = data.get('last_beat_at')
        self.expires_at: Optional[str] = data.get('expires_at')

    def __repr__(self) -> str:
        return f'<QuestTaskHeartbeat last_beat_at={self.last_beat_at!r}>'


class QuestTaskProgress:
    __slots__ = ('event_name', 'value', 'updated_at', 'completed_at', 'heartbeat')

    def __init__(self, data: dict):
        self.event_name: str = data.get('event_name', '')
        self.value: int = data.get('value', 0)
        self.updated_at: Optional[str] = data.get('updated_at')
        self.completed_at: Optional[str] = data.get('completed_at')
        hb = data.get('heartbeat')
        self.heartbeat: Optional[QuestTaskHeartbeat] = QuestTaskHeartbeat(hb) if hb else None

    def __repr__(self) -> str:
        return f'<QuestTaskProgress event={self.event_name!r} value={self.value} completed={self.completed_at is not None}>'

    @property
    def is_complete(self) -> bool:
        return self.completed_at is not None


class QuestUserStatus:
    __slots__ = (
        'user_id', 'quest_id', 'enrolled_at', 'completed_at', 'claimed_at',
        'claimed_tier', 'progress', 'dismissed_quest_content',
    )

    def __init__(self, data: dict):
        self.user_id: str = data.get('user_id', '')
        self.quest_id: Optional[str] = data.get('quest_id')
        self.enrolled_at: Optional[str] = data.get('enrolled_at')
        self.completed_at: Optional[str] = data.get('completed_at')
        self.claimed_at: Optional[str] = data.get('claimed_at')
        self.claimed_tier: Optional[int] = data.get('claimed_tier')
        self.dismissed_quest_content: int = data.get('dismissed_quest_content', 0)
        self.progress: Dict[str, QuestTaskProgress] = {
            k: QuestTaskProgress(v) for k, v in data.get('progress', {}).items()
        }

    def __repr__(self) -> str:
        return (
            f'<QuestUserStatus user_id={self.user_id!r} '
            f'enrolled={self.enrolled_at is not None} '
            f'completed={self.completed_at is not None} '
            f'claimed={self.claimed_at is not None}>'
        )

    @property
    def enrolled(self) -> bool:
        return self.enrolled_at is not None

    @property
    def completed(self) -> bool:
        return self.completed_at is not None

    @property
    def claimed(self) -> bool:
        return self.claimed_at is not None

    def get_task(self, task_type: str) -> Optional[QuestTaskProgress]:
        return self.progress.get(task_type)

    def task_progress_seconds(self, task_type: str) -> int:
        task = self.progress.get(task_type)
        return task.value if task else 0


class QuestReward:
    __slots__ = (
        'type', 'sku_id', 'asset', 'asset_video',
        'name', 'name_with_article', 'approximate_count',
        'redemption_link', 'expires_at', 'orb_quantity',
    )

    def __init__(self, data: dict):
        self.type: int = data.get('type', 0)
        self.sku_id: str = data.get('sku_id', '')
        self.asset: Optional[str] = data.get('asset')
        self.asset_video: Optional[str] = data.get('asset_video')
        self.approximate_count: Optional[int] = data.get('approximate_count')
        self.redemption_link: Optional[str] = data.get('redemption_link')
        self.expires_at: Optional[str] = data.get('expires_at')
        self.orb_quantity: Optional[int] = data.get('orb_quantity')
        messages = data.get('messages', {})
        self.name: str = messages.get('name', '')
        self.name_with_article: str = messages.get('name_with_article', '')

    def __repr__(self) -> str:
        return f'<QuestReward type={self.type} name={self.name!r} sku_id={self.sku_id!r}>'


class QuestConfig:
    __slots__ = (
        'id', 'config_version', 'starts_at', 'expires_at', 'features',
        'application_id', 'application_name', 'quest_name', 'game_title',
        'game_publisher', 'rewards', 'tasks', 'primary_color', 'secondary_color',
        'hero_asset', 'game_tile_asset', 'share_policy', 'cta_link', 'cta_label',
    )

    def __init__(self, data: dict):
        self.id: str = data.get('id', '')
        self.config_version: int = data.get('config_version', 2)
        self.starts_at: Optional[str] = data.get('starts_at')
        self.expires_at: Optional[str] = data.get('expires_at')
        self.features: List[int] = data.get('features', [])

        app = data.get('application', {})
        self.application_id: str = app.get('id', '')
        self.application_name: str = app.get('name', '')

        messages = data.get('messages', {})
        self.quest_name: str = messages.get('quest_name', '')
        self.game_title: str = messages.get('game_title', '')
        self.game_publisher: str = messages.get('game_publisher', '')

        rewards_cfg = data.get('rewards_config', {})
        self.rewards: List[QuestReward] = [QuestReward(r) for r in rewards_cfg.get('rewards', [])]

        task_cfg = data.get('task_config_v2', {})
        self.tasks: Dict[str, Any] = task_cfg.get('tasks', {})

        colors = data.get('colors', {})
        self.primary_color: str = colors.get('primary', '')
        self.secondary_color: str = colors.get('secondary', '')

        assets = data.get('assets', {})
        self.hero_asset: str = assets.get('hero', '')
        self.game_tile_asset: str = assets.get('game_tile', '')

        self.share_policy: str = data.get('share_policy', '')

        cta = data.get('cta_config', {})
        self.cta_link: str = cta.get('link', '')
        self.cta_label: str = cta.get('button_label', '')

    def __repr__(self) -> str:
        return f'<QuestConfig id={self.id!r} game={self.game_title!r} expires={self.expires_at!r}>'

    def get_task_target(self, task_type: str) -> Optional[int]:
        task = self.tasks.get(task_type, {})
        return task.get('target')

    def get_task_application_ids(self, task_type: str) -> List[str]:
        task = self.tasks.get(task_type, {})
        return [a['id'] for a in task.get('applications', [])]


class Quest:
    __slots__ = ('id', 'config', 'user_status', 'preview')

    def __init__(self, data: dict):
        self.id: str = data['id']
        self.config: QuestConfig = QuestConfig(data.get('config', {}))
        self.preview: bool = data.get('preview', False)
        status = data.get('user_status')
        self.user_status: Optional[QuestUserStatus] = QuestUserStatus(status) if status else None

    def __repr__(self) -> str:
        return f'<Quest id={self.id!r} game={self.config.game_title!r} enrolled={self.enrolled}>'

    def __str__(self) -> str:
        return self.config.quest_name

    @property
    def enrolled(self) -> bool:
        return self.user_status is not None and self.user_status.enrolled

    @property
    def completed(self) -> bool:
        return self.user_status is not None and self.user_status.completed

    @property
    def claimed(self) -> bool:
        return self.user_status is not None and self.user_status.claimed

    @property
    def application_id(self) -> str:
        return self.config.application_id

    @property
    def rewards(self) -> List[QuestReward]:
        return self.config.rewards


class ClaimedQuest:
    __slots__ = ('id', 'config', 'user_status')

    def __init__(self, data: dict):
        self.id: str = data['id']
        self.config = data.get('config', {})
        status = data.get('user_status')
        self.user_status: Optional[QuestUserStatus] = QuestUserStatus(status) if status else None

    def __repr__(self) -> str:
        return f'<ClaimedQuest id={self.id!r}>'
