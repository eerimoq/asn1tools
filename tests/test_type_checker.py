#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import datetime
import asn1tools.codecs.type_checker


class Type(object):

    def encode(self, data):
        pass


class Asn1ToolsEncodeTypeCheckerTest(unittest.TestCase):

    maxDiff = None

    def assert_good_bad(self,
                        checker_class,
                        expected_type_string,
                        good_datas,
                        bad_datas):
        checker = checker_class(Type())

        for data in good_datas:
            checker.encode(data)

        for data in bad_datas:
            with self.assertRaises(asn1tools.EncodeError) as cm:
                checker.encode(data)

            self.assertEqual(str(cm.exception),
                             '{}, but got {}.'.format(expected_type_string,
                                                      data))

    def test_boolean(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.Boolean,
                             'Expected data of type bool',
                             good_datas=[True, False],
                             bad_datas=[1, 'foo'])

    def test_integer(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.Integer,
                             'Expected data of type int',
                             good_datas=[1, -1],
                             bad_datas=['1', None])

    def test_float(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.Float,
                             'Expected data of type float or int',
                             good_datas=[1, -1.0],
                             bad_datas=['1.0', None])

    def test_null(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.Null,
                             'Expected None',
                             good_datas=[None],
                             bad_datas=['1.0', 1])

    def test_bit_string(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.BitString,
                             'Expected data of type tuple(bytes, int)',
                             good_datas=[(b'', 0)],
                             bad_datas=[1, '101', (1, 0, 1), None])

    def test_bytes(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.Bytes,
                             'Expected data of type bytes or bytearray',
                             good_datas=[b'7', bytearray()],
                             bad_datas=[1, {}, None])

    def test_string(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.String,
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_dict(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.Dict,
                             'Expected data of type dict',
                             good_datas=[{}],
                             bad_datas=[(1, ), 1, b'101', None])

    def test_choice(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.Choice,
                             'Expected data of type tuple(str, object)',
                             good_datas=[('a', None), ('b', {})],
                             bad_datas=[(1, None), {'a': 1}, None])

    def test_time(self):
        self.assert_good_bad(asn1tools.codecs.type_checker.Time,
                             'Expected data of type datetime.datetime',
                             good_datas=[datetime.datetime(1, 2, 3)],
                             bad_datas=[1.4, None])


if __name__ == '__main__':
    unittest.main()
