import unittest
from datetime import datetime
from datetime import timedelta

import asn1tools
from asn1tools.codecs import utc_time_to_datetime
from asn1tools.codecs import utc_time_from_datetime
from asn1tools.codecs import generalized_time_to_datetime
from asn1tools.codecs import generalized_time_from_datetime

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

    def test_generalized_time(self):
        datas = [
            ('19820102120022',  datetime(1982, 1, 2, 12, 0, 22)),
            ('19820102120023.500000',
             datetime(1982, 1, 2, 12, 0, 23, 500000)),
            ('19820102120024Z',
             datetime(1982, 1, 2, 12, 0, 24, tzinfo=tzinfo(0))),
            ('19820102120025.100000Z',
             datetime(1982, 1, 2, 12, 0, 25, 100000, tzinfo=tzinfo(0))),
            ('19820102120026-1000',
             datetime(1982, 1, 2, 12, 0, 26, tzinfo=tzinfo(-10))),
            ('19820102120027.100000+0100',
             datetime(1982, 1, 2, 12, 0, 27, 100000, tzinfo=tzinfo(1)))
        ]

        for generalized_time, date in datas:
            actual = generalized_time_to_datetime(generalized_time)
            self.assertEqual(actual, date)
            actual = generalized_time_from_datetime(date)
            self.assertEqual(actual, generalized_time)

    def test_utc_time_to_datetime_errors(self):
        datas = [
            '8201021200K'
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

    def test_generalized_time_to_datetime_errors(self):
        datas = [
            '19820102120022K',
            '19820102120022.100000=0100'
        ]

        for generalized_time in datas:
            with self.assertRaises(ValueError):
                generalized_time_to_datetime(generalized_time)


if __name__ == '__main__':
    unittest.main()
