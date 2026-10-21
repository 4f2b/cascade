Quickstart
==========

This page walks through the basics of cascade.

A Minimal Bot
-------------

.. code-block:: python

   import asyncio
   import cascade

   async def main():
       session = cascade.Session(token)

       @session.event
       async def on_ready(user):
           print(f'Logged in as {user.username}')

       @session.event
       async def on_message(message):
           if message.content == '!ping':
               await session.rest.send_message(message.channel_id, 'Pong!')

       await session.start()

   asyncio.run(main())

Using the Command Framework
---------------------------

.. code-block:: python

   from cascade.ext.commands import Bot

   bot = Bot(command_prefix='!', self_bot=True)

   @bot.command()
   async def ping(ctx):
       await ctx.send(f'Pong! {bot.session.gateway.latency:.0f}ms')

   @bot.command()
   async def say(ctx, *, text: str):
       await ctx.send(text)

   bot.run(token)

Platform Spoofing
-----------------

Appear as a different device type. Discord will show the corresponding platform indicator on your profile.

.. code-block:: python

   session = cascade.Session(token, platform='mobile')

   session.set_platform('vr')

   print(session.get_platform_info())

Available platforms: ``desktop``, ``windows``, ``macos``, ``linux``, ``web``, ``mobile``, ``android``, ``ios``, ``iphone``, ``ipad``, ``vr``, ``quest``, ``xbox``, ``playstation``.

Rich Presence
-------------

.. code-block:: python

   from cascade.utils.activity_builder import RichActivity
   import time

   activity = RichActivity.playing('My Game')
   activity.set_state('In Match').set_details('Level 50')
   activity.assets.set_large_image('game_logo', 'My Game')
   activity.timestamps.set_start(int(time.time()))
   activity.add_button('View Profile', 'https://example.com')

   await session.gateway.update_presence(
       status='online',
       activities=[activity.to_dict()]
   )
