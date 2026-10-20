class Color:
    def __init__(self, value: int):
        if not 0 <= value <= 0xFFFFFF:
            raise ValueError('Color value must be between 0 and 0xFFFFFF')
        self.value = value

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> 'Color':
        return cls((r << 16) + (g << 8) + b)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> 'Color':
        if s == 0.0:
            return cls.from_rgb(int(v * 255), int(v * 255), int(v * 255))
        
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = int(255 * (v * (1.0 - s)))
        q = int(255 * (v * (1.0 - s * f)))
        t = int(255 * (v * (1.0 - s * (1.0 - f))))
        v = int(v * 255)
        i = i % 6
        
        if i == 0:
            return cls.from_rgb(v, t, p)
        if i == 1:
            return cls.from_rgb(q, v, p)
        if i == 2:
            return cls.from_rgb(p, v, t)
        if i == 3:
            return cls.from_rgb(p, q, v)
        if i == 4:
            return cls.from_rgb(t, p, v)
        if i == 5:
            return cls.from_rgb(v, p, q)

    def to_rgb(self) -> tuple:
        return (self.value >> 16) & 0xFF, (self.value >> 8) & 0xFF, self.value & 0xFF

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return f'#{self.value:06x}'

    def __repr__(self) -> str:
        return f'<Color value={self.value}>'

    def __eq__(self, other) -> bool:
        return isinstance(other, Color) and self.value == other.value


class Colors:
    DEFAULT = 0x000000
    WHITE = 0xFFFFFF
    AQUA = 0x1ABC9C
    GREEN = 0x57F287
    BLUE = 0x3498DB
    YELLOW = 0xFEE75C
    PURPLE = 0x9B59B6
    LUMINOUS_VIVID_PINK = 0xE91E63
    FUCHSIA = 0xEB459E
    GOLD = 0xF1C40F
    ORANGE = 0xE67E22
    RED = 0xED4245
    GREY = 0x95A5A6
    NAVY = 0x34495E
    DARK_AQUA = 0x11806A
    DARK_GREEN = 0x1F8B4C
    DARK_BLUE = 0x206694
    DARK_PURPLE = 0x71368A
    DARK_VIVID_PINK = 0xAD1457
    DARK_GOLD = 0xC27C0E
    DARK_ORANGE = 0xA84300
    DARK_RED = 0x992D22
    DARK_GREY = 0x979C9F
    DARKER_GREY = 0x7F8C8D
    LIGHT_GREY = 0xBCC0C0
    DARK_NAVY = 0x2C3E50
    BLURPLE = 0x5865F2
    GREYPLE = 0x99AAB5
    DARK_BUT_NOT_BLACK = 0x2C2F33
    NOT_QUITE_BLACK = 0x23272A
    BLACK = 0x000000
