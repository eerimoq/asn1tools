#!/usr/bin/env python

"""A performance example comparing the performance of all codecs.

Example execution:

$ ./codecs.py
Starting encoding and decoding of a message 3000 times. This may take a few seconds.

Encoding the message 3000 times took:

CODEC      SECONDS
jer        0.113198
ber        0.173475
der        0.176935
oer        0.226752
uper       0.326678
per        0.350619
xer        0.476867

Decoding the message 3000 times took:

CODEC      SECONDS
jer        0.166447
ber        0.277560
xer        0.308562
der        0.309008
oer        0.311870
uper       0.383907
per        0.396227
$

"""

from __future__ import print_function

from datetime import datetime
import timeit
import asn1tools

ITERATIONS = 3000


def encode_decode(codec):
    spec = asn1tools.compile_string(
        'Ber DEFINITIONS ::= BEGIN '
        '  A ::= SEQUENCE { '
        '    a BOOLEAN, '
        '    b INTEGER, '
#        '    c REAL, '
        '    d NULL, '
        '    e BIT STRING, '
        '    f OCTET STRING, '
        '    g OBJECT IDENTIFIER, '
        '    h ENUMERATED {a, b}, '
        '    i SEQUENCE {}, '
        '    j SEQUENCE OF NULL, '
        '    k SET {}, '
        '    l SET OF NULL, '
        '    m CHOICE {a NULL}, '
        '    n UTF8String, '
        '    o UTCTime, '
        '    p GeneralizedTime '
        '} '
        'END',
        codec)

    decoded = {
        'a': True,
        'b': 12345678,
        # 'c': 3.14159,
        'd': None,
        'e': (b'\x11\x22\x33\x44\x55\x66\x77', 55),
        'f': 10 * b'x11\x22\x33\x44\x55\x66\x77',
        'g': '1.4.123.4325.23.1.44.22222',
        'h': 'b',
        'i': {},
        'j': 5 * [None],
        'k': {},
        'l': 5 * [None],
        'm': ('a', None),
        'n': 40 * 'a',
        'o': datetime(2018, 6, 13, 11, 1, 59),
        'p': datetime(2018, 6, 13, 11, 1, 58, 5000)
    }

    try:
        encoded = spec.encode('A', decoded)
    except:
        return float('inf'), float('inf')

    def encode():
        spec.encode('A', decoded)

    def decode():
        spec.decode('A', encoded)

    encode_time = timeit.timeit(encode, number=ITERATIONS)
    decode_time = timeit.timeit(decode, number=ITERATIONS)

    return encode_time, decode_time


print('Starting encoding and decoding of a message {} times. This may '
      'take a few seconds.'.format(ITERATIONS))

ber_encode_time, ber_decode_time = encode_decode('ber')
der_encode_time, der_decode_time = encode_decode('der')
jer_encode_time, jer_decode_time = encode_decode('jer')
oer_encode_time, oer_decode_time = encode_decode('oer')
per_encode_time, per_decode_time = encode_decode('per')
uper_encode_time, uper_decode_time = encode_decode('uper')
xer_encode_time, xer_decode_time = encode_decode('xer')

# Encode comparison output.
measurements = [
    ('ber', ber_encode_time),
    ('der', der_encode_time),
    ('jer', jer_encode_time),
    ('oer', oer_encode_time),
    ('per', per_encode_time),
    ('uper', uper_encode_time),
    ('xer', xer_encode_time)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print('Encoding the message {} times took:'.format(ITERATIONS))
print()
print('CODEC      SECONDS')

for package, seconds in measurements:
    print('{:10s} {:f}'.format(package, seconds))

# Decode comparison output.
measurements = [
    ('ber', ber_decode_time),
    ('der', der_decode_time),
    ('jer', jer_decode_time),
    ('oer', oer_decode_time),
    ('per', per_decode_time),
    ('uper', uper_decode_time),
    ('xer', xer_decode_time)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print('Decoding the message {} times took:'.format(ITERATIONS))
print()
print('CODEC      SECONDS')

for package, seconds in measurements:
    print('{:10s} {:f}'.format(package, seconds))
