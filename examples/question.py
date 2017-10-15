#!/usr/bin/env python

"""Encoding and decoding of a question once for each codec.

"""

from __future__ import print_function
import os
from binascii import hexlify
import asn1tools

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FOO_ASN_PATH = os.path.join(SCRIPT_DIR, '..', 'tests', 'files', 'foo.asn')

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
