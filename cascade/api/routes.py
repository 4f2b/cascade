BASE = 'https://discord.com/api/v10'

def channel(channel_id: str) -> str:
    return f'{BASE}/channels/{channel_id}'

def channel_messages(channel_id: str) -> str:
    return f'{BASE}/channels/{channel_id}/messages'

def channel_message(channel_id: str, message_id: str) -> str:
    return f'{BASE}/channels/{channel_id}/messages/{message_id}'

def channel_typing(channel_id: str) -> str:
    return f'{BASE}/channels/{channel_id}/typing'

def channel_pins(channel_id: str) -> str:
    return f'{BASE}/channels/{channel_id}/pins'

def channel_pin(channel_id: str, message_id: str) -> str:
    return f'{BASE}/channels/{channel_id}/pins/{message_id}'

def guild(guild_id: str) -> str:
    return f'{BASE}/guilds/{guild_id}'

def guild_channels(guild_id: str) -> str:
    return f'{BASE}/guilds/{guild_id}/channels'

def guild_members(guild_id: str) -> str:
    return f'{BASE}/guilds/{guild_id}/members'

def guild_member(guild_id: str, user_id: str) -> str:
    return f'{BASE}/guilds/{guild_id}/members/{user_id}'

def guild_bans(guild_id: str) -> str:
    return f'{BASE}/guilds/{guild_id}/bans'

def guild_ban(guild_id: str, user_id: str) -> str:
    return f'{BASE}/guilds/{guild_id}/bans/{user_id}'

def guild_roles(guild_id: str) -> str:
    return f'{BASE}/guilds/{guild_id}/roles'

def guild_role(guild_id: str, role_id: str) -> str:
    return f'{BASE}/guilds/{guild_id}/roles/{role_id}'

def user(user_id: str) -> str:
    return f'{BASE}/users/{user_id}'

def me() -> str:
    return f'{BASE}/users/@me'

def me_guilds() -> str:
    return f'{BASE}/users/@me/guilds'

def me_guild(guild_id: str) -> str:
    return f'{BASE}/users/@me/guilds/{guild_id}'

def me_channels() -> str:
    return f'{BASE}/users/@me/channels'

def me_connections() -> str:
    return f'{BASE}/users/@me/connections'

def me_settings() -> str:
    return f'{BASE}/users/@me/settings'

def gateway() -> str:
    return f'{BASE}/gateway'

def gateway_bot() -> str:
    return f'{BASE}/gateway/bot'

def relationships() -> str:
    return f'{BASE}/users/@me/relationships'

def relationship(user_id: str) -> str:
    return f'{BASE}/users/@me/relationships/{user_id}'

def applications() -> str:
    return f'{BASE}/applications'

def application(app_id: str) -> str:
    return f'{BASE}/applications/{app_id}'
