import unittest
import asn1tools


class Asn1ToolsDerTest(unittest.TestCase):

    maxDiff = None

    def test_encode_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn', 'der')

        self.assertEqual(all_types.encode('Boolean', True), b'\x01\x01\x01')
        self.assertEqual(all_types.encode('Integer', 32768), b'\x02\x03\x00\x80\x00')
        self.assertEqual(all_types.encode('Integer', 32767), b'\x02\x02\x7f\xff')
        self.assertEqual(all_types.encode('Integer', 256), b'\x02\x02\x01\x00')
        self.assertEqual(all_types.encode('Integer', 255), b'\x02\x02\x00\xff')
        self.assertEqual(all_types.encode('Integer', 128), b'\x02\x02\x00\x80')
        self.assertEqual(all_types.encode('Integer', 127), b'\x02\x01\x7f')
        self.assertEqual(all_types.encode('Integer', 1), b'\x02\x01\x01')
        self.assertEqual(all_types.encode('Integer', 0), b'\x02\x01\x00')
        self.assertEqual(all_types.encode('Integer', -1), b'\x02\x01\xff')
        self.assertEqual(all_types.encode('Integer', -128), b'\x02\x01\x80')
        self.assertEqual(all_types.encode('Integer', -129), b'\x02\x02\xff\x7f')
        self.assertEqual(all_types.encode('Integer', -256), b'\x02\x02\xff\x00')
        self.assertEqual(all_types.encode('Integer', -32768), b'\x02\x02\x80\x00')
        self.assertEqual(all_types.encode('Integer', -32769), b'\x02\x03\xff\x7f\xff')
        self.assertEqual(all_types.encode('Bitstring', (b'\x80', 1)), b'\x03\x02\x07\x80')
        self.assertEqual(all_types.encode('Octetstring', b'\x00'), b'\x04\x01\x00')
        self.assertEqual(all_types.encode('Null', None), b'\x05\x00')
        self.assertEqual(all_types.encode('Objectidentifier', '1.2'), b'\x06\x01\x2a')
        self.assertEqual(all_types.encode('Enumerated', 'one'), b'\x0a\x01\x01')
        self.assertEqual(all_types.encode('Utf8string', 'foo'), b'\x0c\x03foo')
        self.assertEqual(all_types.encode('Sequence', {}), b'\x30\x00')
        self.assertEqual(all_types.encode('Set', {}), b'\x31\x00')
        self.assertEqual(all_types.encode('Sequence2', {'a': 1}), b'\x30\x03\x02\x01\x01')
        self.assertEqual(all_types.encode('Set2', {'a': 2}), b'\x31\x03\x02\x01\x02')
        self.assertEqual(all_types.encode('Numericstring', '123'), b'\x12\x03123')
        self.assertEqual(all_types.encode('Printablestring', 'foo'), b'\x13\x03foo')
        self.assertEqual(all_types.encode('Ia5string', 'bar'), b'\x16\x03bar')
        self.assertEqual(all_types.encode('Universalstring', 'bar'), b'\x1c\x03bar')
        self.assertEqual(all_types.encode('Visiblestring', 'bar'), b'\x1a\x03bar')
        self.assertEqual(all_types.encode('Bmpstring', b'bar'), b'\x1e\x03bar')
        self.assertEqual(all_types.encode('Teletexstring', b'fum'), b'\x14\x03fum')
        self.assertEqual(all_types.encode('Utctime', '010203040506'),
                         b'\x17\x0d010203040506Z')
        self.assertEqual(all_types.encode('SequenceOf', []), b'0\x00')
        self.assertEqual(all_types.encode('SetOf', []), b'1\x00')

    def test_decode_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn')

        self.assertEqual(all_types.decode('Boolean', b'\x01\x01\x01'), True)
        self.assertEqual(all_types.decode('Integer', b'\x02\x01\x01'), 1)
        self.assertEqual(all_types.decode('Bitstring', b'\x03\x02\x07\x80'), (b'\x80', 1))
        self.assertEqual(all_types.decode('Octetstring', b'\x04\x01\x00'), b'\x00')
        self.assertEqual(all_types.decode('Null', b'\x05\x00'), None)
        self.assertEqual(all_types.decode('Objectidentifier', b'\x06\x01\x2a'), '1.2')
        self.assertEqual(all_types.decode('Enumerated', b'\x0a\x01\x01'), 'one')
        self.assertEqual(all_types.decode('Utf8string', b'\x0c\x03foo'), 'foo')
        self.assertEqual(all_types.decode('Sequence', b'\x30\x00'), {})
        self.assertEqual(all_types.decode('Set', b'\x31\x00'), {})
        self.assertEqual(all_types.decode('Sequence2', b'\x30\x00'), {'a': 0})
        self.assertEqual(all_types.decode('Sequence2', b'\x30\x03\x02\x01\x01'), {'a': 1})
        self.assertEqual(all_types.decode('Set2', b'\x31\x00'), {'a': 1})
        self.assertEqual(all_types.decode('Set2', b'\x31\x03\x02\x01\x02'), {'a': 2})
        self.assertEqual(all_types.decode('Numericstring', b'\x12\x03123'), '123')
        self.assertEqual(all_types.decode('Printablestring', b'\x13\x03foo'), 'foo')
        self.assertEqual(all_types.decode('Ia5string', b'\x16\x03bar'), 'bar')
        self.assertEqual(all_types.decode('Universalstring', b'\x1c\x03bar'), 'bar')
        self.assertEqual(all_types.decode('Visiblestring', b'\x1a\x03bar'), 'bar')
        self.assertEqual(all_types.decode('Bmpstring', b'\x1e\x03bar'), b'bar')
        self.assertEqual(all_types.decode('Teletexstring', b'\x14\x03fum'), b'fum')
        self.assertEqual(all_types.decode('Utctime', b'\x17\x0d010203040506Z'),
                         '010203040506')
        self.assertEqual(all_types.decode('SequenceOf', b'0\x00'), [])
        self.assertEqual(all_types.decode('SetOf', b'1\x00'), [])


if __name__ == '__main__':
    unittest.main()
