import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import asn1tools


class Asn1ToolsCommandLineTest(unittest.TestCase):

    maxDiff = None

    def test_command_line_decode(self):
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


if __name__ == '__main__':
    unittest.main()
