import asyncio
import sys

import os

TOKEN = os.environ.get('CASCADE_TOKEN', '')
if not TOKEN:
    print('Set CASCADE_TOKEN env var to run live tests')
    import sys; sys.exit(1)

passed = []
failed = []

def ok(n): passed.append(n); print(f'  ok  {n}', flush=True)
def fail(n, e): failed.append((n, str(e))); print(f'  FAIL  {n}: {e}', flush=True)
def skip(n, r): print(f'  skip  {n}: {r}', flush=True)


async def main():
    import cascade

    rest = cascade.RestClient(TOKEN)

    print('\n=== Auth ===', flush=True)
    try:
        me = await rest.get_current_user()
        print(f'  user: {me["username"]} ({me["id"]})', flush=True)
        ok('get_current_user')
        MY_ID = me['id']
    except Exception as e:
        fail('auth', e)
        await rest.close()
        return 1

    print('\n=== Users / Profile ===', flush=True)
    try:
        guilds = await rest.get_user_guilds()
        print(f'  guilds: {len(guilds)}', flush=True)
        ok('get_user_guilds')
    except Exception as e:
        fail('get_user_guilds', e)
        guilds = []

    try:
        rels = await rest.get_relationships()
        print(f'  relationships: {len(rels)}', flush=True)
        ok('get_relationships')
    except Exception as e:
        fail('get_relationships', e)

    try:
        conns = await rest.get_user_connections()
        print(f'  connections: {len(conns)}', flush=True)
        ok('get_user_connections')
    except Exception as e:
        fail('get_user_connections', e)

    try:
        settings = await rest.get_user_settings()
        assert isinstance(settings, dict)
        ok('get_user_settings')
    except Exception as e:
        fail('get_user_settings', e)

    print('\n=== Onboarding / Welcome Screen ===', flush=True)
    for g in guilds[:5]:
        gid = g['id']
        gname = g.get('name', gid)
        try:
            data = await rest.get_guild_welcome_screen(gid)
            chs = data.get('welcome_channels', [])
            print(f'  {gname}: welcome_screen channels={len(chs)}', flush=True)
            ok(f'welcome_screen [{gname}]')
        except Exception as e:
            if any(c in str(e) for c in ['404', '403', 'Unknown', 'Missing']):
                skip(f'welcome_screen [{gname}]', 'no welcome screen')
            else:
                fail(f'welcome_screen [{gname}]', e)

        try:
            data = await rest.get_guild_onboarding(gid)
            prompts = data.get('prompts', [])
            enabled = data.get('enabled', False)
            print(f'  {gname}: onboarding enabled={enabled} prompts={len(prompts)}', flush=True)
            ok(f'onboarding [{gname}]')
        except Exception as e:
            if any(c in str(e) for c in ['404', '403', 'Unknown', 'Missing']):
                skip(f'onboarding [{gname}]', 'no access')
            else:
                fail(f'onboarding [{gname}]', e)

    print('\n=== Audit Log ===', flush=True)
    for g in guilds[:3]:
        gid = g['id']
        gname = g.get('name', gid)
        try:
            data = await rest.get_guild_audit_log(gid, limit=5)
            entries = data.get('audit_log_entries', [])
            from cascade import AuditLog
            al = AuditLog(data, gid)
            print(f'  {gname}: audit_log entries={len(al)}', flush=True)
            ok(f'audit_log [{gname}]')
        except Exception as e:
            if any(c in str(e) for c in ['403', 'Missing']):
                skip(f'audit_log [{gname}]', 'no permissions')
            else:
                fail(f'audit_log [{gname}]', e)

    print('\n=== Bans ===', flush=True)
    for g in guilds[:2]:
        gid = g['id']
        gname = g.get('name', gid)
        try:
            from cascade import Ban
            data = await rest.get_guild_bans(gid)
            bans = [Ban(b, gid) for b in data]
            print(f'  {gname}: bans={len(bans)}', flush=True)
            ok(f'bans [{gname}]')
        except Exception as e:
            if any(c in str(e) for c in ['403', 'Missing']):
                skip(f'bans [{gname}]', 'no permissions')
            else:
                fail(f'bans [{gname}]', e)

    print('\n=== Guild Templates ===', flush=True)
    for g in guilds[:3]:
        gid = g['id']
        gname = g.get('name', gid)
        try:
            templates = await rest.get_guild_templates(gid)
            print(f'  {gname}: templates={len(templates)}', flush=True)
            ok(f'templates [{gname}]')
        except Exception as e:
            if any(c in str(e) for c in ['403', 'Missing', '404']):
                skip(f'templates [{gname}]', 'no access')
            else:
                fail(f'templates [{gname}]', e)

    print('\n=== Sticker Packs ===', flush=True)
    try:
        packs = await rest.list_sticker_packs()
        print(f'  sticker packs: {len(packs)}', flush=True)
        ok('list_sticker_packs')
    except Exception as e:
        fail('list_sticker_packs', e)

    print('\n=== Soundboard ===', flush=True)
    try:
        sounds = await rest.list_default_soundboard_sounds()
        print(f'  default sounds: {len(sounds)}', flush=True)
        ok('list_default_soundboard_sounds')
    except Exception as e:
        fail('list_default_soundboard_sounds', e)

    await rest.close()

    print('\n=== Gateway + Session methods ===', flush=True)

    session = cascade.Session(TOKEN)
    ready = asyncio.Event()
    seen_events = []

    @session.event
    async def on_ready(user):
        ready.set()

    @session.event
    async def on_guild_available(guild):
        seen_events.append(('on_guild_available', guild))

    @session.event
    async def on_guild_join(guild):
        seen_events.append(('on_guild_join', guild))

    runner = asyncio.create_task(_run(session))

    try:
        await asyncio.wait_for(ready.wait(), timeout=30)
        print(f'  gateway user: {session.user.username}', flush=True)
        ok('gateway ready')
    except asyncio.TimeoutError:
        fail('gateway ready', 'timed out after 30s')
        runner.cancel()
        _print_summary()
        return 1

    await asyncio.sleep(2)

    guild_count = len(session.guilds)
    print(f'  cached guilds: {guild_count}', flush=True)
    if guild_count > 0:
        ok('guild cache')
    else:
        fail('guild cache', '0 guilds')

    lat = session.latency
    print(f'  latency: {lat*1000:.0f}ms' if lat != float('inf') else '  latency: not yet available', flush=True)
    ok('latency check')

    if session.guilds:
        g = session.guilds[0]

        try:
            fetched = await session.fetch_guild(int(g.id))
            assert fetched.id == g.id
            ok('fetch_guild')
        except Exception as e:
            fail('fetch_guild', e)

        try:
            fetched_channels = await session.rest.get_guild_channels(g.id)
            if fetched_channels:
                ch = await session.fetch_channel(int(fetched_channels[0]['id']))
                ok('fetch_channel')
            else:
                skip('fetch_channel', 'no channels')
        except Exception as e:
            fail('fetch_channel', e)

        try:
            al = await session.fetch_audit_log(int(g.id), limit=3)
            from cascade import AuditLog
            assert isinstance(al, AuditLog)
            ok('fetch_audit_log')
        except Exception as e:
            if '403' in str(e) or 'Missing' in str(e):
                skip('fetch_audit_log', 'no permissions')
            else:
                fail('fetch_audit_log', e)

        try:
            ws = await session.fetch_welcome_screen(int(g.id))
            from cascade import WelcomeScreen
            assert isinstance(ws, WelcomeScreen)
            ok('fetch_welcome_screen')
        except Exception as e:
            if any(c in str(e) for c in ['404', '403', 'Unknown']):
                skip('fetch_welcome_screen', 'not enabled')
            else:
                fail('fetch_welcome_screen', e)

        try:
            ob = await session.fetch_onboarding(int(g.id))
            from cascade import GuildOnboarding
            assert isinstance(ob, GuildOnboarding)
            print(f'  onboarding: enabled={ob.enabled} prompts={len(ob.prompts)}', flush=True)
            ok('fetch_onboarding')
        except Exception as e:
            if any(c in str(e) for c in ['404', '403', 'Unknown']):
                skip('fetch_onboarding', 'no access')
            else:
                fail('fetch_onboarding', e)

        try:
            bans = await session.fetch_bans(int(g.id))
            print(f'  bans: {len(bans)}', flush=True)
            ok('fetch_bans')
        except Exception as e:
            if '403' in str(e) or 'Missing' in str(e):
                skip('fetch_bans', 'no permissions')
            else:
                fail('fetch_bans', e)

        try:
            templates = await session.fetch_guild_templates(int(g.id))
            print(f'  templates: {len(templates)}', flush=True)
            ok('fetch_guild_templates')
        except Exception as e:
            if any(c in str(e) for c in ['403', 'Missing', '404']):
                skip('fetch_guild_templates', 'no access')
            else:
                fail('fetch_guild_templates', e)

    try:
        me_user = await session.fetch_user(int(MY_ID))
        assert me_user.id == MY_ID
        ok('fetch_user')
    except Exception as e:
        if '40001' in str(e) or 'Unauthorized' in str(e):
            skip('fetch_user', 'user tokens cannot look up arbitrary users via /users/{id}')
        else:
            fail('fetch_user', e)

    try:
        oauth_tokens = await session.fetch_oauth2_tokens()
        print(f'  oauth2 tokens: {len(oauth_tokens)}', flush=True)
        ok('fetch_oauth2_tokens')
    except Exception as e:
        fail('fetch_oauth2_tokens', e)

    runner.cancel()
    try:
        await runner
    except (asyncio.CancelledError, Exception):
        pass
    await session.close()

    return _print_summary()


async def _run(session):
    import cascade
    try:
        await session.start()
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f'  session error: {e}', flush=True)
    finally:
        await session.close()


def _print_summary():
    print(f'\nPASSED {len(passed)}/{len(passed)+len(failed)}', flush=True)
    if failed:
        print('FAILED:', flush=True)
        for n, e in failed:
            print(f'  FAIL  {n}: {e}', flush=True)
        return 1
    print('ALL LIVE TESTS PASSED', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()) or 0)
