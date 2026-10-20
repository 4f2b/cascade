from datetime import datetime, timezone


DISCORD_EPOCH = 1420070400000


def snowflake_time(snowflake: int) -> datetime:
    timestamp = ((snowflake >> 22) + DISCORD_EPOCH) / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def time_snowflake(dt: datetime, high: bool = False) -> int:
    unix_ms = int(dt.timestamp() * 1000)
    discord_ms = unix_ms - DISCORD_EPOCH
    snowflake = discord_ms << 22
    if high:
        snowflake |= 0x3FFFFF
    return snowflake


def snowflake_worker_id(snowflake: int) -> int:
    return (snowflake & 0x3E0000) >> 17


def snowflake_process_id(snowflake: int) -> int:
    return (snowflake & 0x1F000) >> 12


def snowflake_increment(snowflake: int) -> int:
    return snowflake & 0xFFF

class Snowflake:
    @staticmethod
    def creation_time(snowflake: int) -> datetime:
        return snowflake_time(snowflake)
    
    @staticmethod
    def worker_id(snowflake: int) -> int:
        return snowflake_worker_id(snowflake)
    
    @staticmethod
    def process_id(snowflake: int) -> int:
        return snowflake_process_id(snowflake)
    
    @staticmethod
    def increment(snowflake: int) -> int:
        return snowflake_increment(snowflake)
    
    @staticmethod
    def from_timestamp(dt: datetime, high: bool = False) -> int:
        return time_snowflake(dt, high)
