Polls
=====

Discord polls let you create multiple-choice questions inside messages.

Creating a Poll
---------------

Use :class:`~cascade.entities.poll.PollBuilder` to construct the poll payload:

.. code-block:: python

   from cascade import PollBuilder

   poll = (
       PollBuilder('Which language do you prefer?', duration_hours=24)
       .add_answer('Python', '🐍')
       .add_answer('Rust', '🦀')
       .add_answer('Go', '🔵')
   )

   await session.rest.send_message(channel_id, 'Vote below!', poll=poll.to_dict())

For multi-select polls:

.. code-block:: python

   poll = PollBuilder('Pick your favourites', duration_hours=48, allow_multiselect=True)
   poll.add_answer('Coffee').add_answer('Tea').add_answer('Water')

Voting
------

.. code-block:: python

   await session.rest.create_poll_answer(channel_id, message_id, answer_id=1)

   await session.rest.delete_poll_answer(channel_id, message_id, answer_id=1)

Fetching Voters
---------------

.. code-block:: python

   voters = await session.rest.get_poll_answer_voters(channel_id, message_id, answer_id=1, limit=25)
   for voter in voters.get('users', []):
       print(voter['username'])

Ending a Poll
-------------

.. code-block:: python

   await session.rest.end_poll(channel_id, message_id)

Gateway Events
--------------

.. code-block:: python

   @session.event
   async def on_poll_vote_add(data):
       print(data['user_id'], 'voted on answer', data['answer_id'])

   @session.event
   async def on_poll_vote_remove(data):
       print(data['user_id'], 'removed vote on answer', data['answer_id'])

PollBuilder API
---------------

.. code-block:: python

   poll = PollBuilder(question, duration_hours=24, allow_multiselect=False)

   poll.add_answer(text, emoji=None)

   payload = poll.to_dict()

Payload fields: ``question``, ``answers``, ``duration``, ``allow_multiselect``, ``layout_type``.
