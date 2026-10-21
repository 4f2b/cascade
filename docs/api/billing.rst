Billing & Nitro
===============

cascade exposes Discord's billing API for reading subscription status, payment sources, and gift codes.

.. warning::
   These are read-only endpoints for user accounts. Do not automate purchases.

Nitro Status
------------

.. code-block:: python

   status = await session.fetch_nitro_status()
   print(status)

Subscriptions
-------------

.. code-block:: python

   subs = await session.fetch_subscriptions()
   for sub in subs:
       print(sub.status, sub.current_period_end)
       if sub.is_active:
           print('Nitro active until', sub.current_period_end)
       elif sub.is_ending:
           print('Nitro ending', sub.current_period_end)

Payment Sources
---------------

.. code-block:: python

   sources = await session.fetch_payment_sources()
   for source in sources:
       print(source.type, source.last_4, source.brand)
       if source.default:
           print('Default payment source')

Server Boosts
-------------

.. code-block:: python

   boosts = await session.fetch_applied_boosts()
   for boost in boosts:
       print(boost)

Gift Codes
----------

.. code-block:: python

   gift = await session.fetch_gift_code('AAABBB')
   print(gift.url, gift.uses, gift.max_uses, gift.redeemed)

   result = await session.redeem_gift_code('AAABBB')

Attributes
----------

**Subscription**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``id``
     - Subscription ID
   * - ``status``
     - :class:`~cascade.entities.billing.SubscriptionStatus` (``ACTIVE`` 1, ``ENDING`` 2, ``INACTIVE`` 3)
   * - ``current_period_start``
     - Period start ISO timestamp
   * - ``current_period_end``
     - Period end ISO timestamp
   * - ``canceled_at``
     - Cancellation timestamp or ``None``
   * - ``is_active``
     - ``True`` if status is ``ACTIVE``
   * - ``is_ending``
     - ``True`` if status is ``ENDING``

**PaymentSource**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``id``
     - Payment source ID
   * - ``type``
     - :class:`~cascade.entities.billing.PaymentSourceType`
   * - ``invalid``
     - Whether source is invalid/expired
   * - ``default``
     - Whether this is the default source
   * - ``brand``
     - Card brand (``Visa``, ``Mastercard``, etc.)
   * - ``last_4``
     - Last 4 card digits
   * - ``expires_month`` / ``expires_year``
     - Card expiry
   * - ``email``
     - PayPal email (if PayPal source)

**GiftCode**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Description
   * - ``code``
     - Gift code string
   * - ``url``
     - Full ``https://discord.gift/...`` URL
   * - ``uses``
     - Times redeemed
   * - ``max_uses``
     - Maximum redemptions
   * - ``redeemed``
     - Whether you already redeemed it
   * - ``expires_at``
     - Expiry timestamp or ``None``

**PremiumType**

``NONE`` (0), ``NITRO_CLASSIC`` (1), ``NITRO`` (2), ``NITRO_BASIC`` (3)
