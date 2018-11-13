import json
import unittest
from datetime import date
from datetime import time
from datetime import datetime
from .utils import Asn1ToolsBaseTest
import asn1tools


CODECS = ['ber', 'der', 'jer', 'oer', 'per', 'uper', 'xer']
ALL_CODECS = CODECS + ['gser']


def loadb(encoded):
    return json.loads(encoded.decode('utf-8'))


class Asn1ToolsCodecsConsistencyTest(Asn1ToolsBaseTest):

    maxDiff = None

    def encode_decode_all_codecs(self,
                                 type_spec,
                                 values,
                                 numeric_enums=False):
        spec = (
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= " + type_spec + " "
            + "END"
        )

        foos = []

        for codec in CODECS:
            foos.append(asn1tools.compile_string(spec,
                                                 codec,
                                                 numeric_enums=numeric_enums))

        gser = asn1tools.compile_string(spec,
                                        'gser',
                                        numeric_enums=numeric_enums)

        for value in values:
            decoded = value

            for foo in foos:
                encoded = foo.encode('A', decoded)
                decoded = foo.decode('A', encoded)
                self.assertEqual(type(decoded), type(value))
                self.assertEqual(decoded, value)

            gser.encode('A', decoded)

    def encode_decode_codec(self, spec, codec, type_name, decoded, encoded):
        encoded_message = spec.encode(type_name,
                                      decoded,
                                      check_constraints=True)

        if codec == 'jer':
            self.assertEqual(loadb(encoded), loadb(encoded_message))
        else:
            self.assertEqual(encoded_message, encoded)

        if codec == 'gser':
            return

        decoded_message = spec.decode(type_name,
                                      encoded,
                                      check_constraints=True)
        self.assertEqual(decoded_message, decoded)

    def encode_decode_codecs(self,
                             type_spec,
                             decoded,
                             encoded):
        spec = (
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= " + type_spec + " "
            + "END"
        )

        for codec, encoded_message in zip(ALL_CODECS, encoded):
            foo = asn1tools.compile_string(spec, codec)
            self.encode_decode_codec(foo,
                                     codec,
                                     'A',
                                     decoded,
                                     encoded_message)

    def encode_decode_codecs_file(self,
                                  filename,
                                  type_name,
                                  decoded,
                                  encoded):
        for codec, encoded_message in zip(ALL_CODECS, encoded):
            foo = asn1tools.compile_files(filename, codec)
            self.encode_decode_codec(foo,
                                     codec,
                                     type_name,
                                     decoded,
                                     encoded_message)

    def decode_codecs(self, type_spec, decoded, encoded):
        spec = (
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= " + type_spec + " "
            + "END"
        )

        for codec, encoded_message in zip(CODECS, encoded):
            foo = asn1tools.compile_string(spec, codec)
            decoded_message = foo.decode('A',
                                         encoded_message,
                                         check_constraints=True)
            self.assertEqual(decoded_message, decoded)

    def test_boolean(self):
        self.encode_decode_all_codecs("BOOLEAN", [True, False])

    def test_integer(self):
        self.encode_decode_all_codecs("INTEGER", [1, 123456789, -2, 0])

    def test_integer_versions(self):
        decoded_v1 = 2
        decoded_v2 = 2

        encoded_v2 = [
            b'\x02\x01\x02',
            b'\x02\x01\x02',
            b'2',
            b'\x01\x02',
            b'\x80\x01\x02',
            b'\x80\x81\x00',
            b'<A>2</A>'
        ]

        self.decode_codecs('INTEGER (1, ..., 2)',
                           decoded_v2,
                           encoded_v2)

        self.decode_codecs('INTEGER (1, ...)',
                           decoded_v1,
                           encoded_v2)

    def test_real(self):
        self.encode_decode_all_codecs("REAL", [0.0, 1.0, -1.0])

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

    def test_enumerated_numeric(self):
        self.encode_decode_all_codecs("ENUMERATED { a(0), b(5) }",
                                      [0, 5],
                                      numeric_enums=True)

    def test_enumerated_versions(self):
        # Unknown enumeration value 'c' decoded as None.
        decoded_v1 = None
        decoded_v2 = 'c'

        encoded_v2 = [
            b'\x0a\x01\x02',
            b'\x0a\x01\x02',
            b'"c"',
            b'\x02',
            b'\x80',
            b'\x80',
            b'<A><c /></A>'
        ]

        self.decode_codecs('ENUMERATED {a, b, ..., c}',
                           decoded_v2,
                           encoded_v2)

        self.decode_codecs('ENUMERATED {a, b, ...}',
                           decoded_v1,
                           encoded_v2)

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

    def test_choice_versions(self):
        # Unknown choice 'c' decoded as (None, None).
        decoded_v1 = {
            'a': (None, None),
            'd': True
        }

        decoded_v2 = {
            'a': ('c', None),
            'd': True
        }

        encoded_v2 = [
            b'\x30\x07\xa0\x02\x81\x00\x81\x01\xff',
            b'\x30\x07\xa0\x02\x81\x00\x81\x01\xff',
            b'{"a":{"c":null},"d":true}',
            b'\x81\x00\xff',
            b'\x80\x00\x80',
            b'\x80\x00\x80',
            b'<A><a><c /></a><d><true /></d></A>'
        ]

        self.decode_codecs('SEQUENCE { '
                           '  a CHOICE {b NULL, ..., c NULL}, '
                           '  d BOOLEAN '
                           '}',
                           decoded_v2,
                           encoded_v2)

        self.decode_codecs('SEQUENCE { '
                           '  a CHOICE {b NULL, ...}, '
                           '  d BOOLEAN '
                           '}',
                           decoded_v1,
                           encoded_v2)

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
        self.encode_decode_all_codecs("GeneralString", [u'hi'])

    def test_bmp_string(self):
        self.encode_decode_all_codecs("BMPString", [u'hi'])

    def test_graphic_string(self):
        self.encode_decode_all_codecs("GraphicString", [u'hi'])

    def test_teletex_string(self):
        self.encode_decode_all_codecs("TeletexString", [u'hi'])

    def test_universal_string(self):
        self.encode_decode_all_codecs("UniversalString", [u'hi'])

    def test_utc_time(self):
        self.encode_decode_all_codecs("UTCTime", [datetime(2020, 3, 12)])

    def test_generalized_time(self):
        self.encode_decode_all_codecs("GeneralizedTime",
                                      [datetime(2021, 3, 12)])

    def test_error_location(self):
        spec = (
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE { "
            "  a SEQUENCE { "
            "    b CHOICE { "
            "      c SEQUENCE { "
            "        d INTEGER "
            "      } "
            "    } "
            "  } "
            "}"
            "END"
        )

        for codec in ALL_CODECS:
            foo = asn1tools.compile_string(spec, codec)

            with self.assertRaises(asn1tools.EncodeError) as cm:
                foo.encode('A', {'a': {'b': ('c', {})}})

            self.assertEqual(str(cm.exception),
                             "a: b: c: Sequence member 'd' not found in {}.")

    def test_recursive(self):
        spec = (
            "SEQUENCE { "
            "  a B "
            "} "
            "B ::= CHOICE { "
            "  b A, "
            "  c NULL "
            "} "
        )

        self.encode_decode_all_codecs(spec, [{'a': ('b', {'a': ('c', None)})}])

    def test_with_components(self):
        decoded = {
            'a': 1,
            'b': {
                'c': [
                    (
                        'f', True
                    )
                ],
                'd': 2
            }
        }

        encoded = [
            b'\x30\x0d\x80\x01\x01\xa1\x08\xa0\x03\x81\x01\xff\x81\x01\x02',
            b'\x30\x0d\x80\x01\x01\xa1\x08\xa0\x03\x81\x01\xff\x81\x01\x02',
            b'{"a":1,"b":{"c":[{"f":true}],"d":2}}',
            b'\x01\x01\x01\x81\xff\x01\x02',
            b'\x01\x60\x01\x02',
            b'\x01\x60\x20\x40',
            b'<Foo><a>1</a><b><c><f><true /></f></c><d>2</d></b></Foo>',
            b'foo Foo ::= { a 1, b { c { f : TRUE }, d 2 } }'
        ]

        self.encode_decode_codecs_file('tests/files/with_components.asn',
                                       'Foo',
                                       decoded,
                                       encoded)

    def test_integer_min_max(self):
        decoded = 5

        encoded = [
            b'\x02\x01\x05',
            b'\x02\x01\x05',
            b'5',
            b'\x01\x05',
            b'\x01\x05',
            b'\x01\x05',
            b'<A>5</A>',
            b'a A ::= 5'
        ]

        self.encode_decode_codecs('INTEGER (MIN..MAX)',
                                  decoded,
                                  encoded)

    def test_enumerated_all_except(self):
        decoded = 'c'

        encoded = [
            b'\x0a\x01\x02',
            b'\x0a\x01\x02',
            b'"c"',
            b'\x02',
            b'\x40',
            b'\x40',
            b'<A><c /></A>',
            b'a A ::= c'
        ]

        self.encode_decode_codecs('ENUMERATED {a, b, c, d, e} (ALL EXCEPT b)',
                                  decoded,
                                  encoded)

    def test_constraints_extensions(self):
        decoded = {
            'a': b'\x12\x34',
            'b': b'\x56\x78',
            'c': [True, True, False, True, True, False, True, True, False],
            'd': [True, True, False, True, True, False, True, True, False, True],
            'e': [1, 100, 10000],
            'f': [1, 100, 10000, 1000000]
        }

        encoded = [
            b'\x30\x62\x80\x02\x12\x34\x81\x02\x56\x78\xa2\x1b\x01\x01\xff\x01'
            b'\x01\xff\x01\x01\x00\x01\x01\xff\x01\x01\xff\x01\x01\x00\x01\x01'
            b'\xff\x01\x01\xff\x01\x01\x00\xa3\x1e\x01\x01\xff\x01\x01\xff\x01'
            b'\x01\x00\x01\x01\xff\x01\x01\xff\x01\x01\x00\x01\x01\xff\x01\x01'
            b'\xff\x01\x01\x00\x01\x01\xff\xa4\x0a\x02\x01\x01\x02\x01\x64\x02'
            b'\x02\x27\x10\xa5\x0f\x02\x01\x01\x02\x01\x64\x02\x02\x27\x10\x02'
            b'\x03\x0f\x42\x40',
            b'\x30\x62\x80\x02\x12\x34\x81\x02\x56\x78\xa2\x1b\x01\x01\xff\x01'
            b'\x01\xff\x01\x01\x00\x01\x01\xff\x01\x01\xff\x01\x01\x00\x01\x01'
            b'\xff\x01\x01\xff\x01\x01\x00\xa3\x1e\x01\x01\xff\x01\x01\xff\x01'
            b'\x01\x00\x01\x01\xff\x01\x01\xff\x01\x01\x00\x01\x01\xff\x01\x01'
            b'\xff\x01\x01\x00\x01\x01\xff\xa4\x0a\x02\x01\x01\x02\x01\x64\x02'
            b'\x02\x27\x10\xa5\x0f\x02\x01\x01\x02\x01\x64\x02\x02\x27\x10\x02'
            b'\x03\x0f\x42\x40',
            b'{"a":"1234","b":"5678","c":[true,true,false,true,true,false,true'
            b',true,false],"d":[true,true,false,true,true,false,true,true,fals'
            b'e,true],"e":[1,100,10000],"f":[1,100,10000,1000000]}',
            b'\x02\x12\x34\x02\x56\x78\x01\x09\xff\xff\x00\xff\xff\x00\xff\xff'
            b'\x00\x01\x0a\xff\xff\x00\xff\xff\x00\xff\xff\x00\xff\x01\x03\x01'
            b'\x01\x01\x64\x02\x27\x10\x01\x04\x01\x01\x01\x64\x02\x27\x10\x03'
            b'\x0f\x42\x40',
            b'\x40\x12\x34\x40\x56\x78\x6d\xa0\x0a\xdb\x50\x80\x01\x64\x80\x02'
            b'\x27\x10\x80\x04\x08\x01\x64\x80\x02\x27\x10\x80\x03\x0f\x42\x40',
            b'\x44\x8d\x15\x67\x86\xda\x15\xb6\xa1\x01\x64\x81\x13\x88\x41\x02'
            b'\x02\xc9\x02\x27\x10\x81\x87\xa1\x20\x00',
            b'<A><a>1234</a><b>5678</b><c><true /><true /><false /><true /><tr'
            b'ue /><false /><true /><true /><false /></c><d><true /><true /><f'
            b'alse /><true /><true /><false /><true /><true /><false /><true /'
            b'></d><e><INTEGER>1</INTEGER><INTEGER>100</INTEGER><INTEGER>10000'
            b'</INTEGER></e><f><INTEGER>1</INTEGER><INTEGER>100</INTEGER><INTE'
            b'GER>10000</INTEGER><INTEGER>1000000</INTEGER></f></A>',
            b"a A ::= { a '1234'H, b '5678'H, c { TRUE, TRUE, FALSE, TRUE, TRU"
            b"E, FALSE, TRUE, TRUE, FALSE }, d { TRUE, TRUE, FALSE, TRUE, TRUE"
            b", FALSE, TRUE, TRUE, FALSE, TRUE }, e { 1, 100, 10000 }, f { 1, "
            b"100, 10000, 1000000 } }"
        ]

        self.encode_decode_codecs(
            'SEQUENCE {'
            '  a OCTET STRING (SIZE (1..2, ...)),'
            '  b OCTET STRING (SIZE (1..2), ...),'
            '  c SEQUENCE (SIZE (9..9), ...) OF BOOLEAN,'
            '  d SEQUENCE (SIZE (9..9), ...) OF BOOLEAN,'
            '  e SEQUENCE SIZE (2..3, ...) OF INTEGER (1..5, ...),'
            '  f SEQUENCE (SIZE (2..3, ...)) OF INTEGER (1..5, ...)'
            '}',
            decoded,
            encoded)

    def test_date(self):
        decoded = date(1985, 4, 12)

        encoded = [
            b'\x1f\x1f\x08\x31\x39\x38\x35\x30\x34\x31\x32',
            b'\x1f\x1f\x08\x31\x39\x38\x35\x30\x34\x31\x32',
            b'"1985-04-12"',
            b'\x02\x07\xc1\x04\x0c',
            b'\x80\xec\x35\x80',
            b'\xbb\x0d\x60',
            b'<A>1985-04-12</A>',
            b'a A ::= "1985-04-12"'
        ]

        self.encode_decode_codecs('DATE', decoded, encoded)

    def test_time_of_day(self):
        decoded = time(15, 27, 46)

        encoded = [
            b'\x1f\x20\x06\x31\x35\x32\x37\x34\x36',
            b'\x1f\x20\x06\x31\x35\x32\x37\x34\x36',
            b'"15:27:46"',
            b'\x0f\x1b\x2e',
            b'\x7b\x77\x00',
            b'\x7b\x77\x00',
            b'<A>15:27:46</A>',
            b'a A ::= "15:27:46"'
        ]

        self.encode_decode_codecs('TIME-OF-DAY', decoded, encoded)

    def test_date_time(self):
        decoded = [
            datetime(1985, 4, 12, 15, 27, 46),
            datetime(1582, 2, 3, 4, 5, 6)
        ]

        encoded = [
            [
                b'\x1f\x21\x0e\x31\x39\x38\x35\x30\x34\x31\x32\x31\x35\x32\x37\x34'
                b'\x36',
                b'\x1f\x21\x0e\x31\x39\x38\x35\x30\x34\x31\x32\x31\x35\x32\x37\x34'
                b'\x36',
                b'"1985-04-12T15:27:46"',
                b'\x02\x07\xc1\x04\x0c\x0f\x1b\x2e',
                b'\x80\xec\x35\xbd\xbb\x80',
                b'\xbb\x0d\x6f\x6e\xe0',
                b'<A>1985-04-12T15:27:46</A>',
                b'a A ::= "1985-04-12T15:27:46"'
            ],
            [
                b'\x1f\x21\x0e\x31\x35\x38\x32\x30\x32\x30\x33\x30\x34\x30\x35\x30\x36',
                b'\x1f\x21\x0e\x31\x35\x38\x32\x30\x32\x30\x33\x30\x34\x30\x35\x30\x36',
                b'"1582-02-03T04:05:06"',
                b'\x02\x06\x2e\x02\x03\x04\x05\x06',
                b'\xc0\x02\x06\x2e\x11\x10\x51\x80',
                b'\xc0\x81\x8b\x84\x44\x14\x60',
                b'<A>1582-02-03T04:05:06</A>',
                b'a A ::= "1582-02-03T04:05:06"'
            ]
        ]

        for decoded_message, encoded_message in zip(decoded, encoded):
            self.encode_decode_codecs('DATE-TIME',
                                      decoded_message,
                                      encoded_message)

    def test_named_numbers(self):
        datas = [
            (
                'Constants',
                -1,
                [
                    b'\x02\x01\xff',
                    b'\x02\x01\xff',
                    b'-1',
                    b'\xff',
                    b'\x00',
                    b'\x00',
                    b'<Constants>-1</Constants>'
                ]
            ),
            (
                'Constants',
                2,
                [
                    b'\x02\x01\x02',
                    b'\x02\x01\x02',
                    b'2',
                    b'\x02',
                    b'\xc0',
                    b'\xc0',
                    b'<Constants>2</Constants>'
                ]
            ),
            (
                'A',
                -1,
                [
                    b'\x02\x01\xff',
                    b'\x02\x01\xff',
                    b'-1',
                    b'\xff',
                    b'\x00',
                    b'\x00',
                    b'<A>-1</A>'
                ]
            ),
            (
                'A',
                1,
                [
                    b'\x02\x01\x01',
                    b'\x02\x01\x01',
                    b'1',
                    b'\x01',
                    b'\x80',
                    b'\x80',
                    b'<A>1</A>'
                ]
            ),
            (
                'B',
                2,
                [
                    b'\x02\x01\x02',
                    b'\x02\x01\x02',
                    b'2',
                    b'\x02',
                    b'',
                    b'',
                    b'<B>2</B>'
                ]
            ),
            (
                'C',
                0,
                [
                    b'\x02\x01\x00',
                    b'\x02\x01\x00',
                    b'0',
                    b'\x00',
                    b'\x00',
                    b'\x00',
                    b'<C>0</C>'
                ]
            ),
            (
                'C',
                1,
                [
                    b'\x02\x01\x01',
                    b'\x02\x01\x01',
                    b'1',
                    b'\x01',
                    b'\x80',
                    b'\x80',
                    b'<C>1</C>'
                ]
            )
        ]

        for type_name, decoded, encoded in datas:
            self.encode_decode_codecs_file('tests/files/named_numbers.asn',
                                           type_name,
                                           decoded,
                                           encoded)

    def test_named_numbers_errors(self):
        datas = [
            (
                'Constants',
                -2,
                'Expected an integer between -1 and 2, but got -2.'
            ),
            (
                'Constants',
                3,
                'Expected an integer between -1 and 2, but got 3.'
            ),
            (
                'A',
                -2,
                'Expected an integer between -1 and 1, but got -2.'
            ),
            (
                'A',
                2,
                'Expected an integer between -1 and 1, but got 2.'
            ),
            (
                'B',
                1,
                'Expected an integer between 2 and 2, but got 1.'
            ),
            (
                'C',
                -1,
                'Expected an integer between 0 and 1, but got -1.'
            ),
            (
                'C',
                2,
                'Expected an integer between 0 and 1, but got 2.'
            )
        ]

        for codec in ALL_CODECS:
            foo = asn1tools.compile_files('tests/files/named_numbers.asn',
                                          codec)

            for type_name, decoded, message in datas:
                with self.assertRaises(asn1tools.ConstraintsError) as cm:
                    foo.encode(type_name, decoded, check_constraints=True)

                self.assertEqual(str(cm.exception), message)


if __name__ == '__main__':
    unittest.main()
