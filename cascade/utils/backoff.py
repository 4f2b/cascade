import asyncio
import random
from typing import Callable, Any, Optional, Type
from functools import wraps

class ExponentialBackoff:
    def __init__(self, base: float = 1.0, max_value: float = 60.0, jitter: bool = True):
        self.base = base
        self.max_value = max_value
        self.jitter = jitter
        self._attempt = 0
    
    def __next__(self) -> float:
        value = min(self.base * (2 ** self._attempt), self.max_value)
        if self.jitter:
            value = value * (0.5 + random.random() / 2)
        self._attempt += 1
        return value
    
    def reset(self):
        self._attempt = 0

def retry(
    max_attempts: int = 3,
    exceptions: tuple = (Exception,),
    backoff: ExponentialBackoff = None,
    on_retry: Optional[Callable] = None
):
    if backoff is None:
        backoff = ExponentialBackoff()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            backoff.reset()
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = next(backoff)
                        if on_retry:
                            await on_retry(attempt, delay, e)
                        await asyncio.sleep(delay)
                    else:
                        raise
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator
