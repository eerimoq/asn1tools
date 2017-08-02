import unittest

from asn1tools import Module, Sequence, Integer, ber


class Asn1ToolsTest(unittest.TestCase):

    def test_str(self):
        print(Module(
            'Sequence',
            [
                Sequence(
                    'Foo',
                    [
                        Integer('foo', optional=True),
                        Integer('bar', default=5),
                        Sequence(
                            'Fie',
                            [
                                Integer('foo'),
                                Integer('bar'),
                            ])
                    ]),
                Sequence('Bar', [])
            ]))
        
    
    def st_sequence(self):
        sequence = Sequence(
            'Sequence',
            [
                Integer('integer')
            ])

        encoded = ber.encode({'integer': 1}, sequence)
        self.assertEqual(encoded, b'\x10')
        decoded = ber.decode(encoded, sequence)
        self.assertEqual(decoded, {'integer': 1})


if __name__ == '__main__':
    unittest.main()
