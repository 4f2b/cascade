import asyncio
import time
import cascade
from cascade.interactions import Button, ActionRow, SelectMenu, SelectOption, Modal, TextInput, TextInputStyle
from cascade.automod import AutoModAction, AutoModTriggerMetadata, AutoModEventType, AutoModTriggerType
from cascade.utils.activity_builder import RichActivity
from cascade.core.advanced_cache import AdvancedCache, CacheStrategy


async def main():
    session = cascade.Session(token)
    
    message_cache = AdvancedCache(max_size=500, ttl=300, strategy=CacheStrategy.LRU)
    
    @session.event
    async def on_ready(user):
        print(f'Connected as {user.username}')
        print(f'ID: {user.id}')
        
        activity = RichActivity.playing('Cascade Demo')
        activity.set_state('Showcasing Features')
        activity.set_details('High-Performance Library')
        activity.timestamps.set_start(int(time.time()))
        activity.add_button('GitHub', 'https://github.com/4f2b/cascade')
        
        await session.gateway.update_presence(
            status='online',
            activities=[activity.to_dict()]
        )
    
    @session.event
    async def on_message(message):
        if message.author.bot:
            return
        
        message_cache.set(f'msg:{message.id}', message)
        
        if message.content == '!help':
            help_text = '''
**Cascade Feature Showcase**

`!buttons` - Interactive button components
`!select` - Select menu example
`!voice` - Voice state information
`!activity` - Change rich presence
`!automod` - Setup auto-moderation rule
`!cache` - Display cache statistics
`!permissions` - Check your permissions
            '''
            await session.rest.send_message(message.channel_id, help_text)
        
        elif message.content == '!buttons':
            row1 = ActionRow(
                Button.primary('Primary', 'btn_primary'),
                Button.secondary('Secondary', 'btn_secondary'),
                Button.success('Success', 'btn_success'),
                Button.danger('Danger', 'btn_danger')
            )
            
            row2 = ActionRow(
                Button.link('Documentation', 'https://github.com/4f2b/cascade')
            )
            
            await session.rest.send_message(
                message.channel_id,
                'Interactive buttons:',
                components=[row1.to_dict(), row2.to_dict()]
            )
        
        elif message.content == '!select':
            options = [
                SelectOption('Python', 'py', description='Python programming', emoji='🐍'),
                SelectOption('JavaScript', 'js', description='JavaScript development', emoji='📜'),
                SelectOption('Rust', 'rs', description='Systems programming', emoji='🦀'),
                SelectOption('Go', 'go', description='Backend services', emoji='🔵')
            ]
            
            select = SelectMenu(
                custom_id='lang_select',
                options=options,
                placeholder='Choose your language',
                min_values=1,
                max_values=3
            )
            
            await session.rest.send_message(
                message.channel_id,
                'Select your favorite languages:',
                components=[ActionRow(select).to_dict()]
            )
        
        elif message.content == '!voice':
            if message.guild_id:
                voice_states = await session.rest.get_guild(message.guild_id)
                await session.rest.send_message(
                    message.channel_id,
                    f'Voice features available. Use voice state management to join/leave channels.'
                )
        
        elif message.content == '!activity':
            activities = [
                RichActivity.streaming('Live Coding', 'https://twitch.tv/user'),
                RichActivity.listening('Spotify'),
                RichActivity.watching('YouTube Tutorial'),
                RichActivity.competing('Code Tournament')
            ]
            
            selected = activities[int(time.time()) % len(activities)]
            await session.gateway.update_presence(activities=[selected.to_dict()])
            await session.rest.send_message(message.channel_id, 'Activity updated!')
        
        elif message.content.startswith('!automod'):
            if message.guild_id:
                metadata = AutoModTriggerMetadata({
                    'keyword_filter': ['spam', 'scam', 'phishing']
                })
                
                actions = [AutoModAction.block_message()]
                
                await session.rest.send_message(
                    message.channel_id,
                    'Auto-moderation rule structure created. Use with appropriate permissions.'
                )
        
        elif message.content == '!cache':
            stats = message_cache.get_stats()
            stats_text = f'''
**Cache Statistics**
Size: {stats["size"]}/{stats["max_size"]}
Hits: {stats["hits"]}
Misses: {stats["misses"]}
Hit Rate: {stats["hit_rate"]:.1%}
Strategy: {stats["strategy"].upper()}
            '''
            await session.rest.send_message(message.channel_id, stats_text)
        
        elif message.content == '!permissions':
            if message.guild_id and hasattr(message, 'member'):
                perms = cascade.Permissions()
                
                perm_list = [
                    cascade.Permission.SEND_MESSAGES,
                    cascade.Permission.MANAGE_MESSAGES,
                    cascade.Permission.ADMINISTRATOR
                ]
                
                status = '\n'.join([
                    f'{p.name}: {"✓" if perms.has(p) else "✗"}'
                    for p in perm_list
                ])
                
                await session.rest.send_message(
                    message.channel_id,
                    f'**Permission Check**\n{status}'
                )
    
    @session.event
    async def on_interaction(interaction):
        if interaction.type == cascade.InteractionType.MESSAGE_COMPONENT:
            if interaction.custom_id.startswith('btn_'):
                button_type = interaction.custom_id.replace('btn_', '').title()
                await interaction.send_message(f'You clicked: {button_type}', flags=64)
            
            elif interaction.custom_id == 'lang_select':
                langs = ', '.join(interaction.values)
                await interaction.send_message(f'Selected: {langs}', flags=64)
    
    await session.start()


if __name__ == '__main__':
    asyncio.run(main())
