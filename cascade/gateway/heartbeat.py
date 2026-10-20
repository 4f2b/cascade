import asyncio
import time
from typing import Optional


class Heartbeat:
    def __init__(self, ws, interval: float):
        self.ws = ws
        self.interval = interval / 1000.0
        self._task: Optional[asyncio.Task] = None
        self._stop = False
        self._acknowledged = True
        self._last_ack = time.time()
        self._last_send = time.time()

    async def start(self) -> None:
        self._stop = False
        self._task = asyncio.create_task(self._run())

    async def _run(self) -> None:
        while not self._stop:
            await asyncio.sleep(self.interval)
            
            now = time.time()
            if not self._acknowledged:
                if now - self._last_send > self.interval * 2:
                    await self.ws._handle_zombie()
                    return
            
            self._acknowledged = False
            self._last_send = now
            await self.ws.send_heartbeat()

    def ack(self) -> None:
        self._acknowledged = True
        self._last_ack = time.time()

    @property
    def latency(self) -> float:
        return self._last_ack - self._last_send if self._last_ack > self._last_send else 0.0

    async def stop(self) -> None:
        self._stop = True
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
