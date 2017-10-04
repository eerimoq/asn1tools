import unittest
import asn1tools


class Asn1ToolsUPerTest(unittest.TestCase):

    maxDiff = None

    def test_foo(self):
        foo = asn1tools.compile_file('tests/files/foo.asn', 'uper')

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded,
                         b'\x01\x01\x09\x93\xcd\x03\x15\x6c\x5e\xb3\x7e')

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
        rrc = asn1tools.compile_file('tests/files/rrc_8_6_0.asn', 'uper')

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
        all_types = asn1tools.compile_file('tests/files/all_types.asn',
                                           'uper')

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
        self.assertEqual(all_types.encode('Enumerated', 'one'), b'\x00')
        self.assertEqual(all_types.encode('Sequence', {}), b'')
        self.assertEqual(all_types.encode('Ia5string', 'bar'), b'\x03\xc5\x87\x90')

    def test_decode_all_types(self):
        all_types = asn1tools.compile_file('tests/files/all_types.asn',
                                           'uper')

        self.assertEqual(all_types.decode('Boolean', b'\x80'), True)
        self.assertEqual(all_types.decode('Boolean', b'\x00'), False)
        self.assertEqual(all_types.decode('Integer', b'\x03\x00\x80\x00'), 32768)
        self.assertEqual(all_types.decode('Integer', b'\x02\x7f\xff'), 32767)
        self.assertEqual(all_types.decode('Integer', b'\x02\x01\x00'), 256)
        self.assertEqual(all_types.decode('Integer', b'\x02\x00\xff'), 255)
        self.assertEqual(all_types.decode('Integer', b'\x02\x00\x80'), 128)
        self.assertEqual(all_types.decode('Integer', b'\x01\x7f'), 127)
        self.assertEqual(all_types.decode('Integer', b'\x01\x01'), 1)
        self.assertEqual(all_types.decode('Integer', b'\x01\x00'), 0)
        self.assertEqual(all_types.decode('Integer', b'\x01\xff'), -1)
        self.assertEqual(all_types.decode('Integer', b'\x01\x80'), -128)
        self.assertEqual(all_types.decode('Integer', b'\x02\xff\x7f'), -129)
        self.assertEqual(all_types.decode('Integer', b'\x02\xff\x00'), -256)
        self.assertEqual(all_types.decode('Integer', b'\x02\x80\x00'), -32768)
        self.assertEqual(all_types.decode('Integer', b'\x03\xff\x7f\xff'), -32769)
        self.assertEqual(all_types.decode('Bitstring', b'\x04\x40'),
                         (b'\x40', 4))
        self.assertEqual(all_types.decode('Octetstring', b'\x01\x00'),
                         b'\x00')
        self.assertEqual(all_types.decode('Enumerated', b'\x00'), 'one')
        self.assertEqual(all_types.decode('Sequence', b''), {})
        self.assertEqual(all_types.decode('Ia5string', b'\x03\xc5\x87\x90'), 'bar')


if __name__ == '__main__':
    unittest.main()
