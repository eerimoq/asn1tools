import unittest
import asn1tools
import sys
from copy import deepcopy

sys.path.append('tests/files')

from rrc_8_6_0 import RRC_8_6_0


class Asn1ToolsPerTest(unittest.TestCase):

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

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'per')

        # Message 1.
        encoded = rrc.encode('PCCH-Message',
                             {
                                 'message': {
                                     'c1' : {
                                         'paging': {
                                             'systemInfoModification': 'true',
                                             'nonCriticalExtension': {
                                             }
                                         }
                                     }
                                 }
                             })
        self.assertEqual(encoded, b'\x28')

        # Message 2.
        encoded = rrc.encode('PCCH-Message',
                             {
                                 'message': {
                                     'c1' : {
                                         'paging': {
                                         }
                                     }
                                 }
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
            all_types.decode('Bmpstring', b'\x1e\x03bar')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Teletexstring', b'\x14\x03fum')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Utctime', b'\x17\x0d010203040506Y')

    def test_bar(self):
        '''A simple example.

        '''

        bar = asn1tools.compile_files('tests/files/bar.asn', 'per')

        # Message 1.
        decoded_message = {
            'headerOnly': True,
            'lock': False,
            'acceptTypes': {
                'standardTypes': [(b'\x40', 2), (b'\x80', 1)]
            },
            'url': b'/ses/magic/moxen.html'
        }

        encoded_message = (
            b'\xd0\x02\x02\x40\x01\x80\x15\x2f\x73\x65\x73\x2f\x6d\x61\x67\x69'
            b'\x63\x2f\x6d\x6f\x78\x65\x6e\x2e\x68\x74\x6d\x6c'
        )

        encoded = bar.encode('GetRequest', decoded_message)
        self.assertEqual(encoded, encoded_message)

        decoded = bar.decode('GetRequest', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 2.
        decoded_message = {
            'headerOnly': False,
            'lock': False,
            'url': b'0'
        }

        encoded_message = b'\x00\x01\x30'

        encoded = bar.encode('GetRequest', decoded_message)
        self.assertEqual(encoded, encoded_message)

        decoded = bar.decode('GetRequest', encoded)
        self.assertEqual(decoded, decoded_message)


if __name__ == '__main__':
    unittest.main()
