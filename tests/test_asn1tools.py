import unittest

from asn1tools.schema import Module, Sequence, Integer
from asn1tools.codecs import ber


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

    def test_integer(self):
        foo = Integer('foo')

        # BER codec.
        encoded = ber.encode(1, foo)
        self.assertEqual(encoded, b'\x02\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, 1)

    def test_sequence(self):
        foo = Sequence('foo', [Integer('bar')])

        # BER codec.
        encoded = ber.encode({'bar': 5}, foo)
        self.assertEqual(encoded, b'\x30\x03\x80\x01\x05')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, {'bar': 5})


if __name__ == '__main__':
    unittest.main()
