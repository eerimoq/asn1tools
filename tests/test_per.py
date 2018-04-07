import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools
import sys
from copy import deepcopy

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from s1ap_14_4_0 import EXPECTED as S1AP_14_4_0
from x691_a2 import EXPECTED as X691_A2
from x691_a3 import EXPECTED as X691_A3
from x691_a4 import EXPECTED as X691_A4


class Asn1ToolsPerTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_foo(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'per')

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded,
                         b'\x01\x01\x09\x49\x73\x20\x31\x2b\x31\x3d\x33\x3f')

        # Decode the encoded question.
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Encode an answer.
        encoded = foo.encode('Answer', {'id': 1, 'answer': False})
        self.assertEqual(encoded, b'\x01\x01\x00')

        # Decode the encoded answer.
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

        # Encode a question with missing field 'id'.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            encoded = foo.encode('Question', {'question': 'Is 1+1=3?'})

        self.assertEqual(
            str(cm.exception),
            "Sequence member 'id' not found in {'question': 'Is 1+1=3?'}.")

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'per')

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode_length(b'')

        self.assertEqual(str(cm.exception),
                         ': Decode length is not supported for this codec.')

    def test_versions(self):
        foo = asn1tools.compile_files('tests/files/versions.asn', 'per')

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

    def test_x691_a1(self):
        a1 = asn1tools.compile_files('tests/files/x691_a1.asn', 'per')

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
            b'\x31\x37\x04\x4d\x61\x72\x79\x01\x54\x05\x53\x6d\x69\x74\x68\x02'
            b'\x05\x52\x61\x6c\x70\x68\x01\x54\x05\x53\x6d\x69\x74\x68\x08\x31'
            b'\x39\x35\x37\x31\x31\x31\x31\x05\x53\x75\x73\x61\x6e\x01\x42\x05'
            b'\x4a\x6f\x6e\x65\x73\x08\x31\x39\x35\x39\x30\x37\x31\x37'
        )

        self.assert_encode_decode(a1, 'PersonnelRecord', decoded, encoded)

    def test_x691_a2(self):
        a2 = asn1tools.compile_dict(deepcopy(X691_A2), 'per')

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
            b'\x86\x4a\x6f\x68\x6e\x50\x10\x53\x6d\x69\x74\x68\x01\x33\x08\x44'
            b'\x69\x72\x65\x63\x74\x6f\x72\x19\x71\x09\x17\x0c\x4d\x61\x72\x79'
            b'\x54\x10\x53\x6d\x69\x74\x68\x02\x10\x52\x61\x6c\x70\x68\x54\x10'
            b'\x53\x6d\x69\x74\x68\x19\x57\x11\x11\x10\x53\x75\x73\x61\x6e\x42'
            b'\x10\x4a\x6f\x6e\x65\x73\x19\x59\x07\x17'
        )

        with self.assertRaises(AssertionError):
            self.assert_encode_decode(a2, 'PersonnelRecord', decoded, encoded)

    def test_x691_a3(self):
        a3 = asn1tools.compile_dict(deepcopy(X691_A3), 'per')

        return

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
                    'dateOfBirth': '19590717',
                    'sex': 'female'
                }
            ]
        }

        encoded = (
            b'\x40\xc0\x4a\x6f\x68\x6e\x50\x08\x53\x6d\x69\x74\x68\x00\x00\x33'
            b'\x08\x44\x69\x72\x65\x63\x74\x6f\x72\x00\x19\x71\x09\x17\x03\x4d'
            b'\x61\x72\x79\x54\x08\x53\x6d\x69\x74\x68\x01\x00\x52\x61\x6c\x70'
            b'\x68\x54\x08\x53\x6d\x69\x74\x68\x00\x19\x57\x11\x11\x82\x00\x53'
            b'\x75\x73\x61\x6e\x42\x08\x4a\x6f\x6e\x65\x73\x00\x19\x59\x07\x17'
            b'\x01\x01\x40'
        )

        self.assert_encode_decode(a3, 'PersonnelRecord', decoded, encoded)

    def test_x691_a4(self):
        a4 = asn1tools.compile_dict(deepcopy(X691_A4), 'per')

        decoded = {
            'a': 253,
            'b': True,
            'c': ('e', True),
            'g': '123',
            'h': True
        }

        encoded = (
            b'\x9e\x00\x01\x80\x01\x02\x91\xa4'
        )

        self.assert_encode_decode(a4, 'Ax', decoded, encoded)

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'per')

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

        encoded = b'\x28'

        self.assert_encode_decode(rrc, 'PCCH-Message', decoded, encoded)

        # Message 2.
        decoded = {
            'message': (
                'c1',
                (
                    'paging', {
                    }
                )
            )
        }

        encoded = b'\x00'

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

        encoded = b'\x04\x48\xd1'

        self.assert_encode_decode(rrc, 'BCCH-BCH-Message', decoded, encoded)

    def test_all_types_automatic_tags(self):
        all_types = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn', 'per')

        datas = [
            ('Sequence3', {'a': 1, 'c': 2,'d': True}, b'\x00\x01\x01\x01\x02\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_bar(self):
        """A simple example.

        """

        bar = asn1tools.compile_files('tests/files/bar.asn', 'per')

        # Message 1.
        decoded = {
            'headerOnly': True,
            'lock': False,
            'acceptTypes': {
                'standardTypes': [(b'\x40', 2), (b'\x80', 1)]
            },
            'url': b'/ses/magic/moxen.html'
        }

        encoded = (
            b'\xd0\x02\x02\x40\x01\x80\x15\x2f\x73\x65\x73\x2f\x6d\x61\x67\x69'
            b'\x63\x2f\x6d\x6f\x78\x65\x6e\x2e\x68\x74\x6d\x6c'
        )

        self.assert_encode_decode(bar, 'GetRequest', decoded, encoded)

        # Message 2.
        decoded = {
            'headerOnly': False,
            'lock': False,
            'url': b'0'
        }

        encoded = b'\x00\x01\x30'

        self.assert_encode_decode(bar, 'GetRequest', decoded, encoded)

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'per')

        self.assertEqual(repr(all_types.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(all_types.types['Integer']), 'Integer(Integer)')
        self.assertEqual(repr(all_types.types['Bitstring']), 'BitString(Bitstring)')
        self.assertEqual(repr(all_types.types['Octetstring']),
                         'OctetString(Octetstring)')
        self.assertEqual(repr(all_types.types['Null']), 'Null(Null)')
        self.assertEqual(repr(all_types.types['Objectidentifier']),
                         'ObjectIdentifier(Objectidentifier)')
        self.assertEqual(repr(all_types.types['Enumerated']),
                         'Enumerated(Enumerated)')
        self.assertEqual(repr(all_types.types['Utf8string']),
                         'UTF8String(Utf8string)')
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
        self.assertEqual(repr(all_types.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(all_types.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(all_types.types['SetOf']), 'SetOf(SetOf, Integer())')

    @unittest.skip('')
    def test_s1ap_14_4_0(self):
        s1ap = asn1tools.compile_dict(deepcopy(S1AP_14_4_0), 'per')

        # Message 1.
        decoded_message = (
            'successfulOutcome',
            {
                'procedureCode': 17,
                'criticality': 'reject',
                'value': {
                    'protocolIEs': [
                        {
                            'id': 105,
                            'criticality': 'reject',
                            'value': [
                                {
                                    'servedPLMNs': [
                                        b'\xab\xcd\xef',
                                        b'\x12\x34\x56'
                                    ],
                                    'servedGroupIDs': [
                                        b'\x22\x22'
                                    ],
                                    'servedMMECs': [
                                        b'\x11'
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        )

        encoded_message = (
            b'\x20\x11\x00\x15\x00\x00\x01\x00\x69\x00\x0e\x00\x40\xab\xcd\xef\x12'
            b'\x34\x56\x00\x00\x22\x22\x00\x11'
        )

        encoded = s1ap.encode('S1AP-PDU', decoded_message)
        self.assertEqual(encoded, encoded_message)

    @unittest.skip('')
    def test_information_object(self):
        information_object = asn1tools.compile_files(
            'tests/files/information_object.asn', 'per')

        # Message 1 - without constraints.
        decoded_message = {
            'id': 0,
            'value': b'\x05',
            'comment': 'item 0',
            'extra': 2
        }

        encoded_message = (
            b'\x01\x00\x01\x05\x06\x69\x74\x65\x6d\x20\x30\x01\x02'
        )

        encoded = information_object.encode('ItemWithoutConstraints',
                                            decoded_message)
        self.assertEqual(encoded, encoded_message)

        # Message 1 - with constraints.
        decoded_message = {
            'id': 0,
            'value': True,
            'comment': 'item 0',
            'extra': 2
        }

        encoded_message = (
            b'\x01\x00\x01\x80\x06\x69\x74\x65\x6d\x20\x30\x01\x02'
        )

        # ToDo: Constraints are not yet implemented.
        with self.assertRaises(TypeError) as cm:
            encoded = information_object.encode('ItemWithConstraints',
                                                decoded_message)
            self.assertEqual(encoded, encoded_message)

        self.assertEqual(str(cm.exception), "object of type 'bool' has no len()")

        # Message 2.
        decoded_message = {
            'id': 1,
            'value': {
                'myValue': 7,
                'myType': 0
            },
            'comment': 'item 1',
            'extra': 5
        }

        encoded_message = (
            b'\x01\x01\x05\x02\x01\x07\x01\x00\x06\x69\x74\x65\x6d\x20\x31\x01\x05'
        )

        # ToDo: Constraints are not yet implemented.
        with self.assertRaises(TypeError) as cm:
            encoded = information_object.encode('ItemWithConstraints',
                                                decoded_message)
            self.assertEqual(encoded, encoded_message)

        self.assertTrue("can't concat" in str(cm.exception))

        # Message 3 - error class.
        decoded_message = {
            'errorCategory': 'A',
            'errors': [
                {
                    'errorCode': 1,
                    'errorInfo': 3
                },
                {
                    'errorCode': 2,
                    'errorInfo': True
                }
            ]
        }

        encoded_message = (
            b'\x41\x02\x01\x01\x02\x01\x03\x01\x02\x01\x80'
        )

        # ToDo: Constraints are not yet implemented.
        with self.assertRaises(NotImplementedError):
            encoded = information_object.encode('ErrorReturn', decoded_message)
            self.assertEqual(encoded, encoded_message)

    def test_boolean(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b BOOLEAN "
            "} "
            "END",
            'per')

        datas = [
            ('A',                     True, b'\x80'),
            ('A',                    False, b'\x00'),
            ('B', {'a': False, 'b': False}, b'\x00'),
            ('B',  {'a': True, 'b': False}, b'\x80'),
            ('B',  {'a': False, 'b': True}, b'\x40'),
            ('B',   {'a': True, 'b': True}, b'\xc0')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_integer(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "B ::= INTEGER (5..99) "
            "C ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b INTEGER, "
            "  c BOOLEAN, "
            "  d INTEGER (-10..400) "
            "} "
            "END",
            'per')

        datas = [
            ('A',                    32768, b'\x03\x00\x80\x00'),
            ('A',                    32767, b'\x02\x7f\xff'),
            ('A',                      256, b'\x02\x01\x00'),
            ('A',                      255, b'\x02\x00\xff'),
            ('A',                      128, b'\x02\x00\x80'),
            ('A',                      127, b'\x01\x7f'),
            ('A',                        2, b'\x01\x02'),
            ('A',                        1, b'\x01\x01'),
            ('A',                        0, b'\x01\x00'),
            ('A',                       -1, b'\x01\xff'),
            ('A',                     -128, b'\x01\x80'),
            ('A',                     -129, b'\x02\xff\x7f'),
            ('A',                     -256, b'\x02\xff\x00'),
            ('A',                   -32768, b'\x02\x80\x00'),
            ('A',                   -32769, b'\x03\xff\x7f\xff'),
            ('B',                        5, b'\x00'),
            ('B',                        6, b'\x02'),
            ('B',                       99, b'\xbc'),
            ('C',
             {'a': True, 'b': 43554344223, 'c': False, 'd': -9},
             b'\x80\x05\x0a\x24\x0a\x8d\x1f\x00\x00\x01')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_utf8_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE { "
            "    a BOOLEAN, "
            "    b UTF8String, "
            "    c UTF8String OPTIONAL"
            "} "
            "B ::= UTF8String (SIZE (10)) "
            "C ::= UTF8String (SIZE (0..1)) "
            "D ::= UTF8String (SIZE (2..3) ^ (FROM (\"a\"..\"g\"))) "
            "E ::= UTF8String "
            "END",
            'per')

        datas = [
            ('A', {'a': True, 'b': u''}, b'\x40\x00'),
            ('A',
             {'a': True, 'b': u'1', 'c': u'foo'},
             b'\xc0\x01\x31\x03\x66\x6f\x6f'),
            ('A',
             {'a': True, 'b': 300 * u'1'},
             b'\x40\x81\x2c' + 300 * b'\x31'),
            ('B',
             u'1234567890',
             b'\x0a\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30'),
            ('C',                   u'', b'\x00'),
            ('C',                  u'P', b'\x01\x50'),
            ('D',                u'agg', b'\x03\x61\x67\x67'),
            ('E',                u'bar', b'\x03\x62\x61\x72'),
            ('E',           u'a\u1010c', b'\x05\x61\xe1\x80\x90\x63')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        with self.assertRaises(NotImplementedError):
            foo.encode('A', {'a': False, 'b': 16384 * u'0'})

        with self.assertRaises(NotImplementedError):
            foo.decode('A', b'\x40\xc0\x00\x00\x00\x00')

    def test_visible_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= VisibleString (SIZE (19..133)) "
            "B ::= VisibleString (SIZE (5)) "
            "C ::= VisibleString (SIZE (19..1000)) "
            "D ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (1)) "
            "} "
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (2)) "
            "} "
            "F ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (3)) "
            "} "
            "G ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (0..1)) "
            "} "
            "H ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (0..2)) "
            "} "
            "END",
            'per')

        datas = [
            ('A',
             'HejHoppHappHippAbcde',
             b'\x02\x48\x65\x6a\x48\x6f\x70\x70\x48\x61\x70\x70\x48\x69\x70\x70'
             b'\x41\x62\x63\x64\x65'),
            ('B', 'Hejaa', b'\x48\x65\x6a\x61\x61'),
            ('C',
             17 * 'HejHoppHappHippAbcde',
             b'\x01\x41' + 17 * (b'\x48\x65\x6a\x48\x6f\x70\x70\x48\x61\x70'
                                 b'\x70\x48\x69\x70\x70\x41\x62\x63\x64\x65')),
            ('D',   {'a': True, 'b': '1'}, b'\x98\x80'),
            ('E',  {'a': True, 'b': '12'}, b'\x98\x99\x00'),
            ('F', {'a': True, 'b': '123'}, b'\x80\x31\x32\x33'),
            ('G',   {'a': True, 'b': '1'}, b'\xcc\x40'),
            ('H',   {'a': True, 'b': '1'}, b'\xa0\x31')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Bad character 0x19 should raise an exception.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', '\x19')

        self.assertEqual(
            str(cm.exception),
            "expected a character in ' !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEF"
            "GHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~', but got"
            " '.' (0x19)'")

    def test_enumerated(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= ENUMERATED { one(1) } "
            "B ::= ENUMERATED { zero(0), one(1), ... } "
            "C ::= ENUMERATED { one(1), four(4), two(2), ..., six(6), nine(9) } "
            "D ::= ENUMERATED { a, ..., "
            "aa, ab, ac, ad, ae, af, ag, ah, ai, aj, ak, al, am, an, ao, ap, "
            "aq, ar, as, at, au, av, aw, ax, ay, az, ba, bb, bc, bd, be, bf, "
            "bg, bh, bi, bj, bk, bl, bm, bn, bo, bp, bq, br, bs, bt, bu, bv, "
            "bw, bx, by, bz, ca, cb, cc, cd, ce, cf, cg, ch, ci, cj, ck, cl, "
            "cm, cn, co, cp, cq, cr, cs, ct, cu, cv, cw, cx, cy, cz, da, db, "
            "dc, dd, de, df, dg, dh, di, dj, dk, dl, dm, dn, do, dp, dq, dr, "
            "ds, dt, du, dv, dw, dx, dy, dz, ea, eb, ec, ed, ee, ef, eg, eh, "
            "ei, ej, ek, el, em, en, eo, ep, eq, er, es, et, eu, ev, ew, ex, "
            "ey, ez, fa, fb, fc, fd, fe, ff, fg, fh, fi, fj, fk, fl, fm, fn, "
            "fo, fp, fq, fr, fs, ft, fu, fv, fw, fx, fy, fz, ga, gb, gc, gd, "
            "ge, gf, gg, gh, gi, gj, gk, gl, gm, gn, go, gp, gq, gr, gs, gt, "
            "gu, gv, gw, gx, gy, gz, ha, hb, hc, hd, he, hf, hg, hh, hi, hj, "
            "hk, hl, hm, hn, ho, hp, hq, hr, hs, ht, hu, hv, hw, hx, hy, hz, "
            "ia, ib, ic, id, ie, if, ig, ih, ii, ij, ik, il, im, in, io, ip, "
            "iq, ir, is, it, iu, iv, iw, ix, iy, iz, ja, jb, jc, jd, je, jf, "
            "jg, jh, ji, jj, jk, jl, jm, jn, jo, jp, jq, jr, js, jt, ju, jv, "
            "jw, jx, jy, jz } "
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b B "
            "} "
            "END",
            'per')

        datas = [
            ('A',                    'one', b''),
            ('B',                   'zero', b'\x00'),
            ('B',                    'one', b'\x40'),
            ('C',                    'one', b'\x00'),
            ('C',                    'two', b'\x20'),
            ('C',                   'four', b'\x40'),
            ('C',                    'six', b'\x80'),
            ('C',                   'nine', b'\x81'),
            ('D',                     'aa', b'\x80'),
            ('D',                     'cl', b'\xbf'),
            ('D',                     'cm', b'\xc0\x50\x00'),
            ('D',                     'jv', b'\xc0\x7f\xc0'),
            ('D',                     'jw', b'\xc0\x80\x40\x00'),
            ('D',                     'jz', b'\xc0\x80\x40\xc0'),
            ('E', {'a': True, 'b': 'zero'}, b'\x80'),
            ('E',  {'a': True, 'b': 'one'}, b'\xa0')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

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
            "END",
            'per')

        datas = [
            ('A',                                {}, b''),
            ('O',                                {}, b'\x00'),
            ('B',                          {'a': 0}, b'\x00'),
            ('B',                          {'a': 1}, b'\x80\x01\x01'),
            ('C',                       {'a': True}, b'\x40'),
            ('D',                       {'a': True}, b'\x40'),
            ('E',                       {'a': True}, b'\x40'),
            ('H',                       {'a': True}, b'\x40'),
            ('I',                       {'a': True}, b'\x40'),
            ('J',                       {'a': True}, b'\x40'),
            ('K',                       {'a': True}, b'\x40'),
            ('L',                       {'a': True}, b'\x40'),
            ('M',                       {'a': True}, b'\x40'),
            ('N',                       {'a': True}, b'\x00'),
            ('N',                      {'a': False}, b'\x80'),
            ('P',                                {}, b'\x00'),
            ('O',                       {'a': True}, b'\x80\x80\x01\x80'),
            ('O',                      {'a': False}, b'\x80\x80\x01\x00'),
            ('P',            {'a': True, 'b': True}, b'\x80\x80\x01\x40'),
            ('P',           {'a': True, 'b': False}, b'\x80\x80\x01\xc0'),
            ('D',            {'a': True, 'b': True}, b'\xc0\x40\x01\x80'),
            ('E',            {'a': True, 'b': True}, b'\xc0\x40\x01\x80'),
            ('F',            {'a': True, 'c': True}, b'\x60'),
            ('G',            {'a': True, 'd': True}, b'\x60'),
            ('I',            {'a': True, 'b': True}, b'\xc0\x40\x01\x80'),
            ('J',            {'a': True, 'b': True}, b'\xc0\x40\x01\x80'),
            ('K',            {'a': True, 'b': True}, b'\xc0\xc0\x01\x80'),
            ('F', {'a': True, 'b': True, 'c': True}, b'\xe0\x20\x01\x80'),
            ('K', {'a': True, 'b': True, 'c': True}, b'\xc0\xe0\x01\x80\x01\x80'),
            ('L', {'a': True, 'b': True, 'c': True}, b'\xc0\x40\x01\xc0'),
            ('G', {'a': True, 'b': True, 'd': True}, b'\xe0\x60\x01\x80'),
            ('G',
             {'a': True, 'b': True, 'c': True, 'd': True},
             b'\xe0\x70\x01\x80\x01\x80'),
            ('M',
             {'a': True, 'b': {'a': 5}, 'c': True},
             b'\xc0\x40\x04\x80\x01\x05\x80'),
            ('Q',      {'a': {'a': True}, 'b': 100}, b'\x40\x01\x64'),
            ('R',
             {'a': {'a': True, 'b': True}, 'b': 100},
             b'\xc0\x40\x01\x80\x01\x64')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Non-symmetrical encoding and decoding because default values
        # are not encoded, but part of the decoded (given that the
        # root and addition is present).
        self.assertEqual(foo.encode('N', {}), b'\x00')
        self.assertEqual(foo.decode('N', b'\x00'), {'a': True})
        self.assertEqual(foo.encode('P', {'a': True}), b'\x80\x80\x01\x40')
        self.assertEqual(foo.decode('P', b'\x80\x80\x01\x40'),
                         {'a': True, 'b': True})

        # Decode D as C. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('C', b'\xc0\x40\x01\x80'), {'a': True})

        # Decode R as Q. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('Q', b'\xc0\x40\x01\x80\x01\x64'),
                         {'a': {'a': True}, 'b': 100})

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
            "END",
            'per')

        datas = [
            ('A',            ('a', True), b'\x80'),
            ('B',            ('a', True), b'\x40'),
            ('C',            ('a', True), b'\x20'),
            ('C',               ('b', 1), b'\x40\x01\x01'),
            ('C',            ('c', True), b'\x80\x01\x80'),
            ('D',            ('a', True), b'\x40'),
            ('D',            ('b', True), b'\x80\x01\x80'),
            ('E',            ('a', True), b'\x40'),
            ('E',            ('b', True), b'\x80\x01\x80'),
            ('E',            ('c', True), b'\x81\x01\x80'),
            ('F',            ('a', True), b'\x40'),
            ('G',            ('a', True), b'\x40'),
            ('G',            ('b', True), b'\x80\x01\x80'),
            ('H',            ('a', True), b'\x40'),
            ('H',            ('b', True), b'\x80\x01\x80'),
            ('H',            ('c', True), b'\x81\x01\x80'),
            ('I',            ('a', True), b'\x40'),
            ('I',            ('b', True), b'\x80\x01\x80'),
            ('I',            ('c', True), b'\x81\x01\x80'),
            ('J',            ('a', True), b'\x40'),
            ('J',        ('b', ('a', 1)), b'\x80\x02\x01\x01'),
            ('J',            ('c', True), b'\x81\x01\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)


if __name__ == '__main__':
    unittest.main()
