Relationships
=============

cascade gives you full control over Discord's friend and block system through the :class:`~cascade.entities.relationship.Relationship` entity.

Fetching
--------

.. code-block:: python

   relationships = await session.fetch_relationships()

   friends = await session.fetch_friends()

   blocked = await session.fetch_blocked()

   for r in friends:
       print(r.display_name, r.since)

Sending a Friend Request
------------------------

.. code-block:: python

   await session.send_friend_request('username')

Accepting / Removing
--------------------

.. code-block:: python

   relationships = await session.fetch_relationships()

   for r in relationships:
       if r.is_incoming_request:
           await r.accept()

   friend = relationships[0]
   await friend.remove()

Blocking
--------

.. code-block:: python

   await session.rest.block_user(user_id)

   for r in relationships:
       if r.is_friend:
           await r.block()

Nicknames
---------

Set a private nickname on a friend that only you can see:

.. code-block:: python

   await friend.set_nickname('their nickname')

   await friend.set_nickname(None)

Opening a DM
------------

.. code-block:: python

   channel = await friend.open_dm()
   await session.rest.send_message(channel['id'], 'hey')

Relationship Types
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Type
     - Description
   * - ``FRIEND`` (1)
     - Mutual friends
   * - ``BLOCKED`` (2)
     - User blocked by you
   * - ``INCOMING_REQUEST`` (3)
     - They sent you a request
   * - ``OUTGOING_REQUEST`` (4)
     - You sent them a request
   * - ``IMPLICIT`` (5)
     - Shared server member (no explicit relationship)
