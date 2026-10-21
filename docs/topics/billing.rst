Billing & Nitro
===============

Checking subscription status and reading billing data.

Nitro
-----

.. code-block:: python

   from cascade import PremiumType

   status = await session.fetch_nitro_status()

   if session.user.premium:
       ptype = PremiumType(session.user.premium_type)
       print(f'Has {ptype.name}')

Subscriptions
-------------

.. code-block:: python

   subs = await session.fetch_subscriptions()
   active = [s for s in subs if s.is_active]
   ending = [s for s in subs if s.is_ending]

   for sub in active:
       print(f'Active until {sub.current_period_end}')

   for sub in ending:
       print(f'Ending {sub.current_period_end} - will not renew')

Payment Sources
---------------

.. code-block:: python

   sources = await session.fetch_payment_sources()
   for src in sources:
       if src.default:
           print(f'Default: {src.brand} ending {src.last_4}')

Server Boosts
-------------

.. code-block:: python

   boosts = await session.fetch_applied_boosts()
   print(f'Boosting {len(boosts)} servers')

Gift Codes
----------

.. code-block:: python

   gift = await session.fetch_gift_code('GIFTCODE')
   if not gift.redeemed:
       result = await session.redeem_gift_code('GIFTCODE')
       print('Redeemed!')
   else:
       print('Already redeemed')
