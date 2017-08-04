import unittest

import asn1tools
from asn1tools.schema import Module, Sequence, Boolean, Integer
from asn1tools.codecs import ber


class Asn1ToolsTest(unittest.TestCase):

    def test_str(self):
        module = Module(
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
            ])

        self.assertEqual(
            str(module),
            """Sequence DEFINITIONS ::= BEGIN
    Foo ::= SEQUENCE {
        foo INTEGER OPTIONAL,
        bar INTEGER DEFAULT 5,
        Fie SEQUENCE {
            foo INTEGER,
            bar INTEGER
        }
    },
    Bar ::= SEQUENCE {
    }
END""")

    def test_integer(self):
        foo = Integer('foo')

        # BER encode and decode.
        encoded = ber.encode(1, foo)
        self.assertEqual(encoded, b'\x02\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, 1)

        encoded = ber.encode(-32768, foo)
        self.assertEqual(encoded, b'\x02\x02\x80\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, -32768)

        encoded = ber.encode(-32769, foo)
        self.assertEqual(encoded, b'\x02\x03\xff\x7f\xff')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, -32769)

    def test_boolean(self):
        foo = Boolean('foo')

        # BER encode and decode.
        encoded = ber.encode(True, foo)
        self.assertEqual(encoded, b'\x01\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, True)

        encoded = ber.encode(False, foo)
        self.assertEqual(encoded, b'\x01\x01\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, False)

        encoded = ber.encode(1000, foo)
        self.assertEqual(encoded, b'\x01\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, True)

        encoded = ber.encode(0, foo)
        self.assertEqual(encoded, b'\x01\x01\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, False)

    def test_sequence(self):
        foo = Sequence('foo', [Integer('bar', default=0),
                               Boolean('fie')])

        # BER encode and decode.
        encoded = ber.encode({'bar': 5, 'fie': True}, foo)
        self.assertEqual(encoded, b'\x30\x06\x02\x01\x05\x01\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, {'bar': 5, 'fie': True})

        encoded = ber.encode({'bar': -1, 'fie': False}, foo)
        self.assertEqual(encoded, b'\x30\x06\x02\x01\xff\x01\x01\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, {'bar': -1, 'fie': False})

        encoded = ber.encode({'fie': False}, foo)
        self.assertEqual(encoded, b'\x30\x03\x01\x01\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, {'bar': 0, 'fie': False})

    def test_compile_file(self):
        foo = asn1tools.compile_file('tests/files/foo.asn')

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded, b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3?')

        # Decode the encoded question.
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Get an non-existing type.
        with self.assertRaises(LookupError) as cm:
            foo.get_type('Bar')

        self.assertEqual(str(cm.exception), "No item with name 'Bar'.")

        # Get the answer type from the schema.
        answer = foo.get_type('Answer')

        # Encode an answer.
        encoded = answer.encode({'id': 1, 'answer': False})
        self.assertEqual(encoded, b'0\x06\x02\x01\x01\x01\x01\x00')

        # Decode the encoded answer.
        decoded = answer.decode(encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

    def test_rrc_8_6_0(self):
        with self.assertRaises(NotImplementedError):
            rrc = asn1tools.compile_file('tests/files/rrc_8.6.0.asn')
            print(rrc)


if __name__ == '__main__':
    unittest.main()
