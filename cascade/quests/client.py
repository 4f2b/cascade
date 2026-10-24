from __future__ import annotations

import asyncio
import random
import time
from typing import List, Optional, TYPE_CHECKING

from .quest import Quest, ClaimedQuest, QuestUserStatus

if TYPE_CHECKING:
    from ..core.session import Session

BASE = 'https://discord.com/api/v10'

_HEARTBEAT_INTERVAL_MIN = 55.0
_HEARTBEAT_INTERVAL_MAX = 65.0
_HEARTBEAT_JITTER = 5.0


class QuestClient:
    """
    High-level interface for Discord Quests.

    Safety notes:
    - Heartbeats are rate-limited to realistic intervals (55-65s) matching the official client.
    - The Electron user-agent is used automatically since Discord's server validates it.
    - No burst requests — all repeated calls include human-like delays.
    - Never call heartbeat faster than once per minute or Discord will flag the account.
    """

    def __init__(self, session: 'Session'):
        self._session = session
        self._heartbeat_tasks: dict = {}

    @property
    def _rest(self):
        return self._session.rest

    async def get_quests(self) -> List[Quest]:
        data = await self._rest.get(f'{BASE}/quests/@me')
        quests_data = data.get('quests', []) if isinstance(data, dict) else data
        return [Quest(q) for q in quests_data]

    async def get_claimed_quests(self) -> List[ClaimedQuest]:
        data = await self._rest.get(f'{BASE}/quests/@me/claimed')
        quests_data = data.get('quests', []) if isinstance(data, dict) else data
        return [ClaimedQuest(q) for q in quests_data]

    async def get_quest(self, quest_id: str) -> Quest:
        data = await self._rest.get(f'{BASE}/quests/{quest_id}')
        return Quest(data)

    async def get_active_quests(self) -> List[Quest]:
        quests = await self.get_quests()
        return [
            q for q in quests
            if q.enrolled and not q.completed and not q.claimed
        ]

    async def get_completable_quests(self) -> List[Quest]:
        quests = await self.get_quests()
        return [q for q in quests if not q.enrolled and not q.preview]

    async def enroll(self, quest_id: str, location: int = 11) -> QuestUserStatus:
        data = await self._rest.post(
            f'{BASE}/quests/{quest_id}/enroll',
            json={'location': location},
        )
        return QuestUserStatus(data)

    async def claim_reward(self, quest_id: str, platform: int = 0, location: int = 11) -> dict:
        return await self._rest.post(
            f'{BASE}/quests/{quest_id}/claim-reward',
            json={'location': location, 'platform': platform},
        )

    async def get_reward_code(self, quest_id: str) -> dict:
        return await self._rest.get(f'{BASE}/quests/{quest_id}/reward-code')

    async def dismiss_content(self, quest_id: str, content_type: int) -> QuestUserStatus:
        data = await self._rest.post(
            f'{BASE}/quests/{quest_id}/dismissible-content/{content_type}/dismiss',
            json={},
        )
        return QuestUserStatus(data)

    async def send_heartbeat(
        self,
        quest_id: str,
        *,
        application_id: str = None,
        stream_key: str = None,
        terminal: bool = False,
        executable_path: str = None,
    ) -> QuestUserStatus:
        payload: dict = {}
        if application_id:
            payload['application_id'] = application_id
        if stream_key:
            payload['stream_key'] = stream_key
        if terminal:
            payload['terminal'] = True
        if executable_path:
            payload['executable_path'] = executable_path

        data = await self._rest.post(f'{BASE}/quests/{quest_id}/heartbeat', json=payload)
        return QuestUserStatus(data)

    async def send_video_progress(self, quest_id: str, timestamp: int) -> QuestUserStatus:
        data = await self._rest.post(
            f'{BASE}/quests/{quest_id}/video-progress',
            json={'timestamp': timestamp},
        )
        return QuestUserStatus(data)

    async def start_console_quest(self, quest_id: str) -> dict:
        return await self._rest.post(f'{BASE}/quests/{quest_id}/console/start', json={})

    async def stop_console_quest(self, quest_id: str) -> None:
        await self._rest.post(f'{BASE}/quests/{quest_id}/console/stop', json={})

    async def get_quest_placement(self, placement: int, client_ad_session_id: str = None) -> dict:
        params: dict = {'placement': placement}
        if client_ad_session_id:
            params['client_ad_session_id'] = client_ad_session_id
        return await self._rest.get(f'{BASE}/quests/decision', params=params)

    async def run_heartbeat_loop(
        self,
        quest_id: str,
        application_id: str,
        *,
        stream_key: str = None,
        duration_seconds: int = 900,
        on_progress=None,
    ) -> QuestUserStatus:
        """
        Run a heartbeat loop for a play/stream quest. Sends heartbeats at
        realistic intervals (55-65s) until the required duration is met or
        the quest completes.

        Args:
            quest_id: The quest to heartbeat.
            application_id: The Discord application ID of the game.
            stream_key: Required for STREAM_ON_DESKTOP quests.
            duration_seconds: Target duration in seconds (default 900 = 15 min).
            on_progress: Optional async callback(status) called after each heartbeat.

        Returns the final QuestUserStatus.
        """
        elapsed = 0
        last_status: Optional[QuestUserStatus] = None

        while elapsed < duration_seconds:
            interval = random.uniform(_HEARTBEAT_INTERVAL_MIN, _HEARTBEAT_INTERVAL_MAX)
            jitter = random.uniform(0, _HEARTBEAT_JITTER)
            wait = interval + jitter

            await asyncio.sleep(wait)
            elapsed += wait

            is_terminal = elapsed >= duration_seconds
            try:
                last_status = await self.send_heartbeat(
                    quest_id,
                    application_id=application_id,
                    stream_key=stream_key,
                    terminal=is_terminal,
                )
            except Exception:
                await asyncio.sleep(random.uniform(5, 15))
                continue

            if on_progress:
                try:
                    await on_progress(last_status)
                except Exception:
                    pass

            if last_status and last_status.completed:
                break

        return last_status

    async def run_video_quest(
        self,
        quest_id: str,
        target_seconds: int,
        *,
        on_progress=None,
    ) -> QuestUserStatus:
        """
        Run a video quest by sending progress updates at realistic intervals.

        Args:
            quest_id: The quest to progress.
            target_seconds: Total video duration in seconds.
            on_progress: Optional async callback(status) called after each update.
        """
        position = 0
        last_status: Optional[QuestUserStatus] = None
        update_interval = 12

        while position < target_seconds:
            step = random.randint(10, 15)
            position = min(position + step, target_seconds)
            await asyncio.sleep(update_interval + random.uniform(0, 3))

            try:
                last_status = await self.send_video_progress(quest_id, position)
            except Exception:
                await asyncio.sleep(random.uniform(5, 10))
                continue

            if on_progress:
                try:
                    await on_progress(last_status)
                except Exception:
                    pass

            if last_status and last_status.completed:
                break

        return last_status
