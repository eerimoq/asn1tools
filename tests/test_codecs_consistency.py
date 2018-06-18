import unittest
from datetime import datetime
from .utils import Asn1ToolsBaseTest
import asn1tools


CODECS = ['ber', 'der', 'jer', 'oer', 'per', 'uper', 'xer']


class Asn1ToolsCodecsConsistencyTest(Asn1ToolsBaseTest):

    maxDiff = None

    def encode_decode_all_codecs(self, type_spec, values):
        spec = (
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= " + type_spec + " "
            + "END"
        )

        foos = []

        for codec in CODECS:
            foos.append(asn1tools.compile_string(spec, codec))

        gser = asn1tools.compile_string(spec, 'gser')

        for value in values:
            decoded = value

            for foo in foos:
                encoded = foo.encode('A', decoded)
                decoded = foo.decode('A', encoded)
                self.assertEqual(type(decoded), type(value))
                self.assertEqual(decoded, value)

            gser.encode('A', decoded)

    def test_boolean(self):
        self.encode_decode_all_codecs("BOOLEAN", [True, False])

    def test_integer(self):
        self.encode_decode_all_codecs("INTEGER", [1, 123456789, -2, 0])

    def test_real(self):
        with self.assertRaises(NotImplementedError):
            self.encode_decode_all_codecs("REAL", [0.0, 1.0])

    def test_null(self):
        self.encode_decode_all_codecs("NULL", [None])

    def test_bit_string(self):
        self.encode_decode_all_codecs("BIT STRING",
                                      [(b'\x58', 5), (b'\x58\x80', 9)])

    def test_octet_string(self):
        self.encode_decode_all_codecs("OCTET STRING", [b'', b'\x12\x34'])

    def test_object_identifier(self):
        self.encode_decode_all_codecs("OBJECT IDENTIFIER", ['1.2.33'])

    def test_enumerated(self):
        self.encode_decode_all_codecs("ENUMERATED { a(0), b(5) }", ['a', 'b'])

    def test_sequence(self):
        self.encode_decode_all_codecs("SEQUENCE { a NULL }", [{'a': None}])

    def test_sequence_of(self):
        self.encode_decode_all_codecs("SEQUENCE OF NULL", [[], [None, None]])

    def test_set(self):
        self.encode_decode_all_codecs("SET { a NULL }", [{'a': None}])

    def test_set_of(self):
        self.encode_decode_all_codecs("SET OF NULL", [[], [None, None]])

    def test_choice(self):
        self.encode_decode_all_codecs("CHOICE { a NULL }", [('a', None)])

    def test_utf8_string(self):
        self.encode_decode_all_codecs("UTF8String", [u'hi'])

    def test_numeric_string(self):
        self.encode_decode_all_codecs("NumericString", [u'123'])

    def test_printable_string(self):
        self.encode_decode_all_codecs("PrintableString", [u'hi'])

    def test_ia5_string(self):
        self.encode_decode_all_codecs("IA5String", [u'hi'])

    def test_visible_string(self):
        self.encode_decode_all_codecs("VisibleString", [u'hi'])

    def test_general_string(self):
        with self.assertRaises(NotImplementedError):
            self.encode_decode_all_codecs("GeneralString", [u'hi'])

    def test_bmp_string(self):
        self.encode_decode_all_codecs("BMPString", [u'hi'])

    def test_graphic_string(self):
        self.encode_decode_all_codecs("GraphicString", [u'hi'])

    def test_teletex_string(self):
        with self.assertRaises(NotImplementedError):
            self.encode_decode_all_codecs("TeletexString", [u'hi'])

    def test_universal_string(self):
        with self.assertRaises(NotImplementedError):
            self.encode_decode_all_codecs("UniversalString", [u'hi'])

    def test_utc_time(self):
        self.encode_decode_all_codecs("UTCTime", [datetime(2020, 3, 12)])

    def test_generalized_time(self):
        self.encode_decode_all_codecs("GeneralizedTime",
                                      [datetime(2021, 3, 12)])


if __name__ == '__main__':
    unittest.main()
