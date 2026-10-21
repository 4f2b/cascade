import asyncio
import cascade
from cascade.automod import (
    AutoModTriggerType,
    AutoModEventType,
    AutoModAction,
    AutoModTriggerMetadata,
    KeywordPresetType
)


async def main():
    session = cascade.Session(token)
    
    @session.event
    async def on_ready(user):
        print(f'Connected as {user.username}')
        
        guild_id = 123456789
        alert_channel_id = 987654321
        
        trigger_metadata = AutoModTriggerMetadata({
            'keyword_filter': ['badword1', 'badword2'],
            'regex_patterns': [r'\b(spam|scam)\b'],
            'allow_list': ['goodword']
        })
        
        actions = [
            AutoModAction.block_message(),
            AutoModAction.send_alert(alert_channel_id),
            AutoModAction.timeout(60)
        ]
        
        rule_data = {
            'name': 'Bad Words Filter',
            'event_type': int(AutoModEventType.MESSAGE_SEND),
            'trigger_type': int(AutoModTriggerType.KEYWORD),
            'trigger_metadata': trigger_metadata.to_dict(),
            'actions': [action.to_dict() for action in actions],
            'enabled': True
        }
        
        rule = await session.rest.create_automod_rule(guild_id, **rule_data)
        print(f'Created automod rule: {rule["name"]}')
        
        preset_rule_data = {
            'name': 'Profanity Filter',
            'event_type': int(AutoModEventType.MESSAGE_SEND),
            'trigger_type': int(AutoModTriggerType.KEYWORD_PRESET),
            'trigger_metadata': {
                'presets': [int(KeywordPresetType.PROFANITY)]
            },
            'actions': [AutoModAction.block_message().to_dict()],
            'enabled': True
        }
        
        preset_rule = await session.rest.create_automod_rule(guild_id, **preset_rule_data)
        print(f'Created preset rule: {preset_rule["name"]}')
    
    await session.start()


if __name__ == '__main__':
    asyncio.run(main())
