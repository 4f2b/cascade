from typing import Callable, List, Dict, Any
from collections import defaultdict
import asyncio
import inspect

class EventManager:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._once_listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._wait_for: Dict[str, List[asyncio.Future]] = defaultdict(list)
    
    def on(self, event: str):
        def decorator(func: Callable) -> Callable:
            self._listeners[event].append(func)
            return func
        return decorator
    
    def once(self, event: str):
        def decorator(func: Callable) -> Callable:
            self._once_listeners[event].append(func)
            return func
        return decorator
    
    def remove_listener(self, event: str, func: Callable):
        if func in self._listeners[event]:
            self._listeners[event].remove(func)
        if func in self._once_listeners[event]:
            self._once_listeners[event].remove(func)
    
    def remove_all_listeners(self, event: str = None):
        if event:
            self._listeners[event].clear()
            self._once_listeners[event].clear()
        else:
            self._listeners.clear()
            self._once_listeners.clear()
    
    async def emit(self, event: str, *args, **kwargs):
        tasks = []
        
        for listener in self._listeners[event]:
            tasks.append(self._call_listener(listener, *args, **kwargs))
        
        once_listeners = self._once_listeners[event].copy()
        self._once_listeners[event].clear()
        for listener in once_listeners:
            tasks.append(self._call_listener(listener, *args, **kwargs))
        
        for future in self._wait_for.get(event, []):
            if not future.done():
                future.set_result((args, kwargs))
        self._wait_for[event].clear()
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _call_listener(self, func: Callable, *args, **kwargs):
        try:
            if inspect.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
        except Exception as e:
            await self.emit('error', e)
    
    async def wait_for(self, event: str, check: Callable = None, timeout: float = None) -> Any:
        future = asyncio.get_event_loop().create_future()
        self._wait_for[event].append(future)
        
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            args, kwargs = result
            
            if check is None:
                return args[0] if len(args) == 1 else args
            
            if check(*args, **kwargs):
                return args[0] if len(args) == 1 else args
            
            return await self.wait_for(event, check, timeout)
        except asyncio.TimeoutError:
            self._wait_for[event].remove(future)
            raise
    
    def listener_count(self, event: str) -> int:
        return len(self._listeners[event]) + len(self._once_listeners[event])
    
    def has_listeners(self, event: str) -> bool:
        return self.listener_count(event) > 0
