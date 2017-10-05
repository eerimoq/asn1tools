import unittest
import asn1tools


class Asn1ToolsCompileTest(unittest.TestCase):

    maxDiff = None

    def test_unsupported_codec(self):
        with self.assertRaises(ValueError) as cm:
            asn1tools.compile_file('tests/files/foo.asn', 'bad_codec')

        self.assertEqual(str(cm.exception), "unsupported codec 'bad_codec'")


if __name__ == '__main__':
    unittest.main()
