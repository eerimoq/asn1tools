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
        self.assertEqual(all_types.encode('Enumerated', 'one'), b'\x00')


    def test_decode_all_types(self):
        all_types = asn1tools.compile_file('tests/files/all_types.asn',
                                           'uper')

        self.assertEqual(all_types.decode('Boolean', b'\x80'), True)
        self.assertEqual(all_types.decode('Boolean', b'\x00'), False)
        self.assertEqual(all_types.decode('Integer', b'\x01\x02'), 2)
        self.assertEqual(all_types.decode('Enumerated', b'\x00'), 'one')


if __name__ == '__main__':
    unittest.main()
