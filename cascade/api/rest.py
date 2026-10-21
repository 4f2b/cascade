import aiohttp
import asyncio
import base64
import json
import platform
import random
import sys
import time
from typing import Optional, Dict, Any, List
from .ratelimit import RateLimiter
from . import routes

BASE = routes.BASE


class RestClient:
    def __init__(self, token: str):
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None
        self.limiter = RateLimiter()
        self._super_properties = self._build_super_properties()
        self._headers = self._build_headers()

    def _build_super_properties(self) -> str:
        props = {
            'os': 'Windows',
            'browser': 'Chrome',
            'device': '',
            'system_locale': 'en-US',
            'browser_user_agent': self._get_user_agent(),
            'browser_version': '131.0.0.0',
            'os_version': '10',
            'referrer': '',
            'referring_domain': '',
            'referrer_current': '',
            'referring_domain_current': '',
            'release_channel': 'stable',
            'client_build_number': 331288,
            'client_event_source': None,
        }
        return base64.b64encode(json.dumps(props, separators=(',', ':')).encode()).decode()

    def _get_user_agent(self) -> str:
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

    def _build_headers(self) -> Dict[str, str]:
        return {
            'Authorization': self.token,
            'User-Agent': self._get_user_agent(),
            'X-Super-Properties': self._super_properties,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://discord.com/channels/@me',
            'Origin': 'https://discord.com',
            'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Discord-Locale': 'en-US',
            'X-Discord-Timezone': 'America/New_York',
            'X-Debug-Options': 'bugReporterEnabled',
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                limit=100,
                ttl_dns_cache=300,
                ssl=True,
                enable_cleanup_closed=True
            )
            self.session = aiohttp.ClientSession(
                headers=self._headers,
                timeout=timeout,
                connector=connector,
                raise_for_status=False
            )
        return self.session

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def request(
        self,
        method: str,
        route: str,
        **kwargs
    ) -> Any:
        await self.limiter.acquire(route, method)
        session = await self._get_session()

        for attempt in range(5):
            try:
                async with session.request(method, route, **kwargs) as response:
                    headers = dict(response.headers)
                    self.limiter.update_bucket(route, method, headers)

                    if response.status == 429:
                        is_global = headers.get('X-RateLimit-Global', 'false') == 'true'
                        retry_after = float(headers.get('Retry-After', 1))
                        
                        if is_global:
                            self.limiter.global_reset = time.time() + retry_after
                        
                        await asyncio.sleep(retry_after + random.uniform(0.1, 0.5))
                        continue

                    if 200 <= response.status < 300:
                        if response.content_type == 'application/json':
                            return await response.json()
                        return await response.text()

                    if response.status in {500, 502, 503, 504}:
                        backoff = min(60, (2 ** attempt) + random.uniform(0, 1))
                        await asyncio.sleep(backoff)
                        continue

                    if response.status == 403:
                        error_text = await response.text()
                        raise Exception(f'Access denied: {error_text}')
                    
                    if response.status == 401:
                        raise Exception('Authentication failed')

                    error_text = await response.text()
                    raise Exception(f'HTTP {response.status}: {error_text}')
            
            except asyncio.TimeoutError:
                if attempt == 4:
                    raise
                await asyncio.sleep(random.uniform(1, 3))
                continue
            except aiohttp.ClientError as e:
                if attempt == 4:
                    raise
                await asyncio.sleep(random.uniform(1, 3))
                continue

        raise Exception('Maximum retry attempts exceeded')

    async def get(self, route: str, **kwargs) -> Any:
        return await self.request('GET', route, **kwargs)

    async def post(self, route: str, **kwargs) -> Any:
        return await self.request('POST', route, **kwargs)

    async def put(self, route: str, **kwargs) -> Any:
        return await self.request('PUT', route, **kwargs)

    async def patch(self, route: str, **kwargs) -> Any:
        return await self.request('PATCH', route, **kwargs)

    async def delete(self, route: str, **kwargs) -> Any:
        return await self.request('DELETE', route, **kwargs)

    async def send_message(self, channel_id: str, content: str = None, **kwargs) -> Dict[str, Any]:
        payload = {}
        if content:
            payload['content'] = content
        payload.update(kwargs)
        return await self.post(routes.channel_messages(channel_id), json=payload)

    async def edit_message(self, channel_id: str, message_id: str, content: str = None, **kwargs) -> Dict[str, Any]:
        payload = {}
        if content is not None:
            payload['content'] = content
        payload.update(kwargs)
        return await self.patch(routes.channel_message(channel_id, message_id), json=payload)

    async def delete_message(self, channel_id: str, message_id: str) -> None:
        await self.delete(routes.channel_message(channel_id, message_id))

    async def get_messages(self, channel_id: str, limit: int = 50, **kwargs) -> List[Dict[str, Any]]:
        params = {'limit': limit}
        params.update(kwargs)
        return await self.get(routes.channel_messages(channel_id), params=params)

    async def get_message(self, channel_id: str, message_id: str) -> Dict[str, Any]:
        return await self.get(routes.channel_message(channel_id, message_id))

    async def trigger_typing(self, channel_id: str) -> None:
        await self.post(routes.channel_typing(channel_id))

    async def pin_message(self, channel_id: str, message_id: str) -> None:
        await self.put(routes.channel_pin(channel_id, message_id))

    async def unpin_message(self, channel_id: str, message_id: str) -> None:
        await self.delete(routes.channel_pin(channel_id, message_id))

    async def get_channel(self, channel_id: str) -> Dict[str, Any]:
        return await self.get(routes.channel(channel_id))

    async def get_guild(self, guild_id: str) -> Dict[str, Any]:
        return await self.get(routes.guild(guild_id))

    async def get_guild_channels(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(routes.guild_channels(guild_id))

    async def get_guild_member(self, guild_id: str, user_id: str) -> Dict[str, Any]:
        return await self.get(routes.guild_member(guild_id, user_id))

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        return await self.get(routes.user(user_id))

    async def get_current_user(self) -> Dict[str, Any]:
        return await self.get(routes.me())

    async def get_user_guilds(self) -> List[Dict[str, Any]]:
        return await self.get(routes.me_guilds())

    async def leave_guild(self, guild_id: str) -> None:
        await self.delete(routes.me_guild(guild_id))

    async def create_dm(self, recipient_id: str) -> Dict[str, Any]:
        return await self.post(routes.me_channels(), json={'recipient_id': recipient_id})

    async def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> None:
        await self.put(f'{routes.channel_message(channel_id, message_id)}/reactions/{emoji}/@me')

    async def remove_reaction(self, channel_id: str, message_id: str, emoji: str) -> None:
        await self.delete(f'{routes.channel_message(channel_id, message_id)}/reactions/{emoji}/@me')

    async def get_gateway(self) -> Dict[str, Any]:
        return await self.get(routes.gateway())
    
    async def ack_message(self, channel_id: str, message_id: str) -> None:
        await self.post(f'{routes.channel(channel_id)}/messages/{message_id}/ack', json={
            'token': None,
            'manual': True,
            'mention_count': 0
        })
    
    async def search_messages(self, channel_id: str, query: str, limit: int = 25) -> Dict[str, Any]:
        params = {
            'content': query,
            'limit': limit
        }
        return await self.get(f'{routes.channel(channel_id)}/messages/search', params=params)
    
    async def get_user_profile(self, user_id: str, guild_id: str = None) -> Dict[str, Any]:
        params = {}
        if guild_id:
            params['guild_id'] = guild_id
        return await self.get(f'{routes.user(user_id)}/profile', params=params)
    
    async def get_relationships(self) -> List[Dict[str, Any]]:
        return await self.get(routes.relationships())
    
    async def send_friend_request(self, username: str, discriminator: str = None) -> Dict[str, Any]:
        payload = {'username': username}
        if discriminator and discriminator != '0':
            payload['discriminator'] = discriminator
        return await self.post(routes.relationships(), json=payload)
    
    async def remove_friend(self, user_id: str) -> None:
        await self.delete(routes.relationship(user_id))
    
    async def block_user(self, user_id: str) -> None:
        await self.put(routes.relationship(user_id), json={'type': 2})
    
    async def unblock_user(self, user_id: str) -> None:
        await self.delete(routes.relationship(user_id))
    
    async def get_user_notes(self, user_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.me()}/notes/{user_id}')
    
    async def set_user_note(self, user_id: str, note: str) -> None:
        await self.put(f'{routes.me()}/notes/{user_id}', json={'note': note})
    
    async def delete_user_note(self, user_id: str) -> None:
        await self.delete(f'{routes.me()}/notes/{user_id}')
    
    async def join_guild(self, invite_code: str) -> Dict[str, Any]:
        return await self.post(f'{BASE}/invites/{invite_code}')
    
    async def get_invite(self, invite_code: str) -> Dict[str, Any]:
        return await self.get(f'{BASE}/invites/{invite_code}')
    
    async def create_guild(self, name: str, icon: str = None) -> Dict[str, Any]:
        payload = {'name': name}
        if icon:
            payload['icon'] = icon
        return await self.post(f'{BASE}/guilds', json=payload)
    
    async def delete_guild(self, guild_id: str) -> None:
        await self.delete(routes.guild(guild_id))
    
    async def create_channel(self, guild_id: str, name: str, type: int = 0, **kwargs) -> Dict[str, Any]:
        payload = {'name': name, 'type': type}
        payload.update(kwargs)
        return await self.post(routes.guild_channels(guild_id), json=payload)
    
    async def delete_channel(self, channel_id: str) -> None:
        await self.delete(routes.channel(channel_id))
    
    async def edit_channel(self, channel_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(routes.channel(channel_id), json=kwargs)
    
    async def get_channel_invites(self, channel_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.channel(channel_id)}/invites')
    
    async def create_channel_invite(self, channel_id: str, **kwargs) -> Dict[str, Any]:
        return await self.post(f'{routes.channel(channel_id)}/invites', json=kwargs)
    
    async def bulk_delete_messages(self, channel_id: str, message_ids: List[str]) -> None:
        await self.post(f'{routes.channel_messages(channel_id)}/bulk-delete', json={'messages': message_ids})
    
    async def get_guild_roles(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(routes.guild_roles(guild_id))
    
    async def create_guild_role(self, guild_id: str, **kwargs) -> Dict[str, Any]:
        return await self.post(routes.guild_roles(guild_id), json=kwargs)
    
    async def edit_guild_role(self, guild_id: str, role_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(routes.guild_role(guild_id, role_id), json=kwargs)
    
    async def delete_guild_role(self, guild_id: str, role_id: str) -> None:
        await self.delete(routes.guild_role(guild_id, role_id))
    
    async def add_guild_member_role(self, guild_id: str, user_id: str, role_id: str) -> None:
        await self.put(f'{routes.guild_member(guild_id, user_id)}/roles/{role_id}')
    
    async def remove_guild_member_role(self, guild_id: str, user_id: str, role_id: str) -> None:
        await self.delete(f'{routes.guild_member(guild_id, user_id)}/roles/{role_id}')
    
    async def kick_guild_member(self, guild_id: str, user_id: str) -> None:
        await self.delete(routes.guild_member(guild_id, user_id))
    
    async def ban_guild_member(self, guild_id: str, user_id: str, delete_message_days: int = 0) -> None:
        params = {'delete_message_days': delete_message_days}
        await self.put(routes.guild_ban(guild_id, user_id), params=params)
    
    async def unban_guild_member(self, guild_id: str, user_id: str) -> None:
        await self.delete(routes.guild_ban(guild_id, user_id))
    
    async def get_guild_bans(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(routes.guild_bans(guild_id))
    
    async def edit_guild(self, guild_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(routes.guild(guild_id), json=kwargs)
    
    async def get_guild_prune_count(self, guild_id: str, days: int = 7) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/prune', params={'days': days})
    
    async def begin_guild_prune(self, guild_id: str, days: int = 7) -> Dict[str, Any]:
        return await self.post(f'{routes.guild(guild_id)}/prune', json={'days': days})
    
    async def get_guild_webhooks(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.guild(guild_id)}/webhooks')
    
    async def get_channel_webhooks(self, channel_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.channel(channel_id)}/webhooks')
    
    async def create_webhook(self, channel_id: str, name: str, avatar: str = None) -> Dict[str, Any]:
        payload = {'name': name}
        if avatar:
            payload['avatar'] = avatar
        return await self.post(f'{routes.channel(channel_id)}/webhooks', json=payload)
    
    async def edit_webhook(self, webhook_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{BASE}/webhooks/{webhook_id}', json=kwargs)
    
    async def delete_webhook(self, webhook_id: str) -> None:
        await self.delete(f'{BASE}/webhooks/{webhook_id}')
    
    async def execute_webhook(self, webhook_id: str, token: str, **kwargs) -> None:
        await self.post(f'{BASE}/webhooks/{webhook_id}/{token}', json=kwargs)
    
    async def get_user_connections(self) -> List[Dict[str, Any]]:
        return await self.get(routes.me_connections())
    
    async def edit_current_user(self, **kwargs) -> Dict[str, Any]:
        return await self.patch(routes.me(), json=kwargs)
    
    async def get_private_channels(self) -> List[Dict[str, Any]]:
        return await self.get(routes.me_channels())
    
    async def close_dm(self, channel_id: str) -> None:
        await self.delete(routes.channel(channel_id))
    
    async def create_group_dm(self, access_tokens: List[str], nicks: Dict[str, str]) -> Dict[str, Any]:
        return await self.post(routes.me_channels(), json={
            'access_tokens': access_tokens,
            'nicks': nicks
        })
    
    async def add_group_dm_recipient(self, channel_id: str, user_id: str, access_token: str, nick: str = None) -> None:
        payload = {'access_token': access_token}
        if nick:
            payload['nick'] = nick
        await self.put(f'{routes.channel(channel_id)}/recipients/{user_id}', json=payload)
    
    async def remove_group_dm_recipient(self, channel_id: str, user_id: str) -> None:
        await self.delete(f'{routes.channel(channel_id)}/recipients/{user_id}')
    
    async def get_pinned_messages(self, channel_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.channel(channel_id)}/pins')
    
    async def get_guild_emojis(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.guild(guild_id)}/emojis')
    
    async def get_guild_emoji(self, guild_id: str, emoji_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/emojis/{emoji_id}')
    
    async def create_guild_emoji(self, guild_id: str, name: str, image: str, **kwargs) -> Dict[str, Any]:
        payload = {'name': name, 'image': image}
        payload.update(kwargs)
        return await self.post(f'{routes.guild(guild_id)}/emojis', json=payload)
    
    async def edit_guild_emoji(self, guild_id: str, emoji_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{routes.guild(guild_id)}/emojis/{emoji_id}', json=kwargs)
    
    async def delete_guild_emoji(self, guild_id: str, emoji_id: str) -> None:
        await self.delete(f'{routes.guild(guild_id)}/emojis/{emoji_id}')
    
    async def get_guild_stickers(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.guild(guild_id)}/stickers')
    
    async def get_guild_sticker(self, guild_id: str, sticker_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/stickers/{sticker_id}')
    
    async def get_guild_audit_log(self, guild_id: str, **kwargs) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/audit-logs', params=kwargs)
    
    async def get_guild_integrations(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.guild(guild_id)}/integrations')
    
    async def delete_guild_integration(self, guild_id: str, integration_id: str) -> None:
        await self.delete(f'{routes.guild(guild_id)}/integrations/{integration_id}')
    
    async def get_guild_vanity_url(self, guild_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/vanity-url')
    
    async def get_guild_preview(self, guild_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/preview')
    
    async def get_guild_widget(self, guild_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/widget.json')
    
    async def get_guild_widget_settings(self, guild_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/widget')
    
    async def edit_guild_widget(self, guild_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{routes.guild(guild_id)}/widget', json=kwargs)
    
    async def get_guild_welcome_screen(self, guild_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/welcome-screen')
    
    async def edit_guild_welcome_screen(self, guild_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{routes.guild(guild_id)}/welcome-screen', json=kwargs)
    
    async def edit_guild_member(self, guild_id: str, user_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(routes.guild_member(guild_id, user_id), json=kwargs)
    
    async def edit_current_member(self, guild_id: str, nick: str = None) -> Dict[str, Any]:
        payload = {}
        if nick is not None:
            payload['nick'] = nick
        return await self.patch(f'{routes.guild(guild_id)}/members/@me', json=payload)
    
    async def search_guild_members(self, guild_id: str, query: str, limit: int = 1) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.guild(guild_id)}/members/search', params={'query': query, 'limit': limit})
    
    async def list_guild_members(self, guild_id: str, limit: int = 1, after: str = None) -> List[Dict[str, Any]]:
        params = {'limit': limit}
        if after:
            params['after'] = after
        return await self.get(routes.guild_members(guild_id), params=params)
    
    async def get_reactions(self, channel_id: str, message_id: str, emoji: str, limit: int = 25, after: str = None) -> List[Dict[str, Any]]:
        params = {'limit': limit}
        if after:
            params['after'] = after
        return await self.get(f'{routes.channel_message(channel_id, message_id)}/reactions/{emoji}', params=params)
    
    async def crosspost_message(self, channel_id: str, message_id: str) -> Dict[str, Any]:
        return await self.post(f'{routes.channel_message(channel_id, message_id)}/crosspost')
    
    async def follow_news_channel(self, channel_id: str, webhook_channel_id: str) -> Dict[str, Any]:
        return await self.post(f'{routes.channel(channel_id)}/followers', json={'webhook_channel_id': webhook_channel_id})
    
    async def create_thread_from_message(self, channel_id: str, message_id: str, name: str, **kwargs) -> Dict[str, Any]:
        payload = {'name': name}
        payload.update(kwargs)
        return await self.post(f'{routes.channel_message(channel_id, message_id)}/threads', json=payload)
    
    async def create_thread(self, channel_id: str, name: str, **kwargs) -> Dict[str, Any]:
        payload = {'name': name}
        payload.update(kwargs)
        return await self.post(f'{routes.channel(channel_id)}/threads', json=payload)
    
    async def join_thread(self, channel_id: str) -> None:
        await self.put(f'{routes.channel(channel_id)}/thread-members/@me')
    
    async def leave_thread(self, channel_id: str) -> None:
        await self.delete(f'{routes.channel(channel_id)}/thread-members/@me')
    
    async def add_thread_member(self, channel_id: str, user_id: str) -> None:
        await self.put(f'{routes.channel(channel_id)}/thread-members/{user_id}')
    
    async def remove_thread_member(self, channel_id: str, user_id: str) -> None:
        await self.delete(f'{routes.channel(channel_id)}/thread-members/{user_id}')
    
    async def get_thread_member(self, channel_id: str, user_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.channel(channel_id)}/thread-members/{user_id}')
    
    async def list_thread_members(self, channel_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.channel(channel_id)}/thread-members')
    
    async def list_active_threads(self, guild_id: str) -> Dict[str, Any]:
        return await self.get(f'{routes.guild(guild_id)}/threads/active')
    
    async def list_public_archived_threads(self, channel_id: str, before: str = None, limit: int = None) -> Dict[str, Any]:
        params = {}
        if before:
            params['before'] = before
        if limit:
            params['limit'] = limit
        return await self.get(f'{routes.channel(channel_id)}/threads/archived/public', params=params)
    
    async def list_private_archived_threads(self, channel_id: str, before: str = None, limit: int = None) -> Dict[str, Any]:
        params = {}
        if before:
            params['before'] = before
        if limit:
            params['limit'] = limit
        return await self.get(f'{routes.channel(channel_id)}/threads/archived/private', params=params)
    
    async def list_joined_private_archived_threads(self, channel_id: str, before: str = None, limit: int = None) -> Dict[str, Any]:
        params = {}
        if before:
            params['before'] = before
        if limit:
            params['limit'] = limit
        return await self.get(f'{routes.channel(channel_id)}/users/@me/threads/archived/private', params=params)
    
    async def get_application_commands(self, application_id: str, guild_id: str = None) -> List[Dict[str, Any]]:
        if guild_id:
            return await self.get(f'{BASE}/applications/{application_id}/guilds/{guild_id}/commands')
        return await self.get(f'{BASE}/applications/{application_id}/commands')
    
    async def get_guild_scheduled_events(self, guild_id: str, with_user_count: bool = False) -> List[Dict[str, Any]]:
        params = {'with_user_count': str(with_user_count).lower()}
        return await self.get(f'{routes.guild(guild_id)}/scheduled-events', params=params)
    
    async def get_guild_scheduled_event(self, guild_id: str, event_id: str, with_user_count: bool = False) -> Dict[str, Any]:
        params = {'with_user_count': str(with_user_count).lower()}
        return await self.get(f'{routes.guild(guild_id)}/scheduled-events/{event_id}', params=params)
    
    async def create_guild_scheduled_event(self, guild_id: str, **kwargs) -> Dict[str, Any]:
        return await self.post(f'{routes.guild(guild_id)}/scheduled-events', json=kwargs)
    
    async def edit_guild_scheduled_event(self, guild_id: str, event_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{routes.guild(guild_id)}/scheduled-events/{event_id}', json=kwargs)
    
    async def delete_guild_scheduled_event(self, guild_id: str, event_id: str) -> None:
        await self.delete(f'{routes.guild(guild_id)}/scheduled-events/{event_id}')
    
    async def get_guild_scheduled_event_users(self, guild_id: str, event_id: str, limit: int = 100, **kwargs) -> List[Dict[str, Any]]:
        params = {'limit': limit}
        params.update(kwargs)
        return await self.get(f'{routes.guild(guild_id)}/scheduled-events/{event_id}/users', params=params)
    
    async def get_stage_instance(self, channel_id: str) -> Dict[str, Any]:
        return await self.get(f'{BASE}/stage-instances/{channel_id}')
    
    async def create_stage_instance(self, channel_id: str, topic: str, **kwargs) -> Dict[str, Any]:
        payload = {'channel_id': channel_id, 'topic': topic}
        payload.update(kwargs)
        return await self.post(f'{BASE}/stage-instances', json=payload)
    
    async def edit_stage_instance(self, channel_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{BASE}/stage-instances/{channel_id}', json=kwargs)
    
    async def delete_stage_instance(self, channel_id: str) -> None:
        await self.delete(f'{BASE}/stage-instances/{channel_id}')
    
    async def get_guild_voice_regions(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.guild(guild_id)}/regions')
    
    async def get_voice_regions(self) -> List[Dict[str, Any]]:
        return await self.get(f'{BASE}/voice/regions')
    
    async def get_guild_invites(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{routes.guild(guild_id)}/invites')
    
    async def delete_invite(self, invite_code: str) -> Dict[str, Any]:
        return await self.delete(f'{BASE}/invites/{invite_code}')
    
    async def get_current_authorization_info(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/oauth2/@me')
    
    async def get_current_application(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/oauth2/applications/@me')
    
    async def change_voice_state(self, guild_id: str, channel_id: str, self_mute: bool = False, self_deaf: bool = False) -> None:
        await self.gateway.send_json({
            'op': 4,
            'd': {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'self_mute': self_mute,
                'self_deaf': self_deaf
            }
        })
    
    async def update_voice_state(self, guild_id: str, channel_id: str = None, suppress: bool = False, request_to_speak_timestamp: str = None) -> None:
        payload = {
            'guild_id': guild_id,
            'channel_id': channel_id,
            'suppress': suppress
        }
        if request_to_speak_timestamp:
            payload['request_to_speak_timestamp'] = request_to_speak_timestamp
        
        await self.patch(f'{routes.guild(guild_id)}/voice-states/@me', json=payload)
    
    async def edit_user_voice_state(self, guild_id: str, user_id: str, channel_id: str, suppress: bool = False) -> None:
        await self.patch(f'{routes.guild(guild_id)}/voice-states/{user_id}', json={
            'channel_id': channel_id,
            'suppress': suppress
        })

    async def get_user_connections(self) -> List[Dict[str, Any]]:
        return await self.get(f'{BASE}/users/@me/connections')
    
    async def get_user_settings(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/users/@me/settings')
    
    async def modify_user_settings(self, **settings) -> Dict[str, Any]:
        return await self.patch(f'{BASE}/users/@me/settings', json=settings)
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        return await self.get(f'{BASE}/users/{user_id}/profile')
    
    async def get_user_affinities(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/users/@me/affinities/users')
    
    async def get_guild_affinities(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/users/@me/affinities/guilds')
    
    async def get_experiments(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/experiments')
    
    async def get_guild_preview(self, guild_id: str) -> Dict[str, Any]:
        return await self.get(f'{BASE}/guilds/{guild_id}/preview')
    
    async def ack_message(self, channel_id: str, message_id: str, token: str = None) -> None:
        payload = {'token': token} if token else {}
        await self.post(f'{routes.channel_message(channel_id, message_id)}/ack', json=payload if payload else None)
    
    async def ack_guild(self, guild_id: str) -> None:
        await self.post(f'{routes.guild(guild_id)}/ack')
    
    async def get_mentions(self, limit: int = 25, roles: bool = True, everyone: bool = True, guild_id: str = None) -> List[Dict[str, Any]]:
        params = {
            'limit': limit,
            'roles': roles,
            'everyone': everyone
        }
        if guild_id:
            params['guild_id'] = guild_id
        return await self.get(f'{BASE}/users/@me/mentions', params=params)
    
    async def delete_mention(self, message_id: str) -> None:
        await self.delete(f'{BASE}/users/@me/mentions/{message_id}')
    
    async def create_group_dm(self, access_tokens: List[str], nicks: Dict[str, str]) -> Dict[str, Any]:
        return await self.post(f'{BASE}/users/@me/channels', json={
            'access_tokens': access_tokens,
            'nicks': nicks
        })
    
    async def add_group_recipient(self, channel_id: str, user_id: str, access_token: str = None, nick: str = None) -> None:
        payload = {}
        if access_token:
            payload['access_token'] = access_token
        if nick:
            payload['nick'] = nick
        await self.put(f'{routes.channel(channel_id)}/recipients/{user_id}', json=payload if payload else None)
    
    async def remove_group_recipient(self, channel_id: str, user_id: str) -> None:
        await self.delete(f'{routes.channel(channel_id)}/recipients/{user_id}')
    
    async def search_channel_messages(self, channel_id: str, query: str = None, author_id: str = None, 
                                     mentions: str = None, has: str = None, min_id: str = None, 
                                     max_id: str = None, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
        params = {'offset': offset}
        if query:
            params['content'] = query
        if author_id:
            params['author_id'] = author_id
        if mentions:
            params['mentions'] = mentions
        if has:
            params['has'] = has
        if min_id:
            params['min_id'] = min_id
        if max_id:
            params['max_id'] = max_id
        if limit:
            params['limit'] = limit
        return await self.get(f'{routes.channel(channel_id)}/messages/search', params=params)
    
    async def search_guild_messages(self, guild_id: str, query: str = None, author_id: str = None,
                                   mentions: str = None, has: str = None, channel_id: str = None,
                                   min_id: str = None, max_id: str = None, limit: int = 25, 
                                   offset: int = 0) -> Dict[str, Any]:
        params = {'offset': offset}
        if query:
            params['content'] = query
        if author_id:
            params['author_id'] = author_id
        if mentions:
            params['mentions'] = mentions
        if has:
            params['has'] = has
        if channel_id:
            params['channel_id'] = channel_id
        if min_id:
            params['min_id'] = min_id
        if max_id:
            params['max_id'] = max_id
        if limit:
            params['limit'] = limit
        return await self.get(f'{routes.guild(guild_id)}/messages/search', params=params)
    
    async def get_library(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/users/@me/library')
    
    async def get_billing_payment_sources(self) -> List[Dict[str, Any]]:
        return await self.get(f'{BASE}/users/@me/billing/payment-sources')
    
    async def get_billing_subscriptions(self) -> List[Dict[str, Any]]:
        return await self.get(f'{BASE}/users/@me/billing/subscriptions')
    
    async def get_entitlements(self) -> List[Dict[str, Any]]:
        return await self.get(f'{BASE}/users/@me/entitlements')
    
    async def get_guild_entitlements(self, guild_id: str) -> List[Dict[str, Any]]:
        return await self.get(f'{BASE}/users/@me/guilds/{guild_id}/entitlements')
    
    async def get_friend_suggestions(self) -> List[Dict[str, Any]]:
        return await self.get(f'{BASE}/friend-suggestions')
    
    async def get_consents(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/users/@me/consent')
    
    async def get_harvest(self) -> Dict[str, Any]:
        return await self.get(f'{BASE}/users/@me/harvest')
    
    async def get_connections_authorize_url(self, platform: str) -> Dict[str, Any]:
        return await self.get(f'{BASE}/connections/{platform}/authorize')
    
    async def create_connection(self, platform: str, code: str, state: str = None, friend_sync: bool = False) -> Dict[str, Any]:
        payload = {'code': code, 'friend_sync': friend_sync}
        if state:
            payload['state'] = state
        return await self.post(f'{BASE}/connections/{platform}/callback', json=payload)
    
    async def edit_connection(self, platform: str, connection_id: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{BASE}/users/@me/connections/{platform}/{connection_id}', json=kwargs)
    
    async def delete_connection(self, platform: str, connection_id: str) -> None:
        await self.delete(f'{BASE}/users/@me/connections/{platform}/{connection_id}')
    
    async def refresh_connection(self, platform: str, connection_id: str) -> None:
        await self.post(f'{BASE}/users/@me/connections/{platform}/{connection_id}/refresh')

    async def get_automod_rules(self, guild_id: int) -> List[Dict[str, Any]]:
        return await self.get(f'{BASE}/guilds/{guild_id}/auto-moderation/rules')
    
    async def get_automod_rule(self, guild_id: int, rule_id: int) -> Dict[str, Any]:
        return await self.get(f'{BASE}/guilds/{guild_id}/auto-moderation/rules/{rule_id}')
    
    async def create_automod_rule(self, guild_id: int, **kwargs) -> Dict[str, Any]:
        return await self.post(f'{BASE}/guilds/{guild_id}/auto-moderation/rules', json=kwargs)
    
    async def modify_automod_rule(self, guild_id: int, rule_id: int, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{BASE}/guilds/{guild_id}/auto-moderation/rules/{rule_id}', json=kwargs)
    
    async def delete_automod_rule(self, guild_id: int, rule_id: int) -> None:
        await self.delete(f'{BASE}/guilds/{guild_id}/auto-moderation/rules/{rule_id}')
    
    async def create_interaction_response(self, interaction_id: int, token: str, **kwargs) -> None:
        await self.post(f'{BASE}/interactions/{interaction_id}/{token}/callback', json=kwargs)
    
    async def get_original_interaction_response(self, application_id: int, token: str) -> Dict[str, Any]:
        return await self.get(f'{BASE}/webhooks/{application_id}/{token}/messages/@original')
    
    async def edit_original_interaction_response(self, application_id: int, token: str, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{BASE}/webhooks/{application_id}/{token}/messages/@original', json=kwargs)
    
    async def delete_original_interaction_response(self, application_id: int, token: str) -> None:
        await self.delete(f'{BASE}/webhooks/{application_id}/{token}/messages/@original')
    
    async def create_followup_message(self, application_id: int, token: str, **kwargs) -> Dict[str, Any]:
        return await self.post(f'{BASE}/webhooks/{application_id}/{token}', json=kwargs)
    
    async def get_followup_message(self, application_id: int, token: str, message_id: int) -> Dict[str, Any]:
        return await self.get(f'{BASE}/webhooks/{application_id}/{token}/messages/{message_id}')
    
    async def edit_followup_message(self, application_id: int, token: str, message_id: int, **kwargs) -> Dict[str, Any]:
        return await self.patch(f'{BASE}/webhooks/{application_id}/{token}/messages/{message_id}', json=kwargs)
    
    async def delete_followup_message(self, application_id: int, token: str, message_id: int) -> None:
        await self.delete(f'{BASE}/webhooks/{application_id}/{token}/messages/{message_id}')
    
    async def modify_current_user_voice_state(self, guild_id: int, **kwargs) -> None:
        await self.patch(f'{BASE}/guilds/{guild_id}/voice-states/@me', json=kwargs)
    
    async def modify_user_voice_state(self, guild_id: int, user_id: int, **kwargs) -> None:
        await self.patch(f'{BASE}/guilds/{guild_id}/voice-states/{user_id}', json=kwargs)
