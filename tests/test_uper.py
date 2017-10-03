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


if __name__ == '__main__':
    unittest.main()
