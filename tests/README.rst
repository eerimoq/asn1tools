Unit tests
==========

There are a bunch of unit tests to ensure a decent quality of
asn1tools.

Below is a short description of each test suite.

test_{ber,der,gser,jer,oer,per,uper,xer}.py
-------------------------------------------

Codec specific encoding and decoding tests, as the codecs have
different sets of visible constraints which affects the
encoding. PER/UPER/OER uses constraints to make a compact encoding,
while XER/JER/BER/DER/GSER does not. The idea is to test relevant
constructs for each codec.

test_codecs_consistency.py
--------------------------

Tests that all codecs have a common behaviour. Lately common/basic
ASN.1 constructs are encoded and decoded for all codecs in the same
file. The plan is to create a new file, test_all_codecs.py, and move
the encoding/decoding tests there.

test_parse.py
-------------

This file tests the frontend parser module, and verifies that the
ASN.1-files are correctly converted to the internal Python format.

test_compile.py
---------------

Tests the pre processing compilation step and various compilation
errors that are codec independent.

test_command_line.py
--------------------

Tests the command line interface.

test_constraints_checker.py
---------------------------

Tests the constraints checker module.

test_type_checker.py
--------------------

Tests the type checker module.

test_codecs.py
--------------

Tests various utility functions in the codecs module.
