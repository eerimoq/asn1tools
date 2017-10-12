import unittest
import asn1tools


class Asn1ToolsCompileTest(unittest.TestCase):

    maxDiff = None

    def test_unsupported_codec(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_files('tests/files/foo.asn', 'bad_codec')

        self.assertEqual(str(cm.exception), "unsupported codec 'bad_codec'")

    def test_missing_type(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_string('A DEFINITIONS ::= BEGIN A ::= B END')

        self.assertEqual(str(cm.exception), "Type 'B' not found in module 'A'.")

    def test_missing_value(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_string('A DEFINITIONS ::= BEGIN A ::= INTEGER (1..a) END',
                                     'uper')

        self.assertEqual(str(cm.exception), "Value 'a' not found in module 'A'.")

    def test_missing_import_type(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_string(
                'A DEFINITIONS ::= BEGIN IMPORTS B FROM C; D ::= SEQUENCE { a B } END '
                'C DEFINITIONS ::= BEGIN END',
                'uper')

        self.assertEqual(str(cm.exception),
                         "Type 'B' imported by module 'A' not found in module 'C'.")

    def test_missing_import_value(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_string(
                'A DEFINITIONS ::= BEGIN IMPORTS b FROM C; D ::= INTEGER (b..1) END '
                'C DEFINITIONS ::= BEGIN END',
                'uper')

        self.assertEqual(str(cm.exception),
                         "Value 'b' imported by module 'A' not found in module 'C'.")


if __name__ == '__main__':
    unittest.main()
