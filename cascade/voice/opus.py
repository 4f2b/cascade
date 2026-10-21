import array
from typing import Optional


class OpusEncoder:
    SAMPLING_RATE = 48000
    CHANNELS = 2
    FRAME_LENGTH = 20
    SAMPLE_SIZE = 4
    FRAME_SIZE = int(SAMPLING_RATE / 1000 * FRAME_LENGTH)

    def __init__(self, bitrate: int = 128000):
        self.bitrate = bitrate
        self._encoder = None
        self._setup_encoder()

    def _setup_encoder(self):
        try:
            import opuslib
            
            application = opuslib.APPLICATION_AUDIO
            self._encoder = opuslib.Encoder(
                self.SAMPLING_RATE,
                self.CHANNELS,
                application
            )
            self._encoder.bitrate = self.bitrate
        except ImportError:
            pass

    def encode(self, pcm: bytes) -> bytes:
        if not self._encoder:
            return pcm
        
        try:
            return self._encoder.encode(pcm, self.FRAME_SIZE)
        except:
            return pcm

    def set_bitrate(self, bitrate: int):
        self.bitrate = bitrate
        if self._encoder:
            self._encoder.bitrate = bitrate

    def set_fec(self, enabled: bool):
        if self._encoder:
            self._encoder.fec = enabled

    def set_packet_loss_percent(self, percent: int):
        if self._encoder:
            self._encoder.packet_loss_perc = percent
