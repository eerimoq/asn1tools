#!/usr/bin/env python

"""Encoding and decoding of a question once for each codec.

Example execution:

$ ./question.py
ASN.1 specification:

-- A simple protocol taken from Wikipedia.

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

Question to encode: {'question': 'Is 1+1=3?', 'id': 1}

BER:
Encoded: 300e0201011609497320312b313d333f (16 bytes)
Decoded: {'question': 'Is 1+1=3?', 'id': 1}

DER:
Encoded: 300e0201011609497320312b313d333f (16 bytes)
Decoded: {'question': 'Is 1+1=3?', 'id': 1}

JER:
Encoded: 7b227175657374696f6e223a22497320312b313d333f222c226964223a317d (31 bytes)
Decoded: {'question': 'Is 1+1=3?', 'id': 1}

PER:
Encoded: 010109497320312b313d333f (12 bytes)
Decoded: {'question': 'Is 1+1=3?', 'id': 1}

UPER:
Encoded: 01010993cd03156c5eb37e (11 bytes)
Decoded: {'question': 'Is 1+1=3?', 'id': 1}

XER:
Encoded: 3c5175657374696f6e3e3c69643e313c2f69643e3c7175657374696f6e3e497320312b313d333f3c2f7175657374696f6e3e3c2f5175657374696f6e3e (61 bytes)
Decoded: {'question': 'Is 1+1=3?', 'id': 1}
$

"""

from __future__ import print_function
import os
from binascii import hexlify
import asn1tools
from foo_pb2 import Question

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FOO_ASN_PATH = os.path.join(SCRIPT_DIR, '..', '..', 'tests', 'files', 'foo.asn')

# Print the specification.
print('ASN.1 specification:')
print()

with open(FOO_ASN_PATH) as fin:
    print(fin.read())

# The question to encode.
question = {'id': 1, 'question': 'Is 1+1=3?'}

print("Question to encode: {}".format(question))

# Encode and decode the question once for each codec.
for codec in ['ber', 'der', 'jer', 'per', 'uper', 'xer']:
    foo = asn1tools.compile_files(FOO_ASN_PATH, codec)
    encoded = foo.encode('Question', question)
    decoded = foo.decode('Question', encoded)

    print()
    print('{}:'.format(codec.upper()))
    print('Encoded: {} ({} bytes)'.format(hexlify(encoded).decode('ascii'),
                                          len(encoded)))
    print('Decoded: {}'.format(decoded))


# Also encode using protocol buffers.
question = Question()
question.id = 1
question.question = 'Is 1+1=3?'

encoded = question.SerializeToString()
decoded = question

print()
print('Protocol Buffers:')
print('Encoded: {} ({} bytes)'.format(hexlify(encoded).decode('ascii'),
                                      len(encoded)))
print('Decoded:')
print(decoded)
