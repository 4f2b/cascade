import asyncio
import cascade
from cascade.interactions import (
    Button,
    ActionRow,
    SelectMenu,
    SelectOption,
    Modal,
    TextInput,
    TextInputStyle
)


async def main():
    session = cascade.Session(token)
    
    @session.event
    async def on_ready(user):
        print(f'Connected as {user.username}')
    
    @session.event
    async def on_message(message):
        if message.content == '!buttons':
            buttons = ActionRow(
                Button.primary('Click Me', 'button_1'),
                Button.secondary('Cancel', 'button_2'),
                Button.success('Confirm', 'button_3'),
                Button.danger('Delete', 'button_4'),
                Button.link('Visit', 'https://example.com')
            )
            
            await session.rest.send_message(
                message.channel_id,
                content='Choose an option:',
                components=[buttons.to_dict()]
            )
        
        elif message.content == '!select':
            options = [
                SelectOption('Option 1', 'opt_1', description='First choice'),
                SelectOption('Option 2', 'opt_2', description='Second choice'),
                SelectOption('Option 3', 'opt_3', description='Third choice')
            ]
            
            select = SelectMenu(
                custom_id='my_select',
                options=options,
                placeholder='Choose an option',
                min_values=1,
                max_values=2
            )
            
            await session.rest.send_message(
                message.channel_id,
                content='Select options:',
                components=[ActionRow(select).to_dict()]
            )
        
        elif message.content == '!modal':
            modal = Modal.create(
                'feedback_modal',
                'Feedback Form',
                TextInput(
                    custom_id='title',
                    label='Title',
                    style=TextInputStyle.SHORT,
                    placeholder='Enter a title',
                    required=True,
                    max_length=100
                ),
                TextInput(
                    custom_id='feedback',
                    label='Your Feedback',
                    style=TextInputStyle.PARAGRAPH,
                    placeholder='Tell us what you think',
                    required=True,
                    min_length=10,
                    max_length=1000
                )
            )
            
            print('Modal ready - send via interaction response')
    
    @session.event
    async def on_interaction(interaction):
        if interaction.type == cascade.InteractionType.MESSAGE_COMPONENT:
            if interaction.custom_id == 'button_1':
                await interaction.send_message('You clicked the button!')
            
            elif interaction.custom_id.startswith('button_'):
                await interaction.update(f'Button {interaction.custom_id} pressed!')
            
            elif interaction.custom_id == 'my_select':
                selected = ', '.join(interaction.values)
                await interaction.send_message(f'You selected: {selected}')
        
        elif interaction.type == cascade.InteractionType.MODAL_SUBMIT:
            if interaction.custom_id == 'feedback_modal':
                components = interaction.components
                await interaction.send_message('Thank you for your feedback!')
    
    await session.start()


if __name__ == '__main__':
    asyncio.run(main())
