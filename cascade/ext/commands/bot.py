from typing import Callable, Dict, Optional
from ...core.session import Session
from .context import Context


class Bot(Session):
    def __init__(self, token: str, *, command_prefix: str = '!', **kwargs):
        super().__init__(token, **kwargs)
        self.command_prefix = command_prefix
        self.commands: Dict[str, Callable] = {}
        self.event(self._on_message)

    def command(self, name: str = None):
        def decorator(func: Callable):
            cmd_name = name or func.__name__
            self.commands[cmd_name] = func
            return func
        return decorator

    async def _on_message(self, message):
        if message.author.id == self.user.id:
            return
        
        if not message.content.startswith(self.command_prefix):
            return
        
        content = message.content[len(self.command_prefix):]
        if not content:
            return
        
        parts = content.split()
        command_name = parts[0].lower()
        args = parts[1:]
        
        command = self.commands.get(command_name)
        if not command:
            return
        
        ctx = Context(self, message, command_prefix=self.command_prefix)
        
        try:
            await command(ctx, *args)
        except Exception as e:
            await self.on_command_error(ctx, e)

    async def on_command_error(self, ctx: Context, error: Exception):
        pass
