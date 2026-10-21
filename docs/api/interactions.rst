Interactions
============

cascade supports receiving and responding to Discord interactions: buttons, select menus, modals, and slash commands.

Receiving Interactions
----------------------

Listen for the ``on_interaction`` event:

.. code-block:: python

   from cascade.interactions import InteractionType

   @session.event
   async def on_interaction(interaction):
       if interaction.type == InteractionType.MESSAGE_COMPONENT:
           if interaction.custom_id == 'confirm_btn':
               await interaction.send_message('Confirmed!')

       elif interaction.type == InteractionType.MODAL_SUBMIT:
           if interaction.custom_id == 'my_modal':
               await interaction.send_message('Form received!')

Interaction
-----------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``id``
     - Interaction snowflake ID
   * - ``type``
     - :class:`~cascade.interactions.interaction.InteractionType`
   * - ``token``
     - Interaction token (valid 15 minutes)
   * - ``custom_id``
     - Component or modal custom ID
   * - ``values``
     - Selected values (select menus)
   * - ``components``
     - Submitted components (modal)
   * - ``guild_id``
     - Guild ID or ``None``
   * - ``channel_id``
     - Channel ID
   * - ``user_id``
     - User ID

Response methods:

.. code-block:: python

   await interaction.send_message('response', flags=64)

   await interaction.defer()

   await interaction.update('new content')

   await interaction.send_modal(modal)

   await interaction.followup('follow-up message')

   await interaction.edit_original('edited')

   await interaction.delete_original()

``flags=64`` sends an ephemeral (only-you-can-see) response.

Buttons
-------

.. code-block:: python

   from cascade.interactions import Button, ActionRow

   row = ActionRow(
       Button.primary('Click Me', 'btn_click'),
       Button.secondary('Cancel', 'btn_cancel'),
       Button.success('Confirm', 'btn_confirm'),
       Button.danger('Delete', 'btn_delete'),
       Button.link('Visit', 'https://example.com'),
   )

   await session.rest.send_message(channel_id, 'Choose:', components=[row.to_dict()])

Button styles:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Style
     - Description
   * - ``PRIMARY``
     - Blurple
   * - ``SECONDARY``
     - Grey
   * - ``SUCCESS``
     - Green
   * - ``DANGER``
     - Red
   * - ``LINK``
     - Opens a URL (no ``custom_id``, requires ``url``)

A row can hold up to 5 buttons. A message can have up to 5 rows.

Select Menus
------------

.. code-block:: python

   from cascade.interactions import SelectMenu, SelectOption, ActionRow

   options = [
       SelectOption('Option A', 'opt_a', description='First choice', emoji='🅰️'),
       SelectOption('Option B', 'opt_b', description='Second choice'),
       SelectOption('Option C', 'opt_c', default=True),
   ]

   select = SelectMenu(
       custom_id='my_select',
       options=options,
       placeholder='Pick one...',
       min_values=1,
       max_values=2,
   )

   await session.rest.send_message(
       channel_id, 'Select:', components=[ActionRow(select).to_dict()]
   )

Selected values arrive as ``interaction.values`` (list of value strings).

Modals
------

.. code-block:: python

   from cascade.interactions import Modal, TextInput, TextInputStyle

   modal = Modal.create(
       'feedback_modal',
       'Send Feedback',
       TextInput(
           custom_id='subject',
           label='Subject',
           style=TextInputStyle.SHORT,
           placeholder='Brief summary',
           required=True,
           max_length=100,
       ),
       TextInput(
           custom_id='body',
           label='Details',
           style=TextInputStyle.PARAGRAPH,
           required=True,
           min_length=20,
           max_length=2000,
       ),
   )

   await interaction.send_modal(modal)

Submitted values come back as ``interaction.components`` -- a list of action row dicts. Each row contains a component dict with ``custom_id`` and ``value``.

Action Rows
-----------

:class:`~cascade.interactions.components.ActionRow` wraps one or more components.
A message accepts up to 5 action rows. Each row holds up to 5 buttons or 1 select menu.

.. code-block:: python

   row1 = ActionRow(Button.primary('A', 'a'), Button.secondary('B', 'b'))
   row2 = ActionRow(SelectMenu(custom_id='s', options=options))

   await session.rest.send_message(channel_id, 'Pick:', components=[row1.to_dict(), row2.to_dict()])
