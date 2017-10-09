import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import asn1tools


class Asn1ToolsCommandLineTest(unittest.TestCase):

    maxDiff = None

    def test_command_line_decode_foo_question(self):
        argv = ['asn1tools',
                'decode',
                'tests/files/foo.asn',
                'Question',
                '300e0201011609497320312b313d333f']

        stdout = sys.stdout
        sys.argv = argv
        sys.stdout = StringIO()

        try:
            asn1tools._main()

        finally:
            actual_output = sys.stdout.getvalue()
            sys.stdout = stdout

        self.assertTrue('id: 1' in actual_output)
        self.assertTrue('question: Is 1+1=3?' in actual_output)

    def test_command_line_decode_rrc_bcch_dl_sch_message(self):
        argv = ['asn1tools',
                'decode',
                'tests/files/snmp_v1.asn',
                'Message',
                '30819f02010004067075626c6963a3819102013c020100020100308185302206'
                '122b06010401817d08330a0201070a86deb735040c3137322e33312e31392e37'
                '33301706122b06010401817d08330a0201050a86deb960020102302306122b06'
                '010401817d08330a0201070a86deb736040d3235352e3235352e3235352e3030'
                '2106122b06010401817d08330a0201070a86deb738040b3137322e33312e3139'
                '2e32']

        stdout = sys.stdout
        sys.argv = argv
        sys.stdout = StringIO()

        try:
            asn1tools._main()

        finally:
            actual_output = sys.stdout.getvalue()
            sys.stdout = stdout

        print(actual_output)

        expected_output = [
            "community: '7075626c6963'",
            "data:",
            "  set-request:",
            "    variable-bindings:",
            "      [0]:",
            "        value:",
            "          simple:",
            "            string: '3137322e33312e31392e3733'",
            "        name: 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130101",
            "      [1]:",
            "        value:",
            "          simple:",
            "            number: 2",
            "        name: 1.3.6.1.4.1.253.8.51.10.2.1.5.10.14130400",
            "      [2]:",
            "        value:",
            "          simple:",
            "            string: '3235352e3235352e3235352e30'",
            "        name: 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130102",
            "      [3]:",
            "        value:",
            "          simple:",
            "            string: '3137322e33312e31392e32'",
            "        name: 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130104",
            "    error-index: 0",
            "    error-status: 0",
            "    request-id: 60",
            "version: 0"
        ]

        for line in expected_output:
            self.assertTrue(line in actual_output)


if __name__ == '__main__':
    unittest.main()
