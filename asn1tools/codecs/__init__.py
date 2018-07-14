import binascii
from datetime import datetime
from datetime import timedelta

from ..errors import Error
from ..errors import EncodeError as _EncodeError
from ..errors import DecodeError as _DecodeError
from ..errors import ConstraintsError as _ConstraintsError
from .. import compat


class EncodeError(_EncodeError):
    """General ASN.1 encode error.

    """

    def __init__(self, message):
        super(EncodeError, self).__init__()
        self.message = message
        self.location = []

    def __str__(self):
        if self.location:
            return "{}: {}".format(': '.join(self.location[::-1]),
                                   self.message)
        else:
            return self.message


class DecodeError(_DecodeError):
    """General ASN.1 decode error with error location in the message.

    """

    def __init__(self, message):
        super(DecodeError, self).__init__()
        self.message = message
        self.location = []

    def __str__(self):
        if self.location:
            return "{}: {}".format(': '.join(self.location[::-1]),
                                   self.message)
        else:
            return self.message


class ConstraintsError(_ConstraintsError):
    """General ASN.1 constraints error with error location in the message.

    """

    def __init__(self, message):
        super(ConstraintsError, self).__init__()
        self.message = message
        self.location = []

    def __str__(self):
        if self.location:
            return "{}: {}".format(': '.join(self.location[::-1]),
                                   self.message)
        else:
            return self.message


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


class OutOfDataError(DecodeError):

    def __init__(self, offset):
        super(OutOfDataError, self).__init__(
            'out of data at bit offset {} ({}.{} bytes)'.format(
                offset,
                *divmod(offset, 8)))


def _generalized_time_to_datetime(string):
    length = len(string)

    if '.' in string:
        try:
            return datetime.strptime(string, '%Y%m%d%H%M.%f')
        except ValueError:
            return datetime.strptime(string, '%Y%m%d%H%M%S.%f')
    elif ',' in string:
        try:
            return datetime.strptime(string, '%Y%m%d%H%M,%f')
        except ValueError:
            return datetime.strptime(string, '%Y%m%d%H%M%S,%f')
    elif length == 12:
        return datetime.strptime(string, '%Y%m%d%H%M')
    elif length == 14:
        return datetime.strptime(string, '%Y%m%d%H%M%S')
    else:
        raise ValueError


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

    try:
        if string[-1] == 'Z':
            if length == 11:
                return datetime.strptime(string[:-1], '%y%m%d%H%M')
            elif length == 13:
                return datetime.strptime(string[:-1], '%y%m%d%H%M%S')
            else:
                raise ValueError
        elif length == 15:
            return compat.strptime(string, '%y%m%d%H%M%z')
        elif length == 17:
            return compat.strptime(string, '%y%m%d%H%M%S%z')
        else:
            raise ValueError
    except (ValueError, IndexError):
        raise Error(
            "Expected a UTC time string, but got '{}'.".format(string))


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


def restricted_utc_time_to_datetime(string):
    """Convert given restricted ASN.1 UTC time string `string` to a
    ``datetime.datetime`` object.

    """

    try:
        if string[-1] != 'Z':
            raise ValueError

        if len(string) != 13:
            raise ValueError

        return datetime.strptime(string[:-1], '%y%m%d%H%M%S')
    except (ValueError, IndexError):
        raise Error(
            "Expected a restricted UTC time string, but got '{}'.".format(
                string))


def restricted_utc_time_from_datetime(date):
    """Convert given ``datetime.datetime`` object `date` to an restricted
    ASN.1 UTC time string.

    """

    if date.tzinfo is not None:
        date -= date.utcoffset()

    return date.strftime('%y%m%d%H%M%S') + 'Z'


def generalized_time_to_datetime(string):
    """Convert given ASN.1 generalized time string `string` to a
    ``datetime.datetime`` object.

    """

    try:
        if string[-1] == 'Z':
            date = _generalized_time_to_datetime(string[:-1])

            return date.replace(tzinfo=compat.timezone(timedelta(hours=0)))
        elif string[-5] in '-+':
            if '.' in string:
                try:
                    return compat.strptime(string, '%Y%m%d%H%M.%f%z')
                except ValueError:
                    return compat.strptime(string, '%Y%m%d%H%M%S.%f%z')
            elif ',' in string:
                try:
                    return compat.strptime(string, '%Y%m%d%H%M,%f%z')
                except ValueError:
                    return compat.strptime(string, '%Y%m%d%H%M%S,%f%z')
            else:
                return compat.strptime(string, '%Y%m%d%H%M%S%z')
        else:
            return _generalized_time_to_datetime(string)
    except (ValueError, IndexError):
        raise Error(
            "Expected a generalized time string, but got '{}'.".format(
                string))


def generalized_time_from_datetime(date):
    """Convert given ``datetime.datetime`` object `date` to an ASN.1
    generalized time string.

    """

    if date.second == 0:
        if date.microsecond > 0:
            string = date.strftime('%Y%m%d%H%M.%f').rstrip('0')
        else:
            string = date.strftime('%Y%m%d%H%M')
    else:
        if date.microsecond > 0:
            string = date.strftime('%Y%m%d%H%M%S.%f').rstrip('0')
        else:
            string = date.strftime('%Y%m%d%H%M%S')

    if date.tzinfo is not None:
        if date.utcoffset():
            string += date.strftime('%z')
        else:
            string += 'Z'

    return string


def restricted_generalized_time_to_datetime(string):
    """Convert given restricted ASN.1 generalized time string `string` to
    a ``datetime.datetime`` object.

    """

    try:
        if string[-1] != 'Z':
            raise ValueError

        if '.' in string:
            if string[-2] == '0':
                raise ValueError

            if string[14] != '.':
                raise ValueError

            return datetime.strptime(string[:-1], '%Y%m%d%H%M%S.%f')
        elif len(string) != 15:
            raise ValueError

        return datetime.strptime(string[:-1], '%Y%m%d%H%M%S')
    except (ValueError, IndexError):
        raise Error(
            "Expected a restricted generalized time string, but got '{}'.".format(
                string))


def restricted_generalized_time_from_datetime(date):
    """Convert given ``datetime.datetime`` object `date` to an restricted
    ASN.1 generalized time string.

    """

    if date.tzinfo is not None:
        date -= date.utcoffset()

    if date.microsecond > 0:
        string = date.strftime('%Y%m%d%H%M%S.%f').rstrip('0')
    else:
        string = date.strftime('%Y%m%d%H%M%S')

    return string + 'Z'
