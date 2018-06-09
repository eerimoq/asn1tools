import unittest
from .utils import Asn1ToolsBaseTest

import asn1tools


CODECS = ['ber', 'der', 'jer', 'per', 'uper', 'xer']


class Asn1ToolsCodecsConsistencyTest(Asn1ToolsBaseTest):

    maxDiff = None

    def encode_decode_all_codecs(self, spec, values):
        foos = []

        for codec in CODECS:
            foos.append(asn1tools.compile_string(spec, codec))

        for value in values:
            decoded = value

            for foo in foos:
                encoded = foo.encode('A', decoded)
                decoded = foo.decode('A', encoded)
                self.assertEqual(type(decoded), type(value))
                self.assertEqual(decoded, value)

    def test_boolean(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "END",
            [True, False])

    def test_integer(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "END",
            [1, 123456789, -2, 0])

    def test_real(self):
        with self.assertRaises(NotImplementedError):
            self.encode_decode_all_codecs(
                "Foo DEFINITIONS AUTOMATIC TAGS ::= "
                "BEGIN "
                "A ::= REAL "
                "END",
                [0.0, 1.0])

    def test_null(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NULL "
            "END",
            [None])

    def test_bit_string(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BIT STRING "
            "END",
            [(b'\x58', 5), (b'\x58\x80', 9)])

    def test_octet_string(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OCTET STRING "
            "END",
            [b'', b'\x12\x34'])

    def test_object_identifier(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OBJECT IDENTIFIER "
            "END",
            ['1.2.33'])

    def test_enumerated(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= ENUMERATED { a(0), b(5) } "
            "END",
            ['a', 'b'])

    def test_sequence(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE { a NULL } "
            "END",
            [{'a': None}])

    def test_sequence_of(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE OF NULL "
            "END",
            [[], [None, None]])

    def test_choice(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= CHOICE { a NULL } "
            "END",
            [('a', None)])

    def test_utf8_string(self):
        self.encode_decode_all_codecs(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTF8String "
            "END",
            [u'hi'])


if __name__ == '__main__':
    unittest.main()
