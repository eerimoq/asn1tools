#!/usr/bin/env python

"""Encoding and decoding of a question once for each codec.

"""

from __future__ import print_function
import sys
sys.path.insert(0, '..')
import asn1tools
from binascii import hexlify

# Print the specification.
print('ASN.1 specification:')
print()

with open('../tests/files/foo.asn') as fin:
    print(fin.read())

# The question to encode.
question = {'id': 1, 'question': 'Is 1+1=3?'}

print("Question to encode: {}".format(question))

# Encode and decode the question once for each codec.
for codec in ['ber', 'der', 'per', 'uper']:
    foo = asn1tools.compile_file('../tests/files/foo.asn', codec)
    encoded = foo.encode('Question', question)
    decoded = foo.decode('Question', encoded)

    print()
    print('{}:'.format(codec.upper()))
    print('Encoded: {} ({} bytes)'.format(hexlify(encoded).decode('ascii'),
                                          len(encoded)))
    print('Decoded: {}'.format(decoded))
