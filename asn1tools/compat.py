"""Python 2 & 3 compatibility.

"""

import sys
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo


if sys.version_info[0] > 2:
    from datetime import timezone

    UTC = timezone.utc

    def strptime(data, fmt):
        return datetime.strptime(data, fmt)
else:
    class timezone(tzinfo):

        def __init__(self, offset):
            self._utcoffset = offset

        def utcoffset(self, dt):
            return self._utcoffset

        def tzname(self, dt):
            return "-"

        def dst(self, dt):
            return timedelta(0)

    UTC = timezone(timedelta(hours=0, minutes=0))

    def strptime(data, fmt):
        if fmt.endswith('%z'):
            date = datetime.strptime(data[:-5], fmt[:-2])

            try:
                sign = {'-': -1, '+': 1}[data[-5]]
                hours = sign * int(data[-4:-2])
                minutes = sign * int(data[-2:])
            except KeyError:
                raise ValueError(
                    "time data '{}' does not match format '{}'.".format(
                        data,
                        fmt))

            date = date.replace(tzinfo=timezone(timedelta(hours=hours,
                                                          minutes=minutes)))
        else:
            date = datetime.strptime(data, fmt)

        return date
