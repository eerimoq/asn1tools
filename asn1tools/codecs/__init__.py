import binascii
from ..errors import EncodeError as _EncodeError
from ..errors import DecodeError as _DecodeError


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
