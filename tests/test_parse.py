import sys
import unittest
import logging

import asn1tools

sys.path.append('tests/files')
sys.path.append('tests/files/ietf')
sys.path.append('tests/files/3gpp')

from foo import FOO
from rrc_8_6_0 import RRC_8_6_0
from s1ap_14_4_0 import S1AP_14_4_0
from lpp_14_3_0 import LPP_14_3_0
from information_object import INFORMATION_OBJECT
from rfc1155 import RFC1155
from rfc1157 import RFC1157
from rfc2986 import RFC2986
from rfc3161 import RFC3161
from rfc3279 import RFC3279
from rfc3281 import RFC3281
from rfc3447 import RFC3447
from rfc3852 import RFC3852
from rfc4210 import RFC4210
from rfc4211 import RFC4211
from rfc4511 import RFC4511
from rfc5280 import RFC5280
from zforce import ZFORCE
from bar import BAR
from all_types import ALL_TYPES


class Asn1ToolsParseTest(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        logging.basicConfig()
        logging.getLogger('asn1tools.parser').setLevel(logging.DEBUG)

    def tearDown(self):
        logging.getLogger('asn1tools.parser').setLevel(logging.ERROR)

    def test_parse_foo(self):
        foo = asn1tools.parse_files('tests/files/foo.asn')
        self.assertEqual(foo, FOO)

    def test_parse_information_object(self):
        information_object = asn1tools.parse_files('tests/files/information_object.asn')
        self.assertEqual(information_object, INFORMATION_OBJECT)

    def test_parse_rrc_8_6_0(self):
        rrc_8_6_0 = asn1tools.parse_files('tests/files/3gpp/rrc_8_6_0.asn')
        self.assertEqual(rrc_8_6_0, RRC_8_6_0)

    def test_parse_s1ap_14_4_0(self):
        s1ap_14_4_0 = asn1tools.parse_files('tests/files/3gpp/s1ap_14_4_0.asn')
        self.assertEqual(s1ap_14_4_0, S1AP_14_4_0)

    def test_parse_lpp_14_3_0(self):
        lpp_14_3_0 = asn1tools.parse_files('tests/files/3gpp/lpp_14_3_0.asn')
        self.assertEqual(lpp_14_3_0, LPP_14_3_0)

    def test_parse_rfc1155(self):
        rfc1155 = asn1tools.parse_files('tests/files/ietf/rfc1155.asn')
        self.assertEqual(rfc1155, RFC1155)

    def test_parse_rfc1157(self):
        rfc1157 = asn1tools.parse_files('tests/files/ietf/rfc1157.asn')
        self.assertEqual(rfc1157, RFC1157)

    def test_parse_rfc2986(self):
        rfc2986 = asn1tools.parse_files('tests/files/ietf/rfc2986.asn')
        self.assertEqual(rfc2986, RFC2986)

    def test_parse_rfc3161(self):
        rfc3161 = asn1tools.parse_files('tests/files/ietf/rfc3161.asn')
        self.assertEqual(rfc3161, RFC3161)

    def test_parse_rfc3279(self):
        rfc3279 = asn1tools.parse_files('tests/files/ietf/rfc3279.asn')
        self.assertEqual(rfc3279, RFC3279)

    def test_parse_rfc3281(self):
        rfc3281 = asn1tools.parse_files('tests/files/ietf/rfc3281.asn')
        self.assertEqual(rfc3281, RFC3281)

    def test_parse_rfc3447(self):
        rfc3447 = asn1tools.parse_files('tests/files/ietf/rfc3447.asn')
        self.assertEqual(rfc3447, RFC3447)

    def test_parse_rfc3852(self):
        rfc3852 = asn1tools.parse_files('tests/files/ietf/rfc3852.asn')
        self.assertEqual(rfc3852, RFC3852)

    def test_parse_rfc4210(self):
        rfc4210 = asn1tools.parse_files('tests/files/ietf/rfc4210.asn')
        self.assertEqual(rfc4210, RFC4210)

    def test_parse_rfc4211(self):
        rfc4211 = asn1tools.parse_files('tests/files/ietf/rfc4211.asn')
        self.assertEqual(rfc4211, RFC4211)

    def test_parse_rfc4511(self):
        rfc4511 = asn1tools.parse_files('tests/files/ietf/rfc4511.asn')
        self.assertEqual(rfc4511, RFC4511)

    def test_parse_rfc5280(self):
        rfc5280 = asn1tools.parse_files('tests/files/ietf/rfc5280.asn')
        self.assertEqual(rfc5280, RFC5280)

    def test_parse_zforce(self):
        zforce = asn1tools.parse_files('tests/files/zforce.asn')
        self.assertEqual(zforce, ZFORCE)

    def test_parse_bar(self):
        bar = asn1tools.parse_files('tests/files/bar.asn')
        self.assertEqual(bar, BAR)

    def test_parse_all_types(self):
        all_types = asn1tools.parse_files('tests/files/all_types.asn')
        self.assertEqual(all_types, ALL_TYPES)

    def test_parse_imports_global_module_reference(self):
        actual = asn1tools.parse_string('A DEFINITIONS ::= BEGIN '
                                        'IMPORTS '
                                        'a FROM B '
                                        'c, d FROM E global-module-reference '
                                        'f, g FROM H {iso(1)}; '
                                        'END')

        expected = {
            'A': {
                'extensibility-implied': False,
                'imports': {
                    'B': ['a'],
                    'E': ['c', 'd'],
                    'H': ['f', 'g']
                },
                'object-classes': {},
                'object-sets': {},
                'types': {},
                'values': {}
            }
        }

        self.assertEqual(actual, expected)

    def test_parse_x680_14_10(self):
        actual = asn1tools.parse_string('M DEFINITIONS ::= BEGIN'
                                        '      T ::= SEQUENCE {'
                                        '            a BOOLEAN,'
                                        '            b SET OF INTEGER'
                                        '      }'
                                        'END')

        expected = {
            'M': {
                'extensibility-implied': False,
                'imports': {},
                'object-classes': {},
                'object-sets': {},
                'types': {
                    'T': {
                        'type': 'SEQUENCE',
                        'members': [
                            {
                                'name': 'a',
                                'type': 'BOOLEAN',
                                'optional': False
                            },
                            {
                                'name': 'b',
                                'type': 'SET OF',
                                'optional': False,
                                'size': None,
                                'element': {
                                    'type': 'INTEGER'
                                }
                            }
                        ]
                    }
                },
                'values': {}
            }
        }

        self.assertEqual(actual, expected)

    def test_parse_x680_19_5(self):
        actual = asn1tools.parse_string(
            'M DEFINITIONS ::= BEGIN'
            '      C ::= ENUMERATED {'
            '            a,'
            '            b(3),'
            '            ...,'
            '            c(1)'
            '      }'
            '      D ::= ENUMERATED {'
            '            a,'
            '            b,'
            '            ...,'
            '            c(2)'
            '      }'
            'END')

        # ToDo: Incorrect enumeration numbers.
        expected = {
            'M': {
                'extensibility-implied': False,
                'imports': {},
                'object-classes': {},
                'object-sets': {},
                'types': {
                    'C': {
                        'type': 'ENUMERATED',
                        'values': {
                            0: 'a',
                            1: 'c',
                            3: 'b',
                            4: '...'
                        }
                    },
                    'D': {
                        'type': 'ENUMERATED',
                        'values': {
                            0: 'a',
                            1: 'b',
                            2: 'c'
                        }
                    }
                },
                'values': {}
            }
        }

        self.assertEqual(actual, expected)

    def test_parse_x680_19_6(self):
        actual = asn1tools.parse_string(
            'M DEFINITIONS ::= BEGIN'
            '      A ::= ENUMERATED {a, b, ..., c}'
            '      B ::= ENUMERATED {a, b, c(0), ..., d}'
            '      C ::= ENUMERATED {a, b, ..., c(3), d}'
            '      D ::= ENUMERATED {a, z(25), ..., d}'
            'END')

        # ToDo: Incorrect enumeration numbers.
        expected = {
            'M': {
                'extensibility-implied': False,
                'imports': {},
                'object-classes': {},
                'object-sets': {},
                'types': {
                    'A': {'type': 'ENUMERATED',
                          'values': {
                              0: 'a',
                              1: 'b',
                              2: '...',
                              3: 'c'}
                    },
                    'B': {'type': 'ENUMERATED',
                          'values': {0: 'c',
                                     1: '...',
                                     2: 'd'}
                    },
                    'C': {'type': 'ENUMERATED',
                          'values': {0: 'a',
                                     1: 'b',
                                     2: '...',
                                     3: 'c',
                                     4: 'd'}
                    },
                    'D': {'type': 'ENUMERATED',
                          'values': {0: 'a',
                                     25: 'z',
                                     26: '...',
                                     27: 'd'}
                    }
                },
                'values': {}
            }
        }


        self.assertEqual(actual, expected)

    def test_parse_error_empty_string(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 1: '>!<': "
                         "Expected word.")

    def test_parse_error_begin_missing(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= END')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 19: "
                         "'A DEFINITIONS ::= >!<END': Expected BEGIN.")

    def test_parse_error_end_missing(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 24: "
                         "'A DEFINITIONS ::= BEGIN>!<': Expected END.")

    def test_parse_error_type_assignment_missing_assignment(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN A END')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 27: "
                         "'A DEFINITIONS ::= BEGIN A >!<END': "
                         "Expected ::=.")

    def test_parse_error_value_assignment_missing_assignment(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN a INTEGER END')

        self.assertEqual(str(cm.exception),
                         "Invalid ASN.1 syntax at line 1, column 35: "
                         "'A DEFINITIONS ::= BEGIN a INTEGER >!<END': "
                         "Expected ::=.")

    def test_parse_error_sequence_missing_type(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN'
                                   '  A ::= SEQUENCE { a } '
                                   'END')

        self.assertEqual(
            str(cm.exception),
            "Invalid ASN.1 syntax at line 1, column 45: 'A DEFINITIONS ::= BEGIN  "
            "A ::= SEQUENCE { a >!<} END': Expected {CHOICE | INTEGER | NULL | REAL | "
            "BIT STRING | OCTET STRING | ENUMERATED | SEQUENCE OF | SEQUENCE | "
            "ObjectClassFieldType | SET OF | SET | OBJECT IDENTIFIER | BOOLEAN | "
            "ANY DEFINED BY | ReferencedType}.")

    def test_parse_error_sequence_missing_member_name(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A DEFINITIONS ::= BEGIN'
                                   '  A ::= SEQUENCE { A } '
                                   'END')

        self.assertEqual(
            str(cm.exception),
            "Invalid ASN.1 syntax at line 1, column 43: 'A DEFINITIONS ::= "
            "BEGIN  A ::= SEQUENCE { >!<A } END': Expected \"}\".")

    def test_parse_error_definitive_identifier(self):
        with self.assertRaises(asn1tools.ParseError) as cm:
            asn1tools.parse_string('A {} DEFINITIONS ::= BEGIN '
                                   'END')

        self.assertEqual(
            str(cm.exception),
            "Invalid ASN.1 syntax at line 1, column 4: 'A {>!<} DEFINITIONS "
            "::= BEGIN END': Expected {{identifier Suppress:(\"(\") - "
            "definitiveNumberForm - Suppress:(\")\")} | identifier | "
            "definitiveNumberForm}.")


if __name__ == '__main__':
    unittest.main()
