import unittest
from datetime import datetime
from .utils import Asn1ToolsBaseTest
import asn1tools


class Asn1ToolsCheckConstraintsTest(Asn1ToolsBaseTest):

    maxDiff = None

    def assert_encode_decode_ok(self, foo, datas):
        for type_name, decoded in datas:
            encoded = foo.encode(type_name, decoded, check_constraints=True)
            foo.decode(type_name, encoded, check_constraints=True)

    def assert_encode_decode_bad(self, foo, datas, decode_check=True):
        for type_name, decoded, message in datas:
            # Encode check.
            with self.assertRaises(asn1tools.ConstraintsError) as cm:
                foo.encode(type_name, decoded, check_constraints=True)

            self.assertEqual(str(cm.exception), message)

            # Decode check.
            if decode_check:
                encoded = foo.encode(type_name, decoded, check_constraints=False)

                with self.assertRaises(asn1tools.ConstraintsError) as cm:
                    foo.decode(type_name, encoded, check_constraints=True)

                self.assertEqual(str(cm.exception), message)

    def test_all_codecs(self):
        codecs = [
            'ber',
            'der',
            'gser',
            'jer',
            'per',
            'uper',
            'xer'
        ]

        for codec in codecs:
            foo = asn1tools.compile_string(
                "Foo DEFINITIONS AUTOMATIC TAGS ::= "
                "BEGIN "
                "A ::= INTEGER "
                "END",
                codec)

            encoded = foo.encode('A', 0, check_constraints=True)

            if codec != 'gser':
                foo.decode('A', encoded, check_constraints=True)

    def test_boolean(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "END")

        # Ok.
        datas = [
            ('A', True),
            ('A', False)
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_integer(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "B ::= INTEGER (5..99) "
            "C ::= INTEGER (-10..10) "
            "D ::= INTEGER (5..99, ...) "
            "E ::= INTEGER (1000..1000) "
            "F ::= SEQUENCE { "
            "  a INTEGER (4..4), "
            "  b INTEGER (40..40), "
            "  c INTEGER (400..400) "
            "} "
            "G ::= B (6..7) "
            "H ::= INTEGER (MIN..10) "
            "I ::= INTEGER (10..MAX) "
            "J ::= INTEGER (MIN..MAX) "
            "K ::= INTEGER (1..2 | 4..5) "
            "END")

        # Ok.
        datas = [
            ('A',  32768),
            ('A',      0),
            ('A', -32769),
            ('B',      5),
            ('B',      6),
            ('B',     99),
            ('C',    -10),
            ('C',     10),
            ('D',     99),
            ('E',   1000),
            ('F',   {'a': 4, 'b': 40, 'c': 400}),
            ('H',  -1000),
            ('H',     10),
            ('I',     10),
            ('I',   1000),
            ('J',  -1000),
            ('J',   1000),
            ('K',   1),
            ('K',   2)
        ]

        self.assert_encode_decode_ok(foo, datas)

        # ToDo: These should be good.
        datas = [
            ('K',
             4,
             'K: Expected an integer between 1 and 2, but got 4.'),
            ('K',
             5,
             'K: Expected an integer between 1 and 2, but got 5.')
        ]

        self.assert_encode_decode_bad(foo, datas)

        # Not ok.
        datas = [
            ('B',
             4,
             'B: Expected an integer between 5 and 99, but got 4.'),
            ('B',
             100,
             'B: Expected an integer between 5 and 99, but got 100.'),
            ('C',
             -11,
             'C: Expected an integer between -10 and 10, but got -11.'),
            ('C',
             11,
             'C: Expected an integer between -10 and 10, but got 11.'),
            ('E',
             0,
             'E: Expected an integer between 1000 and 1000, but got 0.'),
            ('F',
             {'a': 4, 'b': 41, 'c': 400},
             'F.b: Expected an integer between 40 and 40, but got 41.'),
            ('H',
             11,
             'H: Expected an integer between MIN and 10, but got 11.'),
            ('I',
             9,
             'I: Expected an integer between 10 and MAX, but got 9.'),
            # ToDo: 4..5 are allowed as well.
            ('K',
             3,
             'K: Expected an integer between 1 and 2, but got 3.')
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_real(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= REAL "
            "END")

        # Ok.
        datas = [
            ('A', 1.0)
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_null(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NULL "
            "END")

        # Ok.
        datas = [
            ('A', None)
        ]

        self.assert_encode_decode_ok(foo, datas)

    def test_bit_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BIT STRING "
            "B ::= BIT STRING (SIZE (10)) "
            "END")

        # Ok.
        datas = [
            ('A',  (b'', 0)),
            ('B',  (b'\x01\x23', 10))
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('B',
             (b'\x01\x23', 9),
             'B: Expected between 10 and 10 bits, but got 9.')
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_octet_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OCTET STRING "
            "B ::= OCTET STRING (SIZE (10)) "
            "C ::= OCTET STRING (SIZE (10, ...)) "
            "D ::= OCTET STRING (SIZE (10..MAX)) "
            "END")

        # Ok.
        datas = [
            ('A',  b''),
            ('B',  10 * b'\x23'),
            ('C',  11 * b'\x23'),
            ('D',  44 * b'\x23')
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('B',
             11 * b'\x01',
             'B: Expected between 10 and 10 bytes, but got 11.'),
            ('D',
             9 * b'\x01',
             'D: Expected between 10 and MAX bytes, but got 9.')
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_enumerated(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= ENUMERATED { a, b } "
            "END")

        # Ok.
        datas = [
            ('A',  'a')
        ]

        self.assert_encode_decode_ok(foo, datas)

    def test_sequence(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE { "
            "  a A OPTIONAL "
            "} "
            "END")

        # Ok.
        datas = [
            ('A',  {'a': {}})
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_sequence_of(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE (SIZE (2)) OF INTEGER (3..5)"
            "B ::= SEQUENCE (SIZE (2, ...)) OF INTEGER (3..5)"
            "C ::= SEQUENCE (SIZE (MIN..2)) OF INTEGER (3..5)"
            "END")

        # Ok.
        datas = [
            ('A',  [3, 4]),
            ('B',  [3, 4, 5]),
            ('C',  [3, 4])
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('A',
             [3, 4, 5],
             'A: Expected a list of between 2 and 2 elements, but got 3.'),
            ('A',
             [3, 6],
             'A: Expected an integer between 3 and 5, but got 6.'),
            ('C',
             [3, 4, 5],
             'C: Expected a list of between MIN and 2 elements, but got 3.')
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_numeric_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NumericString "
            "END")

        # Ok.
        datas = [
            ('A',  '0123456789 ')
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('A',
             'a',
             "A: Expected a character in ' 0123456789', but got 'a' (0x61)."),
            ('A',
             '-',
             "A: Expected a character in ' 0123456789', but got '-' (0x2d).")
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_printable_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= PrintableString "
            "END")

        # Ok.
        datas = [
            ('A',  '09azAZ')
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('A',
             '{',
             "A: Expected a character in '"
             "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
             " '()+,-./:=?', but got '{' (0x7b).")
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_ia5_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= IA5String "
            "END")

        # Ok.
        datas = [
            ('A',  '09azAZ')
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('A',
             b'\x81'.decode('latin-1'),
             "A: Expected a character in '................................ !\"#$%"
             "&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcde"
             "fghijklmnopqrstuvwxyz{|}~.', but got '.' (0x81).")
        ]

        self.assert_encode_decode_bad(foo, datas, decode_check=False)

    def test_visible_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= VisibleString "
            "B ::= VisibleString (SIZE (2..5)) "
            "C ::= VisibleString (FROM (\"a\"..\"j\" | \"u\"..\"w\")) "
            "D ::= VisibleString (SIZE (2..5, ...)) "
            "END")

        # Ok.
        datas = [
            ('A',  '123'),
            ('B',  '12'),
            ('B',  '12345'),
            ('C',  'abijuvw'),
            ('D',  '123456')
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('B',
             '1',
             'B: Expected between 2 and 5 characters, but got 1.'),
            ('B',
             '123456',
             'B: Expected between 2 and 5 characters, but got 6.'),
            ('C',
             'k',
             "C: Expected a character in 'abcdefghijuvw', but got 'k' (0x6b).")
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_utf8_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTF8String "
            "B ::= UTF8String (SIZE (2..5)) "
            "END")

        # Ok.
        datas = [
            ('A',  'Hello'),
            ('B',  '12'),
            ('B',  '12345')
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('B',
             '1',
             'B: Expected between 2 and 5 characters, but got 1.'),
            ('B',
             '123456',
             'B: Expected between 2 and 5 characters, but got 6.')
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_utc_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTCTime "
            "END")

        # Ok.
        datas = [
            ('A',  datetime(1982, 1, 2, 12, 0))
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
        ]

        self.assert_encode_decode_bad(foo, datas)

    def test_choice(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= CHOICE { a INTEGER (1..2) } "
            "END")

        # Ok.
        datas = [
            ('A',  ('a', 1))
        ]

        self.assert_encode_decode_ok(foo, datas)

        # Not ok.
        datas = [
            ('A',
             ('a', 3),
             'A.a: Expected an integer between 1 and 2, but got 3.')
        ]

        self.assert_encode_decode_bad(foo, datas)


if __name__ == '__main__':
    unittest.main()
