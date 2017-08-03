|buildstatus|_
|coverage|_

About
=====

ASN.1 tools.

Project homepage: https://github.com/eerimoq/asn1tools

Installation
============

.. code-block:: python

    pip install asn1tools

Example usage
=============

Encode and decode a small ASN.1 sequence called `Foo` using the BER
codec.

.. code-block:: python

   >>> from asn1tools.schema import Sequence, Integer
   >>> from asn1tools.codecs import ber
   >>> foo = Sequence('Foo', [Integer('bar'), Integer('fie', default=22)])
   >>> ber.encode({'bar': 4}, foo)
   >>> b'\x10\x20'
   >>> ber.decode(b'\x10\x20', foo)
   >>> {'bar': 4, 'fie': 22}

See the test suite for additional examples: https://github.com/eerimoq/asn1tools/blob/master/tests/test_asn1tools.py

.. |buildstatus| image:: https://travis-ci.org/eerimoq/asn1tools.svg?branch=master
.. _buildstatus: https://travis-ci.org/eerimoq/asn1tools

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/asn1tools/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/asn1tools
