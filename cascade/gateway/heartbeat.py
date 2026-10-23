import asyncio
import time
from typing import Optional


class Heartbeat:
    def __init__(self, shard, interval_ms: float):
        self._shard = shard
        self._interval = interval_ms / 1000.0
        self._task: Optional[asyncio.Task] = None
        self._acknowledged = True
        self._last_send: float = 0.0
        self._last_ack: float = time.monotonic()
        self._missed = 0

    async def start(self) -> None:
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def ack(self) -> None:
        self._acknowledged = True
        self._last_ack = time.monotonic()
        self._missed = 0

    @property
    def latency(self) -> float:
        if self._last_ack >= self._last_send and self._last_send > 0:
            return self._last_ack - self._last_send
        return 0.0

    async def _loop(self) -> None:
        while True:
            await asyncio.sleep(self._interval)

            if not self._acknowledged:
                self._missed += 1
                if self._missed >= 2:
                    asyncio.create_task(self._shard._handle_zombie())
                    return

            self._acknowledged = False
            self._last_send = time.monotonic()
            try:
                await self._shard.send_heartbeat()
            except Exception:
                return
