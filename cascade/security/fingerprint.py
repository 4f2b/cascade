import random
import time
import hashlib
from typing import Dict, Any


class FingerprintRandomizer:
    def __init__(self):
        self.screen_resolutions = [
            (1920, 1080), (2560, 1440), (3840, 2160),
            (1366, 768), (1440, 900), (1536, 864),
            (1600, 900), (1680, 1050), (1280, 1024)
        ]
        self.timezones = [
            'America/New_York', 'America/Chicago', 'America/Denver',
            'America/Los_Angeles', 'Europe/London', 'Europe/Paris',
            'Asia/Tokyo', 'Australia/Sydney'
        ]
        self.locales = [
            'en-US', 'en-GB', 'en-CA', 'en-AU',
            'fr-FR', 'de-DE', 'es-ES', 'ja-JP'
        ]
        
    def randomize_timing(self, base_delay: float = 0.0) -> float:
        jitter = random.uniform(-0.3, 0.8)
        human_variance = random.gauss(0, 0.2)
        return max(0.1, base_delay + jitter + human_variance)
    
    def generate_canvas_noise(self) -> str:
        noise = ''.join(random.choices('0123456789abcdef', k=64))
        return hashlib.sha256(noise.encode()).hexdigest()
    
    def get_random_screen_resolution(self) -> tuple:
        return random.choice(self.screen_resolutions)
    
    def get_random_timezone(self) -> str:
        return random.choice(self.timezones)
    
    def get_random_locale(self) -> str:
        return random.choice(self.locales)
    
    def generate_mouse_movement(self, steps: int = 10) -> list:
        movements = []
        x, y = random.randint(100, 800), random.randint(100, 600)
        
        for _ in range(steps):
            dx = random.randint(-50, 50)
            dy = random.randint(-50, 50)
            x = max(0, min(1920, x + dx))
            y = max(0, min(1080, y + dy))
            movements.append((x, y, time.time()))
        
        return movements
    
    def generate_typing_pattern(self, text_length: int) -> Dict[str, Any]:
        wpm = random.randint(40, 80)
        avg_delay = 60.0 / (wpm * 5)
        
        keystrokes = []
        current_time = time.time()
        
        for i in range(text_length):
            delay = random.gauss(avg_delay, avg_delay * 0.3)
            current_time += max(0.05, delay)
            
            keystroke = {
                'key': i,
                'press_time': current_time,
                'release_time': current_time + random.uniform(0.05, 0.15)
            }
            keystrokes.append(keystroke)
            
            if random.random() < 0.05:
                pause = random.uniform(0.5, 2.0)
                current_time += pause
        
        return {
            'keystrokes': keystrokes,
            'wpm': wpm,
            'total_time': current_time - time.time()
        }
    
    def get_realistic_headers(self) -> Dict[str, str]:
        headers = {
            'DNT': str(random.choice(['1', '0'])),
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': random.choice(['no-cache', 'max-age=0']),
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'same-site']),
            'Sec-Fetch-User': '?1',
        }
        return headers
