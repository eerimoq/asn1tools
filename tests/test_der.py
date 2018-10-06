#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
from copy import deepcopy
from datetime import datetime
from .utils import Asn1ToolsBaseTest

import asn1tools
from asn1tools.codecs import restricted_utc_time_to_datetime as ut2dt
from asn1tools.codecs import restricted_generalized_time_to_datetime as gt2dt
from asn1tools.compat import timezone
from asn1tools.compat import timedelta

sys.path.append('tests/files/ietf')

from rfc5280 import EXPECTED as RFC5280


class Asn1ToolsDerTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_external(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= EXTERNAL "
            "END",
            'der')

        datas = [
            ('A',
             {'encoding': ('octet-aligned', b'\x12')},
             b'\x28\x03\x81\x01\x12')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_real(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= REAL "
            "END")

        datas = [
            ('A',                 0.0, b'\x09\x00'),
            ('A',               100.0, b'\x09\x03\x80\x02\x19'),
            ('A',              -100.0, b'\x09\x03\xc0\x02\x19'),
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Decode 100.0 in decimal form (1.e2).
        self.assertEqual(foo.decode('A', b'\x09\x05\x03\x31\x2e\x45\x32'),
                         100.0)

    def test_bit_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BIT STRING "
            "B ::= BIT STRING { "
            "  a (0), "
            "  b (1), "
            "  c (2) "
            "} "
            "C ::= SEQUENCE { "
            "  a B DEFAULT {b, c}, "
            "  b B DEFAULT '011'B, "
            "  c B DEFAULT '60'H "
            "} "
            "D ::= SEQUENCE { "
            "  a A DEFAULT '00'B, "
            "  b B DEFAULT '00'B "
            "} "
            "END",
            'der')

        datas = [
            ('A',              (b'', 0), b'\x03\x01\x00'),
            ('A',          (b'\x40', 4), b'\x03\x02\x04\x40'),
            ('A',          (b'\x80', 1), b'\x03\x02\x07\x80'),
            ('A',      (b'\x00\x00', 9), b'\x03\x03\x07\x00\x00'),
            ('B',          (b'\x80', 1), b'\x03\x02\x07\x80'),
            ('B',          (b'\xe0', 3), b'\x03\x02\x05\xe0'),
            ('B',          (b'\x01', 8), b'\x03\x02\x00\x01'),
            ('C',
             {'a': (b'\x40', 2), 'b': (b'\x40', 2), 'c': (b'\x40', 2)},
             b'\x30\x0c\x80\x02\x06\x40\x81\x02\x06\x40\x82\x02\x06\x40'),
            ('C',
             {'a': (b'\x60', 3), 'b': (b'\x60', 3), 'c': (b'\x60', 3)},
             b'\x30\x00'),
            ('D',
             {'a': (b'\x00', 2), 'b': (b'\x00', 2)},
             b'\x30\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Default value is not encoded, but part of decoded. Also
        # ignore dangling bits.
        datas = [
            ('C',
             {},
             b'\x30\x00',
             {'a': (b'\x60', 3), 'b': (b'\x60', 3), 'c': (b'\x60', 3)}),
            ('C',
             {'a': (b'\x60', 4), 'b': (b'\x60', 5), 'c': (b'\x60', 6)},
             b'\x30\x00',
             {'a': (b'\x60', 3), 'b': (b'\x60', 3), 'c': (b'\x60', 3)}),
            ('A',     (b'\xff', 1), b'\x03\x02\x07\x80', (b'\x80', 1)),
            ('D',
             {'a': (b'\x00', 3), 'b': (b'\x00', 3)},
             b'\x30\x04\x80\x02\x05\x00',
             {'a': (b'\x00', 3), 'b': (b'\x00', 2)})
        ]

        for type_name, decoded_1, encoded, decoded_2 in datas:
            self.assertEqual(foo.encode(type_name, decoded_1), encoded)
            self.assertEqual(foo.decode(type_name, encoded), decoded_2)

    def test_set(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS IMPLICIT TAGS ::= "
            "BEGIN "
            "A ::= SET { "
            "  a [0] INTEGER, "
            "  b [1] INTEGER "
            "} "
            "B ::= SET { "
            "  b [1] INTEGER, "
            "  a [0] INTEGER "
            "} "
            "END",
            'ber')

        datas = [
            ('A',     {'a': 3, 'b': 4}, b'\x31\x06\x80\x01\x03\x81\x01\x04'),
            ('B',     {'a': 3, 'b': 4}, b'\x31\x06\x80\x01\x03\x81\x01\x04')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_utf8_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTF8String "
            "END",
            'der')

        datas = [
            ('A',                u'bar', b'\x0c\x03\x62\x61\x72'),
            ('A',           u'a\u1010c', b'\x0c\x05\x61\xe1\x80\x90\x63')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_graphic_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GraphicString "
            "END")

        datas = [
            ('A', 'f', b'\x19\x01\x66')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_universal_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UniversalString "
            "END",
            'der')

        datas = [
            ('A',   'bar', b'\x1c\x0c\x00\x00\x00b\x00\x00\x00a\x00\x00\x00r'),
            ('A',
             u'åäö',
             b'\x1c\x0c\x00\x00\x00\xe5\x00\x00\x00\xe4\x00\x00\x00\xf6')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_utc_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTCTime "
            "END",
            'der')

        datas = [
            ('A',
             datetime(2018, 1, 22, 13, 0),
             b'\x17\x0d\x31\x38\x30\x31\x32\x32\x31\x33\x30\x30\x30\x30\x5a'),
            ('A',
             datetime(2001, 2, 3, 4, 5, 6),
             b'\x17\x0d\x30\x31\x30\x32\x30\x33\x30\x34\x30\x35\x30\x36\x5a')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_generalized_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GeneralizedTime "
            "END",
            'der')

        datas = [
            ('A',
             datetime(2018, 1, 22, 13, 29),
             b'\x18\x0f\x32\x30\x31\x38\x30\x31\x32\x32\x31\x33\x32\x39\x30'
             b'\x30\x5a'),
            ('A',
             datetime(2018, 1, 22, 13, 0),
             b'\x18\x0f\x32\x30\x31\x38\x30\x31\x32\x32\x31\x33\x30\x30\x30'
             b'\x30\x5a'),
            ('A',
             datetime(2000, 12, 31, 23, 59, 59),
             b'\x18\x0f\x32\x30\x30\x30\x31\x32\x33\x31\x32\x33\x35\x39'
             b'\x35\x39\x5a'),
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn', 'der')

        datas = [
            ('Boolean',                 True, b'\x01\x01\xff'),
            ('Boolean',                False, b'\x01\x01\x00'),
            ('Integer',                32768, b'\x02\x03\x00\x80\x00'),
            ('Integer',                32767, b'\x02\x02\x7f\xff'),
            ('Integer',                  256, b'\x02\x02\x01\x00'),
            ('Integer',                  255, b'\x02\x02\x00\xff'),
            ('Integer',                  128, b'\x02\x02\x00\x80'),
            ('Integer',                  127, b'\x02\x01\x7f'),
            ('Integer',                    1, b'\x02\x01\x01'),
            ('Integer',                    0, b'\x02\x01\x00'),
            ('Integer',                   -1, b'\x02\x01\xff'),
            ('Integer',                 -128, b'\x02\x01\x80'),
            ('Integer',                 -129, b'\x02\x02\xff\x7f'),
            ('Integer',                 -256, b'\x02\x02\xff\x00'),
            ('Integer',               -32768, b'\x02\x02\x80\x00'),
            ('Integer',               -32769, b'\x02\x03\xff\x7f\xff'),
            ('Bitstring',       (b'\x80', 1), b'\x03\x02\x07\x80'),
            ('Octetstring',          b'\x00', b'\x04\x01\x00'),
            ('Octetstring',    127 * b'\x55', b'\x04\x7f' + 127 * b'\x55'),
            ('Octetstring',    128 * b'\xaa', b'\x04\x81\x80' + 128 * b'\xaa'),
            ('Null',                    None, b'\x05\x00'),
            ('Objectidentifier',       '1.2', b'\x06\x01\x2a'),
            ('Enumerated',             'one', b'\x0a\x01\x01'),
            ('Utf8string',             'foo', b'\x0c\x03foo'),
            ('Sequence',                  {}, b'\x30\x00'),
            ('Sequence2',           {'a': 0}, b'\x30\x00'),
            ('Sequence2',           {'a': 1}, b'\x30\x03\x02\x01\x01'),
            ('Sequence13', {'a': [1]}, b'\x30\x05\xa0\x03\x02\x01\x01'),
            ('Sequence13', {'b': [1]}, b'\x30\x05\xa1\x03\x02\x01\x01'),
            ('Set',                       {}, b'\x31\x00'),
            ('Set2',                {'a': 1}, b'\x31\x00'),
            ('Set2',                {'a': 2}, b'\x31\x03\x02\x01\x02'),
            ('Numericstring',          '123', b'\x12\x03123'),
            ('Printablestring',        'foo', b'\x13\x03foo'),
            ('Ia5string',              'bar', b'\x16\x03bar'),
            ('Visiblestring',          'bar', b'\x1a\x03bar'),
            ('Generalstring',          'bar', b'\x1b\x03bar'),
            ('Bmpstring',
             'bar',
             b'\x1e\x06\x00\x62\x00\x61\x00\x72'),
            ('Teletexstring',          'fum', b'\x14\x03fum'),
            ('SequenceOf',                [], b'0\x00'),
            ('SetOf',                     [], b'1\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

        all_types.encode('Sequence12', {'a': [{'a': []}]})

        # ToDo: Should return {'a': [{'a': []}]}
        self.assertEqual(
            all_types.decode('Sequence12', b'\x30\x04\xa0\x02\x30\x00'),
            {})

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'der')

        self.assertEqual(repr(all_types.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(all_types.types['Integer']), 'Integer(Integer)')
        self.assertEqual(repr(all_types.types['Real']), 'Real(Real)')
        self.assertEqual(repr(all_types.types['Bitstring']), 'BitString(Bitstring)')
        self.assertEqual(repr(all_types.types['Octetstring']), 'OctetString(Octetstring)')
        self.assertEqual(repr(all_types.types['Null']), 'Null(Null)')
        self.assertEqual(repr(all_types.types['Objectidentifier']),
                         'ObjectIdentifier(Objectidentifier)')
        self.assertEqual(repr(all_types.types['Enumerated']), 'Enumerated(Enumerated)')
        self.assertEqual(repr(all_types.types['Utf8string']), 'UTF8String(Utf8string)')
        self.assertEqual(repr(all_types.types['Sequence']), 'Sequence(Sequence, [])')
        self.assertEqual(repr(all_types.types['Set']), 'Set(Set, [])')
        self.assertEqual(repr(all_types.types['Sequence2']),
                         'Sequence(Sequence2, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Set2']), 'Set(Set2, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Numericstring']),
                         'NumericString(Numericstring)')
        self.assertEqual(repr(all_types.types['Printablestring']),
                         'PrintableString(Printablestring)')
        self.assertEqual(repr(all_types.types['Ia5string']), 'IA5String(Ia5string)')
        self.assertEqual(repr(all_types.types['Universalstring']),
                         'UniversalString(Universalstring)')
        self.assertEqual(repr(all_types.types['Visiblestring']),
                         'VisibleString(Visiblestring)')
        self.assertEqual(repr(all_types.types['Generalstring']),
                         'GeneralString(Generalstring)')
        self.assertEqual(repr(all_types.types['Bmpstring']),
                         'BMPString(Bmpstring)')
        self.assertEqual(repr(all_types.types['Teletexstring']),
                         'TeletexString(Teletexstring)')
        self.assertEqual(repr(all_types.types['Graphicstring']),
                         'GraphicString(Graphicstring)')
        self.assertEqual(repr(all_types.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(all_types.types['GeneralizedTime1']),
                         'GeneralizedTime(GeneralizedTime1)')
        self.assertEqual(repr(all_types.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(all_types.types['SetOf']), 'SetOf(SetOf, Integer())')
        self.assertEqual(repr(all_types.types['Any']), 'Any(Any)')
        self.assertEqual(repr(all_types.types['Sequence12']),
                         'Sequence(Sequence12, [SequenceOf(a, Recursive(Sequence12))])')

    def test_all_types_automatic_tags(self):
        all_types = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn', 'der')

        datas = [
            ('Sequence3',
             {'a': 1, 'c': 2,'d': True},
             b'\x30\x09\x80\x01\x01\x82\x01\x02\x83\x01\xff')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'der')

        # The length can be decoded.
        datas = [
            (b'\x30\x0e\x02\x01\x01\x16\x09Is 1+1=3?',   16),
            (b'\x30\x10\x02\x02\x01\x16\x09Is 1+10=14?', 18),
            (b'\x30\x0d',                                15),
            (b'\x30\x84\x00\x00\x00\xb8',                190),
            (b'\x9f\x1f\x00', 3)
        ]

        for encoded_message, decoded_length in datas:
            length = foo.decode_length(encoded_message)
            self.assertEqual(length, decoded_length)

        # The length cannot be decoded.
        datas = [
            b'0',
            b'',
            b'0\x84\x00\x00\x00'
        ]

        for encoded in datas:
            self.assertIsNone(foo.decode_length(encoded))

    def test_long_tag(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS IMPLICIT TAGS ::= BEGIN "
            "A ::= [31] INTEGER "
            "B ::= [500] INTEGER "
            "END")

        datas = [
            ('A', 1, b'\x9f\x1f\x01\x01'),
            ('B', 1, b'\x9f\x83\x74\x01\x01')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_rfc5280(self):
        rfc5280 = asn1tools.compile_dict(deepcopy(RFC5280), 'der')

        decoded = {
            'tbsCertificate': {
                'version': 'v1',
                'serialNumber': 3578,
                'signature': {
                    'algorithm': '1.2.840.113549.1.1.5',
                    'parameters': b'\x05\x00'
                },
                'issuer': (
                    'rdnSequence',
                    [
                        [{'type': '2.5.4.6',
                          'value': b'\x13\x02\x4a\x50'}],
                        [{'type': '2.5.4.8',
                          'value': b'\x13\x05\x54\x6f\x6b\x79\x6f'}],
                        [{'type': '2.5.4.7',
                          'value': b'\x13\x07\x43\x68\x75\x6f\x2d\x6b\x75'}],
                        [{'type': '2.5.4.10',
                          'value': b'\x13\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'}],
                        [{'type': '2.5.4.11',
                          'value': (b'\x13\x0f\x57\x65\x62\x43\x65\x72\x74\x20\x53'
                                    b'\x75\x70\x70\x6f\x72\x74')}],
                        [{'type': '2.5.4.3',
                          'value': (b'\x13\x0f\x46\x72\x61\x6e\x6b\x34\x44\x44\x20'
                                    b'\x57\x65\x62\x20\x43\x41')}],
                        [{'type': '1.2.840.113549.1.9.1',
                          'value': (b'\x16\x14\x73\x75\x70\x70\x6f\x72\x74\x40\x66'
                                    b'\x72\x61\x6e\x6b\x34\x64\x64\x2e\x63\x6f\x6d')}]
                    ]
                ),
                'validity': {
                    'notAfter': ('utcTime', ut2dt('170821052654Z')),
                    'notBefore': ('utcTime', ut2dt('120822052654Z'))
                },
                'subject': (
                    'rdnSequence',
                    [
                        [{'type': '2.5.4.6',
                          'value': b'\x13\x02\x4a\x50'}],
                        [{'type': '2.5.4.8',
                          'value': b'\x0c\x05\x54\x6f\x6b\x79\x6f'}],
                        [{'type': '2.5.4.10',
                          'value': b'\x0c\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'}],
                        [{'type': '2.5.4.3',
                          'value': (b'\x0c\x0f\x77\x77\x77\x2e\x65\x78\x61\x6d\x70'
                                    b'\x6c\x65\x2e\x63\x6f\x6d')}]
                    ]
                ),
                'subjectPublicKeyInfo': {
                    'algorithm': {
                        'algorithm': '1.2.840.113549.1.1.1',
                        'parameters': b'\x05\x00'
                    },
                    'subjectPublicKey': (b'0H\x02A\x00\x9b\xfcf\x90y\x84B\xbb'
                                         b'\xab\x13\xfd+{\xf8\xde\x15\x12\xe5'
                                         b'\xf1\x93\xe3\x06\x8a{\xb8\xb1\xe1'
                                         b'\x9e&\xbb\x95\x01\xbf\xe70\xedd\x85'
                                         b'\x02\xdd\x15i\xa84\xb0\x06\xec?5<'
                                         b'\x1e\x1b+\x8f\xfa\x8f\x00\x1b\xdf'
                                         b'\x07\xc6\xacS\x07\x02\x03\x01\x00'
                                         b'\x01',
                                         592)
                }
            },
            'signatureAlgorithm': {
                'algorithm': '1.2.840.113549.1.1.5',
                'parameters': b'\x05\x00'
            },
            'signature': (b'\x14\xb6L\xbb\x81y3\xe6q\xa4\xdaQo\xcb\x08\x1d'
                          b'\x8d`\xec\xbc\x18\xc7sGY\xb1\xf2 H\xbba\xfa'
                          b'\xfcM\xad\x89\x8d\xd1!\xeb\xd5\xd8\xe5\xba'
                          b'\xd6\xa66\xfdtP\x83\xb6\x0f\xc7\x1d\xdf}\xe5.\x81'
                          b'\x7fE\xe0\x9f\xe2>y\xee\xd701\xc7 r\xd9X.*\xfe\x12'
                          b'Z4E\xa1\x19\x08|\x89G_J\x95\xbe#!JSr\xda*\x05/.\xc9'
                          b'p\xf6[\xfa\xfd\xdf\xb41\xb2\xc1J\x9c\x06%C\xa1'
                          b'\xe6\xb4\x1e\x7f\x86\x9b\x16@',
                          1024)
        }

        encoded = (
            b'\x30\x82\x02\x12\x30\x82\x01\x7b\x02\x02\x0d\xfa\x30\x0d\x06\x09'
            b'\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05\x05\x00\x30\x81\x9b\x31\x0b'
            b'\x30\x09\x06\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06'
            b'\x03\x55\x04\x08\x13\x05\x54\x6f\x6b\x79\x6f\x31\x10\x30\x0e\x06'
            b'\x03\x55\x04\x07\x13\x07\x43\x68\x75\x6f\x2d\x6b\x75\x31\x11\x30'
            b'\x0f\x06\x03\x55\x04\x0a\x13\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'
            b'\x31\x18\x30\x16\x06\x03\x55\x04\x0b\x13\x0f\x57\x65\x62\x43\x65'
            b'\x72\x74\x20\x53\x75\x70\x70\x6f\x72\x74\x31\x18\x30\x16\x06\x03'
            b'\x55\x04\x03\x13\x0f\x46\x72\x61\x6e\x6b\x34\x44\x44\x20\x57\x65'
            b'\x62\x20\x43\x41\x31\x23\x30\x21\x06\x09\x2a\x86\x48\x86\xf7\x0d'
            b'\x01\x09\x01\x16\x14\x73\x75\x70\x70\x6f\x72\x74\x40\x66\x72\x61'
            b'\x6e\x6b\x34\x64\x64\x2e\x63\x6f\x6d\x30\x1e\x17\x0d\x31\x32\x30'
            b'\x38\x32\x32\x30\x35\x32\x36\x35\x34\x5a\x17\x0d\x31\x37\x30\x38'
            b'\x32\x31\x30\x35\x32\x36\x35\x34\x5a\x30\x4a\x31\x0b\x30\x09\x06'
            b'\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06\x03\x55\x04'
            b'\x08\x0c\x05\x54\x6f\x6b\x79\x6f\x31\x11\x30\x0f\x06\x03\x55\x04'
            b'\x0a\x0c\x08\x46\x72\x61\x6e\x6b\x34\x44\x44\x31\x18\x30\x16\x06'
            b'\x03\x55\x04\x03\x0c\x0f\x77\x77\x77\x2e\x65\x78\x61\x6d\x70\x6c'
            b'\x65\x2e\x63\x6f\x6d\x30\x5c\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7'
            b'\x0d\x01\x01\x01\x05\x00\x03\x4b\x00\x30\x48\x02\x41\x00\x9b\xfc'
            b'\x66\x90\x79\x84\x42\xbb\xab\x13\xfd\x2b\x7b\xf8\xde\x15\x12\xe5'
            b'\xf1\x93\xe3\x06\x8a\x7b\xb8\xb1\xe1\x9e\x26\xbb\x95\x01\xbf\xe7'
            b'\x30\xed\x64\x85\x02\xdd\x15\x69\xa8\x34\xb0\x06\xec\x3f\x35\x3c'
            b'\x1e\x1b\x2b\x8f\xfa\x8f\x00\x1b\xdf\x07\xc6\xac\x53\x07\x02\x03'
            b'\x01\x00\x01\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05'
            b'\x05\x00\x03\x81\x81\x00\x14\xb6\x4c\xbb\x81\x79\x33\xe6\x71\xa4'
            b'\xda\x51\x6f\xcb\x08\x1d\x8d\x60\xec\xbc\x18\xc7\x73\x47\x59\xb1'
            b'\xf2\x20\x48\xbb\x61\xfa\xfc\x4d\xad\x89\x8d\xd1\x21\xeb\xd5\xd8'
            b'\xe5\xba\xd6\xa6\x36\xfd\x74\x50\x83\xb6\x0f\xc7\x1d\xdf\x7d\xe5'
            b'\x2e\x81\x7f\x45\xe0\x9f\xe2\x3e\x79\xee\xd7\x30\x31\xc7\x20\x72'
            b'\xd9\x58\x2e\x2a\xfe\x12\x5a\x34\x45\xa1\x19\x08\x7c\x89\x47\x5f'
            b'\x4a\x95\xbe\x23\x21\x4a\x53\x72\xda\x2a\x05\x2f\x2e\xc9\x70\xf6'
            b'\x5b\xfa\xfd\xdf\xb4\x31\xb2\xc1\x4a\x9c\x06\x25\x43\xa1\xe6\xb4'
            b'\x1e\x7f\x86\x9b\x16\x40'
        )

        self.assert_encode_decode(rfc5280, 'Certificate', decoded, encoded)


if __name__ == '__main__':
    unittest.main()
