from typing import Dict, Optional, Any
from collections import OrderedDict


class CacheStore:
    def __init__(self, max_size: int = 1000):
        self._data: OrderedDict = OrderedDict()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        if key in self._data:
            self._data.move_to_end(key)
            return self._data[key]
        return None

    def set(self, key: str, value: Any) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self._max_size:
            self._data.popitem(last=False)

    def remove(self, key: str) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()


class Cache:
    def __init__(self, message_limit: int = 1000):
        self.messages = CacheStore(max_size=message_limit)
        self.guilds: Dict[str, Any] = {}
        self.channels: Dict[str, Any] = {}
        self.users: Dict[str, Any] = {}
        self.members: Dict[str, Dict[str, Any]] = {}
        self._read_states: Dict[str, Any] = {}

    def get_guild(self, guild_id: str) -> Optional[Any]:
        return self.guilds.get(guild_id)

    def add_guild(self, guild: Any) -> None:
        self.guilds[guild.id] = guild

    def remove_guild(self, guild_id: str) -> None:
        self.guilds.pop(guild_id, None)

    def get_channel(self, channel_id: str) -> Optional[Any]:
        return self.channels.get(channel_id)

    def add_channel(self, channel: Any) -> None:
        self.channels[channel.id] = channel

    def remove_channel(self, channel_id: str) -> None:
        self.channels.pop(channel_id, None)

    def get_user(self, user_id: str) -> Optional[Any]:
        return self.users.get(user_id)

    def add_user(self, user: Any) -> None:
        self.users[user.id] = user

    def get_member(self, guild_id: str, user_id: str) -> Optional[Any]:
        return self.members.get(guild_id, {}).get(user_id)

    def add_member(self, guild_id: str, member: Any) -> None:
        if guild_id not in self.members:
            self.members[guild_id] = {}
        self.members[guild_id][member.id] = member

    def remove_member(self, guild_id: str, user_id: str) -> None:
        if guild_id in self.members:
            self.members[guild_id].pop(user_id, None)

    def get_message(self, message_id: str) -> Optional[Any]:
        return self.messages.get(message_id)

    def add_message(self, message: Any) -> None:
        self.messages.set(message.id, message)

    def remove_message(self, message_id: str) -> None:
        self.messages.remove(message_id)

    def clear(self) -> None:
        self.messages.clear()
        self.guilds.clear()
        self.channels.clear()
        self.users.clear()
        self.members.clear()
