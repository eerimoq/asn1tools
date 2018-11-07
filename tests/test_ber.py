#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import unittest
import timeit
import sys
from copy import deepcopy
from datetime import datetime
from .utils import Asn1ToolsBaseTest

import asn1tools
from asn1tools.codecs import utc_time_to_datetime as ut2dt
from asn1tools.compat import timezone
from asn1tools.compat import timedelta

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')
sys.path.append('tests/files/ietf')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from rfc4511 import EXPECTED as RFC4511
from rfc5280 import EXPECTED as RFC5280
from rfc5280_modified import EXPECTED as RFC5280_MODIFIED
from zforce import EXPECTED as ZFORCE
from enumerated import EXPECTED as ENUMERATED


class Asn1ToolsBerTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_boolean(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "END")

        datas = [
            ('A',  True, b'\x01\x01\xff'),
            ('A', False, b'\x01\x01\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_boolean_explicit_tags(self):
        """Test explicit tags on booleans.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] BOOLEAN END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', True, b'\xa2\x03\x01\x01\xff')

        # Bad explicit tag.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('Foo', b'\xa3\x03\x01\x01\x01')

        self.assertEqual(
            str(cm.exception),
            "Expected ExplicitTag with tag 'a2' at offset 0, but got 'a3'.")

        # Bad tag.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('Foo', b'\xa2\x03\x02\x01\x01')

        self.assertEqual(
            str(cm.exception),
            "Expected BOOLEAN with tag '01' at offset 2, but got '02'.")

    def test_boolean_implicit_tags(self):
        """Test implicit tags on booleans.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] IMPLICIT BOOLEAN END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', True, b'\x82\x01\xff')

    def test_integer(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "END")

        datas = [
            ('A',    32768, b'\x02\x03\x00\x80\x00'),
            ('A',    32767, b'\x02\x02\x7f\xff'),
            ('A',      256, b'\x02\x02\x01\x00'),
            ('A',      255, b'\x02\x02\x00\xff'),
            ('A',      128, b'\x02\x02\x00\x80'),
            ('A',      127, b'\x02\x01\x7f'),
            ('A',        1, b'\x02\x01\x01'),
            ('A',        0, b'\x02\x01\x00'),
            ('A',       -1, b'\x02\x01\xff'),
            ('A',     -128, b'\x02\x01\x80'),
            ('A',     -129, b'\x02\x02\xff\x7f'),
            ('A',     -256, b'\x02\x02\xff\x00'),
            ('A',   -32768, b'\x02\x02\x80\x00'),
            ('A',   -32769, b'\x02\x03\xff\x7f\xff')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_integer_explicit_tags(self):
        """Test explicit tags on integers.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] INTEGER END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', 1, b'\xa2\x03\x02\x01\x01')

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] EXPLICIT INTEGER END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', 1, b'\xa2\x03\x02\x01\x01')

        spec = 'Foo DEFINITIONS EXPLICIT TAGS ::= BEGIN Foo ::= INTEGER END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', 1, b'\x02\x01\x01')

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] BOOLEAN END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', True, b'\xa2\x03\x01\x01\xff')

    def test_integer_implicit_tags(self):
        """Test implicit tags on integers.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] IMPLICIT INTEGER END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', 1, b'\x82\x01\x01')

        spec = 'Foo DEFINITIONS IMPLICIT TAGS ::= BEGIN Foo ::= INTEGER END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', 1, b'\x02\x01\x01')

        spec = ('Foo DEFINITIONS EXPLICIT TAGS ::= BEGIN '
                'Foo ::= [2] IMPLICIT INTEGER END')
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', 1, b'\x82\x01\x01')

    def test_real(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= REAL "
            "END")

        datas = [
            ('A',                 0.0, b'\x09\x00'),
            ('A',                -0.0, b'\x09\x00'),
            ('A',        float('inf'), b'\x09\x01\x40'),
            ('A',       float('-inf'), b'\x09\x01\x41'),
            ('A',                 1.0, b'\x09\x03\x80\x00\x01'),
            ('A',               100.0, b'\x09\x03\x80\x02\x19'),
            ('A',              -100.0, b'\x09\x03\xc0\x02\x19'),
            ('A',           2 ** 1023, b'\x09\x04\x81\x03\xff\x01'),
            ('A',          2 ** -1022, b'\x09\x04\x81\xfc\x02\x01'),
            ('A',
             (2 ** 1023) * (1 + (1 - (2 ** -52))),
             b'\x09\x0a\x81\x03\xcb\x1f\xff\xff\xff\xff\xff\xff'),
            ('A',
             (2 ** -1022) * (1 - (2 ** -52)),
             b'\x09\x0a\x81\xfb\xce\x0f\xff\xff\xff\xff\xff\xff'),
            ('A',          2 ** -1074, b'\x09\x04\x81\xfb\xce\x01'),
            ('A',
             1.1,
             b'\x09\x09\x80\xcd\x08\xcc\xcc\xcc\xcc\xcc\xcd'),
            ('A',
             1234.5678,
             b'\x09\x09\x80\xd6\x13\x4a\x45\x6d\x5c\xfa\xad'),
            ('A',                   8, b'\x09\x03\x80\x03\x01'),
            ('A',               0.625, b'\x09\x03\x80\xfd\x05'),
            ('A',
             10000000000000000146306952306748730309700429878646550592786107871697963642511482159104,
             b'\x09\x0a\x81\x00\xe9\x02\x92\xe3\x2a\xc6\x85\x59'),
            ('A',
             0.00000000000000000000000000000000000000000000000000000000000000000000000000000000000001,
             b'\x09\x0a\x81\xfe\xae\x13\xe4\x97\x06\x5c\xd6\x1f'),
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # NaN cannot be compared.
        encoded = b'\x09\x01\x42'

        self.assertEqual(foo.encode('A', float('nan')), encoded)
        self.assertTrue(math.isnan(foo.decode('A', encoded)))

        # Minus zero.
        self.assertEqual(foo.decode('A', b'\x09\x01\x43'), -0.0)

        # Invalid control words.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x09\x01\x44')

        self.assertEqual(str(cm.exception),
                         'Unsupported special REAL control word 0x44.')

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x09\x02\x82\x00')

        self.assertEqual(str(cm.exception),
                         'Unsupported binary REAL control word 0x82.')

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
            "END")

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

    def test_bit_string_explicit_tags(self):
        """Test explicit tags on bit strings.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] BIT STRING END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', (b'\x56', 7), b'\xa2\x04\x03\x02\x01\x56')

    def test_octet_string_explicit_tags(self):
        """Test explicit tags on octet strings.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] OCTET STRING END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', b'\x56', b'\xa2\x03\x04\x01\x56')

    def test_object_descriptor(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= ObjectDescriptor "
            "B ::= [5] ObjectDescriptor "
            "END")

        datas = [
            ('A',    '1234', b'\x07\x04\x31\x32\x33\x34'),
            ('B',    '1234', b'\xa5\x06\x07\x04\x31\x32\x33\x34')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_external_explicit_tags(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= EXTERNAL "
            "B ::= [0] EXTERNAL "
            "END")

        datas = [
            ('A',
             {'encoding': ('octet-aligned', b'\x12')},
             b'\x28\x03\x81\x01\x12'),
            ('A',
             {
                 'data-value-descriptor': '12',
                 'encoding': ('octet-aligned', b'\x34')
             },
             b'\x28\x07\x07\x02\x31\x32\x81\x01\x34'),
            ('B',
             {'encoding': ('octet-aligned', b'\x12')},
             b'\xa0\x05\x28\x03\x81\x01\x12'),
            ('B',
             {
                 'data-value-descriptor': '12',
                 'encoding': ('octet-aligned', b'\x34')
             },
             b'\xa0\x09\x28\x07\x07\x02\x31\x32\x81\x01\x34')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_external_implicit_tags(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS IMPLICIT TAGS ::= "
            "BEGIN "
            "A ::= EXTERNAL "
            "B ::= [0] EXTERNAL "
            "END")

        datas = [
            ('A',
             {'encoding': ('octet-aligned', b'\x12')},
             b'\x28\x03\x81\x01\x12'),
            ('A',
             {
                 'data-value-descriptor': '12',
                 'encoding': ('octet-aligned', b'\x34')
             },
             b'\x28\x07\x07\x02\x31\x32\x81\x01\x34'),
            ('B',
             {'encoding': ('octet-aligned', b'\x12')},
             b'\xa0\x03\x81\x01\x12'),
            ('B',
             {
                 'data-value-descriptor': '12',
                 'encoding': ('octet-aligned', b'\x34')
             },
             b'\xa0\x07\x07\x02\x31\x32\x81\x01\x34')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_enumerated(self):
        foo = asn1tools.compile_dict(deepcopy(ENUMERATED))

        datas = [
            ('A', 'a', b'\x0a\x01\x00'),
            ('A', 'b', b'\x0a\x01\x01'),
            ('A', 'c', b'\x0a\x01\x02'),
            ('B', 'c', b'\x0a\x01\x00'),
            ('B', 'a', b'\x0a\x01\x01'),
            ('B', 'b', b'\x0a\x01\x02'),
            ('B', 'd', b'\x0a\x01\x03'),
            ('C', 'a', b'\x0a\x01\x00'),
            ('C', 'b', b'\x0a\x01\x01'),
            ('C', 'c', b'\x0a\x01\x03'),
            ('C', 'd', b'\x0a\x01\x04'),
            ('D', 'a', b'\x0a\x01\x00'),
            ('D', 'd', b'\x0a\x01\x01'),
            ('D', 'z', b'\x0a\x01\x19'),
            ('E', 'c', b'\x0a\x01\x00'),
            ('E', 'a', b'\x0a\x01\x01'),
            ('E', 'b', b'\x0a\x01\x02'),
            ('E', 'd', b'\x0a\x01\x03'),
            ('E', 'f', b'\x0a\x01\x04'),
            ('E', 'g', b'\x0a\x01\x05'),
            ('E', 'e', b'\x0a\x01\x19')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Unknown addition value.
        self.assertEqual(foo.decode('F', b'\x0a\x01\xff'), None)

        # No addition present.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('G', b'\x0a\x01\xff')

        self.assertEqual(str(cm.exception),
                         "Expected enumeration value 0, but got -1.")

    def test_sequence(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE {} "
            "B ::= SEQUENCE { "
            "  a INTEGER DEFAULT 0 "
            "} "
            "C ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ... "
            "} "
            "D ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]] "
            "} "
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  ... "
            "} "
            "F ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  ..., "
            "  c BOOLEAN "
            "} "
            "G ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  [[ "
            "  c BOOLEAN "
            "  ]], "
            "  ..., "
            "  d BOOLEAN "
            "} "
            "H ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  ... "
            "} "
            "I ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN "
            "} "
            "J ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN OPTIONAL "
            "} "
            "K ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN, "
            "  c BOOLEAN "
            "} "
            "L ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN, "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "M ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b SEQUENCE { "
            "    a INTEGER"
            "  } OPTIONAL, "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "N ::= SEQUENCE { "
            "  a BOOLEAN DEFAULT TRUE "
            "} "
            "O ::= SEQUENCE { "
            "  ..., "
            "  a BOOLEAN DEFAULT TRUE "
            "} "
            "P ::= SEQUENCE { "
            "  ..., "
            "  [[ "
            "  a BOOLEAN, "
            "  b BOOLEAN DEFAULT TRUE "
            "  ]] "
            "} "
            "Q ::= SEQUENCE { "
            "  a C, "
            "  b INTEGER "
            "} "
            "R ::= SEQUENCE { "
            "  a D, "
            "  b INTEGER "
            "} "
            "S ::= SEQUENCE { "
            "  a INTEGER OPTIONAL "
            "} "
            "T ::= SEQUENCE { "
            "  a T OPTIONAL "
            "} "
            "U ::= SEQUENCE { "
            "  a SEQUENCE OF U OPTIONAL "
            "} "
            "V ::= SEQUENCE { "
            "  a [1] V OPTIONAL, "
            "  b [2] V OPTIONAL, "
            "  c [3] SEQUENCE { "
            "    a [4] V "
            "  } OPTIONAL "
            "} "
            "END",
            'ber')

        datas = [
            ('A',                                {}, b'\x30\x00'),
            ('B',                          {'a': 0}, b'\x30\x00'),
            ('N',                       {'a': True}, b'\x30\x00'),
            ('P',                                {}, b'\x30\x00'),
            ('S',                                {}, b'\x30\x00'),
            ('T',                                {}, b'\x30\x00'),
            ('O',                       {'a': True}, b'\x30\x00'),
            ('T',                         {'a': {}}, b'\x30\x02\xa0\x00'),
            ('B',                          {'a': 1}, b'\x30\x03\x80\x01\x01'),
            ('C',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('D',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('E',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('H',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('I',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('J',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('K',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('L',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('M',                       {'a': True}, b'\x30\x03\x80\x01\xff'),
            ('N',                      {'a': False}, b'\x30\x03\x80\x01\x00'),
            ('O',                      {'a': False}, b'\x30\x03\x80\x01\x00'),
            ('P',            {'a': True, 'b': True}, b'\x30\x03\x80\x01\xff'),
            ('S',                          {'a': 1}, b'\x30\x03\x80\x01\x01'),
            ('U',                       {'a': [{}]}, b'\x30\x04\xa0\x02\x30\x00'),
            ('V',                  {'c': {'a': {}}}, b'\x30\x04\xa3\x02\xa4\x00'),
            ('P',
             {'a': True, 'b': False},
             b'\x30\x06\x80\x01\xff\x81\x01\x00'),
            ('D',
             {'a': True, 'b': True},
             b'\x30\x06\x80\x01\xff\x81\x01\xff'),
            ('E',
             {'a': True, 'b': True},
             b'\x30\x06\x80\x01\xff\x81\x01\xff'),
            ('F',
             {'a': True, 'c': True},
             b'\x30\x06\x80\x01\xff\x82\x01\xff'),
            ('G',
             {'a': True, 'd': True},
             b'\x30\x06\x80\x01\xff\x83\x01\xff'),
            ('I',
             {'a': True, 'b': True},
             b'\x30\x06\x80\x01\xff\x81\x01\xff'),
            ('J',
             {'a': True, 'b': True},
             b'\x30\x06\x80\x01\xff\x81\x01\xff'),
            ('K',
             {'a': True, 'b': True},
             b'\x30\x06\x80\x01\xff\x81\x01\xff'),
            ('F',
             {'a': True, 'b': True, 'c': True},
             b'\x30\x09\x80\x01\xff\x82\x01\xff\x81\x01\xff'),
            ('K',
             {'a': True, 'b': True, 'c': True},
             b'\x30\x09\x80\x01\xff\x81\x01\xff\x82\x01\xff'),
            ('L',
             {'a': True, 'b': True, 'c': True},
             b'\x30\x09\x80\x01\xff\x81\x01\xff\x82\x01\xff'),
            ('G',
             {'a': True, 'b': True, 'd': True},
             b'\x30\x09\x80\x01\xff\x83\x01\xff\x81\x01\xff'),
            ('G',
             {'a': True, 'b': True, 'c': True, 'd': True},
             b'\x30\x0c\x80\x01\xff\x83\x01\xff\x81\x01\xff\x82\x01\xff'),
            ('M',
             {'a': True, 'b': {'a': 5}, 'c': True},
             b'\x30\x0b\x80\x01\xff\xa1\x03\x80\x01\x05\x82\x01\xff'),
            ('Q',
             {'a': {'a': True}, 'b': 100},
             b'\x30\x08\xa0\x03\x80\x01\xff\x81\x01\x64'),
            ('R',
             {'a': {'a': True, 'b': True}, 'b': 100},
             b'\x30\x0b\xa0\x06\x80\x01\xff\x81\x01\xff\x81\x01\x64'),
            ('U',
             {'a': [{'a': []}]},
             b'\x30\x06\xa0\x04\x30\x02\xa0\x00'),
            ('V',
             {'a': {}, 'b': {}, 'c': {'a': {}}},
             b'\x30\x08\xa1\x00\xa2\x00\xa3\x02\xa4\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Non-symmetrical encoding and decoding because default values
        # are not encoded, but part of the decoded (given that the
        # root and addition is present).
        self.assertEqual(foo.encode('N', {}), b'\x30\x00')
        self.assertEqual(foo.decode('N', b'\x30\x00'), {'a': True})
        self.assertEqual(foo.encode('P', {'a': True}), b'\x30\x03\x80\x01\xff')
        self.assertEqual(foo.decode('P', b'\x30\x03\x80\x01\xff'),
                         {'a': True, 'b': True})

        # Decode D as C. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('C', b'\x30\x06\x80\x01\xff\x81\x01\xff'),
                         {'a': True})

        # Decode R as Q. Extension addition "a.b" should be skipped.
        self.assertEqual(
            foo.decode('Q',
                       b'\x30\x0b\xa0\x06\x80\x01\xff\x81\x01\xff\x81\x01\x64'),
            {'a': {'a': True}, 'b': 100})

        # Decode S with end-of-contentes octet , which is not yet
        # supported.
        with self.assertRaises(NotImplementedError) as cm:
            foo.decode('S', b'\x30\x80\x02\x01\x01\x00\x00')

        self.assertEqual(
            str(cm.exception),
            'Decode until an end-of-contents tag is not yet implemented.')

        # Missing member.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('C', {})

        self.assertEqual(str(cm.exception),
                         "Sequence member 'a' not found in {}.")

    def test_sequence_of(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE OF INTEGER "
            "END",
            'ber')

        datas = [
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        with self.assertRaises(NotImplementedError) as cm:
            foo.decode('A', b'\x30\x80\x00\x00')

        self.assertEqual(
            str(cm.exception),
            'Decode until an end-of-contents tag is not yet implemented.')

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

    def test_choice(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= CHOICE { "
            "  a BOOLEAN "
            "} "
            "B ::= CHOICE { "
            "  a BOOLEAN, "
            "  ... "
            "} "
            "C ::= CHOICE { "
            "  a BOOLEAN, "
            "  b INTEGER, "
            "  ..., "
            "  [[ "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "D ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  ... "
            "} "
            "E ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  [[ "
            "  c BOOLEAN "
            "  ]], "
            "  ... "
            "} "
            "F ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  ... "
            "} "
            "G ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN "
            "} "
            "H ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN, "
            "  c BOOLEAN "
            "} "
            "I ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN, "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "J ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b CHOICE { "
            "    a INTEGER"
            "  }, "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "K ::= CHOICE { "
            "  m1 NULL, "
            "  m2 NULL, "
            "  m3 NULL, "
            "  m4 NULL, "
            "  m5 NULL, "
            "  m6 NULL, "
            "  m7 NULL, "
            "  m8 NULL, "
            "  m9 NULL, "
            "  m10 NULL, "
            "  m11 NULL, "
            "  m12 NULL, "
            "  m13 NULL, "
            "  m14 NULL, "
            "  m15 NULL, "
            "  m16 NULL, "
            "  m17 NULL, "
            "  m18 NULL, "
            "  m19 NULL, "
            "  m20 NULL, "
            "  m21 NULL, "
            "  m22 NULL, "
            "  m23 NULL, "
            "  m24 NULL, "
            "  m25 NULL, "
            "  m26 NULL, "
            "  m27 NULL, "
            "  m28 NULL, "
            "  m29 NULL, "
            "  m30 NULL, "
            "  m31 NULL, "
            "  m32 NULL, "
            "  m33 NULL, "
            "  m34 NULL, "
            "  m35 NULL, "
            "  m36 NULL, "
            "  m37 NULL, "
            "  m38 NULL, "
            "  m39 NULL "
            "} "
            "L ::= CHOICE { "
            "  a OCTET STRING "
            "} "
            "M ::= CHOICE { "
            "  a CHOICE { "
            "    b BOOLEAN "
            "  } "
            "} "
            "END")

        datas = [
            ('A',            ('a', True), b'\x80\x01\xff'),
            ('B',            ('a', True), b'\x80\x01\xff'),
            ('C',            ('a', True), b'\x80\x01\xff'),
            ('C',               ('b', 1), b'\x81\x01\x01'),
            ('C',            ('c', True), b'\x82\x01\xff'),
            ('D',            ('a', True), b'\x80\x01\xff'),
            ('D',            ('b', True), b'\x81\x01\xff'),
            ('E',            ('a', True), b'\x80\x01\xff'),
            ('E',            ('b', True), b'\x81\x01\xff'),
            ('E',            ('c', True), b'\x82\x01\xff'),
            ('F',            ('a', True), b'\x80\x01\xff'),
            ('G',            ('a', True), b'\x80\x01\xff'),
            ('G',            ('b', True), b'\x81\x01\xff'),
            ('H',            ('a', True), b'\x80\x01\xff'),
            ('H',            ('b', True), b'\x81\x01\xff'),
            ('H',            ('c', True), b'\x82\x01\xff'),
            ('I',            ('a', True), b'\x80\x01\xff'),
            ('I',            ('b', True), b'\x81\x01\xff'),
            ('I',            ('c', True), b'\x82\x01\xff'),
            ('J',            ('a', True), b'\x80\x01\xff'),
            ('J',        ('b', ('a', 1)), b'\xa1\x03\x80\x01\x01'),
            ('J',            ('c', True), b'\x82\x01\xff'),
            ('K',          ('m31', None), b'\x9e\x00'),
            ('K',          ('m32', None), b'\x9f\x1f\x00'),
            ('K',          ('m33', None), b'\x9f\x20\x00'),
            ('M',     ('a', ('b', True)), b'\xa0\x03\x80\x01\xff')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        self.assertEqual(foo.decode('L', b'\xa0\x03\x04\x01\x12'), ('a', b'\x12'))
        self.assertEqual(foo.decode('L', b'\x80\x01\x12'), ('a', b'\x12'))

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x81\x01\xff')

        self.assertEqual(
            str(cm.exception),
            "Expected choice member tag '80', but got '81'.")

    def test_choice_implicit_tags(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS IMPLICIT TAGS ::= "
            "BEGIN "
            "A ::= CHOICE { "
            "  a BOOLEAN "
            "} "
            "B ::= CHOICE { "
            "  a OCTET STRING "
            "} "
            "C ::= CHOICE { "
            "  a CHOICE { "
            "    b BOOLEAN, "
            "    c INTEGER "
            "  } "
            "} "
            "D ::= [5] CHOICE { "
            "  a BOOLEAN "
            "} "
            "F ::= [5] EXPLICIT CHOICE { "
            "  a BOOLEAN "
            "} "
            "G ::= [APPLICATION 5] EXPLICIT CHOICE { "
            "  a BOOLEAN "
            "} "
            "H ::= [6] IMPLICIT G "
            "I ::= [APPLICATION 6] IMPLICIT F "
            "J ::= [6] IMPLICIT F "
            "K ::= [3] CHOICE { "
            "  a [4] CHOICE { "
            "    a BOOLEAN "
            "  }, "
            "  b [5] CHOICE { "
            "    b INTEGER "
            "  } "
            "} "
            "END")

        datas = [
            ('A',            ('a', True), b'\x01\x01\xff'),
            ('C',     ('a', ('b', True)), b'\x01\x01\xff'),
            ('C',        ('a', ('c', 3)), b'\x02\x01\x03'),
            ('D',            ('a', True), b'\xa5\x03\x01\x01\xff'),
            ('F',            ('a', True), b'\xa5\x03\x01\x01\xff'),
            ('G',            ('a', True), b'\x65\x03\x01\x01\xff'),
            ('H',            ('a', True), b'\xa6\x03\x01\x01\xff'),
            ('I',            ('a', True), b'\x66\x03\x01\x01\xff'),
            ('J',            ('a', True), b'\xa6\x03\x01\x01\xff'),
            ('K',     ('a', ('a', True)), b'\xa3\x05\xa4\x03\x01\x01\xff'),
            ('K',        ('b', ('b', 2)), b'\xa3\x05\xa5\x03\x02\x01\x02')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        self.assertEqual(foo.decode('B', b'\x24\x03\x04\x01\x12'), ('a', b'\x12'))
        self.assertEqual(foo.decode('B', b'\x04\x01\x12'), ('a', b'\x12'))

    def test_utf8_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTF8String "
            "END",
            'ber')

        datas = [
            ('A',                u'bar', b'\x0c\x03\x62\x61\x72'),
            ('A',           u'a\u1010c', b'\x0c\x05\x61\xe1\x80\x90\x63'),
            ('A',
             u'f → ∝',
             b'\x0c\x09\x66\x20\xe2\x86\x92\x20\xe2\x88\x9d')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_bmp_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS IMPLICIT TAGS ::= "
            "BEGIN "
            "A ::= BMPString "
            "END")

        datas = [
            ('A', 'hello', b'\x1e\x0a\x00\x68\x00\x65\x00\x6c\x00\x6c\x00\x6f'),
            ('A', u'\u0102', b'\x1e\x02\x01\x02')
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
            "END")

        datas = [
            ('A',
             'bar',
             b'\x1c\x0c\x00\x00\x00\x62\x00\x00\x00\x61\x00\x00\x00\x72'),
            ('A',
             u'åäö',
             b'\x1c\x0c\x00\x00\x00\xe5\x00\x00\x00\xe4\x00\x00\x00\xf6')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_utc_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS IMPLICIT TAGS ::= "
            "BEGIN "
            "A ::= UTCTime "
            "END")

        datas = [
            ('A',
             ut2dt('001001000000Z'),
             b'\x17\x0b\x30\x30\x31\x30\x30\x31\x30\x30\x30\x30\x5a'),
            ('A',
             ut2dt('010203040506Z'),
             b'\x17\x0d010203040506Z'),
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_utc_time_explicit_tags(self):
        """Test explicit tags on UTC time.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] UTCTime END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo,
                                  'Foo',
                                  ut2dt('121001230001Z'),
                                  b'\xa2\x0f\x17\x0d121001230001Z')

    def test_generalized_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GeneralizedTime "
            "END")

        datas = [
            ('A',
             datetime(2018, 1, 22, 13, 29),
             b'\x18\x0c\x32\x30\x31\x38\x30\x31\x32\x32\x31\x33\x32\x39'),
            ('A',
             datetime(2018, 1, 22, 13, 0),
             b'\x18\x0c\x32\x30\x31\x38\x30\x31\x32\x32\x31\x33\x30\x30'),
            ('A',
             datetime(2018, 1, 22, 13, 2),
             b'\x18\x0c\x32\x30\x31\x38\x30\x31\x32\x32\x31\x33\x30\x32'),
            ('A',
             datetime(2000, 12, 31, 23, 59, 59, 999000,
                      timezone(timedelta(hours=0))),
             b'\x18\x13\x32\x30\x30\x30\x31\x32\x33\x31\x32\x33\x35\x39'
             b'\x35\x39\x2e\x39\x39\x39\x5a')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_foo(self):
        foo = asn1tools.compile_files(['tests/files/foo.asn'])

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded, b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3?')

        # Decode the encoded question.
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Encode an answer.
        encoded = foo.encode('Answer', {'id': 1, 'answer': False})
        self.assertEqual(encoded, b'0\x06\x02\x01\x01\x01\x01\x00')

        # Decode the encoded answer.
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn')

        # The length can be decoded.
        datas = [
            (b'\x30\x0e\x02\x01\x01\x16\x09Is 1+1=3?', 16),
            (b'\x30\x10\x02\x02\x01\x16\x09Is 1+10=14?', 18),
            (b'\x30\x0d', 15),
            (b'\x30\x84\x00\x00\x00\xb8', 190),
            (b'\x9f\x1f\x00', 3),
            (b'\x9f\x80\x80\x01\x02\xff', 7)
       ]

        for encoded, decoded_length in datas:
            length = foo.decode_length(encoded)
            self.assertEqual(length, decoded_length)

        # The length cannot be decoded.
        datas = [
            b'\x30',
            b'',
            b'\x30\x84\x00\x00\x00'
        ]

        for encoded in datas:
            self.assertIsNone(foo.decode_length(encoded))

    def test_complex(self):
        cmplx = asn1tools.compile_files('tests/files/complex.asn')

        decoded = {
            'boolean': True,
            'integer': -7,
            'bit-string': (b'\x80', 3),
            'octet-string': b'\x31\x32',
            'null': None,
            'object-identifier': '1.3.2',
            'enumerated': 'one',
            'sequence': {},
            'ia5-string': 'foo'
        }

        encoded = (
            b'\x30\x1e\x01\x01\xff\x02\x01\xf9\x03\x02\x05\x80\x04\x02\x31\x32'
            b'\x05\x00\x06\x02\x2b\x02\x0a\x01\x01\x30\x00\x16\x03\x66\x6f\x6f'
        )

        self.assert_encode_decode(cmplx, 'AllUniversalTypes', decoded, encoded)

        # Ivalid enumeration value.
        decoded = {
            'boolean': True,
            'integer': -7,
            'bit-string': (b'\x80', 3),
            'octet-string': b'\x31\x32',
            'null': None,
            'object-identifier': '1.3.2',
            'enumerated': 'three',
            'sequence': {},
            'ia5-string': 'foo'
        }

        with self.assertRaises(asn1tools.EncodeError) as cm:
            cmplx.encode('AllUniversalTypes', decoded)

        self.assertEqual(
            str(cm.exception),
            "enumerated: Expected enumeration value 'one' or 'two', but got "
            "'three'.")

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0))

        # Message 1.
        decoded = {
            'message': (
                'c1',
                (
                    'paging',
                    {
                        'systemInfoModification': 'true',
                        'nonCriticalExtension': {
                        }
                    }
                )
            )
        }

        encoded = b'0\x0b\xa0\t\xa0\x07\xa0\x05\x81\x01\x00\xa3\x00'

        self.assert_encode_decode(rrc, 'PCCH-Message', decoded, encoded)

        # Message 2.
        decoded = {
            'message': (
                'c1',
                ('paging', {})
            )
        }

        encoded = b'0\x06\xa0\x04\xa0\x02\xa0\x00'

        self.assert_encode_decode(rrc, 'PCCH-Message', decoded, encoded)

        # Message 3.
        decoded = {
            'message': {
                'dl-Bandwidth': 'n6',
                'phich-Config': {
                    'phich-Duration': 'normal',
                    'phich-Resource': 'half'
                },
                'systemFrameNumber': (b'\x12', 8),
                'spare': (b'\x34\x40', 10)
            }
        }

        encoded = (
            b'0\x16\xa0\x14\x80\x01\x00\xa1\x06\x80\x01\x00\x81\x01\x01\x82'
            b'\x02\x00\x12\x83\x03\x06\x34\x40'
        )

        self.assert_encode_decode(rrc, 'BCCH-BCH-Message', decoded, encoded)

        # Message 4.
        decoded = {
            'message': (
                'c1',
                (
                    'systemInformation',
                    {
                        'criticalExtensions': (
                            'systemInformation-r8',
                            {
                                'sib-TypeAndInfo': [
                                    (
                                        'sib2',
                                        {
                                            'ac-BarringInfo': {
                                                'ac-BarringForEmergency': True,
                                                'ac-BarringForMO-Data': {
                                                    'ac-BarringFactor': 'p95',
                                                    'ac-BarringTime': 's128',
                                                    'ac-BarringForSpecialAC': (b'\xf0', 5)
                                                }
                                            },
                                            'radioResourceConfigCommon': {
                                                'rach-ConfigCommon': {
                                                    'preambleInfo': {
                                                        'numberOfRA-Preambles': 'n24',
                                                        'preamblesGroupAConfig': {
                                                            'sizeOfRA-PreamblesGroupA': 'n28',
                                                            'messageSizeGroupA': 'b144',
                                                            'messagePowerOffsetGroupB': 'minusinfinity'
                                                        }
                                                    },
                                                    'powerRampingParameters': {
                                                        'powerRampingStep': 'dB0',
                                                        'preambleInitialReceivedTargetPower': 'dBm-102'
                                                    },
                                                    'ra-SupervisionInfo': {
                                                        'preambleTransMax': 'n8',
                                                        'ra-ResponseWindowSize': 'sf6',
                                                        'mac-ContentionResolutionTimer': 'sf48'
                                                    },
                                                    'maxHARQ-Msg3Tx': 8
                                                },
                                                'bcch-Config': {
                                                    'modificationPeriodCoeff': 'n2'
                                                },
                                                'pcch-Config': {
                                                    'defaultPagingCycle': 'rf256',
                                                    'nB': 'twoT'
                                                },
                                                'prach-Config': {
                                                    'rootSequenceIndex': 836,
                                                    'prach-ConfigInfo': {
                                                        'prach-ConfigIndex': 33,
                                                        'highSpeedFlag': False,
                                                        'zeroCorrelationZoneConfig': 10,
                                                        'prach-FreqOffset': 64
                                                    }
                                                },
                                                'pdsch-ConfigCommon': {
                                                    'referenceSignalPower': -60,
                                                    'p-b': 2
                                                },
                                                'pusch-ConfigCommon': {
                                                    'pusch-ConfigBasic': {
                                                        'n-SB': 1,
                                                        'hoppingMode': 'interSubFrame',
                                                        'pusch-HoppingOffset': 10,
                                                        'enable64QAM': False
                                                    },
                                                    'ul-ReferenceSignalsPUSCH': {
                                                        'groupHoppingEnabled': True,
                                                        'groupAssignmentPUSCH': 22,
                                                        'sequenceHoppingEnabled': False,
                                                        'cyclicShift': 5
                                                    }
                                                },
                                                'pucch-ConfigCommon': {
                                                    'deltaPUCCH-Shift': 'ds1',
                                                    'nRB-CQI': 98,
                                                    'nCS-AN': 4,
                                                    'n1PUCCH-AN': 2047
                                                },
                                                'soundingRS-UL-ConfigCommon': (
                                                    'setup',
                                                    {
                                                        'srs-BandwidthConfig': 'bw0',
                                                        'srs-SubframeConfig': 'sc4',
                                                        'ackNackSRS-SimultaneousTransmission': True
                                                    }),
                                                'uplinkPowerControlCommon': {
                                                    'p0-NominalPUSCH': -126,
                                                    'alpha': 'al0',
                                                    'p0-NominalPUCCH': -127,
                                                    'deltaFList-PUCCH': {
                                                        'deltaF-PUCCH-Format1': 'deltaF-2',
                                                        'deltaF-PUCCH-Format1b': 'deltaF1',
                                                        'deltaF-PUCCH-Format2': 'deltaF0',
                                                        'deltaF-PUCCH-Format2a': 'deltaF-2',
                                                        'deltaF-PUCCH-Format2b': 'deltaF0'
                                                    },
                                                    'deltaPreambleMsg3': -1
                                                },
                                                'ul-CyclicPrefixLength': 'len1'
                                            },
                                            'ue-TimersAndConstants': {
                                                't300': 'ms100',
                                                't301': 'ms200',
                                                't310': 'ms50',
                                                'n310': 'n2',
                                                't311': 'ms30000',
                                                'n311': 'n2'
                                            },
                                            'freqInfo': {
                                                'additionalSpectrumEmission': 3
                                            },
                                            'timeAlignmentTimerCommon': 'sf500'
                                        }
                                    ),
                                    (
                                        'sib3',
                                        {
                                            'cellReselectionInfoCommon': {
                                                'q-Hyst': 'dB0',
                                                'speedStateReselectionPars': {
                                                    'mobilityStateParameters': {
                                                        't-Evaluation': 's180',
                                                        't-HystNormal': 's180',
                                                        'n-CellChangeMedium': 1,
                                                        'n-CellChangeHigh': 16
                                                    },
                                                    'q-HystSF': {
                                                        'sf-Medium': 'dB-6',
                                                        'sf-High': 'dB-4'
                                                    }
                                                }
                                            },
                                            'cellReselectionServingFreqInfo': {
                                                'threshServingLow': 7,
                                                'cellReselectionPriority': 3
                                            },
                                            'intraFreqCellReselectionInfo': {
                                                'q-RxLevMin': -33,
                                                's-IntraSearch': 0,
                                                'presenceAntennaPort1': False,
                                                'neighCellConfig': (b'\x80', 2),
                                                't-ReselectionEUTRA': 4
                                            }
                                        }
                                    ),
                                    (
                                        'sib4',
                                        {
                                        }
                                    ),
                                    (
                                        'sib5',
                                        {
                                            'interFreqCarrierFreqList': [
                                                {
                                                    'dl-CarrierFreq': 1,
                                                    'q-RxLevMin': -45,
                                                    't-ReselectionEUTRA': 0,
                                                    'threshX-High': 31,
                                                    'threshX-Low': 29,
                                                    'allowedMeasBandwidth': 'mbw6',
                                                    'presenceAntennaPort1': True,
                                                    'neighCellConfig': (b'\x00', 2),
                                                    'q-OffsetFreq': 'dB0'
                                                }
                                            ]
                                        }
                                    ),
                                    (
                                        'sib6',
                                        {
                                            't-ReselectionUTRA': 3
                                        }
                                    ),
                                    ('sib7',
                                     {
                                         't-ReselectionGERAN': 3
                                     }
                                    ),
                                    ('sib8',
                                     {
                                         'parameters1XRTT': {
                                             'longCodeState1XRTT': (b'\x01#Eg\x89\x00', 42)
                                         }
                                     }
                                    ),
                                    (
                                        'sib9',
                                        {
                                            'hnb-Name': b'4'
                                        }
                                    ),
                                    ('sib10',
                                     {
                                         'messageIdentifier': (b'#4', 16),
                                         'serialNumber': (b'\x124', 16),
                                         'warningType': b'2\x12'
                                     }
                                    ),
                                    (
                                        'sib11',
                                        {
                                            'messageIdentifier': (b'g\x88', 16),
                                            'serialNumber': (b'T5', 16),
                                            'warningMessageSegmentType': 'notLastSegment',
                                            'warningMessageSegmentNumber': 19,
                                            'warningMessageSegment': b'\x12'
                                        }
                                    )
                                ]
                            }
                        )
                    }
                )
            )
        }

        encoded = (
            b'\x30\x82\x01\x93\xa0\x82\x01\x8f\xa0\x82\x01\x8b\xa0\x82\x01'
            b'\x87\xa0\x82\x01\x83\xa0\x82\x01\x7f\xa0\x82\x01\x7b\xa0\x81'
            b'\xdd\xa0\x0f\x80\x01\xff\xa2\x0a\x80\x01\x0f\x81\x01\x05\x82'
            b'\x02\x03\xf0\xa1\x81\xad\xa0\x26\xa0\x0e\x80\x01\x05\xa1\x09'
            b'\x80\x01\x06\x81\x01\x01\x82\x01\x00\xa1\x06\x80\x01\x00\x81'
            b'\x01\x09\xa2\x09\x80\x01\x05\x81\x01\x04\x82\x01\x05\x83\x01'
            b'\x08\xa1\x03\x80\x01\x00\xa2\x06\x80\x01\x03\x81\x01\x01\xa3'
            b'\x12\x80\x02\x03\x44\xa1\x0c\x80\x01\x21\x81\x01\x00\x82\x01'
            b'\x0a\x83\x01\x40\xa4\x06\x80\x01\xc4\x81\x01\x02\xa5\x1c\xa0'
            b'\x0c\x80\x01\x01\x81\x01\x00\x82\x01\x0a\x83\x01\x00\xa1\x0c'
            b'\x80\x01\xff\x81\x01\x16\x82\x01\x00\x83\x01\x05\xa6\x0d\x80'
            b'\x01\x00\x81\x01\x62\x82\x01\x04\x83\x02\x07\xff\xa7\x0b\xa1'
            b'\x09\x80\x01\x00\x81\x01\x04\x82\x01\xff\xa8\x1d\x80\x01\x82'
            b'\x81\x01\x00\x82\x01\x81\xa3\x0f\x80\x01\x00\x81\x01\x00\x82'
            b'\x01\x01\x83\x01\x00\x84\x01\x01\x84\x01\xff\x89\x01\x00\xa2'
            b'\x12\x80\x01\x00\x81\x01\x01\x82\x01\x01\x83\x01\x01\x84\x01'
            b'\x06\x85\x01\x01\xa3\x03\x82\x01\x03\x85\x01\x00\xa1\x37\xa0'
            b'\x1b\x80\x01\x00\xa1\x16\xa0\x0c\x80\x01\x03\x81\x01\x03\x82'
            b'\x01\x01\x83\x01\x10\xa1\x06\x80\x01\x00\x81\x01\x01\xa1\x06'
            b'\x81\x01\x07\x82\x01\x03\xa2\x10\x80\x01\xdf\x82\x01\x00\x84'
            b'\x01\x00\x85\x02\x06\x80\x86\x01\x04\xa2\x00\xa3\x1d\xa0\x1b'
            b'\x30\x19\x80\x01\x01\x81\x01\xd3\x83\x01\x00\x85\x01\x1f\x86'
            b'\x01\x1d\x87\x01\x00\x88\x01\xff\x8a\x02\x06\x00\xa4\x03\x82'
            b'\x01\x03\xa5\x03\x80\x01\x03\xa6\x0b\xa3\x09\x81\x07\x06\x01'
            b'\x23\x45\x67\x89\x00\xa7\x03\x80\x01\x34\xa8\x0e\x80\x03\x00'
            b'\x23\x34\x81\x03\x00\x12\x34\x82\x02\x32\x12\xa9\x13\x80\x03'
            b'\x00\x67\x88\x81\x03\x00\x54\x35\x82\x01\x00\x83\x01\x13\x84'
            b'\x01\x12'
        )

        self.assert_encode_decode(rrc, 'BCCH-DL-SCH-Message', decoded, encoded)

    def test_rfc1157(self):
        rfc1157 = asn1tools.compile_files([
            'tests/files/ietf/rfc1155.asn',
            'tests/files/ietf/rfc1157.asn'
        ])

        # First message.
        decoded = {
            "version": 0,
            "community": b'public',
            "data": (
                "set-request",
                {
                    "request-id": 60,
                    "error-status": 0,
                    "error-index": 0,
                    "variable-bindings": [
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130101",
                            "value": (
                                "simple",
                                (
                                    "string",
                                    (b'\x31\x37\x32\x2e\x33\x31'
                                     b'\x2e\x31\x39\x2e\x37\x33')
                                )
                            )
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.5.10.14130400",
                            "value": (
                                "simple", (
                                    "number",
                                    2
                                )
                            )
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130102",
                            "value": (
                                "simple",
                                (
                                    "string",
                                    (b'\x32\x35\x35\x2e\x32\x35'
                                     b'\x35\x2e\x32\x35\x35\x2e'
                                     b'\x30')
                                )
                            )
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130104",
                            "value": (
                                "simple",
                                (
                                    "string",
                                    (b'\x31\x37\x32\x2e\x33\x31'
                                     b'\x2e\x31\x39\x2e\x32')
                                )
                            )
                        }
                    ]
                }
            )
        }

        encoded = (
            b'0\x81\x9f\x02\x01\x00\x04\x06public\xa3\x81\x91\x02'
            b'\x01<\x02\x01\x00\x02\x01\x000\x81\x850"\x06\x12+\x06'
            b'\x01\x04\x01\x81}\x083\n\x02\x01\x07\n\x86\xde\xb75'
            b'\x04\x0c172.31.19.730\x17\x06\x12+\x06\x01\x04\x01\x81'
            b'}\x083\n\x02\x01\x05\n\x86\xde\xb9`\x02\x01\x020#\x06'
            b'\x12+\x06\x01\x04\x01\x81}\x083\n\x02\x01\x07\n\x86\xde'
            b'\xb76\x04\r255.255.255.00!\x06\x12+\x06\x01\x04\x01\x81'
            b'}\x083\n\x02\x01\x07\n\x86\xde\xb78\x04\x0b172.31.19.2'
        )

        self.assert_encode_decode(rfc1157, 'Message', decoded, encoded)

        # Next message.
        decoded = {
            'version': 1,
            'community': b'community',
            'data': (
                'set-request',
                {
                    'request-id': 1687059484,
                    'error-status': 0,
                    'error-index': 0,
                    'variable-bindings': [
                        {
                            'name': '1.3.6.1.999.1.1',
                            'value': (
                                'simple',
                                (
                                    'number', 1
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.2.1',
                            'value': (
                                'simple',
                                (
                                    'string', b'f00'
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': (
                                'application-wide',
                                (
                                    'address',
                                    (
                                        'internet', b'\xc0\xa8\x01\x01'
                                    )
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': (
                                'simple',
                                (
                                    'object', '1.2.3.444.555'
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.1.2',
                            'value': (
                                'simple',
                                (
                                    'number', 1
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.2.2',
                            'value': (
                                'simple',
                                (
                                    'string', b'f00'
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.3.2',
                            'value': (
                                'application-wide',
                                (
                                    'address',
                                    (
                                        'internet', b'\xc0\xa8\x01\x01'
                                    )
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.4.2',
                            'value': (
                                'simple',
                                (
                                    'object', '1.2.3.444.555'
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.1.3',
                            'value': (
                                'simple',
                                (
                                    'number', 1
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.2.3',
                            'value': (
                                'simple',
                                (
                                    'string', b'f00'
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.3.3',
                            'value': (
                                'application-wide',
                                (
                                    'address',
                                    (
                                        'internet', b'\xc0\xa8\x01\x01'
                                    )
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.4.3',
                            'value': (
                                'simple',
                                (
                                    'object', '1.2.3.444.555'
                                )
                            )
                        }
                    ]
                }
            )
        }

        encoded = (
            b'\x30\x81\xe6\x02\x01\x01\x04\x09\x63\x6f\x6d\x6d\x75\x6e\x69\x74'
            b'\x79\xa3\x81\xd5\x02\x04\x64\x8e\x7c\x1c\x02\x01\x00\x02\x01\x00'
            b'\x30\x81\xc6\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x01\x01\x02\x01'
            b'\x01\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x02\x01\x04\x03\x66\x30'
            b'\x30\x30\x0f\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x40\x04\xc0\xa8'
            b'\x01\x01\x30\x11\x06\x07\x2b\x06\x01\x87\x67\x04\x01\x06\x06\x2a'
            b'\x03\x83\x3c\x84\x2b\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x01\x02'
            b'\x02\x01\x01\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x02\x02\x04\x03'
            b'\x66\x30\x30\x30\x0f\x06\x07\x2b\x06\x01\x87\x67\x03\x02\x40\x04'
            b'\xc0\xa8\x01\x01\x30\x11\x06\x07\x2b\x06\x01\x87\x67\x04\x02\x06'
            b'\x06\x2a\x03\x83\x3c\x84\x2b\x30\x0c\x06\x07\x2b\x06\x01\x87\x67'
            b'\x01\x03\x02\x01\x01\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x02\x03'
            b'\x04\x03\x66\x30\x30\x30\x0f\x06\x07\x2b\x06\x01\x87\x67\x03\x03'
            b'\x40\x04\xc0\xa8\x01\x01\x30\x11\x06\x07\x2b\x06\x01\x87\x67\x04'
            b'\x03\x06\x06\x2a\x03\x83\x3c\x84\x2b'
        )

        self.assert_encode_decode(rfc1157, 'Message', decoded, encoded)

        # Next message.
        decoded = {
            'version': 1,
            'community': b'community',
            'data': (
                'set-request',
                {
                    'request-id': 1687059484,
                    'error-status': 0,
                    'error-index': 0,
                    'variable-bindings': [
                        {
                            'name': '1.3.6.1.999.1.1',
                            'value': (
                                'simple',
                                (
                                    'number', -1
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.2.1',
                            'value': (
                                'simple',
                                (
                                    'string', b'f00'
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': (
                                'simple',
                                (
                                    'object', '1.2.3.444.555'
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': (
                                'simple',
                                (
                                    'empty', None
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': (
                                'application-wide',
                                (
                                    'address', (
                                        'internet', b'\xc0\xa8\x01\x01'
                                    )
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': (
                                'application-wide',
                                (
                                    'counter', 0
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': (
                                'application-wide',
                                (
                                    'gauge', 4294967295
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': (
                                'application-wide',
                                (
                                    'ticks', 88
                                )
                            )
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': (
                                'application-wide',
                                (
                                    'arbitrary', b'\x31\x32\x33'
                                )
                            )
                        }
                    ]
                }
            )
        }

        encoded = (
            b'\x30\x81\xad\x02\x01\x01\x04\x09\x63\x6f\x6d\x6d\x75\x6e\x69\x74'
            b'\x79\xa3\x81\x9c\x02\x04\x64\x8e\x7c\x1c\x02\x01\x00\x02\x01\x00'
            b'\x30\x81\x8d\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x01\x01\x02\x01'
            b'\xff\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x02\x01\x04\x03\x66\x30'
            b'\x30\x30\x11\x06\x07\x2b\x06\x01\x87\x67\x04\x01\x06\x06\x2a\x03'
            b'\x83\x3c\x84\x2b\x30\x0b\x06\x07\x2b\x06\x01\x87\x67\x04\x01\x05'
            b'\x00\x30\x0f\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x40\x04\xc0\xa8'
            b'\x01\x01\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x41\x01\x00'
            b'\x30\x10\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x42\x05\x00\xff\xff'
            b'\xff\xff\x30\x0c\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x43\x01\x58'
            b'\x30\x0e\x06\x07\x2b\x06\x01\x87\x67\x03\x01\x44\x03\x31\x32\x33'
        )

        self.assert_encode_decode(rfc1157, 'Message', decoded, encoded)

        # Next message with missing field 'data' -> 'set-request' ->
        # 'variable-bindings[0]' -> 'value' -> 'simple'.
        decoded = {
            'version': 1,
            'community': b'community',
            'data': (
                'set-request',
                {
                    'request-id': 1687059484,
                    'error-status': 0,
                    'error-index': 0,
                    'variable-bindings': [
                        {
                            'name': '1.3.6.1.999.1.1',
                            'value': ('', ())
                        }
                    ]
                }
            )
        }

        with self.assertRaises(asn1tools.EncodeError) as cm:
            rfc1157.encode('Message', decoded)

        self.assertEqual(
            str(cm.exception),
            "data: set-request: variable-bindings: value: Expected choice "
            "'application-wide' or 'simple', but got ''.")

    def test_performance(self):
        cmplx = asn1tools.compile_files('tests/files/complex.asn')

        decoded = {
            'boolean': True,
            'integer': -7,
            'bit-string': (b'\x80', 3),
            'octet-string': b'\x31\x32',
            'null': None,
            'object-identifier': '1.3.2',
            'enumerated': 'one',
            'sequence': {},
            'ia5-string': 'foo'
        }

        encoded = (
            b'\x30\x1e\x01\x01\xff\x02\x01\xf9\x03\x02\x05\x80\x04\x02\x31\x32'
            b'\x05\x00\x06\x02\x2b\x02\x0a\x01\x01\x30\x00\x16\x03\x66\x6f\x6f'
        )

        def encode():
            cmplx.encode('AllUniversalTypes', decoded)

        def decode():
            cmplx.decode('AllUniversalTypes', encoded)

        iterations = 1000

        res = timeit.timeit(encode, number=iterations)
        ms_per_call = 1000 * res / iterations
        print('{} ms per encode call.'.format(round(ms_per_call, 3)))

        res = timeit.timeit(decode, number=iterations)
        ms_per_call = 1000 * res / iterations
        print('{} ms per decode call.'.format(round(ms_per_call, 3)))

    def test_rfc4511(self):
        rfc4511 = asn1tools.compile_dict(deepcopy(RFC4511))

        # A search request message.
        decoded = {
            'messageID': 2,
            'protocolOp': (
                'searchRequest',
                {
                    'baseObject': b'',
                    'scope': 'wholeSubtree',
                    'derefAliases': 'neverDerefAliases',
                    'sizeLimit': 0,
                    'timeLimit': 0,
                    'typesOnly': False,
                    'filter': (
                        'and',
                        [
                            (
                                'substrings',
                                {
                                    'type': b'\x63\x6e',
                                    'substrings': [
                                        ('any', b'\x66\x72\x65\x64')
                                    ]
                                }
                            ),
                            (
                                'equalityMatch',
                                {
                                    'attributeDesc': b'\x64\x6e',
                                    'assertionValue': b'\x6a\x6f\x65'
                                }
                            )
                        ]
                    ),
                    'attributes': [
                    ]
                }
            )
        }

        encoded = (
            b'\x30\x33\x02\x01\x02\x63\x2e\x04\x00\x0a\x01\x02\x0a\x01\x00\x02'
            b'\x01\x00\x02\x01\x00\x01\x01\x00\xa0\x19\xa4\x0c\x04\x02\x63\x6e'
            b'\x30\x06\x81\x04\x66\x72\x65\x64\xa3\x09\x04\x02\x64\x6e\x04\x03'
            b'\x6a\x6f\x65\x30\x00'
        )

        self.assert_encode_decode(rfc4511, 'LDAPMessage', decoded, encoded)

        # A search request message with nested filters and controls
        # (copied from https://github.com/etingof/pyasn1/issues/116).
        decoded = {
            'controls': [
                {
                    'controlType': b'1.2.840.113556.1.4.319',
                    'controlValue': b'0\x06\x02\x02\x03\xe7\x04\x00',
                    'criticality': True
                },
                {
                    'controlType': b'2.16.840.1.113730.3.4.2',
                    'criticality': False
                }
            ],
            'messageID': 5,
            'protocolOp': (
                'searchRequest',
                {
                    'attributes': [
                        b'postOfficeBox',
                        b'givenName',
                        b'sn',
                        b'mail',
                        b'homeDirectory',
                        b'memberOf',
                        b'objectGUID',
                        b'postOfficeBox',
                        b'extensionAttribute1',
                        b'mail',
                        b'sAMAccountName'
                    ],
                    'baseObject': b'dc=arl,dc=local',
                    'derefAliases': 'derefAlways',
                    'filter': (
                        'and',
                        [
                            (
                                'equalityMatch',
                                {
                                    'assertionValue': b'user',
                                    'attributeDesc': b'objectClass'
                                }
                            ),
                            (
                                'or',
                                [
                                    (
                                        'equalityMatch',
                                        {
                                            'assertionValue': b'01107ECBA2',
                                            'attributeDesc': b'postOfficeBox'
                                        }
                                    ),
                                    (
                                        'equalityMatch',
                                        {
                                            'assertionValue': b'01107ECBA2',
                                            'attributeDesc': b'extensionAttribute1'
                                        }
                                    )
                                ]
                            )
                        ]
                    ),
                    'scope': 'wholeSubtree',
                    'sizeLimit': 0,
                    'timeLimit': 0,
                    'typesOnly': False
                }
            )
        }

        encoded = (
            b'\x30\x82\x01\x49\x02\x01\x05\x63\x81\xff\x04\x0f\x64\x63\x3d\x61'
            b'\x72\x6c\x2c\x64\x63\x3d\x6c\x6f\x63\x61\x6c\x0a\x01\x02\x0a\x01'
            b'\x03\x02\x01\x00\x02\x01\x00\x01\x01\x00\xa0\x57\xa3\x13\x04\x0b'
            b'\x6f\x62\x6a\x65\x63\x74\x43\x6c\x61\x73\x73\x04\x04\x75\x73\x65'
            b'\x72\xa1\x40\xa3\x1b\x04\x0d\x70\x6f\x73\x74\x4f\x66\x66\x69\x63'
            b'\x65\x42\x6f\x78\x04\x0a\x30\x31\x31\x30\x37\x45\x43\x42\x41\x32'
            b'\xa3\x21\x04\x13\x65\x78\x74\x65\x6e\x73\x69\x6f\x6e\x41\x74\x74'
            b'\x72\x69\x62\x75\x74\x65\x31\x04\x0a\x30\x31\x31\x30\x37\x45\x43'
            b'\x42\x41\x32\x30\x81\x83\x04\x0d\x70\x6f\x73\x74\x4f\x66\x66\x69'
            b'\x63\x65\x42\x6f\x78\x04\x09\x67\x69\x76\x65\x6e\x4e\x61\x6d\x65'
            b'\x04\x02\x73\x6e\x04\x04\x6d\x61\x69\x6c\x04\x0d\x68\x6f\x6d\x65'
            b'\x44\x69\x72\x65\x63\x74\x6f\x72\x79\x04\x08\x6d\x65\x6d\x62\x65'
            b'\x72\x4f\x66\x04\x0a\x6f\x62\x6a\x65\x63\x74\x47\x55\x49\x44\x04'
            b'\x0d\x70\x6f\x73\x74\x4f\x66\x66\x69\x63\x65\x42\x6f\x78\x04\x13'
            b'\x65\x78\x74\x65\x6e\x73\x69\x6f\x6e\x41\x74\x74\x72\x69\x62\x75'
            b'\x74\x65\x31\x04\x04\x6d\x61\x69\x6c\x04\x0e\x73\x41\x4d\x41\x63'
            b'\x63\x6f\x75\x6e\x74\x4e\x61\x6d\x65\xa0\x42\x30\x25\x04\x16\x31'
            b'\x2e\x32\x2e\x38\x34\x30\x2e\x31\x31\x33\x35\x35\x36\x2e\x31\x2e'
            b'\x34\x2e\x33\x31\x39\x01\x01\xff\x04\x08\x30\x06\x02\x02\x03\xe7'
            b'\x04\x00\x30\x19\x04\x17\x32\x2e\x31\x36\x2e\x38\x34\x30\x2e\x31'
            b'\x2e\x31\x31\x33\x37\x33\x30\x2e\x33\x2e\x34\x2e\x32'
        )

        self.assert_encode_decode(rfc4511, 'LDAPMessage', decoded, encoded)

        # A search result done message.
        decoded = {
            'messageID': 2,
            'protocolOp': (
                'searchResDone',
                {
                    'resultCode': 'noSuchObject',
                    'matchedDN': b'',
                    'diagnosticMessage': b''
                }
            )
        }

        encoded = (
            b'\x30\x0c\x02\x01\x02\x65\x07\x0a\x01\x20\x04\x00\x04\x00'
        )

        self.assert_encode_decode(rfc4511, 'LDAPMessage', decoded, encoded)

        # A bind request message.
        decoded = {
            'messageID': 1,
            'protocolOp': (
                'bindRequest',
                {
                    'version': 3,
                    'name': b'uid=tesla,dc=example,dc=com',
                    'authentication': (
                        'simple', b'password'
                    )
                }
            )
        }

        encoded = (
            b'\x30\x2f\x02\x01\x01\x60\x2a\x02\x01\x03\x04\x1b\x75\x69\x64\x3d'
            b'\x74\x65\x73\x6c\x61\x2c\x64\x63\x3d\x65\x78\x61\x6d\x70\x6c\x65'
            b'\x2c\x64\x63\x3d\x63\x6f\x6d\x80\x08\x70\x61\x73\x73\x77\x6f\x72'
            b'\x64'
        )

        self.assert_encode_decode(rfc4511, 'LDAPMessage', decoded, encoded)

        # A bind response message.
        decoded = {
            'messageID': 1,
            'protocolOp': (
                'bindResponse',
                {
                    'resultCode': 'success',
                    'matchedDN': b'',
                    'diagnosticMessage': b''
                }
            )
        }

        encoded = (
            b'\x30\x0c\x02\x01\x01\x61\x07\x0a\x01\x00\x04\x00\x04\x00'
        )

        self.assert_encode_decode(rfc4511, 'LDAPMessage', decoded, encoded)

    def test_rfc5280(self):
        rfc5280 = asn1tools.compile_dict(deepcopy(RFC5280))

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

    def test_rfc5280_modified(self):
        any_defined_by_choices = {
            ('PKIX1Explicit88', 'AlgorithmIdentifier', 'parameters'): {
                '1.2.840.113549.1.1.1': 'NULL',
                '1.2.840.113549.1.1.5': 'NULL'
            },
            ('PKIX1Explicit88', 'AttributeValue'): {
                '2.5.4.3': 'DirectoryString',
                '2.5.4.6': 'PrintableString',
                '2.5.4.7': 'PrintableString',
                '2.5.4.8': 'DirectoryString',
                '2.5.4.10': 'DirectoryString',
                '2.5.4.11': 'PrintableString',
                '1.2.840.113549.1.9.1': 'IA5String'
            }
        }

        rfc5280 = asn1tools.compile_dict(
            deepcopy(RFC5280_MODIFIED),
            any_defined_by_choices=any_defined_by_choices)

        decoded = {
            'tbsCertificate': {
                'version': 'v1',
                'serialNumber': 3578,
                'signature': {
                    'algorithm': '1.2.840.113549.1.1.5',
                    'parameters': None
                },
                'issuer': (
                    'rdnSequence',
                    [
                        [{'type': '2.5.4.6', 'value': 'JP'}],
                        [{'type': '2.5.4.8',
                          'value': ('printableString', 'Tokyo')}],
                        [{'type': '2.5.4.7', 'value': 'Chuo-ku'}],
                        [{'type': '2.5.4.10',
                          'value': ('printableString', 'Frank4DD')}],
                        [{'type': '2.5.4.11', 'value': 'WebCert Support'}],
                        [{'type': '2.5.4.3',
                          'value': ('printableString', 'Frank4DD Web CA')}],
                        [{'type': '1.2.840.113549.1.9.1',
                          'value': 'support@frank4dd.com'}]
                    ]
                ),
                'validity': {
                    'notAfter': ('utcTime', ut2dt('170821052654Z')),
                    'notBefore': ('utcTime', ut2dt('120822052654Z'))
                },
                'subject': (
                    'rdnSequence',
                    [
                        [{'type': '2.5.4.6', 'value': 'JP'}],
                        [{'type': '2.5.4.8', 'value': ('utf8String', 'Tokyo')}],
                        [{'type': '2.5.4.10',
                          'value': ('utf8String', 'Frank4DD')}],
                        [{'type': '2.5.4.3',
                          'value': ('utf8String', 'www.example.com')}]
                    ]
                ),
                'subjectPublicKeyInfo': {
                    'algorithm': {
                        'algorithm': '1.2.840.113549.1.1.1',
                        'parameters': None
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
                'parameters': None
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

        # Explicit tagging.
        decoded = (
            'psap-address',
            {
                'pSelector': b'\x12',
                'nAddresses': [ b'\x34' ]
            }
        )

        encoded = b'\xa0\x0c\xa0\x03\x04\x01\x12\xa3\x05\x31\x03\x04\x01\x34'

        self.assert_encode_decode(rfc5280, 'ExtendedNetworkAddress', decoded, encoded)

    def test_rfc5280_errors(self):
        rfc5280 = asn1tools.compile_dict(deepcopy(RFC5280))

        # Empty data.
        encoded = b''

        with self.assertRaises(asn1tools.DecodeError) as cm:
            rfc5280.decode('Certificate', encoded)

        self.assertEqual(
            str(cm.exception),
            "Expected SEQUENCE with tag '30' at offset 0, but got ''.")

        # Only tag and length, no contents.
        encoded = b'\x30\x81\x9f'

        with self.assertRaises(asn1tools.DecodeError) as cm:
            rfc5280.decode('Certificate', encoded)

        self.assertEqual(
            str(cm.exception),
            'Expected at least 159 contents byte(s) at offset 3, but got 0.')

        # Unexpected tag 'ff'.
        encoded = b'\xff\x01\x00'

        with self.assertRaises(asn1tools.DecodeError) as cm:
            rfc5280.decode('Certificate', encoded)

        self.assertEqual(
            str(cm.exception),
            "Expected SEQUENCE with tag '30' at offset 0, but got 'ff'.")

        # Unexpected type '31' embedded in the data.
        encoded = bytearray(
            b'\x30\x82\x02\x12\x30\x82\x01\x7b\x02\x02\x0d\xfa\x30\x0d\x06\x09'
            b'\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05\x05\x00\x30\x81\x9b\x31\x0b'
            b'\x30\x09\x06\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06'
            b'\x03\x55\x04\x08\x13\x05\x54\x6f\x6b\x79\x6f\x31\x10\x30\x0e\x06'
            b'\x03\x55\x04\x07\x13\x07\x43\x68\x75\x6f\x2d\x6b\x75\x31\x11\x30'
            b'\x0f\x06\x03\x55\x04\x0a\x13\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'
            b'\x31\x18\x30\x16\x06\x03\x55\x04\x0b\x13\x0f\x57\x65\x62\x43\x65'
            b'\x72\x74\x20\x53\x75\x70\x70\x6f\x72\x74\x31\x18\x30\x16\x06\x03'
            b'\x55\x04\x03\x13\x0f\x46\x72\x61\x6e\x6b\x34\x44\x44\x20\x57\x65'
            b'\x62\x20\x43\x41\x31\x23'
            b'\x31'
            b'\x21\x06\x09\x2a\x86\x48\x86\xf7\x0d'
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

        self.assertEqual(encoded[150], 49)

        with self.assertRaises(asn1tools.DecodeError) as cm:
            rfc5280.decode('Certificate', encoded)

        self.assertEqual(str(cm.exception),
                         "tbsCertificate: issuer: Expected SEQUENCE with tag "
                         "'30' at offset 150, but got '31'.")

    def test_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

        datas = [
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
            ('SequenceOf',                [], b'\x30\x00'),
            ('SetOf',                     [], b'\x31\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

        all_types.encode('Sequence12', {'a': [{'a': []}]})

        # ToDo: Should return {'a': [{'a': []}]}
        self.assertEqual(
            all_types.decode('Sequence12', b'\x30\x04\x30\x02\x30\x00'),
            {'a': [{}]})

    def test_all_types_automatic_tags(self):
        all_types = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn')

        datas = [
            ('Sequence3',
             {'a': 1, 'c': 2,'d': True},
             b'\x30\x09\x80\x01\x01\x82\x01\x02\x83\x01\xff'),
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_module_tags_explicit(self):
        all_types = asn1tools.compile_files('tests/files/module_tags_explicit.asn')

        datas = [
            ('CBA',      1, b'\xa5\x07\xa4\x05\xa3\x03\x02\x01\x01'),
            ('CBIAI',    1, b'\xa5\x03\x84\x01\x01'),
            ('CIBIA',    1, b'\xa5\x03\x02\x01\x01'),
            ('CIBIAI',   1, b'\x85\x01\x01'),
            ('S2',
             {'a': 1, 'b': {'a': 3}, 'c': ('a', True)},
             b'\x30\x0d\x02\x01\x01\xa2\x05\x30\x03\x02\x01\x03\x01\x01\xff'),
            ('S3',
             {'a': 1, 'b': {'a': 3}, 'c': ('a', True)},
             b'\x30\x0f\x02\x01\x01\xa2\x05\x30\x03\x02\x01\x03\xa3\x03\x01'
             b'\x01\xff'),
            ('S4',
             {'a': 1, 'b': ('a', ('a', 2)), 'c': {'a': 3}, 'd': ('a', True)},
             b'\x30\x16\x02\x01\x01\xa1\x07\xa0\x05\xa0\x03\x02\x01\x02\xa2'
             b'\x05\x30\x03\x02\x01\x03\x01\x01\xff'),
            ('Type1', 'Jones', b'\x1a\x05\x4a\x6f\x6e\x65\x73'),
            ('Type2', 'Jones', b'\x43\x05\x4a\x6f\x6e\x65\x73'),
            ('Type3', 'Jones', b'\xa2\x07\x43\x05\x4a\x6f\x6e\x65\x73'),
            ('Type4', 'Jones', b'\x67\x07\x43\x05\x4a\x6f\x6e\x65\x73'),
            ('Type5', 'Jones', b'\x82\x05\x4a\x6f\x6e\x65\x73')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_module_tags_implicit(self):
        all_types = asn1tools.compile_files('tests/files/module_tags_implicit.asn')

        datas = [
            ('CBA',      1, b'\x85\x01\x01'),
            ('CBIAI',    1, b'\x85\x01\x01'),
            ('CIBIA',    1, b'\x85\x01\x01'),
            ('CIBIAI',   1, b'\x85\x01\x01'),
            ('S2',
             {'a': 1, 'b': {'a': 3}, 'c': ('a', True)},
             b'\x30\x0b\x02\x01\x01\xa2\x03\x02\x01\x03\x01\x01\xff'),
            ('S3',
             {'a': 1, 'b': {'a': 3}, 'c': ('a', True)},
             b'\x30\x0d\x02\x01\x01\xa2\x03\x02\x01\x03\xa3\x03\x01\x01\xff'),
            ('S4',
             {'a': 1, 'b': ('a', ('a', 2)), 'c': {'a': 3}, 'd': ('a', True)},
             b'\x30\x12\x02\x01\x01\xa1\x05\xa0\x03\x80\x01\x02\xa2\x03\x02'
             b'\x01\x03\x01\x01\xff')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_module_tags_automatic(self):
        all_types = asn1tools.compile_files('tests/files/module_tags_automatic.asn')

        datas = [
            ('CBA',      1, b'\x85\x01\x01'),
            ('CBIAI',    1, b'\x85\x01\x01'),
            ('CIBIA',    1, b'\x85\x01\x01'),
            ('CIBIAI',   1, b'\x85\x01\x01'),
            ('S2',
             {'a': 1, 'b': {'a': 3}, 'c': ('a', True)},
             b'\x30\x0b\x02\x01\x01\xa2\x03\x80\x01\x03\x80\x01\xff'),
            ('S3',
             {'a': 1, 'b': {'a': 3}, 'c': ('a', True)},
             b'\x30\x0d\x02\x01\x01\xa2\x03\x80\x01\x03\xa3\x03\x80\x01\xff'),
            ('S4',
             {'a': 1, 'b': ('a', ('a', 2)), 'c': {'a': 3}, 'd': ('a', True)},
             b'\x30\x12\x02\x01\x01\xa1\x05\xa0\x03\x80\x01\x02\xa2\x03\x80'
             b'\x01\x03\x80\x01\xff'
            )
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_decode_all_types_errors(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

        # BOOLEAN.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Boolean', b'\xff')

        self.assertEqual(
            str(cm.exception),
            "Expected BOOLEAN with tag '01' at offset 0, but got 'ff'.")

        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Boolean', b'\x01\x02\x01\x01')

        self.assertEqual(
            str(cm.exception),
            "Expected BOOLEAN contents length 1 at offset 1, but got 2.")

        # INTEGER.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Integer', b'\xfe')

        self.assertEqual(
            str(cm.exception),
            "Expected INTEGER with tag '02' at offset 0, but got 'fe'.")

        # BIT STRING.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Bitstring', b'\xfd')

        self.assertEqual(
            str(cm.exception),
            "Expected BIT STRING with tag '03' at offset 0, but got 'fd'.")

        # OCTET STRING.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Octetstring', b'\xfc')

        self.assertEqual(
            str(cm.exception),
            "Expected OCTET STRING with tag '04' at offset 0, but got 'fc'.")

        # NULL.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Null', b'\xfb')

        self.assertEqual(
            str(cm.exception),
            "Expected NULL with tag '05' at offset 0, but got 'fb'.")

        # OBJECT IDENTIFIER.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Objectidentifier', b'\xfa')

        self.assertEqual(
            str(cm.exception),
            "Expected OBJECT IDENTIFIER with tag '06' at offset 0, "
            "but got 'fa'.")

        # ENUMERATED.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Enumerated', b'\xf9')

        self.assertEqual(
            str(cm.exception),
            "Expected ENUMERATED with tag '0a' at offset 0, but got 'f9'.")

        # UTF8String.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Utf8string', b'\xf8')

        self.assertEqual(
            str(cm.exception),
            "Expected UTF8String with tag '0c' at offset 0, but got 'f8'.")

        # SEQUENCE.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Sequence', b'\xf7')

        self.assertEqual(
            str(cm.exception),
            "Expected SEQUENCE with tag '30' at offset 0, but got 'f7'.")

        # SET.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Set', b'\xf6')

        self.assertEqual(str(cm.exception),
                         "Expected SET with tag '31' at offset 0, but got 'f6'.")

        # NumericString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Numericstring', b'\xf5')

        self.assertEqual(str(cm.exception),
                         "Expected NumericString with tag '12' at offset 0, "
                         "but got 'f5'.")

        # PrintableString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Printablestring', b'\xf4')

        self.assertEqual(str(cm.exception),
                         "Expected PrintableString with tag '13' at offset 0, "
                         "but got 'f4'.")

        # IA5String.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Ia5string', b'\xf3')

        self.assertEqual(
            str(cm.exception),
            "Expected IA5String with tag '16' at offset 0, but got 'f3'.")

        # UniversalString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Universalstring', b'\xf2')

        self.assertEqual(
            str(cm.exception),
            "Expected UniversalString with tag '1c' at offset 0, but got 'f2'.")

        # VisibleString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Visiblestring', b'\xf1')

        self.assertEqual(
            str(cm.exception),
            "Expected VisibleString with tag '1a' at offset 0, but got 'f1'.")

        # GeneralString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Generalstring', b'\xf1')

        self.assertEqual(
            str(cm.exception),
            "Expected GeneralString with tag '1b' at offset 0, but got 'f1'.")

        # BMPString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Bmpstring', b'\xf0')

        self.assertEqual(
            str(cm.exception),
            "Expected BMPString with tag '1e' at offset 0, but got 'f0'.")

        # TeletexString.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Teletexstring', b'\xef')

        self.assertEqual(
            str(cm.exception),
            "Expected TeletexString with tag '14' at offset 0, but got 'ef'.")

        # UTCTime.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('Utctime', b'\xee')

        self.assertEqual(
            str(cm.exception),
            "Expected UTCTime with tag '17' at offset 0, but got 'ee'.")

        # SequenceOf.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('SequenceOf', b'\xed')

        self.assertEqual(
            str(cm.exception),
            "Expected SEQUENCE OF with tag '30' at offset 0, but got 'ed'.")

        # SetOf.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            all_types.decode('SetOf', b'\xec')

        self.assertEqual(
            str(cm.exception),
            "Expected SET OF with tag '31' at offset 0, but got 'ec'.")

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

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
        self.assertEqual(repr(all_types.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(all_types.types['SetOf']), 'SetOf(SetOf, Integer())')
        self.assertEqual(repr(all_types.types['GeneralizedTime1']),
                         'GeneralizedTime(GeneralizedTime1)')
        self.assertEqual(repr(all_types.types['Choice']),
                         'Choice(Choice, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Any']), 'Any(Any)')
        self.assertEqual(repr(all_types.types['Sequence12']),
                         'Sequence(Sequence12, [SequenceOf(a, Recursive(Sequence12))])')

    def test_utf8_string_explicit_tags(self):
        """Test explicit tags on UTC time.

        """

        spec = 'Foo DEFINITIONS ::= BEGIN Foo ::= [2] UTF8String END'
        foo = asn1tools.compile_string(spec)
        self.assert_encode_decode(foo, 'Foo', 'foo', b'\xa2\x05\x0c\x03foo')

    def test_nested_explicit_tags(self):
        """Test nested explicit tags.

        Based on https://github.com/wbond/asn1crypto/issues/63 by tiran.

        """

        spec = """
        TESTCASE DEFINITIONS EXPLICIT TAGS ::=
        BEGIN
        INNERSEQ ::= SEQUENCE {
        innernumber       [21] INTEGER
        }

        INNER ::= [APPLICATION 20] INNERSEQ

        OUTERSEQ ::= SEQUENCE {
        outernumber  [11] INTEGER,
        inner        [12] INNER
        }

        OUTER ::= [APPLICATION 10] OUTERSEQ
        END
        """

        decoded = {
            'outernumber': 23,
            'inner': {
                'innernumber': 42
            }
        }

        encoded = (
            b'\x6a\x12\x30\x10\xab\x03\x02\x01\x17\xac\x09\x74\x07\x30'
            b'\x05\xb5\x03\x02\x01\x2a'
        )

        testcase = asn1tools.compile_string(spec)
        self.assert_encode_decode(testcase, 'OUTER', decoded, encoded)

    def test_zforce(self):
        """

        """

        zforce = asn1tools.compile_dict(deepcopy(ZFORCE))

        # PDU 1.
        decoded = (
            'request',
            {
                'deviceAddress': b'\x00\x01'
            }
        )
        encoded = b'\xee\x04\x40\x02\x00\x01'

        self.assert_encode_decode(zforce, 'ProtocolMessage', decoded, encoded)

        # PDU 2.
        decoded = (
            'request',
            {
                'enable': {
                    'enable': 1
                }
            }
        )
        encoded = b'\xee\x05\x65\x03\x81\x01\x01'

        self.assert_encode_decode(zforce, 'ProtocolMessage', decoded, encoded)

        # PDU 3.
        decoded = (
            'response',
            {
                'enable': {
                    'reset': None
                },
                'openShort': {
                    'openShortInfo': [],
                    'errorCount': 34
                }
            }
        )
        encoded = (
            b'\xef\x0b\x65\x02\x82\x00\x6a\x05\xa0\x00\x81\x01\x22'
        )

        self.assert_encode_decode(zforce, 'ProtocolMessage', decoded, encoded)

        # PDU 4.
        decoded = (
            'notification',
            {
                'notificationMessage': (
                    'ledLevels',
                    [
                        ('uint8', b'\x55\x44\x33\x22'),
                        ('uint16', b'\x01\x02')
                    ]
                ),
                'notificationTimestamp': 1,
                'notificationLatency': 21
            }
        )
        encoded = (
            b'\xf0\x13\x6b\x0a\x80\x04\x55\x44\x33\x22\x82\x02\x01\x02\x58'
            b'\x01\x01\x5f\x23\x01\x15'
        )

        self.assert_encode_decode(zforce, 'ProtocolMessage', decoded, encoded)

        # PDU 5.
        decoded = (
            'request',
            {
                'errorLog': -2,
                'errorThresholds': {
                    'asicsThresholds': [
                        {
                            'asicIdentifier': -256,
                            'irLedOpenThresholds': {
                                'low': -4500,
                                'high': 100000
                            }
                        }
                    ]
                }
            }
        )
        encoded = (
            b'\xee\x1a\x5f\x21\x01\xfe\x7f\x22\x13\xa0\x11\xa0\x0f\x80\x02'
            b'\xff\x00\xa1\x09\x80\x02\xee\x6c\x81\x03\x01\x86\xa0'
        )

        self.assert_encode_decode(zforce, 'ProtocolMessage', decoded, encoded)

    def test_bar(self):
        """A simple example.

        """

        bar = asn1tools.compile_files('tests/files/bar.asn')

        # Message 1.
        decoded = {
            'headerOnly': True,
            'lock': False,
            'acceptTypes': {
                'standardTypes': [(b'\x40', 4), (b'\x80', 4)]
            },
            'url': b'/ses/magic/moxen.html'
        }

        encoded = (
            b'\x60\x29\x01\x01\xff\x01\x01\x00\x61\x0a\xa0\x08\x03\x02\x04'
            b'\x40\x03\x02\x04\x80\x04\x15\x2f\x73\x65\x73\x2f\x6d\x61\x67'
            b'\x69\x63\x2f\x6d\x6f\x78\x65\x6e\x2e\x68\x74\x6d\x6c'
        )

        self.assert_encode_decode(bar, 'GetRequest', decoded, encoded)

        # Message 2.
        decoded = {
            'headerOnly': False,
            'lock': False,
            'url': b'0'
        }

        encoded = b'\x60\x09\x01\x01\x00\x01\x01\x00\x04\x01\x30'

        self.assert_encode_decode(bar, 'GetRequest', decoded, encoded)

    def test_any_defined_by_integer(self):
        spec = """
        Foo DEFINITIONS ::= BEGIN

        Fie ::= SEQUENCE {
            bar INTEGER,
            fum ANY DEFINED BY bar
        }

        END
        """

        any_defined_by_choices = {
            ('Foo', 'Fie', 'fum'): {
                0: 'NULL',
                1: 'INTEGER'
            }
        }

        foo = asn1tools.compile_string(
            spec,
            any_defined_by_choices=any_defined_by_choices)

        # Message 1.
        decoded = {
            'bar': 0,
            'fum': None
        }

        encoded = b'\x30\x05\x02\x01\x00\x05\x00'

        self.assert_encode_decode(foo, 'Fie', decoded, encoded)

        # Message 2.
        decoded = {
            'bar': 1,
            'fum': 5
        }

        encoded = b'\x30\x06\x02\x01\x01\x02\x01\x05'

        self.assert_encode_decode(foo, 'Fie', decoded, encoded)

        # Message 3, key not found.
        decoded = {
            'bar': 2,
            'fum': 5
        }

        encoded = b'\x30\x06\x02\x01\x02\x02\x01\x05'

        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('Fie', decoded)

        self.assertEqual(str(cm.exception), "fum: Bad AnyDefinedBy choice 2.")

        with self.assertRaises(asn1tools.DecodeError) as cm:
            decoded = foo.decode('Fie', encoded)

        self.assertEqual(str(cm.exception), "fum: Bad AnyDefinedBy choice 2.")

    def test_any_defined_by_object_identifier(self):
        spec = """
        Foo DEFINITIONS ::= BEGIN

        Fie ::= SEQUENCE {
            bar OBJECT IDENTIFIER,
            fum ANY DEFINED BY bar
        }

        END
        """

        any_defined_by_choices = {
            ('Foo', 'Fie', 'fum'): {
                '1.3.6.2':    'IA5String',
                '1.3.1000.7': 'BOOLEAN'
            }
        }

        foo = asn1tools.compile_string(
            spec,
            any_defined_by_choices=any_defined_by_choices)

        # Message 1.
        decoded = {
            'bar': '1.3.6.2',
            'fum': 'Hello!'
        }

        encoded = b'0\r\x06\x03+\x06\x02\x16\x06Hello!'

        self.assert_encode_decode(foo, 'Fie', decoded, encoded)

        # Message 2.
        decoded = {
            'bar': '1.3.1000.7',
            'fum': True
        }

        encoded = b'0\t\x06\x04+\x87h\x07\x01\x01\xff'

        self.assert_encode_decode(foo, 'Fie', decoded, encoded)

        # Message 3, key not found.
        decoded = {
            'bar': '1.3.1000.8',
            'fum': True
        }

        encoded = b'0\t\x06\x04+\x87h\x08\x01\x01\x01'

        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('Fie', decoded)

        self.assertEqual(str(cm.exception),
                         "fum: Bad AnyDefinedBy choice 1.3.1000.8.")

        with self.assertRaises(asn1tools.DecodeError) as cm:
            decoded = foo.decode('Fie', encoded)

        self.assertEqual(str(cm.exception),
                         "fum: Bad AnyDefinedBy choice 1.3.1000.8.")

    def test_decode_bad_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn')

        datas = [
            (b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3',
             'Expected at least 14 contents byte(s) at offset 2, but got 13.'),
            (b'0\x0f\x02\x01\x01\x16\x09Is 1+1=3?',
             'Expected at least 15 contents byte(s) at offset 2, but got 14.'),
            (b'0\x0e\x02\x01\x01\x16\x0aIs 1+1=3?',
             'question: Expected at least 10 contents byte(s) at offset 7, but got 9.'),
            (b'0\x0e\x02\x02\x01\x16\x09Is 1+1=3?',
             "question: Expected IA5String with tag '16' at offset 6, but got '09'.")
        ]

        for encoded, message in datas:
            with self.assertRaises(asn1tools.DecodeError) as cm:
                foo.decode('Question', encoded)

            self.assertEqual(str(cm.exception), message)

    def test_all_types_constructed_definite_length(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

        datas = [
            ('Bitstring',       (b'\x80', 1), b'\x03\x02\x07\x80'),
            ('Octetstring',      b'\x00\x01', b'\x24\x06\x04\x01\x00\x04\x01\x01'),
            ('Utf8string',             'foo', b'\x2c\x07\x04\x02fo\x04\x01o'),
            ('Numericstring',          '123', b'\x32\x07\x04\x0212\x04\x013'),
            ('Printablestring',        'foo', b'\x33\x07\x04\x02fo\x04\x01o'),
            ('Ia5string',              'bar', b'\x36\x07\x04\x02ba\x04\x01r'),
            ('Universalstring',
             'bar',
             b'\x3c\x10\x04\x08\x00\x00\x00b\x00\x00\x00a\x04\x04\x00\x00\x00r'),
            ('Visiblestring',          'bar', b'\x3a\x07\x04\x02ba\x04\x01r'),
            ('Generalstring',          'bar', b'\x3b\x07\x04\x02ba\x04\x01r'),
            ('Bmpstring',
             'fie',
             b'\x3e\x0a\x04\x02\x00\x66\x04\x04\x00\x69\x00\x65'),
            ('Teletexstring',          'fum', b'\x34\x07\x04\x01f\x04\x02um')
        ]

        for type_name, decoded, encoded in datas:
            self.assertEqual(all_types.decode(type_name, encoded), decoded)

    def test_all_types_constructed_indefinite_length(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

        datas = [
            ('Bitstring',
             (b'\x11\x22\x80', 17),
             b'\x23\x80\x03\x02\x00\x11\x03\x02\x00\x22\x03\x02\x07\x80\x00\x00'),
            ('Octetstring',
             b'\x00\x01',
             b'\x24\x80\x04\x01\x00\x24\x80\x04\x01\x01\x00\x00\x00\x00'),
            ('Utf8string',             'foo', b'\x2c\x80\x04\x02fo\x04\x01o\x00\x00'),
            #('Sequence',                  {}, b'\x30\x80\x00\x00'),
            #('Set',                       {}, b'\x31\x80\x00\x00'),
            ('Numericstring',          '123', b'\x32\x80\x04\x0212\x04\x013\x00\x00'),
            ('Printablestring',        'foo', b'\x33\x80\x04\x02fo\x04\x01o\x00\x00'),
            ('Ia5string',              'bar', b'\x36\x80\x04\x02ba\x04\x01r\x00\x00'),
            ('Universalstring',
             'bar',
             b'\x3c\x80\x04\x08\x00\x00\x00b\x00\x00\x00a\x04\x04\x00\x00\x00r\x00\x00'),
            ('Visiblestring',          'bar', b'\x3a\x80\x04\x02ba\x04\x01r\x00\x00'),
            ('Generalstring',          'bar', b'\x3b\x80\x04\x02ba\x04\x01r\x00\x00'),
            ('Bmpstring',
             'fie',
             b'\x3e\x80\x04\x02\x00\x66\x04\x04\x00\x69\x00\x65\x00\x00'),
            ('Teletexstring',          'fum', b'\x34\x80\x04\x01f\x04\x02um\x00\x00'),
            #('SequenceOf',                [], b'\x30\x80\x00\x00'),
            #('SetOf',                     [], b'\x31\x80\x00\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assertEqual(all_types.decode(type_name, encoded), decoded)

    def test_decode_indefinite_length_in_primitive_encoding(self):
        """A BOOLEAN always uses primitive encoding with definite length, and
        decoding should fail if an indefinite length is found.

        """

        spec = 'A DEFINITIONS ::= BEGIN A ::= BOOLEAN END'
        foo = asn1tools.compile_string(spec)

        encoded = b'\x01\x80\xff'

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', encoded)

        self.assertEqual(
            str(cm.exception),
            'Expected definite length at offset 1, but got indefinite.')

    def test_versions(self):
        foo = asn1tools.compile_files('tests/files/versions.asn')

        # Encode as V1, decode as V1, V2 and V3
        decoded_v1 = {
            'userName': 'myUserName',
            'password': 'myPassword',
            'accountNumber': 54224445
        }

        encoded_v1 = foo.encode('V1', decoded_v1)

        self.assertEqual(foo.decode('V1', encoded_v1), decoded_v1)
        self.assertEqual(foo.decode('V2', encoded_v1), decoded_v1)
        self.assertEqual(foo.decode('V3', encoded_v1), decoded_v1)

        # Encode as V2, decode as V1, V2 and V3
        decoded_v2 = {
            'userName': 'myUserName',
            'password': 'myPassword',
            'accountNumber': 54224445,
            'minutesLastLoggedIn': 5
        }

        encoded_v2 = foo.encode('V2', decoded_v2)

        self.assertEqual(foo.decode('V1', encoded_v2), decoded_v1)
        self.assertEqual(foo.decode('V2', encoded_v2), decoded_v2)
        self.assertEqual(foo.decode('V3', encoded_v2), decoded_v2)

        # Encode as V3, decode as V1, V2 and V3
        decoded_v3 = {
            'userName': 'myUserName',
            'password': 'myPassword',
            'accountNumber': 54224445,
            'minutesLastLoggedIn': 5,
            'certificate': None,
            'thumb': None
        }

        encoded_v3 = foo.encode('V3', decoded_v3)

        self.assertEqual(foo.decode('V1', encoded_v3), decoded_v1)
        self.assertEqual(foo.decode('V2', encoded_v3), decoded_v2)
        self.assertEqual(foo.decode('V3', encoded_v3), decoded_v3)

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

    def test_issue_34(self):
        """Test that a choice type with a recursive member can be compiled and
        used.

        """

        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN "
            "A ::= SEQUENCE { "
            "  a B "
            "} "
            "B ::= CHOICE { "
            "  b A, "
            "  c NULL "
            "} "
            "END ")

        decoded = {'a': ('b', {'a': ('c', None)})}
        encoded = b'\x30\x08\xa0\x06\xa0\x04\xa0\x02\x81\x00'
        self.assert_encode_decode(foo, 'A', decoded, encoded)


if __name__ == '__main__':
    unittest.main()
