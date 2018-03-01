import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools
import sys
from copy import deepcopy

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from s1ap_14_4_0 import EXPECTED as S1AP_14_4_0


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
                         ': Decode length not supported for this codec.')

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

        with self.assertRaises(NotImplementedError):
            self.assert_encode_decode(a1, 'PersonnelRecord', decoded, encoded)

    def test_x691_a2(self):
        a2 = asn1tools.compile_files('tests/files/x691_a2.asn', 'per')

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

        with self.assertRaises(NotImplementedError):
            self.assert_encode_decode(a2, 'PersonnelRecord', decoded, encoded)

    def test_x691_a3(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            a3 = asn1tools.compile_files('tests/files/x691_a3.asn', 'per')

        self.assertEqual(
            str(cm.exception),
            "Invalid ASN.1 syntax at line 10, column 22: 'SEQUENCE >!<"
            "(SIZE(2, ...)) OF ChildInformation OPTIONAL,': Expected \"{\".")

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
        a4 = asn1tools.compile_files('tests/files/x691_a4.asn', 'per')

        decoded = {
            'a': 253,
            'b': True,
            'c': (
                'e', True
            ),
            'g': '123',
            'h': True
        }

        encoded = (
            b'\x9e\x00\x01\x80\x01\x02\x91\xa4'
        )

        with self.assertRaises(NotImplementedError):
            self.assert_encode_decode(a4, 'Ax', decoded, encoded)

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'per')

        # Message 1.
        encoded = rrc.encode('PCCH-Message',
                             {
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
                             })
        self.assertEqual(encoded, b'\x28')

        # Message 2.
        encoded = rrc.encode('PCCH-Message',
                             {
                                 'message': (
                                     'c1',
                                     (
                                         'paging', {
                                         }
                                     )
                                 )
                             })
        self.assertEqual(encoded, b'\x00')

        # Message 3.
        encoded = rrc.encode('BCCH-BCH-Message',
                             {
                                 'message': {
                                     'dl-Bandwidth': 'n6',
                                     'phich-Config': {
                                         'phich-Duration': 'normal',
                                         'phich-Resource': 'half'
                                     },
                                     'systemFrameNumber': (b'\x12', 8),
                                     'spare': (b'\x34\x56', 10)
                                 }
                             })
        self.assertEqual(encoded, b'\x04\x48\xd1')

    def test_encode_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'per')

        self.assertEqual(all_types.encode('Boolean', True), b'\x80')
        self.assertEqual(all_types.encode('Boolean', False), b'\x00')
        self.assertEqual(all_types.encode('Integer', 32768), b'\x03\x00\x80\x00')
        self.assertEqual(all_types.encode('Integer', 32767), b'\x02\x7f\xff')
        self.assertEqual(all_types.encode('Integer', 256), b'\x02\x01\x00')
        self.assertEqual(all_types.encode('Integer', 255), b'\x02\x00\xff')
        self.assertEqual(all_types.encode('Integer', 128), b'\x02\x00\x80')
        self.assertEqual(all_types.encode('Integer', 127), b'\x01\x7f')
        self.assertEqual(all_types.encode('Integer', 1), b'\x01\x01')
        self.assertEqual(all_types.encode('Integer', 0), b'\x01\x00')
        self.assertEqual(all_types.encode('Integer', -1), b'\x01\xff')
        self.assertEqual(all_types.encode('Integer', -128), b'\x01\x80')
        self.assertEqual(all_types.encode('Integer', -129), b'\x02\xff\x7f')
        self.assertEqual(all_types.encode('Integer', -256), b'\x02\xff\x00')
        self.assertEqual(all_types.encode('Integer', -32768), b'\x02\x80\x00')
        self.assertEqual(all_types.encode('Integer', -32769), b'\x03\xff\x7f\xff')
        self.assertEqual(all_types.encode('Bitstring', (b'\x40', 4)),
                         b'\x04\x40')
        self.assertEqual(all_types.encode('Octetstring', b'\x00'),
                         b'\x01\x00')
        self.assertEqual(all_types.encode('Null', None), b'')
        self.assertEqual(all_types.encode('Objectidentifier', '1.2'),
                         b'\x01\x2a')
        self.assertEqual(all_types.encode('Objectidentifier', '1.2.333'),
                         b'\x03\x2a\x82\x4d')
        self.assertEqual(all_types.encode('Enumerated', 'one'), b'\x00')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Utf8string', 'foo')

        self.assertEqual(all_types.encode('Sequence', {}), b'')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Sequence12', {'a': [{'a': []}]})

        with self.assertRaises(NotImplementedError):
            all_types.encode('Set', {})

        with self.assertRaises(NotImplementedError):
            all_types.encode('Numericstring', '123')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Printablestring', 'foo')

        self.assertEqual(all_types.encode('Ia5string', 'bar'), b'\x03bar')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Universalstring', 'bar')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Visiblestring', 'bar')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Generalstring', 'bar')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Bmpstring', b'bar')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Teletexstring', b'fum')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Utctime', '010203040506')

    def test_decode_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'per')

        self.assertEqual(all_types.decode('Boolean', b'\x80'), True)
        self.assertEqual(all_types.decode('Boolean', b'\x00'), False)
        self.assertEqual(all_types.decode('Integer', b'\x01\x02'), 2)
        self.assertEqual(all_types.decode('Bitstring', b'\x04\x40'),
                         (b'\x40', 4))
        self.assertEqual(all_types.decode('Octetstring', b'\x01\x00'),
                         b'\x00')
        self.assertEqual(all_types.decode('Null', b'\x05\x00'), None)
        self.assertEqual(all_types.decode('Objectidentifier', b'\x01\x2a'),
                         '1.2')
        self.assertEqual(all_types.decode('Objectidentifier', b'\x03\x2a\x82\x4d'),
                         '1.2.333')
        self.assertEqual(all_types.decode('Enumerated', b'\x00'), 'one')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Utf8string', b'\x0c\x03foo')

        self.assertEqual(all_types.decode('Sequence', b''), {})

        with self.assertRaises(NotImplementedError):
            all_types.decode('Sequence12', b'\x80\x01\x00')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Set', b'\x31\x00')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Numericstring', b'\x12\x03123')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Printablestring', b'\x13\x03foo')

        self.assertEqual(all_types.decode('Ia5string', b'\x03bar'), 'bar')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Universalstring', b'\x1c\x03bar')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Visiblestring', b'\x1a\x03bar')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Generalstring', b'\x1b\x03bar')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Bmpstring', b'\x1e\x03bar')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Teletexstring', b'\x14\x03fum')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Utctime', b'\x17\x0d010203040506Y')

    def test_all_types_automatic_tags(self):
        all_types = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn', 'per')

        datas = [
            ('Sequence3',
             {'a': 1, 'c': 2,'d': True},
             b'\x00\x01\x01\x01\x02\x80')
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
        self.assertEqual(repr(all_types.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(all_types.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(all_types.types['SetOf']), 'SetOf(SetOf, Integer())')

    def test_s1ap_14_4_0(self):
        with self.assertRaises(TypeError):
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


if __name__ == '__main__':
    unittest.main()
