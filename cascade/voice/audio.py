import subprocess
import asyncio
from typing import Optional
from abc import ABC, abstractmethod


class AudioSource(ABC):
    def __init__(self):
        self._finished = False

    @abstractmethod
    def read(self) -> bytes:
        raise NotImplementedError

    def is_finished(self) -> bool:
        return self._finished

    def cleanup(self):
        pass


class PCMAudio(AudioSource):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    def read(self) -> bytes:
        data = self.stream.read(3840)
        if len(data) != 3840:
            self._finished = True
            return b''
        return data

    def cleanup(self):
        if hasattr(self.stream, 'close'):
            self.stream.close()


class FFmpegAudio(AudioSource):
    def __init__(self, source: str, *, bitrate: int = 128):
        super().__init__()
        self.source = source
        self.bitrate = bitrate
        self._process = None
        self._stdout = None
        self._create_process()

    def _create_process(self):
        args = [
            'ffmpeg',
            '-i', self.source,
            '-f', 's16le',
            '-ar', '48000',
            '-ac', '2',
            '-loglevel', 'warning',
            'pipe:1'
        ]
        
        self._process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self._stdout = self._process.stdout

    def read(self) -> bytes:
        if not self._stdout:
            return b''
        
        data = self._stdout.read(3840)
        if len(data) != 3840:
            self._finished = True
            return b''
        return data

    def cleanup(self):
        if self._process:
            self._process.kill()
            self._process = None
        if self._stdout:
            self._stdout.close()
            self._stdout = None


class YTDLSource(FFmpegAudio):
    def __init__(self, url: str, *, bitrate: int = 128):
        self.url = url
        self._extract_info()
        super().__init__(self._stream_url, bitrate=bitrate)

    def _extract_info(self):
        import yt_dlp
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
            self._stream_url = info['url']
            self.title = info.get('title', 'Unknown')
            self.duration = info.get('duration', 0)
