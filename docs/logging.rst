Logging
=======

cascade uses Python's standard :mod:`logging` module.

.. code-block:: python

   import logging
   import cascade

   logging.basicConfig(level=logging.DEBUG)

   session = cascade.Session(token)

Recommended setup for production:

.. code-block:: python

   import logging

   logger = logging.getLogger('cascade')
   logger.setLevel(logging.WARNING)

   handler = logging.FileHandler('cascade.log')
   handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
   logger.addHandler(handler)
