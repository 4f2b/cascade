Rich Presence
=============

cascade supports full rich presence through the :class:`~cascade.utils.activity_builder.RichActivity` builder.

Basic Activities
----------------

.. code-block:: python

   from cascade.utils.activity_builder import RichActivity

   playing = RichActivity.playing('My Game')
   streaming = RichActivity.streaming('My Stream', 'https://twitch.tv/user')
   listening = RichActivity.listening('Spotify')
   watching = RichActivity.watching('YouTube')
   competing = RichActivity.competing('Tournament')
   custom = RichActivity.custom('Away for now')

Fluent Builder
--------------

All setters return ``self`` so you can chain them:

.. code-block:: python

   activity = (
       RichActivity.playing('My Game')
       .set_state('In Match')
       .set_details('Level 50 · Rank Diamond')
   )

Assets
------

.. code-block:: python

   activity.assets.set_large_image('game_logo', 'My Game')
   activity.assets.set_small_image('rank_icon', 'Diamond')

Timestamps
----------

.. code-block:: python

   import time

   activity.timestamps.set_start(int(time.time()))
   activity.timestamps.set_end(int(time.time()) + 3600)

Party
-----

.. code-block:: python

   activity.party.set_id('party_abc123')
   activity.party.set_size(current=2, maximum=4)

Buttons
-------

Up to two buttons can be added:

.. code-block:: python

   activity.add_button('View Profile', 'https://example.com')
   activity.add_button('Join Game', 'https://example.com/join')

Updating Presence
-----------------

.. code-block:: python

   await session.gateway.update_presence(
       status='online',
       activities=[activity.to_dict()]
   )
