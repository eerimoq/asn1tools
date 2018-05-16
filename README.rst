|buildstatus|_
|coverage|_

About
=====

A Python package for `ASN.1`_ parsing, encoding and decoding.

This project is *under development* and does only support a subset
of the ASN.1 specification syntax.

Codecs under development:

- Basic Encoding Rules (BER)
- Distinguished Encoding Rules (DER)
- Generic String Encoding Rules (GSER)
- JSON Encoding Rules (JER)
- Aligned Packed Encoding Rules (PER)
- Unaligned Packed Encoding Rules (UPER)
- XML Encoding Rules (XER)

Planned codecs:

- Octet Encoding Rules (OER)

Project homepage: https://github.com/eerimoq/asn1tools

Documentation: http://asn1tools.readthedocs.org/en/latest

Known limitations
=================

- The CLASS keyword and its friends are not supported.

Installation
============

.. code-block:: python

    pip install asn1tools

Example Usage
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

Scripting
---------

`Compile`_ the ASN.1 specification, and `encode`_ and `decode`_ a
question using the default codec (BER).

.. code-block:: python

   >>> import asn1tools
   >>> foo = asn1tools.compile_files('tests/files/foo.asn')
   >>> encoded = foo.encode('Question', {'id': 1, 'question': 'Is 1+1=3?'})
   >>> encoded
   bytearray(b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3?')
   >>> foo.decode('Question', encoded)
   {'id': 1, 'question': 'Is 1+1=3?'}

The same ASN.1 specification, but using the PER codec.

.. code-block:: python

   >>> import asn1tools
   >>> foo = asn1tools.compile_files('tests/files/foo.asn', 'per')
   >>> encoded = foo.encode('Question', {'id': 1, 'question': 'Is 1+1=3?'})
   >>> encoded
   bytearray(b'\x01\x01\tIs 1+1=3?')
   >>> foo.decode('Question', encoded)
   {'id': 1, 'question': 'Is 1+1=3?'}

See the `examples`_ folder for additional examples.

Command line tool
-----------------

The shell subcommand
^^^^^^^^^^^^^^^^^^^^

Use the command line shell to convert data between given formats. The
default input codec is BER and output codec is GSER (produces human
readable text).

.. code-block:: text

   > asn1tools shell

   Welcome to the asn1tools shell!

   $ help
   Commands:
     compile
     convert
     exit
     help
   $ compile tests/files/foo.asn
   $ convert Question 300e0201011609497320312b313d333f
   question Question ::= {
       id 1,
       question "Is 1+1=3?"
   }
   $ compile --output-codec xer tests/files/foo.asn
   $ convert Question 300e0201011609497320312b313d333f
   <Question>
       <id>1</id>
       <question>Is 1+1=3?</question>
   </Question>
   $ compile -o uper tests/files/foo.asn
   $ convert Question 300e0201011609497320312b313d333f
   01010993cd03156c5eb37e
   $ exit
   >

The convert subcommand
^^^^^^^^^^^^^^^^^^^^^^

Convert given encoded Question from BER to GSER (produces human
readable text).

.. code-block:: text

   > asn1tools convert tests/files/foo.asn Question 300e0201011609497320312b313d333f
   question Question ::= {
       id 1,
       question "Is 1+1=3?"
   }
   >

Convert given encoded Question from UPER to XER (xml).

.. code-block:: text

   > asn1tools convert -i uper -o xer tests/files/foo.asn Question 01010993cd03156c5eb37e
   <Question>
       <id>1</id>
       <question>Is 1+1=3?</question>
   </Question>
   >

Convert given encoded Question from UPER to JER (json).

.. code-block:: text

   > asn1tools convert -i uper -o jer tests/files/foo.asn Question 01010993cd03156c5eb37e
   {
       "id": 1,
       "question": "Is 1+1=3?"
   }
   >

Continuously convert encoded Questions read from standard input. Any
line that cannot be converted is printed as is, in this example the
dates.

.. code-block:: text

   > cat encoded.txt
   2018-02-24 11:22:09
   300e0201011609497320312b313d333f
   2018-02-24 11:24:15
   300e0201021609497320322b323d353f
   > cat encoded.txt | asn1tools convert tests/files/foo.asn Question -
   2018-02-24 11:22:09
   question Question ::= {
       id 1,
       question "Is 1+1=3?"
   }
   2018-02-24 11:24:15
   question Question ::= {
       id 2,
       question "Is 2+2=5?"
   }
   >

Contributing
============

#. Fork the repository.

#. Install prerequisites.

   .. code-block:: text

      pip install -r requirements.txt

#. Implement the new feature or bug fix.

#. Implement test case(s) to ensure that future changes do not break
   legacy.

#. Run the tests.

   .. code-block:: text

      make test

#. Create a pull request.

Specifications
==============

ASN.1 specifications released by ITU and IETF.

General
-------

- `X.680: Specification of basic notation
  <https://www.itu.int/ITU-T/studygroups/com17/languages/X.680-0207.pdf>`_

- `X.681: Information object specification
  <https://www.itu.int/ITU-T/studygroups/com17/languages/X.681-0207.pdf>`_

- `X.682: Constraint specification
  <https://www.itu.int/ITU-T/studygroups/com17/languages/X.682-0207.pdf>`_

- `X.683: Parameterization of ASN.1 specifications
  <https://www.itu.int/ITU-T/studygroups/com17/languages/X.683-0207.pdf>`_

Encodings
---------

- `X.690: Specification of Basic Encoding Rules (BER), Canonical
  Encoding Rules (CER) and Distinguished Encoding Rules (DER)
  <https://www.itu.int/ITU-T/studygroups/com17/languages/X.690-0207.pdf>`_

- `X.691: Specification of Packed Encoding Rules (PER)
  <https://www.itu.int/ITU-T/studygroups/com17/languages/X.691-0207.pdf>`_

- `X.693: XML Encoding Rules (XER)
  <https://www.itu.int/ITU-T/studygroups/com17/languages/X.693-0112.pdf>`_

- `RFC 3641: Generic String Encoding Rules (GSER) for ASN.1
  <https://tools.ietf.org/html/rfc3641>`_

- `Overview of the JSON Encoding Rules (JER)
  <http://www.oss.com/asn1/resources/asn1-papers/Overview_of_JER.pdf>`_

.. |buildstatus| image:: https://travis-ci.org/eerimoq/asn1tools.svg?branch=master
.. _buildstatus: https://travis-ci.org/eerimoq/asn1tools

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/asn1tools/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/asn1tools

.. _ASN.1: https://en.wikipedia.org/wiki/Abstract_Syntax_Notation_One

.. _Compile: http://asn1tools.readthedocs.io/en/latest/#asn1tools.compile_files
.. _encode: http://asn1tools.readthedocs.io/en/latest/#asn1tools.compiler.Specification.encode
.. _decode: http://asn1tools.readthedocs.io/en/latest/#asn1tools.compiler.Specification.decode
.. _examples: https://github.com/eerimoq/asn1tools/tree/master/examples
