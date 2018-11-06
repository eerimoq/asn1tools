#!/usr/bin/env python

"""Example execution:

$ ./main.py
Encoded: 300e8001018109497320312b313d333f
Decoded: {'id': 1, 'question': 'Is 1+1=3?'}
$

"""

import os
import binascii
import asn1tools


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
MY_PROTOCOL_ASN_PATH = os.path.realpath(
    os.path.join(SCRIPT_DIR, 'my_protocol.asn'))
PROGRAMMING_TYPES_ASN_PATH = os.path.realpath(
    os.path.join(SCRIPT_DIR, 'programming_types.asn'))

my_protocol = asn1tools.compile_files([
    MY_PROTOCOL_ASN_PATH,
    PROGRAMMING_TYPES_ASN_PATH
])

encoded = my_protocol.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
print('Encoded:', binascii.hexlify(encoded).decode('ascii'))

decoded = my_protocol.decode('Question', encoded)
print('Decoded:', decoded)
