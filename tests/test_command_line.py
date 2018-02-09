import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import asn1tools


class Asn1ToolsCommandLineTest(unittest.TestCase):

    maxDiff = None

    def test_command_line_help(self):
        argv = ['asn1tools', '--help']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit):
                    asn1tools._main()

        expected_output = [
            "usage: asn1tools [-h] [-d] [-v {0,1,2}] [--version] {decode} ...",
            "",
            "Various ASN.1 utilities.",
            "",
            "optional arguments:",
            "  -h, --help            show this help message and exit",
            "  -d, --debug",
            "  -v {0,1,2}, --verbose {0,1,2}",
            "                        Control the verbosity; ",
            "disable(0),",
            "warning(1)",
            "and",
            "debug(2).",
            "(default: 1).",
            "  --version             Print version information and exit.",
            "",
            "subcommands:",
            "  {decode}"
        ]

        for line in expected_output:
            self.assertIn(line, stdout.getvalue())

    def test_command_line_decode_help(self):
        argv = ['asn1tools', 'decode', '--help']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit):
                    asn1tools._main()

        expected_output = [
            "asn1tools decode [-h] [-c {ber,der,jer,per,uper,xer}]",
            "                        specification [specification ...] type hexstring",
            "",
            "Decode given hextring and print it to standard output.",
            "",
            "positional arguments:",
            "  specification         ASN.1 specification as one or more .asn files.",
            "  type                  Type to decode.",
            "  hexstring             Hexstring to decode.",
            "",
            "optional arguments:",
            "  -h, --help            show this help message and exit",
            "  -c {ber,der,jer,per,uper,xer}, --codec {ber,der,jer,per,uper,xer}",
            "                        Codec (default: ber)."
        ]

        for line in expected_output:
            self.assertIn(line, stdout.getvalue())

    def test_command_line_decode_ber_foo_question(self):
        argv = ['asn1tools',
                'decode',
                'tests/files/foo.asn',
                'Question',
                '300e0201011609497320312b313d333f']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        self.assertIn('id: 1', stdout.getvalue())
        self.assertIn('question: Is 1+1=3?', stdout.getvalue())

    def test_command_line_decode_uper_foo_question(self):
        argv = ['asn1tools',
                'decode',
                '--codec', 'uper',
                'tests/files/foo.asn',
                'Question',
                '01010993cd03156c5eb37e']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        self.assertIn('id: 1', stdout.getvalue())
        self.assertIn('question: Is 1+1=3?', stdout.getvalue())

    def test_command_line_decode_ber_rrc_bcch_dl_sch_message(self):
        argv = ['asn1tools',
                'decode',
                'tests/files/ietf/rfc1155.asn',
                'tests/files/ietf/rfc1157.asn',
                'Message',
                '30819f02010004067075626c6963a3819102013c020100020100308185302206'
                '122b06010401817d08330a0201070a86deb735040c3137322e33312e31392e37'
                '33301706122b06010401817d08330a0201050a86deb960020102302306122b06'
                '010401817d08330a0201070a86deb736040d3235352e3235352e3235352e3030'
                '2106122b06010401817d08330a0201070a86deb738040b3137322e33312e3139'
                '2e32']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

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
            self.assertIn(line, stdout.getvalue())

    def test_command_line_decode_bad_type_name(self):
        argv = ['asn1tools',
                'decode',
                'tests/files/foo.asn',
                'Question2',
                '01010993cd03156c5eb37e']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit) as cm:
                    asn1tools._main()

                self.assertEqual(
                    str(cm.exception),
                    "error: type 'Question2' not found in types dictionary")

    def test_command_line_decode_bad_data(self):
        argv = ['asn1tools',
                'decode',
                'tests/files/foo.asn',
                'Question',
                '012']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit) as cm:
                    asn1tools._main()

                self.assertEqual(str(cm.exception),
                                 "error: '012': Odd-length string")


if __name__ == '__main__':
    unittest.main()
