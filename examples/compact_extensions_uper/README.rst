About
=====

An example using ``OPTIONAL`` and power of two ``CHOICE`` instead of
extension markers ``...`` for more compact UPER encoding.

`v1.asn` contains the first version of the protocol, and `v2.asn` the
second. Notice how the last member in ``Foo`` version 1 is ``extension
NULL OPTIONAL`` instead of ``...``. In version 2 it has been replaced
with ``v2 SEQUENCE``, which also has the last member ``extension NULL
OPTIONAL``, allowing future extensions of the ``Foo`` message.

To allow more than four messages in ``Message``, the last member,
``extension3 NULL`` must be replaced with ``more CHOICE {fum Fum,
extension1 NULL, extension2 NULL, extension3 NULL}`` once the first
three messages are used.

Example execution
=================

.. code-block:: text

   $ ./main.py
   Encode V1:

     Input: ('foo', {'b': 55, 'e': 'on', 'a': True, 'c': 3, 'd': False})
     Output: 16ec (2 bytes)

   Encode V2:

     Input: ('foo', {'b': 55, 'e': 'on', 'a': True, 'c': 3, 'd': False})
     Output: 16ec (2 bytes)
     Input: ('foo', {'v2': {'b': True, 'a': -1}, 'b': 55, 'd': False, 'c': 3, 'e': 'on', 'a': True})
     Output: 36ec3fc0 (4 bytes)
     Input: ('bar', 3)
     Output: 46 (1 bytes)

   Encode V2 with extension markers:

     Input: ('foo', {'b': 55, 'e': 'on', 'a': True, 'c': 3, 'd': False})
     Output: 2dd8 (2 bytes)
     Input: ('foo', {'b': 55, 'd': False, 'g': True, 'c': 3, 'e': 'on', 'a': True, 'f': -1})
     Output: 6dd80204ff00 (6 bytes)
     Input: ('bar', 3)
     Output: 800118 (3 bytes)

   Decode V1 with V1:

     Input: 16ec
     Output: ('foo', {'b': 55, 'e': 'on', 'a': True, 'c': 3, 'd': False})

   Decode V1 with V2:

     Input: 16ec
     Output: ('foo', {'b': 55, 'e': 'on', 'a': True, 'c': 3, 'd': False})

   Decode V2 with V1:

     Input: 16ec
     Output: ('foo', {'b': 55, 'e': 'on', 'a': True, 'c': 3, 'd': False})
     Input: 36ec3fc0
     Output: ('foo', {'b': 55, 'extension': None, 'd': False, 'c': 3, 'e': 'on', 'a': True})
     Input: 46
     Output: ('extension1', None)

   Decode V2 with V2:

     Input: 16ec
     Output: ('foo', {'b': 55, 'e': 'on', 'a': True, 'c': 3, 'd': False})
     Input: 36ec3fc0
     Output: ('foo', {'v2': {'b': True, 'a': -1}, 'b': 55, 'd': False, 'c': 3, 'e': 'on', 'a': True})
     Input: 46
     Output: ('bar', 3)
   $
