import unittest
from datetime import datetime
from datetime import timedelta

import asn1tools
from asn1tools.codecs import utc_time_to_datetime
from asn1tools.codecs import utc_time_from_datetime
from asn1tools.codecs import generalized_time_to_datetime
from asn1tools.codecs import generalized_time_from_datetime
from asn1tools.codecs import restricted_utc_time_to_datetime
from asn1tools.codecs import restricted_utc_time_from_datetime
from asn1tools.codecs import restricted_generalized_time_to_datetime
from asn1tools.codecs import restricted_generalized_time_from_datetime

try:
    from datetime import timezone
except ImportError:
    from asn1tools.compat import timezone


def tzinfo(hours, minutes=0):
    return timezone(timedelta(hours=hours, minutes=minutes))


class Asn1ToolsUtilsTest(unittest.TestCase):

    maxDiff = None

    def test_utc_time(self):
        datas = [
            ('8201021200Z',     datetime(1982, 1, 2, 12, 0)),
            ('820102120005Z',   datetime(1982, 1, 2, 12, 0, 5)),
            ('8201021200+0100',
             datetime(1982, 1, 2, 12, 0, tzinfo=tzinfo(1))),
            ('8201021200-0500',
             datetime(1982, 1, 2, 12, 0, tzinfo=tzinfo(-5))),
            ('180102120003+0000',
             datetime(2018, 1, 2, 12, 0, 3, tzinfo=tzinfo(0)))
        ]

        for utc_time, date in datas:
            actual = utc_time_to_datetime(utc_time)
            self.assertEqual(actual, date)
            actual = utc_time_from_datetime(date)
            self.assertEqual(actual, utc_time)

    def test_restricted_utc_time(self):
        datas = [
            (
                datetime(1982, 1, 2, 12, 0, 5),
                '820102120005Z',
                datetime(1982, 1, 2, 12, 0, 5)
            ),
            (
                datetime(1982, 1, 2, 12, 0, 5, tzinfo=tzinfo(1)),
                '820102110005Z',
                datetime(1982, 1, 2, 11, 0, 5)
            ),
            (
                datetime(1982, 1, 2, 12, 0, 5, tzinfo=tzinfo(-12)),
                '820103000005Z',
                datetime(1982, 1, 3, 0, 0, 5)
            ),
            (
                datetime(2032, 12, 31),
                '321231000000Z',
                datetime(2032, 12, 31)
            )
        ]

        for date_in, utc_time, date_out in datas:
            actual = restricted_utc_time_from_datetime(date_in)
            self.assertEqual(actual, utc_time)
            actual = restricted_utc_time_to_datetime(utc_time)
            self.assertEqual(actual, date_out)

    def test_generalized_time(self):
        datas = [
            ('19820102120022',  datetime(1982, 1, 2, 12, 0, 22)),
            ('19820102120023.5',
             datetime(1982, 1, 2, 12, 0, 23, 500000)),
            ('19820102120024Z',
             datetime(1982, 1, 2, 12, 0, 24, tzinfo=tzinfo(0))),
            ('19820102120025.1Z',
             datetime(1982, 1, 2, 12, 0, 25, 100000, tzinfo=tzinfo(0))),
            ('19820102120026-1000',
             datetime(1982, 1, 2, 12, 0, 26, tzinfo=tzinfo(-10))),
            ('19820102120027.1+0100',
             datetime(1982, 1, 2, 12, 0, 27, 100000, tzinfo=tzinfo(1)))
        ]

        for generalized_time, date in datas:
            actual = generalized_time_to_datetime(generalized_time)
            self.assertEqual(actual, date)
            actual = generalized_time_from_datetime(date)
            self.assertEqual(actual, generalized_time)

    def test_restricted_generalized_time(self):
        datas = [
            (
                datetime(1982, 1, 2, 12, 0, 5),
                '19820102120005Z',
                datetime(1982, 1, 2, 12, 0, 5)
            ),
            (
                datetime(1982, 1, 2, 12, 0, 5, tzinfo=tzinfo(1)),
                '19820102110005Z',
                datetime(1982, 1, 2, 11, 0, 5)
            ),
            (
                datetime(1982, 1, 2, 12, 0, 5, tzinfo=tzinfo(-12)),
                '19820103000005Z',
                datetime(1982, 1, 3, 0, 0, 5)
            ),
            (
                datetime(1932, 12, 31),
                '19321231000000Z',
                datetime(1932, 12, 31)
            ),
            (
                datetime(2032, 12, 31, 0, 2, 1, 100000),
                '20321231000201.1Z',
                datetime(2032, 12, 31, 0, 2, 1, 100000)
            ),
            (
                datetime(1931, 12, 31, 0, 2, 2, 999000),
                '19311231000202.999Z',
                datetime(1931, 12, 31, 0, 2, 2, 999000)
            )
        ]

        for date_in, generalized_time, date_out in datas:
            actual = restricted_generalized_time_from_datetime(date_in)
            self.assertEqual(actual, generalized_time)
            actual = restricted_generalized_time_to_datetime(generalized_time)
            self.assertEqual(actual, date_out)

    def test_utc_time_to_datetime_errors(self):
        datas = [
            '8201021200K',
            'Z820102120011Z'
        ]

        for utc_time in datas:
            with self.assertRaises(asn1tools.Error):
                utc_time_to_datetime(utc_time)

        datas = [
            '820102120060Z',
            '8201021200*0100',
            '82010212000000100'
        ]

        for utc_time in datas:
            with self.assertRaises(ValueError):
                utc_time_to_datetime(utc_time)

    def test_restricted_utc_time_errors(self):
        with self.assertRaises(asn1tools.Error) as cm:
            restricted_utc_time_to_datetime('8201021200Z')

        self.assertEqual(
            str(cm.exception),
            "Expected a restricted UTC time string of length 13, but "
            "got '8201021200Z'.")

        with self.assertRaises(asn1tools.Error) as cm:
            restricted_utc_time_to_datetime('8201021200+0100')

        self.assertEqual(
            str(cm.exception),
            "Expected a restricted UTC time string ending with 'Z', but "
            "got '8201021200+0100'.")

        with self.assertRaises(asn1tools.Error) as cm:
            restricted_utc_time_to_datetime('180102120003+0000')

        self.assertEqual(
            str(cm.exception),
            "Expected a restricted UTC time string ending with 'Z', but "
            "got '180102120003+0000'.")

    def test_generalized_time_to_datetime_errors(self):
        datas = [
            '19820102120022K',
            '19820102120022.1=0100'
        ]

        for generalized_time in datas:
            with self.assertRaises(ValueError):
                generalized_time_to_datetime(generalized_time)

    def test_restricted_generalized_time_errors(self):
        with self.assertRaises(asn1tools.Error) as cm:
            restricted_generalized_time_to_datetime('198201021200Z')

        self.assertEqual(
            str(cm.exception),
            "Expected a restricted generalized time string, but got "
            "'198201021200Z'.")

        with self.assertRaises(asn1tools.Error) as cm:
            restricted_generalized_time_to_datetime('198201021200+0100')

        self.assertEqual(
            str(cm.exception),
            "Expected a restricted generalized time string ending "
            "with 'Z', but got '198201021200+0100'.")

        with self.assertRaises(asn1tools.Error) as cm:
            restricted_generalized_time_to_datetime('20180102120003.0Z')

        self.assertEqual(
            str(cm.exception),
            "Expected a restricted generalized time string with no trailing "
            "zeros, but got '20180102120003.0Z'.")

        with self.assertRaises(ValueError) as cm:
            restricted_generalized_time_to_datetime('20180102120003.Z')

        self.assertEqual(
            str(cm.exception),
            "time data '20180102120003.' does not match format "
            "'%Y%m%d%H%M%S.%f'")


if __name__ == '__main__':
    unittest.main()
