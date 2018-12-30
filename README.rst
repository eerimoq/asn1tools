|buildstatus|_
|coverage|_

About
=====

A Python package for `ASN.1`_ parsing, encoding and decoding.

This project is *under development* and does only support a subset
of the ASN.1 specification syntax.

Supported codecs:

- Basic Encoding Rules (BER)
- Distinguished Encoding Rules (DER)
- Generic String Encoding Rules (GSER)
- JSON Encoding Rules (JER)
- Basic Octet Encoding Rules (OER)
- Aligned Packed Encoding Rules (PER)
- Unaligned Packed Encoding Rules (UPER)
- XML Encoding Rules (XER)

Miscellaneous features:

- `C` source code generator (with lots of restrictions).

Project homepage: https://github.com/eerimoq/asn1tools

Documentation: http://asn1tools.readthedocs.org/en/latest

Known limitations
=================

- The ``CLASS`` keyword (X.681) and its friends are not yet supported.

- Parametrization (X.683) is not yet supported.

- The ``EMBEDDED PDV`` type is not yet supported.

- The ``ANY`` and ``ANY DEFINED BY`` types are not supported. They
  were removed from the ASN.1 standard 1994.

- ``WITH COMPONENT`` and ``WITH COMPONENTS`` constraints are ignored,
  except for OER ``REAL``.

- The ``DURATION`` type is not yet supported.

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

The convert subcommand with a cache
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Convert given encoded PCCH-Message from UPER to GSER with the
``--cache-dir`` option set to ``my_cache``. Using a cache
significantly reduces the command execution time after the first call.

.. code-block:: text

   > time asn1tools convert --cache-dir my_cache -i uper tests/files/3gpp/rrc_8_6_0.asn PCCH-Message 28
   pcch-message PCCH-Message ::= {
       message c1 : paging : {
           systemInfoModification true,
           nonCriticalExtension {
           }
       }
   }

   real    0m2.090s
   user    0m1.977s
   sys     0m0.032s
   > time asn1tools convert --cache-dir my_cache -i uper tests/files/3gpp/rrc_8_6_0.asn PCCH-Message 28
   pcch-message PCCH-Message ::= {
       message c1 : paging : {
           systemInfoModification true,
           nonCriticalExtension {
           }
       }
   }

   real    0m0.276s
   user    0m0.197s
   sys     0m0.026s
   >

The parse subcommand
^^^^^^^^^^^^^^^^^^^^

Parse given ASN.1 specification and write it as a Python dictionary to
given file. Use the created file to convert given encoded Question
from BER to GSER (produces human readable text). The conversion is
significantly faster than passing .asn-file(s) to the convert
subcommand, especially for larger ASN.1 specifications.

.. code-block:: text

   > asn1tools parse tests/files/foo.asn foo.py
   > asn1tools convert foo.py Question 300e0201011609497320312b313d333f
   question Question ::= {
       id 1,
       question "Is 1+1=3?"
   }
   >

The generate C source subcommand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generate OER or UPER C source code from an ASN.1 specification.

**NOTE**: The UPER generator is not yet implemented!!!

The OER and UPER generators supports the ASN.1 types ``BOOLEAN``,
``INTEGER``, ``NULL``, ``OCTET STRING``, ``ENUMERATED``, ``SEQUENCE``,
``SEQUENCE OF``, and ``CHOICE``. The OER generator also supports
``REAL``.

No dynamic memory is used in the generated code. To achieve this all
types in the ASN.1 specification must have a known maximum size,
i.e. ``INTEGER (0..7)``, ``OCTET STRING (SIZE(12))``, etc.

Known lmitations:

- All types must have a known maximum size, i.e. ``INTEGER (0..7)``,
  ``OCTET STRING (SIZE(12))``.

- ``INTEGER`` must be 64 bits or less.

- ``REAL`` must be IEEE 754 binary32 or binary64. binary32 is
  generated as ``float`` and binary64 as ``double``.

- Extension additions (``...``) are not yet supported.

- Named numbers in ``ENUMERATED`` are not yet supported.

- ``CHOICE`` tags longer than one byte are not yet supported.

Below is an example generating OER C source code from two ASN.1
files.

.. code-block:: text

   > asn1tools generate_c_source --codec oer --namespace oer tests/files/c_source.asn examples/programming_types/programming_types.asn
   Successfully generated oer_c_source.h and oer_c_source.c.

See `oer_c_source.h`_ and `oer_c_source.c`_ for the contents of the
generated files.

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

- `X.696: Specification of Octet Encoding Rules (OER)
  <https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-X.696-201508-I!!PDF-E&type=items>`_

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

.. _oer_c_source.h: https://github.com/eerimoq/asn1tools/blob/master/tests/files/c_source/oer_c_source.h

.. _oer_c_source.c: https://github.com/eerimoq/asn1tools/blob/master/tests/files/c_source/oer_c_source.c
