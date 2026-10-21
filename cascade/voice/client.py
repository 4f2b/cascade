import asyncio
import socket
import struct
import json
from typing import Optional, Callable, Dict, Any
import websockets


class VoiceClient:
    def __init__(self, session, guild_id: int, channel_id: int):
        self.session = session
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.token = None
        self.endpoint = None
        self.session_id = None
        self.ws = None
        self.udp_socket = None
        self.ssrc = None
        self.ip = None
        self.port = None
        self.mode = 'xsalsa20_poly1305'
        self.secret_key = None
        self._connected = False
        self._sequence = 0
        self._timestamp = 0

    async def connect(self, voice_server_data: Dict[str, Any]):
        self.token = voice_server_data['token']
        self.endpoint = voice_server_data['endpoint'].replace(':80', '')
        
        ws_url = f'wss://{self.endpoint}?v=4'
        self.ws = await websockets.connect(ws_url)
        
        await self._send_identify()
        await self._handle_hello()
        await self._discover_ip()
        await self._send_select_protocol()
        
        self._connected = True

    async def _send_identify(self):
        await self.ws.send(json.dumps({
            'op': 0,
            'd': {
                'server_id': str(self.guild_id),
                'user_id': str(self.session.user.id),
                'session_id': self.session_id,
                'token': self.token
            }
        }))

    async def _handle_hello(self):
        async for msg in self.ws:
            data = json.loads(msg)
            
            if data['op'] == 8:
                heartbeat_interval = data['d']['heartbeat_interval']
                asyncio.create_task(self._heartbeat_loop(heartbeat_interval))
            
            elif data['op'] == 2:
                self.ssrc = data['d']['ssrc']
                self.ip = data['d']['ip']
                self.port = data['d']['port']
                break

    async def _discover_ip(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setblocking(False)
        
        packet = bytearray(74)
        struct.pack_into('>H', packet, 0, 1)
        struct.pack_into('>H', packet, 2, 70)
        struct.pack_into('>I', packet, 4, self.ssrc)
        
        self.udp_socket.sendto(packet, (self.ip, self.port))
        
        loop = asyncio.get_event_loop()
        data = await loop.sock_recv(self.udp_socket, 74)
        
        ip_start = 8
        ip_end = data.index(0, ip_start)
        self.ip = data[ip_start:ip_end].decode('ascii')
        self.port = struct.unpack_from('>H', data, len(data) - 2)[0]

    async def _send_select_protocol(self):
        await self.ws.send(json.dumps({
            'op': 1,
            'd': {
                'protocol': 'udp',
                'data': {
                    'address': self.ip,
                    'port': self.port,
                    'mode': self.mode
                }
            }
        }))
        
        async for msg in self.ws:
            data = json.loads(msg)
            if data['op'] == 4:
                self.secret_key = bytes(data['d']['secret_key'])
                break

    async def _heartbeat_loop(self, interval: int):
        while self._connected:
            await asyncio.sleep(interval / 1000)
            await self.ws.send(json.dumps({
                'op': 3,
                'd': int(asyncio.get_event_loop().time() * 1000)
            }))

    def play_audio(self, source: 'AudioSource'):
        asyncio.create_task(self._play_audio_task(source))

    async def _play_audio_task(self, source: 'AudioSource'):
        while not source.is_finished():
            data = source.read()
            if data:
                await self._send_audio(data)
            await asyncio.sleep(0.02)

    async def _send_audio(self, data: bytes):
        header = bytearray(12)
        header[0] = 0x80
        header[1] = 0x78
        
        struct.pack_into('>H', header, 2, self._sequence)
        struct.pack_into('>I', header, 4, self._timestamp)
        struct.pack_into('>I', header, 8, self.ssrc)
        
        nonce = bytearray(24)
        nonce[:12] = header
        
        from nacl.secret import SecretBox
        box = SecretBox(self.secret_key)
        encrypted = box.encrypt(bytes(data), bytes(nonce))
        
        packet = header + encrypted.ciphertext
        self.udp_socket.sendto(packet, (self.ip, self.port))
        
        self._sequence = (self._sequence + 1) % 65536
        self._timestamp = (self._timestamp + 960) % 4294967296

    async def disconnect(self):
        self._connected = False
        if self.ws:
            await self.ws.close()
        if self.udp_socket:
            self.udp_socket.close()

    def is_connected(self) -> bool:
        return self._connected
