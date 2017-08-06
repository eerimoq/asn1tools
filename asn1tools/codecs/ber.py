"""BER (Basic Encoding Rules) codec.

"""

import struct
import math

import bitstruct

from . import EncodeError, DecodeError
from ..schema import Module, Sequence, Integer, Boolean, IA5String


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
    if decoded == 0:
        bits = 8
    else:
        bits = int(8 * math.ceil((math.log(abs(decoded), 2) + 1) / 8))

    return bitstruct.pack('u8u8s' + str(bits),
                          Number.INTEGER,
                          bits / 8,
                          decoded)


def _encode_boolean(decoded):
    return bitstruct.pack('u8u8b8',
                          Number.BOOLEAN,
                          1,
                          decoded)


def _encode_ia5_string(decoded):
    return (bitstruct.pack('u8u8', Number.IA5_STRING, len(decoded))
            + decoded.encode('ascii'))


def _encode_sequence(decoded, schema):
    encoded = b''

    for item in schema.values:
        if item.name in decoded:
            encoded += _encode_item(decoded[item.name], item)
        elif item.default is None:
            raise EncodeError("Missing value for item '{}' in schema '{}'.".format(
                item.name,
                schema.name))

    return struct.pack('BB',
                       Encoding.CONSTRUCTED | Number.SEQUENCE,
                       len(encoded)) + encoded


def _encode_module(decoded, schema):
    if len(decoded) != 1:
        raise EncodeError()

    for key in decoded.keys():
        name = key

    item = schema.get_item_by_name(name)

    return _encode_item(decoded[name], item)


def _encode_item(decoded, schema):
    if isinstance(schema, Integer):
        encoded = _encode_integer(decoded)
    elif isinstance(schema, Boolean):
        encoded = _encode_boolean(decoded)
    elif isinstance(schema, Sequence):
        encoded = _encode_sequence(decoded, schema)
    elif isinstance(schema, IA5String):
        encoded = _encode_ia5_string(decoded)
    elif isinstance(schema, Module):
        encoded = _encode_module(decoded, schema)
    else:
        raise NotImplementedError('encoding of schema {} is not supported'.format(
            type(schema)))

    return encoded


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


def _decode_boolean(encoded):
    class_, encoding, number, encoded = _decode_identifier(encoded)

    if not ((class_ == Class.CONTEXT_SPECIFIC)
            or (class_ == Class.UNIVERSAL and number == Number.BOOLEAN)):
        raise DecodeError()

    if encoding != Encoding.PRIMITIVE:
        raise DecodeError()

    length, encoded = _decode_length_definite(encoded)

    if length != 1:
        raise DecodeError()

    return bitstruct.unpack('b8', encoded)[0], encoded[length:]


def _decode_ia5_string(encoded):
    _, encoding, number, encoded = _decode_identifier(encoded)

    if number != Number.IA5_STRING:
        raise DecodeError()

    if encoding != Encoding.PRIMITIVE:
        raise DecodeError()

    length, encoded = _decode_length_definite(encoded)

    return encoded[:length].decode('ascii'), encoded[length:]


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

    if length > len(encoded):
        raise DecodeError()

    values = {}

    for item in schema.values:
        try:
            decoded, encoded = _decode_item(encoded, item)
            value = decoded

        except DecodeError:
            if item.optional:
                continue

            if item.default is None:
                raise DecodeError()

            value = item.default

        values[item.name] = value

    return values, encoded


def _decode_module(encoded, schema):
    raise NotImplementedError()


def _decode_item(encoded, schema):
    if isinstance(schema, Integer):
        decoded, encoded = _decode_integer(encoded)
    elif isinstance(schema, Boolean):
        decoded, encoded = _decode_boolean(encoded)
    elif isinstance(schema, IA5String):
        decoded, encoded = _decode_ia5_string(encoded)
    elif isinstance(schema, Sequence):
        decoded, encoded = _decode_sequence(encoded, schema)
    elif isinstance(schema, Module):
        decoded, encoded = _decode_module(encoded, schema)
    else:
        raise NotImplementedError('decoding of schema {} is not supported'.format(
            type(schema)))

    return decoded, encoded


def encode(data, schema):
    """Encode given dictionary `data` using given schema `schema` and
    return the encoded data as a bytes object.

    """

    return _encode_item(data, schema)


def decode(data, schema):
    """Decode given bytes object `data` using given schema `schema` and
    return the decoded data as a dictionary.

    """

    return _decode_item(bytearray(data), schema)[0]
