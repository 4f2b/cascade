from typing import Callable


def command(name: str = None):
    def decorator(func: Callable):
        func.__command_name__ = name or func.__name__
        return func
    return decorator
