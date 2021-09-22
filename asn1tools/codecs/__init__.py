import binascii
from datetime import datetime
from datetime import timedelta
from functools import wraps

from ..errors import Error
from ..errors import EncodeError as _EncodeError
from ..errors import DecodeError as _DecodeError
from ..errors import ConstraintsError as _ConstraintsError
from .. import compat


class BaseType(object):
    """
    Base Type class containing common functionality between all codecs
    """

    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
        self.optional = False
        self.default = None

    def set_default(self, value):
        self.default = value

    def get_default(self):
        return self.default

    def has_default(self):
        return self.default is not None

    def is_default(self, value):
        return value == self.default

    def encode(self, *args, **kwargs):
        raise NotImplementedError('To be implemented by subclasses.')

    def decode(self, *args, **kwargs):
        raise NotImplementedError('To be implemented by subclasses.')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)

    def type_label(self):
        return '{}({})'.format(self.type_name, self.name) if self.name else self.type_name


class ErrorWithLocation(Exception):
    """
    Mixin for Error classes which have location list
    """
    def __init__(self, message, location=None):
        self.message = message
        self.location = [location] if location else []

    def add_location(self, element_name):
        self.location.append(element_name)

    def __str__(self):
        if self.location:
            return "{}: {}".format('.'.join(self.location[::-1]),
                                   self.message)
        else:
            return self.message


class EncodeError(ErrorWithLocation, _EncodeError):
    """General ASN.1 encode error.

    """
    pass


class DecodeError(ErrorWithLocation, _DecodeError):
    """
    General ASN.1 decode error with error location in the message.
    """

    def __init__(self, message, offset=None, location=None):
        """

        :param str message: Message for error
        :param int offset: Data offset at which error occurred. Can be bits or bytes depending on codec
        :param str location: Name of element in which error occured
        """
        super(DecodeError, self).__init__(message, location=location)
        self.offset = offset

    def __str__(self):
        if self.location:
            _str = "{}: {}".format('.'.join(self.location[::-1]), self.message)
        else:
            _str = self.message
        if self.offset is not None:
            _str += self.get_offset_message()
        return _str

    def get_offset_message(self):
        """
        Get offset details to add to error message
        :return:
        """
        return ' (At offset: {})'.format(self.offset)


class ConstraintsError(ErrorWithLocation, _ConstraintsError):
    """
    General ASN.1 constraints error with error location in the message.
    """
    pass


class DecodeContentsLengthError(DecodeError):
    """ASN.1 contents length decode error.

    """

    def __init__(self, length, offset, contents_max, location=None):
        message = 'Expected at least {} contents byte(s), but got {}.'.format(length, contents_max - offset)
        super(DecodeContentsLengthError, self).__init__(message, offset=offset, location=location)

        self.length = length
        self.contents_max = contents_max


class OutOfDataError(DecodeError):

    def __init__(self, offset_bits, location=None):
        super(OutOfDataError, self).__init__(
            'out of data', offset=offset_bits, location=location)

    def get_offset_message(self):
        """
        Get offset details to add to error message
        :return:
        """
        return ' (At bit offset: {})'.format(self.offset)


def add_error_location(method):
    """
    Method decorator which catches ErrorWithLocation subclasses and adds element name to location
    If decorator is applied to parent Type class method, this functionality can be disabled on a per-child
    Type basis by setting no_error_location=True
    :param method:
    :return:
    """
    @wraps(method)
    def new_method(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except ErrorWithLocation as e:
            # Don't add name if it is blank (for SEQUENCE OF, SET OF etc)
            if self.name and not getattr(self, 'no_error_location', False):
                e.add_location(self.name)
            raise e
    return new_method


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


def format_bytes(tag):
    """
    Format tag as hex string
    :param bytes tag:
    :return:
    """
    return binascii.hexlify(tag).decode('ascii')