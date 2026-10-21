import base64
import json
from typing import Dict, Any, Optional


PLATFORM_PRESETS = {
    "desktop": {
        "os": "Windows", "browser": "Discord Client", "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9262 Chrome/155.0.0.0 Electron/36.0.0 Safari/537.36",
        "browser_version": "1.0.9262", "os_version": "10.0.22631",
        "client_build_number": 630444, "release_channel": "stable",
    },
    "windows": {
        "os": "Windows", "browser": "Discord Client", "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9262 Chrome/155.0.0.0 Electron/36.0.0 Safari/537.36",
        "browser_version": "1.0.9262", "os_version": "10.0.22631",
        "client_build_number": 630444, "release_channel": "stable",
    },
    "macos": {
        "os": "Mac OS X", "browser": "Discord Client", "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9262 Chrome/155.0.0.0 Electron/36.0.0 Safari/537.36",
        "browser_version": "1.0.9262", "os_version": "14.5.0",
        "client_build_number": 630444, "release_channel": "stable",
    },
    "linux": {
        "os": "Linux", "browser": "Discord Client", "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9262 Chrome/155.0.0.0 Electron/36.0.0 Safari/537.36",
        "browser_version": "1.0.9262", "os_version": "6.8.0",
        "client_build_number": 630444, "release_channel": "stable",
    },
    "web": {
        "os": "Windows", "browser": "Discord Web", "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
        "browser_version": "155.0.0.0", "os_version": "10",
        "client_build_number": 630444, "release_channel": "stable",
    },
    "mobile": {
        "os": "Android", "browser": "Discord Android", "device": "Pixel 8",
        "system_locale": "en-US",
        "browser_user_agent": "Discord-Android/349.9;ROM:14;Device:Pixel 8",
        "browser_version": "349.9", "os_version": "14",
        "client_build_number": 349009, "release_channel": "stable",
    },
    "android": {
        "os": "Android", "browser": "Discord Android", "device": "Pixel 8",
        "system_locale": "en-US",
        "browser_user_agent": "Discord-Android/349.9;ROM:14;Device:Pixel 8",
        "browser_version": "349.9", "os_version": "14",
        "client_build_number": 349009, "release_channel": "stable",
    },
    "ios": {
        "os": "iOS", "browser": "Discord iOS", "device": "iPhone16,2",
        "system_locale": "en-US",
        "browser_user_agent": "Discord/349.0 CFNetwork/1490 Darwin/23.6.0",
        "browser_version": "349.0", "os_version": "18.0",
        "client_build_number": 349000, "release_channel": "stable",
    },
    "iphone": {
        "os": "iOS", "browser": "Discord iOS", "device": "iPhone16,2",
        "system_locale": "en-US",
        "browser_user_agent": "Discord/349.0 CFNetwork/1490 Darwin/23.6.0",
        "browser_version": "349.0", "os_version": "18.0",
        "client_build_number": 349000, "release_channel": "stable",
    },
    "ipad": {
        "os": "iOS", "browser": "Discord iOS", "device": "iPad13,4",
        "system_locale": "en-US",
        "browser_user_agent": "Discord/349.0 CFNetwork/1490 Darwin/23.6.0",
        "browser_version": "349.0", "os_version": "18.0",
        "client_build_number": 349000, "release_channel": "stable",
    },
    "vr": {
        "os": "Console", "browser": "Discord VR", "device": "Meta Quest 3",
        "system_locale": "en-US",
        "browser_user_agent": "DiscordVR/23.7.91",
        "browser_version": "23.7.91", "os_version": "10.0.45",
        "client_build_number": 230791, "release_channel": "stable",
    },
    "quest": {
        "os": "Console", "browser": "Discord VR", "device": "Meta Quest 3",
        "system_locale": "en-US",
        "browser_user_agent": "DiscordVR/23.7.91",
        "browser_version": "23.7.91", "os_version": "10.0.45",
        "client_build_number": 230791, "release_channel": "stable",
    },
    "quest2": {
        "os": "Console", "browser": "Discord VR", "device": "Meta Quest 2",
        "system_locale": "en-US",
        "browser_user_agent": "DiscordVR/23.7.91",
        "browser_version": "23.7.91", "os_version": "10.0.45",
        "client_build_number": 230791, "release_channel": "stable",
    },
    "quest3": {
        "os": "Console", "browser": "Discord VR", "device": "Meta Quest 3",
        "system_locale": "en-US",
        "browser_user_agent": "DiscordVR/23.7.91",
        "browser_version": "23.7.91", "os_version": "10.0.45",
        "client_build_number": 230791, "release_channel": "stable",
    },
    "xbox": {
        "os": "Console", "browser": "Discord Embedded", "device": "Xbox Series X",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox Series X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
        "browser_version": "", "os_version": "",
        "client_build_number": 1, "release_channel": "stable",
    },
    "playstation": {
        "os": "Console", "browser": "Discord Embedded", "device": "PlayStation 5",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (PlayStation 5 3.11) AppleWebKit/605.1.15 (KHTML, like Gecko)",
        "browser_version": "", "os_version": "",
        "client_build_number": 1, "release_channel": "stable",
    },
    "ps5": {
        "os": "Console", "browser": "Discord Embedded", "device": "PlayStation 5",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (PlayStation 5 3.11) AppleWebKit/605.1.15 (KHTML, like Gecko)",
        "browser_version": "", "os_version": "",
        "client_build_number": 1, "release_channel": "stable",
    },
}


class PlatformSpoofer:
    def __init__(self, platform: str = "desktop"):
        self.platform = platform.lower()
        self.properties = self._build_properties(self.platform)

    def _build_properties(self, platform: str) -> Dict[str, Any]:
        preset = PLATFORM_PRESETS.get(platform, PLATFORM_PRESETS["desktop"])
        props = dict(preset)
        props.setdefault("referrer", "")
        props.setdefault("referring_domain", "")
        props.setdefault("referrer_current", "")
        props.setdefault("referring_domain_current", "")
        props.setdefault("client_event_source", None)
        props.setdefault("has_client_mods", False)
        props.setdefault("client_app_state", "focused")
        return props

    def set_platform(self, platform: str):
        self.platform = platform.lower()
        self.properties = self._build_properties(self.platform)

    def get_identify_properties(self) -> Dict[str, Any]:
        return dict(self.properties)

    def get_super_properties(self) -> str:
        return base64.b64encode(
            json.dumps(self.properties, separators=(",", ":")).encode()
        ).decode()

    def get_user_agent(self) -> str:
        return self.properties.get("browser_user_agent", "")

    def patch_identify_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return payload

        if payload.get("op") == 2:
            d = dict(payload.get("d", {}))
            d["properties"] = dict(self.properties)
            d["client_properties"] = dict(self.properties)
            payload = dict(payload)
            payload["d"] = d
        
        return payload

    @staticmethod
    def list_platforms() -> list:
        return list(PLATFORM_PRESETS.keys())

    def get_platform_info(self) -> Dict[str, str]:
        return {
            "platform": self.platform,
            "os": self.properties.get("os", ""),
            "browser": self.properties.get("browser", ""),
            "device": self.properties.get("device", ""),
            "build": str(self.properties.get("client_build_number", "")),
        }
