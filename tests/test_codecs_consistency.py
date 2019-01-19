import sys
import json
import unittest
from datetime import date
from datetime import time
from datetime import datetime
from copy import deepcopy
from .utils import Asn1ToolsBaseTest
import asn1tools

sys.path.append('tests/files')

from parameterization import EXPECTED as PARAMETERIZATION


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

    def test_programming_types(self):
        specs = []

        for codec in CODECS:
            specs.append(asn1tools.compile_files(
                'examples/programming_types/programming_types.asn',
                codec))

        decoded = 1

        encoded_messages = [
            b'\x02\x01\x01',
            b'\x02\x01\x01',
            b'1',
            b'\x00\x00\x00\x01',
            b'\xc0\x80\x00\x00\x01',
            b'\x80\x00\x00\x01',
            b'<Int32>1</Int32>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'Int32', decoded, encoded)

    def test_c_source(self):
        specs = []

        for codec in CODECS:
            specs.append(asn1tools.compile_files([
                'tests/files/c_source/c_source.asn',
                'examples/programming_types/programming_types.asn'
            ], codec))

        # Type A.
        decoded = {
            'a': -1,
            'b': -2,
            'c': -3,
            'd': -4,
            'e': 1,
            'f': 2,
            'g': 3,
            'h': 4,
            'i': True,
            'j': 11 * b'\x05'
        }

        encoded_messages = [
            b'\x30\x28\x80\x01\xff\x81\x01\xfe\x82\x01\xfd\x83\x01\xfc\x84'
            b'\x01\x01\x85\x01\x02\x86\x01\x03\x87\x01\x04\x88\x01\xff\x89'
            b'\x0b\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05',
            b'\x30\x28\x80\x01\xff\x81\x01\xfe\x82\x01\xfd\x83\x01\xfc\x84'
            b'\x01\x01\x85\x01\x02\x86\x01\x03\x87\x01\x04\x88\x01\xff\x89'
            b'\x0b\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05',
            b'{"c":-3,"f":2,"d":-4,"a":-1,"i":true,"e":1,"j":"050505050505'
            b'0505050505","h":4,"b":-2,"g":3}',
            b'\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xfc'
            b'\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04'
            b'\xff\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05',
            b'\x7f\x7f\xfe\xc0\x7f\xff\xff\xfd\xe0\x7f\xff\xff\xff\xff\xff'
            b'\xff\xfc\x01\x00\x02\x00\x03\x00\x04\x80\x05\x05\x05\x05\x05'
            b'\x05\x05\x05\x05\x05\x05',
            b'\x7f\x7f\xfe\x7f\xff\xff\xfd\x7f\xff\xff\xff\xff\xff\xff\xfc'
            b'\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04'
            b'\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82\x80',
            b'<A><a>-1</a><b>-2</b><c>-3</c><d>-4</d><e>1</e><f>2</f><g>3<'
            b'/g><h>4</h><i><true /></i><j>0505050505050505050505</j></A>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'A', decoded, encoded)

        # Type B, choice a.
        decoded = ('a', -10)

        encoded_messages = [
            b'\x80\x01\xf6',
            b'\x80\x01\xf6',
            b'{"a": -10}',
            b'\x80\xf6',
            b'\x00\x76',
            b'\x1d\x80',
            b'<B><a>-10</a></B>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'B', decoded, encoded)

        # Type B, choice b.
        decoded = (
            'b',
            {
                'a': -1,
                'b': -2,
                'c': -3,
                'd': -4,
                'e': 1,
                'f': 2,
                'g': 3,
                'h': 4,
                'i': True,
                'j': 11 * b'\x05'
            }
        )

        encoded_messages = [
            b'\xa1\x28\x80\x01\xff\x81\x01\xfe\x82\x01\xfd\x83\x01\xfc\x84'
            b'\x01\x01\x85\x01\x02\x86\x01\x03\x87\x01\x04\x88\x01\xff\x89'
            b'\x0b\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05',
            b'\xa1\x28\x80\x01\xff\x81\x01\xfe\x82\x01\xfd\x83\x01\xfc\x84'
            b'\x01\x01\x85\x01\x02\x86\x01\x03\x87\x01\x04\x88\x01\xff\x89'
            b'\x0b\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05',
            b'{"b":{"h":4,"f":2,"i":true,"d":-4,"a":-1,"j":"05050505050505'
            b'05050505","e":1,"g":3,"c":-3,"b":-2}}',
            b'\x81\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff'
            b'\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00'
            b'\x04\xff\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05',
            b'\x40\x7f\x7f\xfe\xc0\x7f\xff\xff\xfd\xe0\x7f\xff\xff\xff\xff'
            b'\xff\xff\xfc\x01\x00\x02\x00\x03\x00\x04\x80\x05\x05\x05\x05'
            b'\x05\x05\x05\x05\x05\x05\x05',
            b'\x5f\xdf\xff\x9f\xff\xff\xff\x5f\xff\xff\xff\xff\xff\xff\xff'
            b'\x00\x40\x00\x80\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x01'
            b'\x20\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0',
            b'<B><b><a>-1</a><b>-2</b><c>-3</c><d>-4</d><e>1</e><f>2</f><g'
            b'>3</g><h>4</h><i><true /></i><j>0505050505050505050505</j></'
            b'b></B>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'B', decoded, encoded)

        # Type C - empty.
        decoded = []

        encoded_messages = [
            b'\x30\x00',
            b'\x30\x00',
            b'[]',
            b'\x01\x00',
            b'\x00',
            b'\x00',
            b'<C />'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'C', decoded, encoded)

        # Type C - 2 elements.
        decoded = [('a', -11), ('a', 13)]

        encoded_messages = [
            b'\x30\x06\x80\x01\xf5\x80\x01\x0d',
            b'\x30\x06\x80\x01\xf5\x80\x01\x0d',
            b'[{"a": -11}, {"a": 13}]',
            b'\x01\x02\x80\xf5\x80\x0d',
            b'\x80\x75\x00\x8d',
            b'\x87\x52\x34',
            b'<C><a>-11</a><a>13</a></C>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'C', decoded, encoded)

        # Type D.
        decoded = [
            {
                'a': {
                    'b': ('c', 0),
                    'e': [None, None, None],
                    'f': None
                },
                'g': {
                    'h': 'j',
                    'l': b'\x54\x55'
                },
                'm': {
                    'n': False,
                    'o': 2,
                    'p': {
                        'q': 5 * b'\x03',
                        'r': True
                    }
                }
            }
        ]

        encoded_messages = [
            b'\x30\x30\x30\x2e\xa0\x0f\xa0\x03\x80\x01\x00\xa1\x06\x05\x00\x05'
            b'\x00\x05\x00\x82\x00\xa1\x07\x80\x01\x01\x81\x02\x54\x55\xa2\x12'
            b'\x80\x01\x00\x81\x01\x02\xa2\x0a\x80\x05\x03\x03\x03\x03\x03\x81'
            b'\x01\xff',
            b'\x30\x30\x30\x2e\xa0\x0f\xa0\x03\x80\x01\x00\xa1\x06\x05\x00\x05'
            b'\x00\x05\x00\x82\x00\xa1\x07\x80\x01\x01\x81\x02\x54\x55\xa2\x12'
            b'\x80\x01\x00\x81\x01\x02\xa2\x0a\x80\x05\x03\x03\x03\x03\x03\x81'
            b'\x01\xff',
            b'[{"m":{"p":{"q":"0303030303","r":true},"o":2,"n":false},"g":{"l"'
            b':"5455","h":"j"},"a":{"b":{"c":0},"e":[null,null,null],"f":null}'
            b'}]',
            b'\x01\x01\x80\x00\x01\x03\x01\x02\x54\x55\xe0\x00\x02\x80\x03\x03'
            b'\x03\x03\x03\xff',
            b'\x00\xc0\x54\x55\xe9\x03\x03\x03\x03\x03\x80',
            b'\x00\xd5\x15\x7a\x40\xc0\xc0\xc0\xc0\xe0',
            b'<D><SEQUENCE><a><b><c>0</c></b><e><NULL /><NULL /><NULL /></e><f'
            b' /></a><g><h><j /></h><l>5455</l></g><m><n><false /></n><o>2</o>'
            b'<p><q>0303030303</q><r><true /></r></p></m></SEQUENCE></D>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'D', decoded, encoded)

        # Type D - some missing.
        decoded = [
            {
                'a': {
                    'b': ('d', False),
                    'e': [None, None, None],
                    'f': None
                },
                'g': {
                    'h': 'k',
                    'l': b'\x54'
                },
                'm': {
                    'o': 3,
                    'p': {
                        'q': 5 * b'\x03'
                    }
                }
            }
        ]

        encoded_messages = [
            b'\x30\x26\x30\x24\xa0\x0f\xa0\x03\x81\x01\x00\xa1\x06\x05\x00\x05'
            b'\x00\x05\x00\x82\x00\xa1\x06\x80\x01\x02\x81\x01\x54\xa2\x09\xa2'
            b'\x07\x80\x05\x03\x03\x03\x03\x03',
            b'\x30\x26\x30\x24\xa0\x0f\xa0\x03\x81\x01\x00\xa1\x06\x05\x00\x05'
            b'\x00\x05\x00\x82\x00\xa1\x06\x80\x01\x02\x81\x01\x54\xa2\x09\xa2'
            b'\x07\x80\x05\x03\x03\x03\x03\x03',
            b'[{"a":{"b":{"d":false},"e":[null,null,null],"f":null},"g":{"h":"'
            b'k","l":"54"},"m":{"o":3,"p":{"q":"0303030303"}}}]',
            b'\x01\x01\x81\x00\x01\x03\x02\x01\x54\x20\x00\x03\x03\x03\x03\x03',
            b'\x09\x00\x54\x20\x03\x03\x03\x03\x03',
            b'\x09\x15\x08\x0c\x0c\x0c\x0c\x0c',
            b'<D><SEQUENCE><a><b><d><false /></d></b><e><NULL /><NULL /><NULL '
            b'/></e><f /></a><g><h><k /></h><l>54</l></g><m><o>3</o><p><q>0303'
            b'030303</q></p></m></SEQUENCE></D>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'D', decoded, encoded)

        # Type E.
        decoded = {'a': ('b', ('c', True))}

        encoded_messages = [
            b'\x30\x07\xa0\x05\xa0\x03\x80\x01\xff',
            b'\x30\x07\xa0\x05\xa0\x03\x80\x01\xff',
            b'{"a": {"b": {"c": true}}}',
            b'\x80\x80\xff',
            b'\x80',
            b'\x80',
            b'<E><a><b><c><true /></c></b></a></E>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'E', decoded, encoded)

        # Type F.
        decoded = [[False], [True]]

        encoded_messages = [
            b'0\n0\x03\x01\x01\x000\x03\x01\x01\xff',
            b'0\n0\x03\x01\x01\x000\x03\x01\x01\xff',
            b'[[false], [true]]',
            b'\x01\x02\x01\x01\x00\x01\x01\xff',
            b'\xa0',
            b'\xa0',
            b'<F><SEQUENCE_OF><false /></SEQUENCE_OF><SEQUENCE_OF><true /></SE'
            b'QUENCE_OF></F>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'F', decoded, encoded)

        # Type G.
        decoded = {'a': True, 'i': True}

        encoded_messages = [
            b'\x30\x06\x80\x01\xff\x88\x01\xff',
            b'\x30\x06\x80\x01\xff\x88\x01\xff',
            b'{"a": true, "i": true}',
            b'\x80\x80\xff\xff',
            b'\x80\xe0',
            b'\x80\xe0',
            b'<G><a><true /></a><i><true /></i></G>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'G', decoded, encoded)

        # Type H.
        decoded = None

        encoded_messages = [
            b'\x05\x00',
            b'\x05\x00',
            b'null',
            b'',
            b'',
            b'',
            b'<H />'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'H', decoded, encoded)

        # Type I.
        decoded = (
            b'\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03'
            b'\x04\x01\x02\x03\x04\x01\x02\x03\x04'
        )

        encoded_messages = [
            b'\x04\x18\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01'
            b'\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04',
            b'\x04\x18\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01'
            b'\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04',
            b'"010203040102030401020304010203040102030401020304"',
            b'\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03'
            b'\x04\x01\x02\x03\x04\x01\x02\x03\x04',
            b'\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03'
            b'\x04\x01\x02\x03\x04\x01\x02\x03\x04',
            b'\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03'
            b'\x04\x01\x02\x03\x04\x01\x02\x03\x04',
            b'<I>010203040102030401020304010203040102030401020304</I>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'I', decoded, encoded)

        # Type J.
        decoded = (
            b'\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03'
            b'\x04\x01\x02\x03\x04\x01\x02'
        )

        encoded_messages = [
            b'\x04\x16\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01'
            b'\x02\x03\x04\x01\x02\x03\x04\x01\x02',
            b'\x04\x16\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01'
            b'\x02\x03\x04\x01\x02\x03\x04\x01\x02',
            b'"01020304010203040102030401020304010203040102"',
            b'\x16\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02'
            b'\x03\x04\x01\x02\x03\x04\x01\x02',
            b'\x00\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02'
            b'\x03\x04\x01\x02\x03\x04\x01\x02',
            b'\x00\x81\x01\x82\x00\x81\x01\x82\x00\x81\x01\x82\x00\x81\x01'
            b'\x82\x00\x81\x01\x82\x00\x81\x00',
            b'<J>01020304010203040102030401020304010203040102</J>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'J', decoded, encoded)

        # Type K.
        decoded = 'a'

        encoded_messages = [
            b'\x0a\x01\x00',
            b'\x0a\x01\x00',
            b'"a"',
            b'\x00',
            b'',
            b'',
            b'<K><a /></K>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'K', decoded, encoded)

        # Type L.
        decoded = 260 * b'\xa5'

        encoded_messages = [
            b'\x04\x82\x01\x04' + 260 * b'\xa5',
            b'\x04\x82\x01\x04' + 260 * b'\xa5',
            b'"' + 260 * b'A5' + b'"',
            b'\x82\x01\x04' + 260 * b'\xa5',
            b'\x01\x04' + 260 * b'\xa5',
            b'\x82\x52' + 259 * b'\xd2' + b'\x80',
            b'<L>' + 260 * b'A5' + b'</L>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'L', decoded, encoded)

        # Type O.
        decoded = 260 * [True]

        encoded_messages = [
            b'\x30\x82\x03\x0c' + 260 * b'\x01\x01\xff',
            b'\x30\x82\x03\x0c' + 260 * b'\x01\x01\xff',
            b'[' + 259 * b'true,' + b'true]',
            b'\x02\x01\x04' + 260 * b'\xff',
            b'\x01\x03' + 32 * b'\xff' + b'\xf0',
            b'\x81' + 32 * b'\xff' + b'\xf8',
            b'<O>' + 260 * b'<true />' + b'</O>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'O', decoded, encoded)

        # Type Q.
        decoded = ('c256', True)

        encoded_messages = [
            b'\x9f\x81\x7f\x01\xff',
            b'\x9f\x81\x7f\x01\xff',
            b'{"c256": true}',
            b'\xbf\x81\x7f\xff',
            b'\x00\xff\x80',
            b'\x7f\xc0',
            b'<Q><c256><true /></c256></Q>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'Q', decoded, encoded)

        # Type Q.
        decoded = ('c257', True)

        encoded_messages = [
            b'\x9f\x82\x00\x01\xff',
            b'\x9f\x82\x00\x01\xff',
            b'{"c257": true}',
            b'\xbf\x82\x00\xff',
            b'\x01\x00\x80',
            b'\x80\x40',
            b'<Q><c257><true /></c257></Q>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'Q', decoded, encoded)

        # Type R.
        decoded = -1

        encoded_messages = [
            b'\x02\x01\xff',
            b'\x02\x01\xff',
            b'-1',
            b'\xff',
            b'\x00',
            b'\x00',
            b'<R>-1</R>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'R', decoded, encoded)

        decoded = 0

        encoded_messages = [
            b'\x02\x01\x00',
            b'\x02\x01\x00',
            b'0',
            b'\x00',
            b'\x80',
            b'\x80',
            b'<R>0</R>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'R', decoded, encoded)

        # Type S.
        decoded = -2

        encoded_messages = [
            b'\x02\x01\xfe',
            b'\x02\x01\xfe',
            b'-2',
            b'\xfe',
            b'\x00',
            b'\x00',
            b'<S>-2</S>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'S', decoded, encoded)

        decoded = 1

        encoded_messages = [
            b'\x02\x01\x01',
            b'\x02\x01\x01',
            b'1',
            b'\x01',
            b'\xc0',
            b'\xc0',
            b'<S>1</S>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'S', decoded, encoded)

        # Type T.
        decoded = -1

        encoded_messages = [
            b'\x02\x01\xff',
            b'\x02\x01\xff',
            b'-1',
            b'\xff',
            b'\x00',
            b'\x00',
            b'<T>-1</T>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'T', decoded, encoded)

        decoded = 2

        encoded_messages = [
            b'\x02\x01\x02',
            b'\x02\x01\x02',
            b'2',
            b'\x02',
            b'\xc0',
            b'\xc0',
            b'<T>2</T>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'T', decoded, encoded)

        # Type U.
        decoded = -64

        encoded_messages = [
            b'\x02\x01\xc0',
            b'\x02\x01\xc0',
            b'-64',
            b'\xc0',
            b'\x00',
            b'\x00',
            b'<U>-64</U>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'U', decoded, encoded)

        # Type V.
        decoded = -128

        encoded_messages = [
            b'\x02\x01\x80',
            b'\x02\x01\x80',
            b'-128',
            b'\x80',
            b'\x00',
            b'\x00',
            b'<V>-128</V>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'V', decoded, encoded)

        # Type W.
        decoded = -1

        encoded_messages = [
            b'\x02\x01\xff',
            b'\x02\x01\xff',
            b'-1',
            b'\xff\xff',
            b'\x00\x00',
            b'\x00\x00',
            b'<W>-1</W>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'W', decoded, encoded)

        decoded = 510

        encoded_messages = [
            b'\x02\x02\x01\xfe',
            b'\x02\x02\x01\xfe',
            b'510',
            b'\x01\xfe',
            b'\x01\xff',
            b'\xff\x80',
            b'<W>510</W>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'W', decoded, encoded)

        # Type X.
        decoded = -2

        encoded_messages = [
            b'\x02\x01\xfe',
            b'\x02\x01\xfe',
            b'-2',
            b'\xff\xfe',
            b'\x00\x00',
            b'\x00\x00',
            b'<X>-2</X>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'X', decoded, encoded)

        decoded = 510

        encoded_messages = [
            b'\x02\x02\x01\xfe',
            b'\x02\x02\x01\xfe',
            b'510',
            b'\x01\xfe',
            b'\x02\x00',
            b'\x80\x00',
            b'<X>510</X>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'X', decoded, encoded)

        # Type Y.
        decoded = 10000

        encoded_messages = [
            b'\x02\x02\x27\x10',
            b'\x02\x02\x27\x10',
            b'10000',
            b'\x27\x10',
            b'\x00\x00',
            b'\x00\x00',
            b'<Y>10000</Y>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'Y', decoded, encoded)

        decoded = 10512

        encoded_messages = [
            b'\x02\x02\x29\x10',
            b'\x02\x02\x29\x10',
            b'10512',
            b'\x29\x10',
            b'\x02\x00',
            b'\x80\x00',
            b'<Y>10512</Y>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'Y', decoded, encoded)

        # AB.
        decoded = {
            'a': 0,
            'b': 10300
        }

        encoded_messages = [
            b'\x30\x0b\xa0\x03\x02\x01\x00\xa1\x04\x02\x02\x28\x3c',
            b'\x30\x0b\xa0\x03\x02\x01\x00\xa1\x04\x02\x02\x28\x3c',
            b'{"a": 0, "b": 10300}',
            b'\x00\x28\x3c',
            b'\x80\x01,',
            b'\xa5\x80',
            b'<AB><a>0</a><b>10300</b></AB>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'AB', decoded, encoded)

    def test_parameterization(self):
        specs = []

        for codec in CODECS:
            specs.append(asn1tools.compile_dict(deepcopy(PARAMETERIZATION),
                                                codec))

        # A-Boolean.
        decoded = {'a': True}

        encoded_messages = [
            b'\x30\x05\xa0\x03\x01\x01\xff',
            b'\x30\x05\xa0\x03\x01\x01\xff',
            b'{"a": true}',
            b'\xff',
            b'\x80',
            b'\x80',
            b'<A-Boolean><a><true /></a></A-Boolean>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'A-Boolean', decoded, encoded)

        # A-Integer.
        decoded = {'a': 555}

        encoded_messages = [
            b'\x30\x06\xa0\x04\x02\x02\x02\x2b',
            b'\x30\x06\xa0\x04\x02\x02\x02\x2b',
            b'{"a": 555}',
            b'\x02\x02\x2b',
            b'\x02\x02\x2b',
            b'\x02\x02\x2b',
            b'<A-Integer><a>555</a></A-Integer>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'A-Integer', decoded, encoded)

        # B-BooleanInteger.
        decoded = {
            'a': True,
            'b': -40000
        }

        encoded_messages = [
            b'\x30\x0c\xa0\x03\x01\x01\xff\xa1\x05\x02\x03\xff\x63\xc0',
            b'\x30\x0c\xa0\x03\x01\x01\xff\xa1\x05\x02\x03\xff\x63\xc0',
            b'{"a": true, "b": -40000}',
            b'\x80\xff\x03\xff\x63\xc0',
            b'\xc0\x03\xff\x63\xc0',
            b'\xc0\xff\xd8\xf0\x00',
            b'<B-BooleanInteger><a><true /></a><b>-40000</b></B-BooleanInteger>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec,
                                     codec,
                                     'B-BooleanInteger',
                                     decoded,
                                     encoded)

        # D.
        decoded = {
            'a': ('a', {'a': True}),
            'b': ('c', {'a': {'a': None, 'b': 5}})
        }

        encoded_messages = [
            b'\x30\x1c\xa0\x09\xa0\x07\x30\x05\xa0\x03\x01\x01\xff\xa1\x0f\xa0'
            b'\x0d\xa0\x0b\x30\x09\xa0\x02\x05\x00\xa1\x03\x02\x01\x05',
            b'\x30\x1c\xa0\x09\xa0\x07\x30\x05\xa0\x03\x01\x01\xff\xa1\x0f\xa0'
            b'\x0d\xa0\x0b\x30\x09\xa0\x02\x05\x00\xa1\x03\x02\x01\x05',
            b'{"a": {"a": {"a": true}}, "b": {"c": {"a": {"a": null, "b": 5}}}'
            b'}',
            b'\x80\x00\xff\x80\x80\x01\x05',
            b'\x28\x01\x05',
            b'\x28\x08\x28',
            b'<D><a><a><a><true /></a></a></a><b><c><a><a /><b>5</b></a></c></'
            b'b></D>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'D', decoded, encoded)

        decoded = {
            'a': ('a', {'a': True}),
            'b': ('d', {'a': None, 'b': 5})
        }

        encoded_messages = [
            b'\x30\x18\xa0\x09\xa0\x07\x30\x05\xa0\x03\x01\x01\xff\xa1\x0b\xa1'
            b'\x09\xa0\x02\x05\x00\xa1\x03\x02\x01\x05',
            b'\x30\x18\xa0\x09\xa0\x07\x30\x05\xa0\x03\x01\x01\xff\xa1\x0b\xa1'
            b'\x09\xa0\x02\x05\x00\xa1\x03\x02\x01\x05',
            b'{"a": {"a": {"a": true}}, "b": {"d": {"a": null, "b": 5}}}',
            b'\x80\x00\xff\x81\x80\x01\x05',
            b'\x38\x01\x05',
            b'\x38\x08\x28',
            b'<D><a><a><a><true /></a></a></a><b><d><a /><b>5</b></d></b></D>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'D', decoded, encoded)

        decoded = {
            'a': ('b', {'a': {'a': True}}),
            'b': ('d', {'a': None, 'b': 5})
        }

        encoded_messages = [
            b'\x30\x1a\xa0\x0b\xa1\x09\xa0\x07\x30\x05\xa0\x03\x01\x01\xff\xa1'
            b'\x0b\xa1\x09\xa0\x02\x05\x00\xa1\x03\x02\x01\x05',
            b'\x30\x1a\xa0\x0b\xa1\x09\xa0\x07\x30\x05\xa0\x03\x01\x01\xff\xa1'
            b'\x0b\xa1\x09\xa0\x02\x05\x00\xa1\x03\x02\x01\x05',
            b'{"a": {"b": {"a": {"a": true}}}, "b": {"d": {"a": null, "b": 5}}}',
            b'\x81\x00\x00\xff\x81\x80\x01\x05',
            b'\x9c\x01\x05',
            b'\x9c\x04\x14',
            b'<D><a><b><a><a><true /></a></a></b></a><b><d><a /><b>5</b></d></b'
            b'></D>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'D', decoded, encoded)

        # F.
        decoded = [('b', {'c': [{'a': 2, 'b': True}]})]

        encoded_messages = [
            b'\x30\x10\xa1\x0e\xa0\x0c\x30\x0a\xa0\x03\x02\x01\x02\xa1\x03\x01'
            b'\x01\xff',
            b'\x30\x10\xa1\x0e\xa0\x0c\x30\x0a\xa0\x03\x02\x01\x02\xa1\x03\x01'
            b'\x01\xff',
            b'[{"b": {"c": [{"a": 2, "b": true}]}}]',
            b'\x01\x01\x81\x01\x01\x80\x01\x02\xff',
            b'\x30\x01\x80\x01\x02\x80',
            b'\x30\x18\x08\x14',
            b'<F><b><c><SEQUENCE><a>2</a><b><true /></b></SEQUENCE></c></b></'
            b'F>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'F', decoded, encoded)

        # H.
        decoded = [True]

        encoded_messages = [
            b'\x30\x03\x01\x01\xff',
            b'\x30\x03\x01\x01\xff',
            b'[true]',
            b'\x01\x01\xff',
            b'\x30',
            b'\x30',
            b'<H><true /></H>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'H', decoded, encoded)

        # I.
        decoded = [True]

        encoded_messages = [
            b'\x30\x03\x01\x01\xff',
            b'\x30\x03\x01\x01\xff',
            b'[true]',
            b'\x01\x01\xff',
            b'\xc0',
            b'\xc0',
            b'<I><true /></I>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'I', decoded, encoded)

        # S.
        decoded = {'a': True, 'b': 7}

        encoded_messages = [
            b'\x30\x08\xa0\x03\x01\x01\xff\x81\x01\x07',
            b'\x30\x08\xa0\x03\x01\x01\xff\x81\x01\x07',
            b'{"a": true, "b": 7}',
            b'\xff\x01\x07',
            b'\x80\x01\x07',
            b'\x80\x83\x80',
            b'<S><a><true /></a><b>7</b></S>'
        ]

        for spec, codec, encoded in zip(specs, CODECS, encoded_messages):
            self.encode_decode_codec(spec, codec, 'S', decoded, encoded)


if __name__ == '__main__':
    unittest.main()
