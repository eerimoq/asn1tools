Perparations and testing.

.. code-block:: text

   $ yarn install
   $ yarn test

The JavaScript client periodically sends a message to the server. The
server replies with the same message.

Requires ``pip3 install websockets``.

First start the servers. The web browser should start automatically
when running ``yarn start``.

.. code-block:: text

   $ python3 server.py &
   $ yarn start
