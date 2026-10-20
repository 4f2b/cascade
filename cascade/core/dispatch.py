import asyncio
from typing import Dict, List, Callable, Any, Coroutine


class EventDispatcher:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._waiters: Dict[str, List[asyncio.Future]] = {}

    def register(self, event: str, callback: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def unregister(self, event: str, callback: Callable) -> None:
        if event in self._listeners:
            try:
                self._listeners[event].remove(callback)
            except ValueError:
                pass

    def dispatch(self, event: str, *args, **kwargs) -> None:
        if event in self._listeners:
            for callback in self._listeners[event]:
                asyncio.create_task(self._execute_callback(callback, *args, **kwargs))
        
        if event in self._waiters:
            waiters = self._waiters.pop(event)
            for future in waiters:
                if not future.done():
                    future.set_result((args, kwargs))

    async def _execute_callback(self, callback: Callable, *args, **kwargs) -> None:
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)
        except Exception as e:
            pass

    async def wait_for(self, event: str, check: Callable = None, timeout: float = None) -> Any:
        future = asyncio.get_event_loop().create_future()
        
        if event not in self._waiters:
            self._waiters[event] = []
        self._waiters[event].append(future)

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            args, kwargs = result
            
            if check is None:
                return args[0] if len(args) == 1 else args
            
            if check(*args, **kwargs):
                return args[0] if len(args) == 1 else args
            else:
                return await self.wait_for(event, check, timeout)
        except asyncio.TimeoutError:
            self._waiters[event].remove(future)
            raise
