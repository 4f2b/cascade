Applications & Teams
====================

cascade supports full application and team management through :class:`~cascade.entities.application.Application` and :class:`~cascade.entities.team.Team`.

Fetching Applications
---------------------

.. code-block:: python

   apps = await session.fetch_my_applications()
   for app in apps:
       print(app.name, app.id)

   app = await session.fetch_application(application_id)
   print(app.name, app.description)
   print(app.icon_url)

Editing an Application
----------------------

All fields are optional -- only pass what you want to change:

.. code-block:: python

   await app.edit(
       name='New Name',
       description='Updated description',
       bot_public=False,
       tags=['tool', 'utility'],
       terms_of_service_url='https://example.com/tos',
       privacy_policy_url='https://example.com/privacy',
   )

Assets
------

.. code-block:: python

   assets = await app.get_assets()

   asset = await app.upload_asset('my_image', base64_image_data)

   await app.delete_asset(asset['id'])

Transferring to a Team
----------------------

.. code-block:: python

   await app.transfer(team_id)

Deleting
--------

.. code-block:: python

   await app.delete()

Teams
-----

Fetch all teams you belong to:

.. code-block:: python

   teams = await session.fetch_teams()
   for team in teams:
       print(team.name, team.id)
       for member in team.members:
           print(f'  {member.username} ({member.role}) accepted={member.accepted}')

Create a team:

.. code-block:: python

   team = await session.create_team('My Team')

Edit a team:

.. code-block:: python

   await team.edit(name='New Name')

Managing members:

.. code-block:: python

   await team.invite_member('username')

   await team.remove_member(user_id)

   await team.transfer_ownership(user_id)

Fetch applications owned by a team:

.. code-block:: python

   apps = await session.rest.get_team_applications(team.id)

Application Flags
-----------------

.. code-block:: python

   from cascade import ApplicationFlags

   if app.flags & ApplicationFlags.GATEWAY_MESSAGE_CONTENT:
       print('app has message content intent approved')
