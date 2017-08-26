import sys
import logging
import unittest

import asn1tools

sys.path.append('tests/files')

from foo import FOO
from rrc_8_6_0 import RRC_8_6_0
from rfc5280 import RFC5280
from zforce import ZFORCE
from bar import BAR


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


if __name__ == '__main__':
    unittest.main()
