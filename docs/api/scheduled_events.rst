Scheduled Events
================

Guild scheduled events let you create events that appear in the server's event list.

Creating an Event
-----------------

.. code-block:: python

   from cascade import ScheduledEventEntityType, ScheduledEventPrivacyLevel

   event = await session.create_scheduled_event(
       guild_id,
       name='Community Meetup',
       description='Monthly voice hangout',
       scheduled_start_time='2026-11-15T18:00:00',
       scheduled_end_time='2026-11-15T20:00:00',
       privacy_level=int(ScheduledEventPrivacyLevel.GUILD_ONLY),
       entity_type=int(ScheduledEventEntityType.VOICE),
       channel_id=voice_channel_id,
   )

For external events (location outside Discord):

.. code-block:: python

   event = await session.create_scheduled_event(
       guild_id,
       name='IRL Meetup',
       scheduled_start_time='2026-12-01T14:00:00',
       scheduled_end_time='2026-12-01T17:00:00',
       privacy_level=2,
       entity_type=int(ScheduledEventEntityType.EXTERNAL),
       entity_metadata={'location': 'Central Park, New York'},
   )

Fetching Events
---------------

.. code-block:: python

   events = await session.fetch_scheduled_events(guild_id)
   for event in events:
       print(event.name, event.status, event.user_count)

   event = await session.rest.get_guild_scheduled_event(guild_id, event_id)

Managing Lifecycle
------------------

.. code-block:: python

   await event.start()

   await event.complete()

   await event.cancel()

   await event.edit(name='Updated Name', description='New description')

   await event.delete()

Fetching Attendees
------------------

.. code-block:: python

   users = await event.fetch_users(limit=100, with_member=True)
   for user in users:
       print(user['user']['username'])

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``id``
     - Event snowflake ID
   * - ``guild_id``
     - Guild ID
   * - ``name``
     - Event name
   * - ``description``
     - Event description
   * - ``scheduled_start_time``
     - ISO start timestamp
   * - ``scheduled_end_time``
     - ISO end timestamp or ``None``
   * - ``status``
     - :class:`~cascade.entities.scheduled_event.ScheduledEventStatus`
   * - ``entity_type``
     - :class:`~cascade.entities.scheduled_event.ScheduledEventEntityType`
   * - ``channel_id``
     - Voice/stage channel ID or ``None``
   * - ``user_count``
     - Number of interested users
   * - ``image`` / ``cover_url``
     - Cover image hash / CDN URL
   * - ``location``
     - External location string (from entity_metadata)

Enumerations
------------

**ScheduledEventStatus**

``SCHEDULED`` (1), ``ACTIVE`` (2), ``COMPLETED`` (3), ``CANCELED`` (4)

**ScheduledEventEntityType**

``STAGE_INSTANCE`` (1), ``VOICE`` (2), ``EXTERNAL`` (3)
