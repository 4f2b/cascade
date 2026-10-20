from enum import IntFlag

class Permission(IntFlag):
    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    MANAGE_GUILD = 1 << 5
    ADD_REACTIONS = 1 << 6
    VIEW_AUDIT_LOG = 1 << 7
    PRIORITY_SPEAKER = 1 << 8
    STREAM = 1 << 9
    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    SEND_TTS_MESSAGES = 1 << 12
    MANAGE_MESSAGES = 1 << 13
    EMBED_LINKS = 1 << 14
    ATTACH_FILES = 1 << 15
    READ_MESSAGE_HISTORY = 1 << 16
    MENTION_EVERYONE = 1 << 17
    USE_EXTERNAL_EMOJIS = 1 << 18
    VIEW_GUILD_INSIGHTS = 1 << 19
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MUTE_MEMBERS = 1 << 22
    DEAFEN_MEMBERS = 1 << 23
    MOVE_MEMBERS = 1 << 24
    USE_VAD = 1 << 25
    CHANGE_NICKNAME = 1 << 26
    MANAGE_NICKNAMES = 1 << 27
    MANAGE_ROLES = 1 << 28
    MANAGE_WEBHOOKS = 1 << 29
    MANAGE_GUILD_EXPRESSIONS = 1 << 30
    USE_APPLICATION_COMMANDS = 1 << 31
    REQUEST_TO_SPEAK = 1 << 32
    MANAGE_EVENTS = 1 << 33
    MANAGE_THREADS = 1 << 34
    CREATE_PUBLIC_THREADS = 1 << 35
    CREATE_PRIVATE_THREADS = 1 << 36
    USE_EXTERNAL_STICKERS = 1 << 37
    SEND_MESSAGES_IN_THREADS = 1 << 38
    USE_EMBEDDED_ACTIVITIES = 1 << 39
    MODERATE_MEMBERS = 1 << 40
    VIEW_CREATOR_MONETIZATION_ANALYTICS = 1 << 41
    USE_SOUNDBOARD = 1 << 42
    USE_EXTERNAL_SOUNDS = 1 << 45
    SEND_VOICE_MESSAGES = 1 << 46

class Permissions:
    def __init__(self, permissions: int = 0):
        self.value = permissions
    
    def has(self, *perms: Permission) -> bool:
        return all((self.value & perm) == perm for perm in perms)
    
    def add(self, *perms: Permission):
        for perm in perms:
            self.value |= perm
    
    def remove(self, *perms: Permission):
        for perm in perms:
            self.value &= ~perm
    
    def is_subset(self, other: 'Permissions') -> bool:
        return (self.value & other.value) == self.value
    
    def is_superset(self, other: 'Permissions') -> bool:
        return (self.value & other.value) == other.value
    
    def is_admin(self) -> bool:
        return self.has(Permission.ADMINISTRATOR)
    
    @classmethod
    def all(cls) -> 'Permissions':
        return cls((1 << 47) - 1)
    
    @classmethod
    def none(cls) -> 'Permissions':
        return cls(0)
    
    @classmethod
    def text(cls) -> 'Permissions':
        perms = cls()
        perms.add(
            Permission.VIEW_CHANNEL,
            Permission.SEND_MESSAGES,
            Permission.EMBED_LINKS,
            Permission.ATTACH_FILES,
            Permission.ADD_REACTIONS,
            Permission.USE_EXTERNAL_EMOJIS,
            Permission.READ_MESSAGE_HISTORY
        )
        return perms
    
    @classmethod
    def voice(cls) -> 'Permissions':
        perms = cls()
        perms.add(
            Permission.VIEW_CHANNEL,
            Permission.CONNECT,
            Permission.SPEAK,
            Permission.STREAM,
            Permission.USE_VAD
        )
        return perms
    
    def __repr__(self) -> str:
        return f'<Permissions value={self.value}>'
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Permissions) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
