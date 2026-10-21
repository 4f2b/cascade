REST Client
===========

The REST client is available as ``session.rest`` and handles all HTTP requests to the Discord API.

All methods are ``async`` and return parsed JSON dicts or lists unless otherwise noted.

Rate limiting is handled automatically per-bucket with exponential backoff on 429 responses.

Users
-----

.. code-block:: python

   me       = await session.rest.get_current_user()
   user     = await session.rest.get_user(user_id)
   profile  = await session.rest.get_user_profile(user_id)
   await session.rest.modify_current_user(username='new_name')

Settings & Connections
----------------------

.. code-block:: python

   settings    = await session.rest.get_user_settings()
   connections = await session.rest.get_user_connections()
   notes       = await session.rest.get_user_note(user_id)
   await session.rest.set_user_note(user_id, note='text')

Relationships
-------------

.. code-block:: python

   rels    = await session.rest.get_relationships()
   await session.rest.send_friend_request(username)
   await session.rest.accept_friend_request(user_id)
   await session.rest.remove_relationship(user_id)
   await session.rest.block_user(str(user_id))
   await session.rest.set_relationship_nickname(user_id, nickname)
   mutual  = await session.rest.get_mutual_friends(user_id)
   suggs   = await session.rest.get_friend_suggestions()
   await session.rest.delete_friend_suggestion(user_id)

Guilds
------

.. code-block:: python

   guilds   = await session.rest.get_guilds()
   guild    = await session.rest.get_guild(guild_id)
   await session.rest.leave_guild(guild_id)
   await session.rest.modify_guild(guild_id, name='new name')
   await session.rest.delete_guild(guild_id)
   await session.rest.create_guild(name='My Guild')
   preview  = await session.rest.get_guild_preview(guild_id)
   vanity   = await session.rest.get_guild_vanity_url(guild_id)
   bans     = await session.rest.get_guild_bans(guild_id)
   await session.rest.ban_member(guild_id, user_id, delete_message_days=1)
   await session.rest.unban_member(guild_id, user_id)
   await session.rest.kick_member(guild_id, user_id)
   prune    = await session.rest.get_guild_prune_count(guild_id, days=7)
   invites  = await session.rest.get_guild_invites(guild_id)
   widgets  = await session.rest.get_guild_widget(guild_id)

Members
-------

.. code-block:: python

   member   = await session.rest.get_guild_member(guild_id, user_id)
   members  = await session.rest.list_guild_members(guild_id, limit=100)
   await session.rest.modify_guild_member(guild_id, user_id, nick='nickname')
   await session.rest.add_guild_member_role(guild_id, user_id, role_id)
   await session.rest.remove_guild_member_role(guild_id, user_id, role_id)
   await session.rest.modify_current_member(guild_id, nick='nickname')

Channels
--------

.. code-block:: python

   channel  = await session.rest.get_channel(channel_id)
   channels = await session.rest.get_guild_channels(guild_id)
   await session.rest.create_guild_channel(guild_id, name='general', type=0)
   await session.rest.modify_channel(channel_id, name='new-name', topic='topic')
   await session.rest.delete_channel(channel_id)
   await session.rest.trigger_typing(channel_id)

Messages
--------

.. code-block:: python

   msg      = await session.rest.send_message(channel_id, 'hello')
   msg      = await session.rest.get_message(channel_id, message_id)
   msgs     = await session.rest.get_messages(channel_id, limit=50)
   await session.rest.edit_message(channel_id, message_id, content='edited')
   await session.rest.delete_message(channel_id, message_id)
   await session.rest.bulk_delete_messages(channel_id, [id1, id2, id3])
   await session.rest.pin_message(channel_id, message_id)
   await session.rest.unpin_message(channel_id, message_id)
   pins     = await session.rest.get_pinned_messages(channel_id)
   await session.rest.ack_message(channel_id, message_id)
   results  = await session.rest.search_channel_messages(channel_id, query='keyword')

Reactions
---------

.. code-block:: python

   await session.rest.add_reaction(channel_id, message_id, '👍')
   await session.rest.remove_reaction(channel_id, message_id, '👍')
   users    = await session.rest.get_reactions(channel_id, message_id, '👍')

Roles
-----

.. code-block:: python

   roles    = await session.rest.get_guild_roles(guild_id)
   role     = await session.rest.create_guild_role(guild_id, name='Mod', color=0xff0000)
   await session.rest.modify_guild_role(guild_id, role_id, name='Admin')
   await session.rest.delete_guild_role(guild_id, role_id)

Threads
-------

.. code-block:: python

   thread   = await session.rest.create_thread(channel_id, message_id, name='Discussion')
   await session.rest.join_thread(thread_id)
   await session.rest.leave_thread(thread_id)
   threads  = await session.rest.get_active_threads(guild_id)

Webhooks
--------

.. code-block:: python

   webhook  = await session.rest.create_webhook(channel_id, name='Hook')
   webhooks = await session.rest.get_channel_webhooks(channel_id)
   await session.rest.modify_webhook(webhook_id, name='New Name')
   await session.rest.delete_webhook(webhook_id)
   await session.rest.execute_webhook(webhook_id, token, content='hi')

Applications & Teams
--------------------

.. code-block:: python

   apps     = await session.rest.get_my_applications()
   app      = await session.rest.get_application(app_id)
   await session.rest.edit_application(app_id, name='New Name')
   await session.rest.delete_application(app_id)
   await session.rest.transfer_application(app_id, team_id)
   assets   = await session.rest.get_application_assets(app_id)
   asset    = await session.rest.create_application_asset(app_id, 'name', base64_data)
   await session.rest.delete_application_asset(app_id, asset_id)

   teams    = await session.rest.get_my_teams()
   team     = await session.rest.create_team('Name')
   team     = await session.rest.get_team(team_id)
   await session.rest.modify_team(team_id, name='New Name')
   members  = await session.rest.get_team_members(team_id)
   await session.rest.invite_team_member(team_id, 'username')
   await session.rest.remove_team_member(team_id, user_id)
   await session.rest.delete_team(team_id)

Auto-Moderation
---------------

.. code-block:: python

   rules    = await session.rest.get_automod_rules(guild_id)
   rule     = await session.rest.get_automod_rule(guild_id, rule_id)
   rule     = await session.rest.create_automod_rule(guild_id, **rule_data)
   await session.rest.modify_automod_rule(guild_id, rule_id, enabled=False)
   await session.rest.delete_automod_rule(guild_id, rule_id)

Interactions
------------

.. code-block:: python

   await session.rest.create_interaction_response(interaction_id, token, type=4, data={'content': 'hi'})
   await session.rest.edit_original_interaction_response(app_id, token, content='edited')
   await session.rest.delete_original_interaction_response(app_id, token)
   await session.rest.create_followup_message(app_id, token, content='followup')

Voice
-----

.. code-block:: python

   await session.rest.modify_current_user_voice_state(guild_id, channel_id=channel_id)
   await session.rest.modify_user_voice_state(guild_id, user_id, suppress=False)

Invites
-------

.. code-block:: python

   invite   = await session.rest.get_invite('abc123')
   await session.rest.delete_invite('abc123')
   invite   = await session.rest.create_channel_invite(channel_id, max_age=86400)
   invites  = await session.rest.get_channel_invites(channel_id)
