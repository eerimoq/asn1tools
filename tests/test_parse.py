import sys
import unittest

import asn1tools

sys.path.append('tests/files')

from foo import FOO
from rrc_8_6_0 import RRC_8_6_0
from rfc5280 import RFC5280
from zforce import ZFORCE
from bar import BAR
from all_types import ALL_TYPES


class Asn1ToolsParseTest(unittest.TestCase):

    maxDiff = None

    def test_parse_foo(self):
        foo = asn1tools.parse_file('tests/files/foo.asn')
        self.assertEqual(foo, FOO)

    def test_parse_rrc_8_6_0(self):
        rrc_8_6_0 = asn1tools.parse_file('tests/files/rrc_8_6_0.asn')
        self.assertEqual(rrc_8_6_0, RRC_8_6_0)

    def test_parse_rfc5280(self):
        rfc5280 = asn1tools.parse_file('tests/files/rfc5280.asn')
        self.assertEqual(rfc5280, RFC5280)

    def test_parse_zforce(self):
        zforce = asn1tools.parse_file('tests/files/zforce.asn')
        self.assertEqual(zforce, ZFORCE)

    def test_parse_bar(self):
        bar = asn1tools.parse_file('tests/files/bar.asn')
        self.assertEqual(bar, BAR)

    def test_parse_all_types(self):
        all_types = asn1tools.parse_file('tests/files/all_types.asn')
        self.assertEqual(all_types, ALL_TYPES)

    def test_parse_error_empty_string(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 1: '>!<'.")

    def test_parse_error_begin_missing(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= END')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 19: "
                         "'A DEFINITIONS ::= >!<END': Expected \"BEGIN\".")

    def test_parse_error_end_missing(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 24: "
                         "'A DEFINITIONS ::= BEGIN>!<': Expected \"END\".")

    def test_parse_error_type_assignment_missing_assignment(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN A END')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 27: "
                         "'A DEFINITIONS ::= BEGIN A >!<END': "
                         "Expected \"::=\".")

    def test_parse_error_value_assignment_missing_assignment(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN a INTEGER END')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 35: "
                         "'A DEFINITIONS ::= BEGIN a INTEGER >!<END': "
                         "Expected \"::=\".")

    def test_parse_error_sequence_missing_type(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN'
                                   '  A ::= SEQUENCE { a } '
                                   'END')

        self.assertEqual(
            str(cm.exception),
            "Invalid ASN.1 syntax at line 1, column 45: 'A DEFINITIONS ::= BEGIN  "
            "A ::= SEQUENCE { a >!<} END': Expected {CHOICE | INTEGER | REAL | "
            "BIT STRING | OCTET STRING | ENUMERATED | SEQUENCE OF | SEQUENCE | "
            "SET OF | SET | OBJECT IDENTIFIER | BOOLEAN | ANY DEFINED BY | ...}.")


if __name__ == '__main__':
    unittest.main()
