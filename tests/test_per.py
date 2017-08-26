import unittest
import asn1tools


class Asn1ToolsPerTest(unittest.TestCase):

    maxDiff = None

    def test_encode_all_types(self):
        all_types = asn1tools.compile_file('tests/files/all_types.asn',
                                           'per')

        self.assertEqual(all_types.encode('Boolean', True), b'\x80')
        self.assertEqual(all_types.encode('Boolean', False), b'\x00')
        self.assertEqual(all_types.encode('Integer', 2), b'\x01\x02')
        self.assertEqual(all_types.encode('Integer', 255), b'\x02\x00\xff')
        self.assertEqual(all_types.encode('Bitstring', (b'\x40', 4)),
                         b'\x04\x40')
        self.assertEqual(all_types.encode('Octetstring', b'\x00'),
                         b'\x01\x00')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Null', None)

        with self.assertRaises(NotImplementedError):
            all_types.encode('Objectidentifier', '1.2')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Enumerated', 'one')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Utf8string', 'foo')

        self.assertEqual(all_types.encode('Sequence', {}), b'')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Set', {})

        with self.assertRaises(NotImplementedError):
            all_types.encode('Numericstring', '123')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Printablestring', 'foo')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Ia5string', 'bar')

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
        all_types = asn1tools.compile_file('tests/files/all_types.asn',
                                           'per')

        self.assertEqual(all_types.decode('Boolean', b'\x80'), True)
        self.assertEqual(all_types.decode('Boolean', b'\x00'), False)
        self.assertEqual(all_types.decode('Integer', b'\x01\x02'), 2)
        self.assertEqual(all_types.decode('Bitstring', b'\x04\x40'),
                         (b'\x40', 4))
        self.assertEqual(all_types.decode('Octetstring', b'\x01\x00'), b'\x00')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Null', b'\x05\x00')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Objectidentifier', b'\x06\x01\x2a')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Enumerated', b'\x0a\x01\x01')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Utf8string', b'\x0c\x03foo')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Sequence', b'\x30\x00')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Set', b'\x31\x00')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Numericstring', b'\x12\x03123')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Printablestring', b'\x13\x03foo')

        with self.assertRaises(NotImplementedError):
            all_types.decode('Ia5string', b'\x16\x03bar')

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

        bar = asn1tools.compile_file('tests/files/bar.asn', 'per')

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

        #decoded = bar.decode('GetRequest', encoded)
        #self.assertEqual(decoded, decoded_message)


if __name__ == '__main__':
    unittest.main()
