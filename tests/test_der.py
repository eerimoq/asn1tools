import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools


class Asn1ToolsDerTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn', 'der')

        datas = [
            ('Boolean',                 True, b'\x01\x01\xff'),
            ('Boolean',                False, b'\x01\x01\x00'),
            ('Integer',                32768, b'\x02\x03\x00\x80\x00'),
            ('Integer',                32767, b'\x02\x02\x7f\xff'),
            ('Integer',                  256, b'\x02\x02\x01\x00'),
            ('Integer',                  255, b'\x02\x02\x00\xff'),
            ('Integer',                  128, b'\x02\x02\x00\x80'),
            ('Integer',                  127, b'\x02\x01\x7f'),
            ('Integer',                    1, b'\x02\x01\x01'),
            ('Integer',                    0, b'\x02\x01\x00'),
            ('Integer',                   -1, b'\x02\x01\xff'),
            ('Integer',                 -128, b'\x02\x01\x80'),
            ('Integer',                 -129, b'\x02\x02\xff\x7f'),
            ('Integer',                 -256, b'\x02\x02\xff\x00'),
            ('Integer',               -32768, b'\x02\x02\x80\x00'),
            ('Integer',               -32769, b'\x02\x03\xff\x7f\xff'),
            ('Bitstring',       (b'\x80', 1), b'\x03\x02\x07\x80'),
            ('Octetstring',          b'\x00', b'\x04\x01\x00'),
            ('Octetstring',    127 * b'\x55', b'\x04\x7f' + 127 * b'\x55'),
            ('Octetstring',    128 * b'\xaa', b'\x04\x81\x80' + 128 * b'\xaa'),
            ('Null',                    None, b'\x05\x00'),
            ('Objectidentifier',       '1.2', b'\x06\x01\x2a'),
            ('Enumerated',             'one', b'\x0a\x01\x01'),
            ('Utf8string',             'foo', b'\x0c\x03foo'),
            ('Sequence',                  {}, b'\x30\x00'),
            ('Sequence2',           {'a': 0}, b'\x30\x00'),
            ('Sequence2',           {'a': 1}, b'\x30\x03\x02\x01\x01'),
            ('Sequence13', {'a': [1]}, b'\x30\x05\xa0\x03\x02\x01\x01'),
            ('Sequence13', {'b': [1]}, b'\x30\x05\xa1\x03\x02\x01\x01'),
            ('Set',                       {}, b'\x31\x00'),
            ('Set2',                {'a': 1}, b'\x31\x00'),
            ('Set2',                {'a': 2}, b'\x31\x03\x02\x01\x02'),
            ('Numericstring',          '123', b'\x12\x03123'),
            ('Printablestring',        'foo', b'\x13\x03foo'),
            ('Ia5string',              'bar', b'\x16\x03bar'),
            ('Universalstring',        'bar', b'\x1c\x03bar'),
            ('Visiblestring',          'bar', b'\x1a\x03bar'),
            ('Generalstring',          'bar', b'\x1b\x03bar'),
            ('Bmpstring',             b'bar', b'\x1e\x03bar'),
            ('Teletexstring',         b'fum', b'\x14\x03fum'),
            ('Utctime',       '010203040506', b'\x17\x0d010203040506Z'),
            ('GeneralizedTime1',
             '20001231235959Z',
             b'\x18\x0f\x32\x30\x30\x30\x31\x32\x33\x31\x32\x33\x35\x39'
             b'\x35\x39\x5a'),
            ('SequenceOf',                [], b'0\x00'),
            ('SetOf',                     [], b'1\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

        with self.assertRaises(NotImplementedError):
            all_types.encode('Sequence12', {'a': [{'a': []}]})

        # ToDo: Should return {'a': [{'a': []}]}
        self.assertEqual(
            all_types.decode('Sequence12', b'\x30\x04\xa0\x02\x30\x00'),
            {})

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'der')

        self.assertEqual(repr(all_types.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(all_types.types['Integer']), 'Integer(Integer)')
        self.assertEqual(repr(all_types.types['Bitstring']), 'BitString(Bitstring)')
        self.assertEqual(repr(all_types.types['Octetstring']), 'OctetString(Octetstring)')
        self.assertEqual(repr(all_types.types['Null']), 'Null(Null)')
        self.assertEqual(repr(all_types.types['Objectidentifier']),
                         'ObjectIdentifier(Objectidentifier)')
        self.assertEqual(repr(all_types.types['Enumerated']), 'Enumerated(Enumerated)')
        self.assertEqual(repr(all_types.types['Utf8string']), 'UTF8String(Utf8string)')
        self.assertEqual(repr(all_types.types['Sequence']), 'Sequence(Sequence, [])')
        self.assertEqual(repr(all_types.types['Set']), 'Set(Set, [])')
        self.assertEqual(repr(all_types.types['Sequence2']),
                         'Sequence(Sequence2, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Set2']), 'Set(Set2, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Numericstring']),
                         'NumericString(Numericstring)')
        self.assertEqual(repr(all_types.types['Printablestring']),
                         'PrintableString(Printablestring)')
        self.assertEqual(repr(all_types.types['Ia5string']), 'IA5String(Ia5string)')
        self.assertEqual(repr(all_types.types['Universalstring']),
                         'UniversalString(Universalstring)')
        self.assertEqual(repr(all_types.types['Visiblestring']),
                         'VisibleString(Visiblestring)')
        self.assertEqual(repr(all_types.types['Generalstring']),
                         'GeneralString(Generalstring)')
        self.assertEqual(repr(all_types.types['Bmpstring']),
                         'BMPString(Bmpstring)')
        self.assertEqual(repr(all_types.types['Teletexstring']),
                         'TeletexString(Teletexstring)')
        self.assertEqual(repr(all_types.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(all_types.types['GeneralizedTime1']),
                         'GeneralizedTime(GeneralizedTime1)')
        self.assertEqual(repr(all_types.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(all_types.types['SetOf']), 'SetOf(SetOf, Integer())')

    def test_all_types_automatic_tags(self):
        all_types = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn', 'der')

        datas = [
            ('Sequence3',
             {'a': 1, 'c': 2,'d': True},
             b'\x30\x09\x80\x01\x01\x82\x01\x02\x83\x01\xff')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'der')

        # The length can be decoded.
        datas = [
            (b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3?', 16),
            (b'0\x10\x02\x02\x01\x16\x09Is 1+10=14?', 18),
            (b'0\x0d', 15),
            (b'0\x84\x00\x00\x00\xb8', 190)
        ]

        for encoded_message, decoded_length in datas:
            length = foo.decode_length(encoded_message)
            self.assertEqual(length, decoded_length)

        # The length cannot be decoded.
        datas = [
            b'0',
            b'',
            b'0\x84\x00\x00\x00'
        ]

        for encoded in datas:
            with self.assertRaises(asn1tools.DecodeError) as cm:
                foo.decode_length(encoded)

            self.assertEqual(str(cm.exception),
                             ': not enough data to decode the length')

    def test_long_tag(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS IMPLICIT TAGS ::= BEGIN "
            "A ::= [31] INTEGER "
            "B ::= [500] INTEGER "
            "END")

        datas = [
            ('A', 1, b'\x9f\x1f\x01\x01'),
            ('B', 1, b'\x9f\x83\x74\x01\x01')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)


if __name__ == '__main__':
    unittest.main()
