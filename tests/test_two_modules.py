import unittest
import asn1tools


class Asn1ToolsTwoModulesTest(unittest.TestCase):

    maxDiff = None

    def test_uper(self):
        files = [
            'tests/files/module-1.asn',
            'tests/files/module-2.asn'
        ]

        spec = asn1tools.compile_files(files, 'uper')

        # Message 1.
        decoded_message = {
            'priority': 'high',
            'src': 1,
            'dst': 2,
            'num': 0,
            'length': 256
        }

        encoded_message = b'\x14\x04\x00'

        encoded = spec.encode('ASequence', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = spec.decode('ASequence', encoded_message)
        self.assertEqual(decoded, decoded_message)

        # Message 2.
        decoded_message = {
            'isvalide': True,
            'name': 'toto',
            'identity': 5
        }

        encoded_message = b'\x82\x74\xdf\xd3\x7d'

        encoded = spec.encode('SeqMod2', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = spec.decode('SeqMod2', encoded_message)
        self.assertEqual(decoded, decoded_message)


if __name__ == '__main__':
    unittest.main()
