import json
import unittest
import asn1tools


def loads(encoded):
    return json.loads(encoded.decode('utf-8'))


class Asn1ToolsJerTest(unittest.TestCase):

    maxDiff = None

    def test_foo(self):
        foo = asn1tools.compile_files(['tests/files/foo.asn'], 'jer')

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Question.
        decoded_message = {'id': 1, 'question': 'Is 1+1=3?'}
        encoded_message = b'{"id":1,"question":"Is 1+1=3?"}'

        encoded = foo.encode('Question', decoded_message)
        self.assertEqual(loads(encoded), loads(encoded_message))
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, decoded_message)

        # Answer.
        decoded_message = {'id': 1, 'answer': False}
        encoded_message = b'{"id":1,"answer":false}'

        encoded = foo.encode('Answer', decoded_message)
        self.assertEqual(loads(encoded), loads(encoded_message))
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, decoded_message)

        # Encode a question with missing field 'id'.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            encoded = foo.encode('Question', {'question': 'Is 1+1=3?'})

        self.assertEqual(
            str(cm.exception),
            "Sequence member 'id' not found in {'question': 'Is 1+1=3?'}.")

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_files('tests/files/rrc_8_6_0.asn', 'jer')

        # Message 1.
        decoded_message = {
            'message': {
                'c1' : {
                    'paging': {
                        'systemInfoModification': 'true',
                        'nonCriticalExtension': {
                        }
                    }
                }
            }
        }

        encoded_message = (
            b'{"message":{"c1":{"paging":{"systemInfoModification":0,"'
            b'nonCriticalExtension":{}}}}}'
        )

        encoded = rrc.encode('PCCH-Message', decoded_message)
        self.assertEqual(loads(encoded), loads(encoded_message))
        decoded = rrc.decode('PCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)


if __name__ == '__main__':
    unittest.main()
