from typing import TYPE_CHECKING
import asyncio
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from .rest import RESTClient

class TypingIndicator:
    def __init__(self, rest: 'RESTClient', channel_id: int):
        self._rest = rest
        self._channel_id = channel_id
        self._task = None
        self._last_sent = None
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, *args):
        await self.stop()
        
    async def start(self):
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._typing_loop())
        
    async def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None
        self._last_sent = None
        
    async def _typing_loop(self):
        try:
            while True:
                now = datetime.utcnow()
                if self._last_sent is None or now - self._last_sent >= timedelta(seconds=8):
                    await self._rest.trigger_typing(self._channel_id)
                    self._last_sent = now
                await asyncio.sleep(8)
        except asyncio.CancelledError:
            pass
