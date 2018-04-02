import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools


class Asn1ToolsCheckConstraintsTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_all_codecs(self):
        codecs = [
            'ber',
            'der',
            'gser',
            'jer',
            'per',
            'uper',
            'xer'
        ]

        for codec in codecs:
            foo = asn1tools.compile_string(
                "Foo DEFINITIONS AUTOMATIC TAGS ::= "
                "BEGIN "
                "A ::= INTEGER "
                "END",
                codec)

            with self.assertRaises(NotImplementedError):
                foo.check_constraints('A', 0)

    def test_integer(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "B ::= INTEGER (5..99) "
            "C ::= INTEGER (-10..10) "
            "D ::= INTEGER (5..99, ...) "
            "E ::= INTEGER (1000..1000) "
            "F ::= SEQUENCE { "
            "  a INTEGER (4..4), "
            "  b INTEGER (40..40), "
            "  c INTEGER (400..400) "
            "} "
            "G ::= B (6..7) "
            "END")

        # Ok.
        datas = [
            ('A',  32768),
            ('A',      0),
            ('A', -32769),
            ('B',      5),
            ('B',      6),
            ('B',     99),
            ('C',    -10),
            ('C',     10),
            ('D',     99),
            ('E',   1000),
            ('F',   {'a': 4, 'b': 40, 'c': 400})
        ]

        for type_name, decoded in datas:
            with self.assertRaises(NotImplementedError):
                foo.check_constraints(type_name, decoded)

        # Not ok.
        datas = [
            ('B',      4, ': 4 does not fulfill 5..99'),
            ('B',    100, ': 100 does not fulfill 5..99'),
            ('C',    -11, ': -11 does not fulfill -10..10'),
            ('C',     11, ': 11 does not fulfill -10..10'),
            ('D',    100, ': 100 does not fulfill 5..99'),
            ('E',      0, ': 0 does not fulfill 1000..1000'),
            ('F',
             {'a': 4, 'b': 41, 'c': 400},
             'b: 41 does not fulfill 40..40')
        ]

        for type_name, decoded, message in datas:
            with self.assertRaises(NotImplementedError):
                with self.assertRaises(asn1tools.ConstraintsError) as cm:
                    foo.check_constraints(type_name, decoded)

                self.assertEqual(str(cm.exception), message)


if __name__ == '__main__':
    unittest.main()
