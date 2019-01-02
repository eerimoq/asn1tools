#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
from .utils import Asn1ToolsBaseTest
from datetime import datetime
from copy import deepcopy
import asn1tools

sys.path.append('tests/files/ieee')

from ieee1609_2 import EXPECTED as IEEE1609_2


class Asn1ToolsOerTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_boolean(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "END",
            'oer')

        datas = [
            ('A',                     True, b'\xff'),
            ('A',                    False, b'\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_integer(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "B ::= INTEGER (-128..127) "
            "C ::= INTEGER (-32768..32767) "
            "D ::= INTEGER (-2147483648..2147483647) "
            "E ::= INTEGER (-9223372036854775808..9223372036854775807) "
            "F ::= INTEGER (0..255) "
            "G ::= INTEGER (0..65536) "
            "H ::= INTEGER (0..4294967296) "
            "I ::= INTEGER (0..18446744073709551615) "
            "J ::= INTEGER (0..18446744073709551616) "
            "END",
            'oer')

        datas = [
            ('A',              0, b'\x01\x00'),
            ('A',            128, b'\x02\x00\x80'),
            ('A',         100000, b'\x03\x01\x86\xa0'),
            ('A',           -255, b'\x02\xff\x01'),
            ('A',       -1234567, b'\x03\xed\x29\x79'),
            ('B',             -2, b'\xfe'),
            ('C',             -2, b'\xff\xfe'),
            ('D',             -2, b'\xff\xff\xff\xfe'),
            ('E',             -2, b'\xff\xff\xff\xff\xff\xff\xff\xfe'),
            ('B',              1, b'\x01'),
            ('C',              1, b'\x00\x01'),
            ('D',              1, b'\x00\x00\x00\x01'),
            ('E',              1, b'\x00\x00\x00\x00\x00\x00\x00\x01'),
            ('B',            127, b'\x7f'),
            ('C',            127, b'\x00\x7f'),
            ('D',            127, b'\x00\x00\x00\x7f'),
            ('E',            127, b'\x00\x00\x00\x00\x00\x00\x00\x7f'),
            ('J',              1, b'\x01\x01')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_real(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= REAL "
            "B ::= REAL (WITH COMPONENTS { "
            "                mantissa (-16777215..16777215), "
            "                base (2), "
            "                exponent (-149..104) "
            "            })"
            "C ::= REAL (WITH COMPONENTS { "
            "                mantissa (-9007199254740991..9007199254740991), "
            "                base (2), "
            "                exponent (-1074..971) "
            "            })"
            "D ::= REAL (WITH COMPONENTS { "
            "                mantissa (-1..1), "
            "                base (10), "
            "                exponent (-1..1) "
            "            })"
            "E ::= REAL (WITH COMPONENTS { "
            "                mantissa (1..2) "
            "            })"
            "END",
            'oer')

        datas = [
            ('A',                        0.0, b'\x00'),
            ('A',                        1.0, b'\x03\x80\x00\x01'),
            ('A',                      100.0, b'\x03\x80\x02\x19'),
            ('A',                     -100.0, b'\x03\xc0\x02\x19'),
            ('B',                        0.0, b'\x00\x00\x00\x00'),
            ('B',                        1.0, b'\x3f\x80\x00\x00'),
            ('B',                  2 ** -126, b'\x00\x80\x00\x00'),
            ('B',  (1 - 2 ** -24) * 2 ** 128, b'\x7f\x7f\xff\xff'),
            ('C',                        0.0, b'\x00\x00\x00\x00\x00\x00\x00\x00'),
            ('C',                        1.0, b'\x3f\xf0\x00\x00\x00\x00\x00\x00'),
            ('C',                 2 ** -1022, b'\x00\x10\x00\x00\x00\x00\x00\x00'),
            ('C', (2 - 2 ** -52) * 2 ** 1023, b'\x7f\xef\xff\xff\xff\xff\xff\xff')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Too large values.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('B', 2 ** 128)

        self.assertEqual(
            str(cm.exception),
            'Expected an IEEE 754 32 bits floating point number, but got '
            '340282366920938463463374607431768211456.')

        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('C', 2 ** 1024)

        self.assertEqual(
            str(cm.exception),
            'Expected an IEEE 754 64 bits floating point number, but got '
            '17976931348623159077293051907890247336179769789423065727343008115'
            '77326758055009631327084773224075360211201138798713933576587897688'
            '14416622492847430639474124377767893424865485276302219601246094119'
            '45308295208500576883815068234246288147391311054082723716335051068'
            '4586298239947245938479716304835356329624224137216.')

        # Non-float value.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('C', 2 ** 1025)

        self.assertEqual(
            str(cm.exception),
            'Expected an IEEE 754 64 bits floating point number, but got 35953'
            '86269724631815458610381578049467235953957884613145468601623154653'
            '51611001926265416954644815072042240227759742786715317579537628833'
            '24498569486127894824875553578684973097055260443920249218823890616'
            '59041700115376763013646849257629478262210816544743267010213691725'
            '96479894491876959432609670712659248448274432.')

    def test_null(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NULL "
            "END",
            'oer')

        datas = [
            ('A',        None, b'')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_bit_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BIT STRING "
            "B ::= BIT STRING (SIZE (9)) "
            "C ::= BIT STRING (SIZE (9, ...)) "
            "D ::= BIT STRING (SIZE (5..7)) "
            "END",
            'oer')

        datas = [
            ('A',          (b'\x40', 4), b'\x02\x04\x40'),
            ('A',          (b'\x41', 8), b'\x02\x00\x41'),
            ('B',      (b'\x12\x80', 9), b'\x12\x80'),
            ('C',      (b'\x12\x80', 9), b'\x03\x07\x12\x80'),
            ('D',          (b'\x34', 6), b'\x02\x02\x34')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_octet_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OCTET STRING "
            "B ::= OCTET STRING (SIZE (3)) "
            "C ::= OCTET STRING (SIZE (3, ...)) "
            "D ::= OCTET STRING (SIZE (3..7)) "
            "END",
            'oer')

        datas = [
            ('A',      b'\x12\x34', b'\x02\x12\x34'),
            ('A',      999 * b'\x01', b'\x82\x03\xe7' + 999 * b'\x01'),
            ('B',  b'\x12\x34\x56', b'\x12\x34\x56'),
            ('C',  b'\x12\x34\x56', b'\x03\x12\x34\x56'),
            ('D',  b'\x12\x34\x56', b'\x03\x12\x34\x56')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_object_identifier(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OBJECT IDENTIFIER "
            "END",
            'oer')

        datas = [
            ('A',                   '1.2', b'\x01\x2a'),
            ('A',              '1.2.3321', b'\x03\x2a\x99\x79')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_external(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= EXTERNAL "
            "END",
            'oer')

        datas = [
            ('A',
             {'encoding': ('octet-aligned', b'\x12')},
             b'\x00\x81\x01\x12')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_enumerated(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= ENUMERATED { a(1) } "
            "B ::= ENUMERATED { a(128) } "
            "C ::= ENUMERATED { a(0), b(127) } "
            "D ::= ENUMERATED { a(0), ..., b(127) } "
            "E ::= ENUMERATED { a(-1), b(1234) } "
            "END",
            'oer')

        datas = [
            ('A',                    'a', b'\x01'),
            ('B',                    'a', b'\x82\x00\x80'),
            ('C',                    'a', b'\x00'),
            ('C',                    'b', b'\x7f'),
            ('D',                    'a', b'\x00'),
            ('D',                    'b', b'\x7f'),
            ('E',                    'a', b'\x81\xff'),
            ('E',                    'b', b'\x82\x04\xd2')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Encoding bad enumeration value.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('C', 'c')

        self.assertEqual(
            str(cm.exception),
            "Expected enumeration value 'a' or 'b', but got 'c'.")

        # Decoding bad enumeration value.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x02')

        self.assertEqual(str(cm.exception),
                         "Expected enumeration value 1, but got 2.")

    def test_sequence(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE {} "
            "B ::= SEQUENCE { "
            "  a INTEGER DEFAULT 0 "
            "} "
            "C ::= SEQUENCE { "
            "  a BOOLEAN "
            "} "
            "D ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ... "
            "} "
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN "
            "} "
            "F ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]] "
            "} "
            "G ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN OPTIONAL "
            "} "
            "H ::= SEQUENCE { "
            "  a H OPTIONAL "
            "} "
            "I ::= SEQUENCE { "
            "  a BOOLEAN OPTIONAL "
            "} "
            "J ::= I (WITH COMPONENTS { a PRESENT }) "
            "K ::= I (WITH COMPONENTS { a ABSENT }) "
            "L ::= I (J | K) "
            "M ::= SEQUENCE { "
            "  a D, "
            "  b INTEGER "
            "} "
            "N ::= SEQUENCE { "
            "  a E, "
            "  b INTEGER "
            "} "
            "END",
            'oer')

        datas = [
            ('A',                     {}, b''),
            ('B',               {'a': 0}, b'\x00'),
            ('B',               {'a': 1}, b'\x80\x01\x01'),
            ('C',            {'a': True}, b'\xff'),
            ('D',            {'a': True}, b'\x00\xff'),
            ('E',            {'a': True}, b'\x00\xff'),
            ('E',
             {'a': True, 'b': True},
             b'\x80\xff\x02\x07\x80\x01\xff'),
            ('F',            {'a': True}, b'\x00\xff'),
            ('F',
             {'a': True, 'b': True},
             b'\x80\xff\x02\x07\x80\x01\xff'),
            ('G',            {'a': True}, b'\x00\xff'),
            ('G',
             {'a': True, 'b': True},
             b'\x80\xff\x02\x07\x80\x01\xff'),
            ('H',                     {}, b'\x00'),
            ('H',              {'a': {}}, b'\x80\x00'),
            ('J',            {'a': True}, b'\x80\xff'),
            ('K',                     {}, b'\x00'),
            ('L',            {'a': True}, b'\x80\xff'),
            ('L',                     {}, b'\x00'),
            ('N',
             {'a': {'a': True, 'b': True}, 'b': 5},
             b'\x80\xff\x02\x07\x80\x01\xff\x01\x05')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Non-symmetrical encoding and decoding because default values
        # are not encoded, but part of the decoded (given that the
        # root and addition is present).
        self.assertEqual(foo.encode('B', {}), b'\x00')
        self.assertEqual(foo.decode('B', b'\x00'), {'a': 0})

        # Decode E as D. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('D', b'\x80\xff\x02\x07\x80\x01\xff'),
                         {'a': True})

        # Decode N as M. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('M', b'\x80\xff\x02\x07\x80\x01\xff\x01\x05'),
                         {'a': {'a': True}, 'b': 5})

        # Out of data skipping extension member a.b.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('M', b'\x80\xff\x02\x07\x80\x01')

        self.assertEqual(str(cm.exception),
                         "a: out of data at bit offset 48 (6.0 bytes)")

        # Out of data decoding extension member a.b.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('N', b'\x80\xff\x02\x07\x80\x01')

        self.assertEqual(str(cm.exception),
                         'a: b: out of data at bit offset 48 (6.0 bytes)')

    def test_set(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SET { "
            "  a [444] INTEGER, "
            "  b [5] INTEGER, "
            "  c [APPLICATION 5] INTEGER "
            "} "
            "END",
            'oer')

        datas = [
            ('A', {'a': 5, 'b': 6, 'c': 7}, b'\x01\x07\x01\x06\x01\x05')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_sequence_of(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE OF INTEGER "
            "END",
            'oer')

        datas = [
            ('A',                [], b'\x01\x00'),
            ('A',            [1, 2], b'\x01\x02\x01\x01\x01\x02'),
            ('A',
             1000 * [0],
             b'\x02\x03\xe8' + 1000 * b'\x01\x00')
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
            "  ..., "
            "  b BOOLEAN, "
            "  c INTEGER "
            "} "
            "C ::= CHOICE { "
            "  a CHOICE { "
            "    a [3] INTEGER"
            "  } "
            "} "
            "D ::= CHOICE { "
            "  a [62] BOOLEAN, "
            "  b [APPLICATION 63] BOOLEAN, "
            "  c [PRIVATE 963] BOOLEAN "
            "} "
            "END",
            'oer')

        datas = [
            ('A',          ('a', True), b'\x80\xff'),
            ('B',          ('a', True), b'\x80\xff'),
            ('B',          ('b', True), b'\x81\x01\xff'),
            ('B',             ('c', 0), b'\x82\x02\x01\x00'),
            ('B',          ('c', 1000), b'\x82\x03\x02\x03\xe8'),
            ('C',    ('a', ('a', 150)), b'\x80\x83\x02\x00\x96'),
            ('D',         ('a', False), b'\xbe\x00'),
            ('D',         ('b', False), b'\x7f\x3f\x00'),
            ('D',         ('c', False), b'\xff\x87\x43\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Encode bad value.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('B', ('foo', None))

        self.assertEqual(str(cm.exception),
                         "Expected choice 'a', 'b' or 'c', but got 'foo'.")

        # Decode bad value.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x81\x00\xff')

        self.assertEqual(
            str(cm.exception),
            "Expected choice member tag '80', but got '81'.")

    def test_uft8_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTF8String "
            "B ::= UTF8String (SIZE (3)) "
            "C ::= UTF8String (SIZE (3, ...)) "
            "D ::= UTF8String (SIZE (3..7)) "
            "END",
            'oer')

        datas = [
            ('A',        'foo', b'\x03\x66\x6f\x6f'),
            ('B',        'foo', b'\x66\x6f\x6f'),
            ('C',        'foo', b'\x03\x66\x6f\x6f'),
            ('D',        'foo', b'\x03\x66\x6f\x6f')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_numeric_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NumericString "
            "B ::= NumericString (SIZE (3)) "
            "C ::= NumericString (SIZE (3, ...)) "
            "D ::= NumericString (SIZE (3..7)) "
            "END",
            'oer')

        datas = [
            ('A',        '123', b'\x03\x31\x32\x33'),
            ('B',        '123', b'\x31\x32\x33'),
            ('C',        '123', b'\x03\x31\x32\x33'),
            ('D',        '123', b'\x03\x31\x32\x33')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_printable_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= PrintableString "
            "B ::= PrintableString (SIZE (3)) "
            "C ::= PrintableString (SIZE (3, ...)) "
            "D ::= PrintableString (SIZE (3..7)) "
            "END",
            'oer')

        datas = [
            ('A',        'foo', b'\x03\x66\x6f\x6f'),
            ('B',        'foo', b'\x66\x6f\x6f'),
            ('C',        'foo', b'\x03\x66\x6f\x6f'),
            ('D',        'foo', b'\x03\x66\x6f\x6f')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_ia5_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= IA5String "
            "B ::= IA5String (SIZE (3)) "
            "C ::= IA5String (SIZE (3, ...)) "
            "D ::= IA5String (SIZE (3..7)) "
            "END",
            'oer')

        datas = [
            ('A',        'foo', b'\x03\x66\x6f\x6f'),
            ('B',        'foo', b'\x66\x6f\x6f'),
            ('C',        'foo', b'\x03\x66\x6f\x6f'),
            ('D',        'foo', b'\x03\x66\x6f\x6f')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_visible_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= VisibleString "
            "B ::= VisibleString (SIZE (3)) "
            "C ::= VisibleString (SIZE (3, ...)) "
            "D ::= VisibleString (SIZE (3..7)) "
            "END",
            'oer')

        datas = [
            ('A',        'foo', b'\x03\x66\x6f\x6f'),
            ('B',        'foo', b'\x66\x6f\x6f'),
            ('C',        'foo', b'\x03\x66\x6f\x6f'),
            ('D',        'foo', b'\x03\x66\x6f\x6f')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_general_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GeneralString "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b GeneralString "
            "} "
            "END",
            'oer')

        datas = [
            ('A',                      '', b'\x00'),
            ('A',                     '2', b'\x01\x32'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\x01\x4b')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_graphic_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GraphicString "
            "END",
            'oer')

        datas = [
            ('A',                      '', b'\x00'),
            ('A',                     '2', b'\x01\x32')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_teletex_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= TeletexString "
            "END",
            'oer')

        datas = [
            ('A',                  u'123', b'\x03\x31\x32\x33')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_universal_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UniversalString "
            "END",
            'oer')

        datas = [
            ('A',
             u'åäö',
             b'\x0c\x00\x00\x00\xe5\x00\x00\x00\xe4\x00\x00\x00\xf6'),
            ('A',
             u'1𐈃Q',
             b'\x0c\x00\x00\x00\x31\x00\x01\x02\x03\x00\x00\x00\x51')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_utc_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS IMPLICIT TAGS ::= "
            "BEGIN "
            "A ::= UTCTime "
            "END",
            'oer')

        datas = [
            ('A',
             datetime(2043, 1, 31, 23, 59, 59),
             b'\x0d\x34\x33\x30\x31\x33\x31\x32\x33\x35\x39\x35\x39\x5a')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_generalized_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GeneralizedTime "
            "END",
            'oer')

        datas = [
            ('A',
             datetime(2080, 10, 9, 13, 0, 5, 342000),
             b'\x12\x32\x30\x38\x30\x31\x30\x30\x39\x31\x33\x30\x30\x30\x35'
             b'\x2e\x33\x34\x32')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'oer')

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

    def test_overview_of_oer(self):
        foo = asn1tools.compile_files('tests/files/overview_of_oer.asn',
                                      'oer')

        datas = [
            ('A',
             {'a1': 4, 'a2': 4, 'a3': 4, 'a4': 4, 'a5': 1024, 'a6': 4, 'a7': 4},
             (
                 b'\xc0\x04\x00\x04\x00\x04\x00\x00\x00\x04\x02\x04\x00\x01\x04'
                 b'\x01\x04'
             )),
            ('B',
             {
                 'b1': 'ABC',
                 'b2': 'ABC',
                 'b3': 'ABC',
                 'b4': b'\x01\x02\x03\x04',
                 'b5': (b'\x50', 4),
                 'b6': (b'\x50', 4)
             },
             (
                 b'\x03\x41\x42\x43\x41\x42\x43\x03\x41\x42\x43\x04\x01\x02\x03'
                 b'\x04\x50\x02\x04\x50'
             )),
            ('C',
             ('c2', ['b', 'c', 'd', 'e']),
             b'\x81\x01\x04\x01\x02\x03\x04')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_x691_a1(self):
        a1 = asn1tools.compile_files('tests/files/x691_a1.asn', 'oer')

        decoded = {
            'name': {
                'givenName': 'John',
                'initial': 'P',
                'familyName': 'Smith'
            },
            'title': 'Director',
            'number': 51,
            'dateOfHire': '19710917',
            'nameOfSpouse': {
                'givenName': 'Mary',
                'initial': 'T',
                'familyName': 'Smith'
            },
            'children': [
                {
                    'name': {
                        'givenName': 'Ralph',
                        'initial': 'T',
                        'familyName': 'Smith'
                    },
                    'dateOfBirth': '19571111'
                },
                {
                    'name': {
                        'givenName': 'Susan',
                        'initial': 'B',
                        'familyName': 'Jones'
                    },
                    'dateOfBirth': '19590717'
                }
            ]
        }

        encoded = (
            b'\x80\x04\x4a\x6f\x68\x6e\x01\x50\x05\x53\x6d\x69\x74\x68\x01\x33'
            b'\x08\x44\x69\x72\x65\x63\x74\x6f\x72\x08\x31\x39\x37\x31\x30\x39'
            b'\x31\x37\x04\x4d\x61\x72\x79\x01\x54\x05\x53\x6d\x69\x74\x68\x01'
            b'\x02\x05\x52\x61\x6c\x70\x68\x01\x54\x05\x53\x6d\x69\x74\x68\x08'
            b'\x31\x39\x35\x37\x31\x31\x31\x31\x05\x53\x75\x73\x61\x6e\x01\x42'
            b'\x05\x4a\x6f\x6e\x65\x73\x08\x31\x39\x35\x39\x30\x37\x31\x37'
        )

        self.assert_encode_decode(a1, 'PersonnelRecord', decoded, encoded)

    def test_ieee1609_2(self):
        foo = asn1tools.compile_dict(deepcopy(IEEE1609_2), 'oer')

        decoded = {
            'version': 1,
            'content': (
                'caCerts',
                [
                    {
                        'version': 3,
                        'type': 'explicit',
                        'issuer': ('sha256AndDigest', 8 * b'\x01'),
                        'toBeSigned': {
                            'id': ('none', None),
                            'cracaId': 3 * b'\x32',
                            'crlSeries': 65535,
                            'validityPeriod': {
                                'start': 12345,
                                'duration': ('seconds', 5)
                            },
                            'appPermissions': [],
                            'certIssuePermissions': [],
                            'certRequestPermissions': [],
                            'verifyKeyIndicator': (
                                'verificationKey',
                                (
                                    'ecdsaNistP256',
                                    (
                                        'uncompressed',
                                        {
                                            'x': 32 * b'\x14',
                                            'y': 32 * b'\x54'
                                        }
                                    )
                                )
                            )
                        },
                        'signature': (
                            'ecdsaNistP256Signature',
                            {
                                'r' : ('x-only' , 32 * b'\x98'),
                                's' : 32 * b'\xab'
                            }
                        )
                    }
                ]
            )
        }

        encoded = (
            b'\x01\x80\x01\x01\x80\x03\x00\x80\x01\x01\x01\x01\x01\x01\x01\x01'
            b'\x1c\x83\x32\x32\x32\xff\xff\x00\x00\x30\x39\x82\x00\x05\x01\x00'
            b'\x01\x00\x01\x00\x80\x80\x84\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14\x14'
            b'\x14\x14\x14\x14\x14\x14\x14\x54\x54\x54\x54\x54\x54\x54\x54\x54'
            b'\x54\x54\x54\x54\x54\x54\x54\x54\x54\x54\x54\x54\x54\x54\x54\x54'
            b'\x54\x54\x54\x54\x54\x54\x54\x80\x80\x98\x98\x98\x98\x98\x98\x98'
            b'\x98\x98\x98\x98\x98\x98\x98\x98\x98\x98\x98\x98\x98\x98\x98\x98'
            b'\x98\x98\x98\x98\x98\x98\x98\x98\x98\xab\xab\xab\xab\xab\xab\xab'
            b'\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab'
            b'\xab\xab\xab\xab\xab\xab\xab\xab\xab'
        )

        self.assert_encode_decode(foo,
                                  'Ieee1609dot2Peer2PeerPDU',
                                  decoded,
                                  encoded)

    def test_out_of_data(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "B ::= OCTET STRING "
            "C ::= SEQUENCE { "
            "  ..., "
            "  a BOOLEAN "
            "} "
            "END",
            'oer')

        # Fails trying to read a non-negative number.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'')

        self.assertEqual(str(cm.exception),
                         "out of data at bit offset 0 (0.0 bytes)")

        # Fails trying to read 2 bytes, but only one available.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('B', b'\x02\x00')

        self.assertEqual(str(cm.exception),
                         "out of data at bit offset 8 (1.0 bytes)")

        # Fails trying to read the single additions present bit.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('C', b'')

        self.assertEqual(str(cm.exception),
                         "out of data at bit offset 0 (0.0 bytes)")

    def test_c_source(self):
        files = [
            'tests/files/c_source/c_source.asn'
        ]
        foo = asn1tools.compile_files(files, 'oer')

        # Type L - decode error bad length.
        with self.assertRaises(asn1tools.codecs.OutOfDataError):
            foo.decode('L', b'\x82\x01\xff')

        with self.assertRaises(asn1tools.codecs.OutOfDataError):
            foo.decode('L', b'\x83\x01\xff\x00')

        with self.assertRaises(asn1tools.codecs.OutOfDataError):
            foo.decode('L', b'\x84\x01\x00\x01\x00')

        with self.assertRaises(asn1tools.codecs.OutOfDataError):
            foo.decode('L', b'\x83')

        with self.assertRaises(asn1tools.codecs.OutOfDataError):
            foo.decode('L', b'\xff\x00')


if __name__ == '__main__':
    unittest.main()
