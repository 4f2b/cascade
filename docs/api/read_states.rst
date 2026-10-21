Read States
===========

Read states track which channels have unread messages and mention counts.

Fetching
--------

.. code-block:: python

   states = await session.fetch_read_states()
   for state in states:
       if state.unread:
           print(f'Channel {state.channel_id}: {state.mention_count} mentions')

Acknowledging
-------------

Mark a specific channel as read:

.. code-block:: python

   await state.ack()

   await session.rest.ack_channel(channel_id)

Acknowledge all messages in a guild:

.. code-block:: python

   await session.rest.ack_all_channels(guild_id)

Acknowledge a specific message:

.. code-block:: python

   await session.rest.ack_message(channel_id, message_id)

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``channel_id``
     - Channel ID
   * - ``last_message_id``
     - Last read message ID or ``None``
   * - ``mention_count``
     - Number of unread mentions
   * - ``badge_count``
     - Badge count
   * - ``flags``
     - Read state flags
   * - ``unread``
     - ``True`` if ``mention_count > 0``
