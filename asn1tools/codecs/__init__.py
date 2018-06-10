import binascii
from datetime import datetime
from datetime import timedelta

from ..errors import Error
from ..errors import EncodeError as _EncodeError
from ..errors import DecodeError as _DecodeError
from .. import compat


class EncodeError(_EncodeError):
    """General ASN.1 encode error.

    """

    pass


class DecodeError(_DecodeError):
    """General ASN.1 decode error with error location in the message.

    """

    def __init__(self, message):
        super(DecodeError, self).__init__()
        self.message = message
        self.location = []

    def __str__(self):
        return "{}: {}".format(': '.join(self.location[::-1]),
                               self.message)


class DecodeTagError(DecodeError):
    """ASN.1 tag decode error.

    """

    def __init__(self, type_name, expected_tag, actual_tag, offset):
        message = "Expected {} with tag '{}' at offset {}, but got '{}'.".format(
            type_name,
            binascii.hexlify(expected_tag).decode('ascii'),
            offset,
            binascii.hexlify(actual_tag).decode('ascii'))
        super(DecodeTagError, self).__init__(message)


class DecodeContentsLengthError(DecodeError):
    """ASN.1 contents length decode error.

    """

    def __init__(self, length, offset, contents_max):
        message = ('Expected at least {} contents byte(s) at offset {}, '
                   'but got {}.').format(length,
                                         offset,
                                         contents_max - offset)
        super(DecodeContentsLengthError, self).__init__(message)

        self.length = length
        self.offset = offset
        self.contents_max = contents_max


def format_or(items):
    """Return a string of comma separated items, with the last to items
    separated by "or".

    [1, 2, 3] -> "1, 2 or 3"

    """

    formatted_items = []

    for item in items:
        try:
            item = "'" + item + "'"
        except TypeError:
            item = str(item)

        formatted_items.append(item)

    if len(items) == 1:
        return formatted_items[0]
    else:
        return '{} or {}'.format(', '.join(formatted_items[:-1]),
                                 formatted_items[-1])


def utc_time_to_datetime(string):
    """Convert given ASN.1 UTC time string `string` to a
    ``datetime.datetime`` object.

    """

    length = len(string)

    if string[-1] == 'Z':
        if length == 11:
            return datetime.strptime(string[:10], '%y%m%d%H%M')
        elif length == 13:
            return datetime.strptime(string[:12], '%y%m%d%H%M%S')
        else:
            raise Error(
                "Expected an UTC time string, but got '{}'.".format(string))
    elif length == 15:
        return compat.strptime(string, '%y%m%d%H%M%z')
    elif length == 17:
        return compat.strptime(string, '%y%m%d%H%M%S%z')
    else:
        raise Error(
            "Expected an UTC time string, but got '{}'.".format(string))


def utc_time_from_datetime(date):
    """Convert given ``datetime.datetime`` object `date` to an ASN.1 UTC
    time string.

    """

    fmt = '%y%m%d%H%M'

    if date.second > 0:
        fmt += '%S'

    if date.tzinfo is None:
        fmt += 'Z'
    else:
        fmt += '%z'

    return date.strftime(fmt)


def generalized_time_to_datetime(string):
    """Convert given ASN.1 generalized time string `string` to a
    ``datetime.datetime`` object.

    """

    length = len(string)

    if string[-1] == 'Z':
        if length == 15:
            date = datetime.strptime(string[:14], '%Y%m%d%H%M%S')
        else:
            date = datetime.strptime(string[:-1], '%Y%m%d%H%M%S.%f')

        return date.replace(tzinfo=compat.timezone(timedelta(hours=0)))
    elif string[-5] in '-+':
        if length == 19:
            return compat.strptime(string, '%Y%m%d%H%M%S%z')
        else:
            return compat.strptime(string, '%Y%m%d%H%M%S.%f%z')
    else:
        if length == 14:
            return compat.strptime(string, '%Y%m%d%H%M%S')
        else:
            return compat.strptime(string, '%Y%m%d%H%M%S.%f')


def generalized_time_from_datetime(date):
    """Convert given ``datetime.datetime`` object `date` to an ASN.1
    generalized time string.

    """

    fmt = '%Y%m%d%H%M%S'

    if date.microsecond > 0:
        fmt += '.%f'

    if date.tzinfo is not None:
        if date.utcoffset():
            fmt += '%z'
        else:
            fmt += 'Z'

    return date.strftime(fmt)
