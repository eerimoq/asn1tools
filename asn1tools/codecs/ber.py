"""BER codec.

"""

import struct

import bitstruct

from . import DecodeError
from ..schema import *


class Class(object):
    UNIVERSAL        = 0x00
    APPLICATION      = 0x40
    CONTEXT_SPECIFIC = 0x80
    PRIVATE          = 0xc0


class Encoding(object):
    PRIMITIVE   = 0x00
    CONSTRUCTED = 0x20


class Number(object):
    END_OF_CONTENTS   = 0x00
    BOOLEAN           = 0x01
    INTEGER           = 0x02
    BIT_STRING        = 0x03
    OCTET_STRING      = 0x04
    NULL              = 0x05
    OBJECT_IDENTIFIER = 0x06
    OBJECT_DESCRIPTOR = 0x07
    EXTERNAL          = 0x08
    REAL              = 0x09
    ENUMERATED        = 0x0a
    EMBEDDED_PDV      = 0x0b
    UTF8_STRING       = 0x0c
    RELATIVE_OID      = 0x0d
    SEQUENCE          = 0x10
    SET               = 0x11
    NUMERIC_STRING    = 0x12
    PRINTABLE_STRING  = 0x13
    T61_STRING        = 0x14
    VIDEOTEX_STRING   = 0x15
    IA5_STRING        = 0x16
    UTC_TIME          = 0x17
    GENERALIZED_TIME  = 0x18
    GRAPHIC_STRING    = 0x19
    VISIBLE_STRING    = 0x1a
    GENERAL_STRING    = 0x1b
    UNIVERSAL_STRING  = 0x1c
    CHARACTER_STRING  = 0x1d
    BMP_STRING        = 0x1e


def _encode_integer(decoded):
    return struct.pack('BBB',
                       Number.INTEGER,
                       1,
                       decoded)


def _encode_sequence(decoded, schema):
    return b'\x30\x03\x80\x01\x05'


def _encode_item(decoded, schema):
    if isinstance(schema, Integer):
        encoded = _encode_integer(decoded)
    elif isinstance(schema, Sequence):
        encoded = _encode_sequence(decoded, schema)
    else:
        raise NotImplementedError('encoding not supported')

    return encoded, None

def _decode_length_definite(encoded):
    octet = encoded[0]

    if octet & 0x80:
        raise NotImplementedError()
    else:
        length = octet & 0x7f

    return length, encoded[1:]


def _decode_identifier(encoded):
    """Decode identifier octets.

    """

    octet = encoded[0]
    class_ = (octet & 0xc0)
    encoding = (octet & 0x20)
    number = (octet & 0x1f)

    return class_, encoding, number, encoded[1:]


def _decode_integer(encoded):
    class_, encoding, number, encoded = _decode_identifier(encoded)

    if not ((class_ == Class.CONTEXT_SPECIFIC)
            or (class_ == Class.UNIVERSAL and number == Number.INTEGER)):
        raise DecodeError()

    if encoding != Encoding.PRIMITIVE:
        raise DecodeError()

    length, encoded = _decode_length_definite(encoded)

    return bitstruct.unpack('s' + str(8 * length), encoded)[0], encoded[length:]


def _decode_sequence(encoded, schema):
    _, encoding, number, encoded = _decode_identifier(encoded)

    if number != Number.SEQUENCE:
        raise DecodeError()

    if encoding != Encoding.CONSTRUCTED:
        raise DecodeError()

    if encoded[0] == 0x80:
        # Decode until an end-of-contents number is found.
        raise NotImplementedError()
    else:
        length, encoded = _decode_length_definite(encoded)

    values = {}

    for item in schema.items:
        decoded, encoded = _decode_item(encoded, item)
        values[item.name] = decoded

    return values, encoded


def _decode_ia5_string(encoded):
    return encoded.decode('ascii')


def _decode_item(encoded, schema):
    if isinstance(schema, Integer):
        decoded, encoded = _decode_integer(encoded)
    elif isinstance(schema, Sequence):
        decoded, encoded = _decode_sequence(encoded, schema)
    else:
        raise NotImplementedError()

    return decoded, encoded


def encode(data, schema):
    """Encode given data dictionary using given schema and return the
    encoded data as a bytes object.

    """

    return _encode_item(data, schema)[0]


def decode(data, schema):
    """Decode given binary data using given schema and retuns the decoded
    data as a dictionary.

    """

    return _decode_item(bytearray(data), schema)[0]
