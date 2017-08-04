|buildstatus|_
|coverage|_

About
=====

A Python package for ASN.1 parsing, encoding and decoding.

Project homepage: https://github.com/eerimoq/asn1tools

Documentation: http://asn1tools.readthedocs.org/en/latest

Installation
============

.. code-block:: python

    pip install asn1tools

Example usage
=============

This is an example ASN.1 specification defining the messages of a
fictitious Foo protocol (based on the FooProtocol on Wikipedia).

.. code-block:: text

   Foo DEFINITIONS ::= BEGIN

       Question ::= SEQUENCE {
           id        INTEGER,
           question  IA5String
       }

       Answer ::= SEQUENCE {
           id        INTEGER,
           answer    BOOLEAN
       }

   END

Compile the ASN.1 specification, and encode and decode a question
using the default codec (BER).

.. code-block:: python

   >>> import asn1tools
   >>> foo = asn1tools.compile_file('tests/files/foo.asn')
   >>> encoded = foo.encode('Question', {'id': 1, 'question': 'What is 1+1?'})
   >>> encoded
   b'0\x11\x02\x01\x01\x16\x0cWhat is 1+1?'
   >>> foo.decode('Question', encoded)
   {'id': 1, 'question': 'What is 1+1?'}

See the test suite for additional examples: https://github.com/eerimoq/asn1tools/blob/master/tests/test_asn1tools.py

.. |buildstatus| image:: https://travis-ci.org/eerimoq/asn1tools.svg?branch=master
.. _buildstatus: https://travis-ci.org/eerimoq/asn1tools

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/asn1tools/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/asn1tools
