"""BER codec.

"""

from . import DecodeError
from ..types import Sequence


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


def _decode_length_definite(data):
    octet = data[0]

    if octet & 0x80:
        raise NotImplementedError()
    else:
        length = octet & 0x7f

    return length, data[1:]


def _decode_identifier(data):
    """Decode identifier octets.

    """

    octet = data[0]

    class_ = (octet & 0xc0)
    encoding = (octet & 0x20)
    number = (octet & 0x1f)

    print(class_, encoding, number)

    if number > 30:
        raise NotImplementedError()

    if class_ != Class.UNIVERSAL:
        raise NotImplementedError()

    return class_, encoding, number, data[1:]


def _decode_sequence(data, schema):
    class_, encoding, number, data = _decode_identifier(data)

    if number != Number.SEQUENCE:
        raise DecodeError()
    
    if encoding != Encoding.CONSTRUCTED:
        raise DecodeError()
    
    if data[1] == 0x80:
        # Decode until an end-of-contents number is found.
        raise NotImplementedError()
    else:
        length, data = _decode_length_definite(data[1:])

    values = {}

    for item in schema.items:
        decoded, data = _decode_item(data, item)
        values[item.name] = decoded

    return values


def _decode_integer(data):
    if len(data) > 1:
        raise NotImplementedError()

    return data[0]


def _decode_ia5_string(data):
    return data.decode('ascii')


def _decode_item(data, schema):
    if isinstance(schema, Sequence):
        decoded, data = _decode_sequence(data, schema)
    if isinstance(schema, Integer):
        decoded, data = _decode_integer(data, schema)
    else:
        raise NotImplementedError()

    return decoded

#    # Decode identifier octets.
#    octet = data[0]
#
#    class_ = octet >> 6
#    encoding = (octet >> 5) & 1
#    number = octet & 0x1f
#
#    #print(class_, encoding, number)
#
#    if number > 30:
#        raise NotImplementedError()
#
#    if class_ != Class.UNIVERSAL:
#        raise NotImplementedError()
#
#    # Decode length octets.
#    if encoding == Encoding.PRIMITIVE:
#        length, data = _decode_length_definite(data[1:])
#    else:
#        octet = data[1]
#
#        if octet == 0x80:
#            # Decode until an end-of-contents number is found.
#            raise NotImplementedError()
#        else:
#            length, data = _decode_length_definite(data[1:])
#
#    if len(data) < length:
#        raise Exception()
#
#    # Decode contents octets.
#    if number == Number.SEQUENCE:
#        decoded = _decode_sequence(data[:length])
#    elif number == Number.INTEGER:
#        decoded = _decode_integer(data[:length])
#    elif number == Number.IA5_STRING:
#        decoded = _decode_ia5_string(data[:length])
#    else:
#        raise NotImplementedError('Unsupported tag number {}.'.format(number))
#
#    return (number, decoded), data[length:]


def encode(data, schema):
    """Encode given BER data dictionary.

    """

    return b''


def decode(data, schema):
    """Decode given BER encoded data.

    """

    return _decode_item(data, schema)[0]
