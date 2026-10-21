Auto-Moderation
===============

cascade supports creating and managing auto-moderation rules via the Discord AutoMod API.

Creating a Rule
---------------

.. code-block:: python

   from cascade.automod import (
       AutoModTriggerType,
       AutoModEventType,
       AutoModAction,
       AutoModTriggerMetadata,
   )

   metadata = AutoModTriggerMetadata({
       'keyword_filter': ['badword', 'spam'],
       'regex_patterns': [r'\b(scam|phish)\b'],
       'allow_list': ['notbad'],
   })

   actions = [
       AutoModAction.block_message(),
       AutoModAction.send_alert(alert_channel_id),
       AutoModAction.timeout(300),
   ]

   rule_data = {
       'name': 'Word Filter',
       'event_type': int(AutoModEventType.MESSAGE_SEND),
       'trigger_type': int(AutoModTriggerType.KEYWORD),
       'trigger_metadata': metadata.to_dict(),
       'actions': [a.to_dict() for a in actions],
       'enabled': True,
       'exempt_roles': [],
       'exempt_channels': [staff_channel_id],
   }

   result = await session.rest.create_automod_rule(guild_id, **rule_data)

Preset Filters
--------------

Use ``KEYWORD_PRESET`` trigger type to enable Discord's built-in word lists:

.. code-block:: python

   from cascade.automod import KeywordPresetType

   metadata = AutoModTriggerMetadata({
       'presets': [int(KeywordPresetType.PROFANITY), int(KeywordPresetType.SLURS)],
   })

Available presets: ``PROFANITY`` (1), ``SEXUAL_CONTENT`` (2), ``SLURS`` (3).

Mention Spam
------------

.. code-block:: python

   metadata = AutoModTriggerMetadata({
       'mention_total_limit': 5,
       'mention_raid_protection_enabled': True,
   })

   rule_data = {
       'trigger_type': int(AutoModTriggerType.MENTION_SPAM),
       'trigger_metadata': metadata.to_dict(),
       ...
   }

Fetching Rules
--------------

.. code-block:: python

   rules = await session.rest.get_automod_rules(guild_id)

   rule = await session.rest.get_automod_rule(guild_id, rule_id)

Editing a Rule
--------------

.. code-block:: python

   from cascade.automod import AutoModRule

   rule = AutoModRule(rule_data, session)

   await rule.edit(enabled=False)

   await rule.edit(
       actions=[AutoModAction.block_message()],
       exempt_channels=[channel_id],
   )

Deleting
--------

.. code-block:: python

   await rule.delete()

   await session.rest.delete_automod_rule(guild_id, rule_id)

Trigger Types
-------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Type
     - Description
   * - ``KEYWORD`` (1)
     - Custom keyword filter with regex support
   * - ``SPAM`` (3)
     - Discord's built-in spam detection
   * - ``KEYWORD_PRESET`` (4)
     - Discord's built-in word lists
   * - ``MENTION_SPAM`` (5)
     - Mention count threshold

Action Types
------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Action
     - Description
   * - ``block_message()``
     - Silently block the message
   * - ``send_alert(channel_id)``
     - Send a log message to a channel
   * - ``timeout(seconds)``
     - Timeout the user for N seconds (max 2419200 / 4 weeks)
