Polls
=====

Full poll guide including creation, voting, and results.

Creating
--------

.. code-block:: python

   from cascade import PollBuilder

   poll = (
       PollBuilder('What should we build next?', duration_hours=48)
       .add_answer('CLI tool', '🛠️')
       .add_answer('Web dashboard', '🌐')
       .add_answer('Discord bot', '🤖')
   )

   await session.rest.send_message(channel_id, 'Vote!', poll=poll.to_dict())

Multi-select:

.. code-block:: python

   poll = PollBuilder('Pick all that apply', allow_multiselect=True)
   poll.add_answer('Python').add_answer('Rust').add_answer('Go')

Handling Votes
--------------

.. code-block:: python

   @session.event
   async def on_poll_vote_add(data):
       user_id    = data['user_id']
       message_id = data['message_id']
       channel_id = data['channel_id']
       answer_id  = data['answer_id']
       guild_id   = data.get('guild_id')

       print(f'User {user_id} voted for answer {answer_id}')

   @session.event
   async def on_poll_vote_remove(data):
       print(f'User {data["user_id"]} removed their vote')

Fetching Results
----------------

.. code-block:: python

   voters = await session.rest.get_poll_answer_voters(
       channel_id, message_id, answer_id=1, limit=100
   )
   print(f'{len(voters.get("users", []))} people voted for answer 1')

Ending Early
------------

.. code-block:: python

   await session.rest.end_poll(channel_id, message_id)
