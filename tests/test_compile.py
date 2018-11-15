import sys
import unittest
import asn1tools
from copy import deepcopy
import shutil
import os

sys.path.append('tests/files')
sys.path.append('tests/files/ietf')
sys.path.append('tests/files/3gpp')

from extensibility_implied import EXPECTED as EXTENSIBILITY_IMPLIED
from extensibility_implied_pp import EXPECTED as EXTENSIBILITY_IMPLIED_PP
from all_types_automatic_tags import EXPECTED as ALL_TYPES_AUTOMATIC_TAGS
from all_types_automatic_tags_pp import EXPECTED as ALL_TYPES_AUTOMATIC_TAGS_PP
from module_tags_explicit import EXPECTED as MODULE_TAGS_EXPLICIT
from module_tags_explicit_pp import EXPECTED as MODULE_TAGS_EXPLICIT_PP
from module_tags_implicit import EXPECTED as MODULE_TAGS_IMPLICIT
from module_tags_implicit_pp import EXPECTED as MODULE_TAGS_IMPLICIT_PP
from module_tags_automatic import EXPECTED as MODULE_TAGS_AUTOMATIC
from module_tags_automatic_pp import EXPECTED as MODULE_TAGS_AUTOMATIC_PP
from x683 import EXPECTED as X683
from x683_pp import EXPECTED as X683_PP
from time_types import EXPECTED as TIME_TYPES
from time_types_pp import EXPECTED as TIME_TYPES_PP


class Asn1ToolsCompileTest(unittest.TestCase):

    maxDiff = None

    def test_pre_process_extensibility_implied(self):
        actual = asn1tools.pre_process_dict(deepcopy(EXTENSIBILITY_IMPLIED))
        self.assertEqual(actual, EXTENSIBILITY_IMPLIED_PP)

    def test_pre_process_all_types_automatic_tags(self):
        actual = asn1tools.pre_process_dict(deepcopy(ALL_TYPES_AUTOMATIC_TAGS))
        self.assertEqual(actual, ALL_TYPES_AUTOMATIC_TAGS_PP)

    def test_pre_process_module_tags_explicit(self):
        actual = asn1tools.pre_process_dict(deepcopy(MODULE_TAGS_EXPLICIT))
        self.assertEqual(actual, MODULE_TAGS_EXPLICIT_PP)

    def test_pre_process_module_tags_implicit(self):
        actual = asn1tools.pre_process_dict(deepcopy(MODULE_TAGS_IMPLICIT))
        self.assertEqual(actual, MODULE_TAGS_IMPLICIT_PP)

    def test_pre_process_module_tags_automatic(self):
        actual = asn1tools.pre_process_dict(deepcopy(MODULE_TAGS_AUTOMATIC))
        self.assertEqual(actual, MODULE_TAGS_AUTOMATIC_PP)

    def test_pre_process_x683(self):
        actual = asn1tools.pre_process_dict(deepcopy(X683))

        with self.assertRaises(AssertionError):
            self.assertEqual(actual, X683_PP)

    def test_pre_process_time_types(self):
        actual = asn1tools.pre_process_dict(deepcopy(TIME_TYPES))
        self.assertEqual(actual, TIME_TYPES_PP)

    def test_unsupported_codec(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_files('tests/files/foo.asn', 'bad_codec')

        self.assertEqual(str(cm.exception), "Unsupported codec 'bad_codec'.")

    def test_encode_decode_bad_type_name(self):
        foo = asn1tools.compile_files('tests/files/foo.asn')

        # Encode.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('BadTypeName', b'')

        self.assertEqual(
            str(cm.exception),
            "Type 'BadTypeName' not found in types dictionary.")

        # Decode.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('BadTypeName', b'')

        self.assertEqual(
            str(cm.exception),
            "Type 'BadTypeName' not found in types dictionary.")

    def test_encoding(self):
        asn1tools.compile_files('tests/files/foo.asn', encoding='ascii')

    def test_import_imported(self):
        asn1tools.compile_files('tests/files/import_imported.asn')

    def test_missing_type(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_string('A DEFINITIONS ::= BEGIN A ::= B END')

        self.assertEqual(str(cm.exception), "Type 'B' not found in module 'A'.")

    def test_missing_value(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            asn1tools.compile_string(
                'A DEFINITIONS ::= BEGIN A ::= INTEGER (1..a) END',
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

    def test_duplicated_type(self):
        """Duplicated types are not part of types dictionary.

        """

        spec = asn1tools.compile_string(
            "Foo DEFINITIONS ::= BEGIN Fum ::= INTEGER END "
            "Bar DEFINITIONS ::= BEGIN Fum ::= BOOLEAN END "
            "Fie DEFINITIONS ::= BEGIN Fum ::= REAL END ")

        self.assertEqual(spec.types, {})

    def test_cache(self):
        cache_dir = 'test_cache'

        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

        foo = asn1tools.compile_files('tests/files/foo.asn',
                                      cache_dir=cache_dir)
        foo_cached = asn1tools.compile_files('tests/files/foo.asn',
                                             cache_dir=cache_dir)

        encoded = foo.encode('Question',
                             {'id': 1, 'question': '???'})
        encoded_cached = foo_cached.encode('Question',
                                           {'id': 1, 'question': '???'})

        self.assertEqual(encoded, encoded_cached)


if __name__ == '__main__':
    unittest.main()
