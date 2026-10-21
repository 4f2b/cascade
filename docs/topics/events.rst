Event Reference
===============

Events are dispatched via the ``@session.event`` decorator or by subclassing and overriding methods.

.. code-block:: python

   @session.event
   async def on_ready(user):
       ...

Gateway Events
--------------

on_ready
~~~~~~~~

Called when the gateway receives the READY event.

:param user: The logged-in user.
:type user: :class:`~cascade.entities.user.ClientUser`

on_message
~~~~~~~~~~

Called when a message is created in any channel the user can see.

:param message: The message that was created.
:type message: :class:`~cascade.entities.message.Message`

on_message_edit
~~~~~~~~~~~~~~~

Called when a message is edited.

:param before: The message before editing.
:param after: The message after editing.
:type before: :class:`~cascade.entities.message.Message`
:type after: :class:`~cascade.entities.message.Message`

on_message_delete
~~~~~~~~~~~~~~~~~

Called when a message is deleted.

:param message: The deleted message.
:type message: :class:`~cascade.entities.message.Message`

on_guild_join
~~~~~~~~~~~~~

Called when the user joins a guild.

:param guild: The guild that was joined.
:type guild: :class:`~cascade.entities.guild.Guild`

on_guild_remove
~~~~~~~~~~~~~~~

Called when the user leaves or is removed from a guild.

:param guild: The guild that was left.
:type guild: :class:`~cascade.entities.guild.Guild`

on_member_join
~~~~~~~~~~~~~~

Called when a member joins a guild.

:param member: The member that joined.
:type member: :class:`~cascade.entities.member.Member`

on_member_remove
~~~~~~~~~~~~~~~~

Called when a member leaves a guild.

:param member: The member that left.
:type member: :class:`~cascade.entities.member.Member`

on_reaction_add
~~~~~~~~~~~~~~~

Called when a reaction is added to a message.

:param reaction: The reaction payload.

on_reaction_remove
~~~~~~~~~~~~~~~~~~

Called when a reaction is removed from a message.

:param reaction: The reaction payload.

on_presence_update
~~~~~~~~~~~~~~~~~~

Called when a user's presence is updated.

:param presence: The updated presence.
:type presence: :class:`~cascade.entities.presence.Presence`

on_voice_state_update
~~~~~~~~~~~~~~~~~~~~~

Called when a user's voice state changes.

:param state: The updated voice state.
:type state: :class:`~cascade.voice.state.VoiceState`

on_interaction
~~~~~~~~~~~~~~

Called when the user receives an interaction.

:param interaction: The interaction.
:type interaction: :class:`~cascade.interactions.interaction.Interaction`

on_typing
~~~~~~~~~

Called when a user starts typing in a channel.

:param channel_id: The channel ID.
:param user_id: The user ID.
:param timestamp: When typing started.

on_error
~~~~~~~~

Called when an unhandled exception occurs in an event handler.

:param event: The event name.
:param error: The exception.
