import re
from typing import Optional

USERNAME_REGEX = re.compile(r'^.{2,32}$')
DISCRIMINATOR_REGEX = re.compile(r'^\d{4}$')
SNOWFLAKE_REGEX = re.compile(r'^[0-9]{17,20}$')
INVITE_REGEX = re.compile(r'(?:https?://)?(?:www\.)?(?:discord\.gg|discord(?:app)?\.com/invite)/([a-zA-Z0-9-]+)')
MESSAGE_LINK_REGEX = re.compile(r'https?://(?:ptb\.|canary\.)?discord(?:app)?\.com/channels/(\d+|@me)/(\d+)/(\d+)')

def is_valid_username(username: str) -> bool:
    return USERNAME_REGEX.match(username) is not None

def is_valid_discriminator(discriminator: str) -> bool:
    return DISCRIMINATOR_REGEX.match(discriminator) is not None

def is_valid_snowflake(snowflake: str) -> bool:
    return SNOWFLAKE_REGEX.match(str(snowflake)) is not None

def extract_invite_code(text: str) -> Optional[str]:
    match = INVITE_REGEX.search(text)
    return match.group(1) if match else None

def parse_message_link(url: str) -> Optional[tuple]:
    match = MESSAGE_LINK_REGEX.match(url)
    if match:
        guild_id, channel_id, message_id = match.groups()
        return (
            int(guild_id) if guild_id != '@me' else None,
            int(channel_id),
            int(message_id)
        )
    return None

def validate_token(token: str) -> bool:
    parts = token.split('.')
    return len(parts) == 3 and all(parts)
