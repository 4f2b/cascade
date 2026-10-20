from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.session import Session
    from ...entities.message import Message


class Context:
    def __init__(self, bot: 'Session', message: 'Message', *, command_prefix: str):
        self.bot = bot
        self.message = message
        self.command_prefix = command_prefix
        self.channel = message.channel
        self.guild = message.guild
        self.author = message.author

    async def send(self, content: str = None, **kwargs):
        return await self.channel.send(content, **kwargs)

    async def reply(self, content: str = None, mention: bool = False, **kwargs):
        return await self.message.reply(content, mention=mention, **kwargs)
