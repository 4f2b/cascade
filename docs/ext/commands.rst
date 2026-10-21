Commands Extension
==================

The commands extension provides a ``Bot`` class that wraps :class:`~cascade.core.session.Session` and adds a prefixed command framework.

Bot
---

.. code-block:: python

   from cascade.ext.commands import Bot

   bot = Bot(command_prefix='!', self_bot=True)

   @bot.command()
   async def ping(ctx):
       await ctx.send(f'Pong! {bot.latency * 1000:.0f}ms')

   @bot.command(name='hi')
   async def hello(ctx):
       await ctx.send(f'Hello {ctx.author.name}')

   bot.run(token)

Constructor parameters:

- **token** -- Discord user token
- **command_prefix** -- string prefix (default ``'!'``)
- **message_cache_limit** -- passed to :class:`~cascade.core.session.Session`
- **platform** -- device spoof preset (default ``'desktop'``)

``Bot`` inherits all :class:`~cascade.core.session.Session` attributes and methods.

The ``@bot.command()`` decorator
---------------------------------

.. code-block:: python

   @bot.command()
   async def name(ctx):
       ...

   @bot.command(name='alias')
   async def something(ctx):
       ...

The function name is used as the command name unless ``name`` is passed explicitly.
Command names are matched case-insensitively.

Arguments are passed as positional string arguments after ``ctx``:

.. code-block:: python

   @bot.command()
   async def say(ctx, *args):
       await ctx.send(' '.join(args))

   @bot.command()
   async def add(ctx, a, b):
       await ctx.send(str(int(a) + int(b)))

Error handling
--------------

Override ``on_command_error`` to handle exceptions raised inside commands:

.. code-block:: python

   bot = Bot('!', self_bot=True)

   @bot.event
   async def on_command_error(ctx, error):
       await ctx.send(f'Error: {error}')

Context
-------

Every command receives a :class:`~cascade.ext.commands.context.Context` as its first argument.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Attribute
     - Description
   * - ``ctx.bot``
     - The :class:`Bot` instance
   * - ``ctx.message``
     - The triggering :class:`~cascade.entities.message.Message`
   * - ``ctx.channel``
     - The channel the command was sent in
   * - ``ctx.guild``
     - The guild, or ``None`` for DMs
   * - ``ctx.author``
     - The :class:`~cascade.entities.user.User` who ran the command
   * - ``ctx.command_prefix``
     - The active prefix string

.. code-block:: python

   async def greet(ctx):
       await ctx.send(f'Hey {ctx.author.name}!')

       await ctx.reply('replying to your message')

       print(ctx.guild.name if ctx.guild else 'DM')
