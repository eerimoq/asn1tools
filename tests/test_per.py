import unittest
import asn1tools


class Asn1ToolsPerTest(unittest.TestCase):

    maxDiff = None

    def test_encode_all_types(self):
        all_types = asn1tools.compile_file('tests/files/all_types.asn',
                                           'per')

        self.assertEqual(all_types.encode('Boolean', True), b'\x80')
        self.assertEqual(all_types.encode('Boolean', False), b'\x00')

    def test_decode_all_types(self):
        all_types = asn1tools.compile_file('tests/files/all_types.asn',
                                           'per')

        self.assertEqual(all_types.decode('Boolean', b'\x80'), True)
        self.assertEqual(all_types.decode('Boolean', b'\x00'), False)


if __name__ == '__main__':
    unittest.main()
