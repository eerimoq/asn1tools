"""Python type checker.

"""

import sys
import logging
import datetime

from . import EncodeError


LOGGER = logging.getLogger(__name__)


class Type(object):

    TYPE = None

    def __init__(self, inner):
        self.inner = inner

    def encode(self, data, *args, **kwargs):
        if not isinstance(data, self.TYPE):
            raise EncodeError(
                'Expected data of type {}, but got {}.'.format(self.TYPE.__name__,
                                                               data))

        return self.inner.encode(data, *args, **kwargs)

    def decode(self, *args, **kwargs):
        return self.inner.decode(*args, **kwargs)

    def __repr__(self):
        return repr(self.inner)


class Boolean(Type):

    TYPE = bool


class Integer(Type):

    TYPE = int


class Float(Type):

    def encode(self, data, *args, **kwargs):
        if not isinstance(data, (float, int)):
            raise EncodeError(
                'Expected data of type float or int, but got {}.'.format(data))

        return self.inner.encode(data, *args, **kwargs)


class Null(Type):

    def encode(self, data, *args, **kwargs):
        if data is not None:
            raise EncodeError('Expected None, but got {}.'.format(data))

        return self.inner.encode(data, *args, **kwargs)


class BitString(Type):

    def encode(self, data, *args, **kwargs):
        if (not isinstance(data, tuple)
            or len(data) != 2
            or not isinstance(data[0], bytes)
            or not isinstance(data[1], int)):
            raise EncodeError(
                'Expected data of type tuple(bytes, int), but got {}.'.format(
                    data))

        return self.inner.encode(data, *args, **kwargs)


class Bytes(Type):

    def encode(self, data, *args, **kwargs):
        if not isinstance(data, (bytes, bytearray)):
            raise EncodeError(
                'Expected data of type bytes or bytearray, but got {}.'.format(
                    data))

        return self.inner.encode(data, *args, **kwargs)


class String(Type):

    def encode(self, data, *args, **kwargs):
        if sys.version_info[0] > 2:
            if not isinstance(data, str):
                raise EncodeError(
                    'Expected data of type str, but got {}.'.format(data))
        else:
            if not isinstance(data, (str, unicode)):
                raise EncodeError(
                    'Expected data of type str, but got {}.'.format(data))

        return self.inner.encode(data, *args, **kwargs)


class Dict(Type):

    TYPE = dict


class Choice(Type):

    def encode(self, data, *args, **kwargs):
        if (not isinstance(data, tuple)
            or len(data) != 2
            or not isinstance(data[0], str)):
            raise EncodeError(
                'Expected data of type tuple(str, object), but got {}.'.format(
                    data))

        return self.inner.encode(data, *args, **kwargs)


class Time(Type):

    def encode(self, data, *args, **kwargs):
        if not isinstance(data, datetime.datetime):
            raise EncodeError(
                'Expected data of type datetime.datetime, but got {}.'.format(
                    data))

        return self.inner.encode(data, *args, **kwargs)
