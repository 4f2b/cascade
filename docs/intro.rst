Introduction
============

cascade is a Python library for interacting with the Discord user API. It is built on top of ``aiohttp`` and ``websockets``, and is designed for speed, reliability, and production use.

Requirements
------------

- Python 3.10 or higher
- ``aiohttp`` 3.9+
- ``websockets`` 12.0+

Optional dependencies:

- ``PyNaCl`` - voice encryption
- ``opuslib`` - Opus audio encoding
- ``cryptography`` - token encryption via :class:`~cascade.security.TokenManager`

Installing
----------

.. code-block:: bash

   pip install cascade-discord

With voice support:

.. code-block:: bash

   pip install "cascade-discord[voice]"

From source:

.. code-block:: bash

   git clone https://github.com/4f2b/cascade
   cd cascade
   pip install -e .
