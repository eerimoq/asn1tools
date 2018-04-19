#!/usr/bin/env python

from __future__ import print_function
from binascii import hexlify
import asn1tools


SPECIFICATION = '''
HelloWorld DEFINITIONS ::= BEGIN

    Message ::= SEQUENCE {
        number      INTEGER,
        text        UTF8String
    }

END
'''

hello_world = asn1tools.compile_string(SPECIFICATION, 'uper')

message = {'number': 2, 'text': u'Hi!'}
encoded = hello_world.encode('Message', message)
decoded = hello_world.decode('Message', encoded)

print('Message:', message)
print('Encoded:', hexlify(encoded).decode('ascii'))
print('Decoded:', decoded)
