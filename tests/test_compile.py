import sys
import unittest
import asn1tools
from copy import deepcopy

sys.path.append('tests/files')
sys.path.append('tests/files/ietf')
sys.path.append('tests/files/3gpp')

from extensibility_implied import EXPECTED as EXTENSIBILITY_IMPLIED
from extensibility_implied_pp import EXPECTED as EXTENSIBILITY_IMPLIED_PP
from all_types_automatic_tags import EXPECTED as ALL_TYPES_AUTOMATIC_TAGS
from all_types_automatic_tags_pp import EXPECTED as ALL_TYPES_AUTOMATIC_TAGS_PP


class Asn1ToolsCompileTest(unittest.TestCase):

    maxDiff = None

    def test_pre_process_extensibility_implied(self):
        actual = asn1tools.pre_process_dict(deepcopy(EXTENSIBILITY_IMPLIED))
        self.assertEqual(actual, EXTENSIBILITY_IMPLIED_PP)

    def test_pre_process_all_types_automatic_tags(self):
        actual = asn1tools.pre_process_dict(deepcopy(ALL_TYPES_AUTOMATIC_TAGS))
        self.assertEqual(actual, ALL_TYPES_AUTOMATIC_TAGS_PP)

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

    def test_missing_import_type_module(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_string(
                'A DEFINITIONS ::= BEGIN IMPORTS B FROM C; D ::= SEQUENCE { a B } END ',
                'uper')

        self.assertEqual(str(cm.exception),
                         "Module 'A' cannot import type 'B' from missing module 'C'.")

    def test_missing_import_value_module(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_string(
                'A DEFINITIONS ::= BEGIN IMPORTS b FROM C; D ::= INTEGER (b..1) END ',
                'uper')

        self.assertEqual(str(cm.exception),
                         "Module 'A' cannot import value 'b' from missing module 'C'.")


if __name__ == '__main__':
    unittest.main()
