Stage Instances
===============

Stage instances represent an active stage channel broadcast.

Creating a Stage
----------------

.. code-block:: python

   from cascade import StagePrivacyLevel

   stage = await session.create_stage_instance(
       channel_id=stage_channel_id,
       topic='Q&A with the team',
       privacy_level=int(StagePrivacyLevel.GUILD_ONLY),
   )

Fetching
--------

.. code-block:: python

   stage = await session.fetch_stage_instance(channel_id)
   print(stage.topic, stage.privacy_level)

Editing
-------

.. code-block:: python

   await stage.edit(topic='New Topic')

   await stage.edit(privacy_level=int(StagePrivacyLevel.GUILD_ONLY))

Requesting to Speak
-------------------

.. code-block:: python

   await stage.request_to_speak()

Deleting
--------

.. code-block:: python

   await stage.delete()

Attributes
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``id``
     - Stage instance ID
   * - ``guild_id``
     - Guild ID
   * - ``channel_id``
     - Stage voice channel ID
   * - ``topic``
     - Stage topic string
   * - ``privacy_level``
     - :class:`~cascade.entities.stage.StagePrivacyLevel`
   * - ``discoverable_disabled``
     - Whether hidden from discovery
   * - ``guild_scheduled_event_id``
     - Linked scheduled event ID or ``None``

**StagePrivacyLevel**: ``PUBLIC`` (1), ``GUILD_ONLY`` (2)
