"""Basic Encoding Rules (BER) codec.

"""

import math
import binascii
from copy import copy

from . import EncodeError
from . import DecodeError
from . import DecodeTagError
from . import DecodeContentsLengthError
from . import compiler
from .compiler import enum_values_as_dict


class Class(object):
    UNIVERSAL        = 0x00
    APPLICATION      = 0x40
    CONTEXT_SPECIFIC = 0x80
    PRIVATE          = 0xc0


class Encoding(object):
    PRIMITIVE   = 0x00
    CONSTRUCTED = 0x20


class Tag(object):
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


class DecodeChoiceError(Exception):
    pass


def encode_length_definite(length):
    if length <= 127:
        encoded = bytearray([length])
    else:
        encoded = bytearray()

        while length > 0:
            encoded.append(length & 0xff)
            length >>= 8

        encoded.append(0x80 | len(encoded))
        encoded.reverse()

    return encoded


def decode_length_definite(encoded, offset):
    length = encoded[offset]
    offset += 1

    if length > 127:
        if length == 128:
            raise DecodeError(
                'expected definite length at offset {}, but got indefinite'.format(
                    offset - 1))

        number_of_bytes = (length & 0x7f)
        encoded_length = encoded[offset:number_of_bytes + offset]

        if len(encoded_length) != number_of_bytes:
            raise IndexError(
                'expected {} length byte(s) at offset {}, but got {}'.format(
                    number_of_bytes,
                    offset,
                    len(encoded_length)))

        length = decode_integer(encoded_length)
        offset += number_of_bytes

    if offset + length > len(encoded):
        raise DecodeContentsLengthError(length, offset, len(encoded))

    return length, offset


def decode_length_constructed(encoded, offset):
    length = encoded[offset]

    if length == 128:
        return None, offset + 1
    else:
        return decode_length_definite(encoded, offset)


def decode_integer(data):
    value = 0

    for byte in data:
        value <<= 8
        value += byte

    return value


def encode_signed_integer(data):
    encoded = bytearray()

    if data < 0:
        data *= -1
        data -= 1
        carry = not data

        while data > 0:
            encoded.append((data & 0xff) ^ 0xff)
            carry = (data & 0x80)
            data >>= 8

        if carry:
            encoded.append(0xff)
    elif data > 0:
        while data > 0:
            encoded.append(data & 0xff)
            data >>= 8

        if encoded[-1] & 0x80:
            encoded.append(0)
    else:
        encoded.append(0)

    encoded.append(len(encoded))
    encoded.reverse()

    return encoded


def decode_signed_integer(data):
    value = 0
    is_negative = (data[0] & 0x80)

    for byte in data:
        value <<= 8
        value += byte

    if is_negative:
        value -= (1 << (8 * len(data)))

    return value


def encode_tag(number, flags):
    if number < 31:
        tag = bytearray([flags | number])
    else:
        tag = bytearray([flags | 0x1f])
        encoded = bytearray()

        while number > 0:
            encoded.append(0x80 | (number & 0x7f))
            number >>= 7

        encoded[0] &= 0x7f
        encoded.reverse()
        tag.extend(encoded)

    return tag


def decode_tag(_, offset):
    return 0, 0, offset + 1


def encode_real(data):
    if data == float('inf'):
        data = b'\x40'
    elif data == float('-inf'):
        data = b'\x41'
    elif math.isnan(data):
        data = b'\x42'
    elif data == 0.0:
        data = b''
    else:
        mantissa, exponent = math.frexp(data)
        mantissa = int(mantissa * 2 ** 53)
        lowest_set_bit = (mantissa & -mantissa).bit_length() - 1
        mantissa >>= lowest_set_bit
        mantissa |= (0x80 << (8 * ((mantissa.bit_length() // 8) + 1)))
        mantissa = binascii.unhexlify(hex(mantissa)[4:].rstrip('L'))
        exponent = (52 - lowest_set_bit - exponent)

        if -129 < exponent < 128:
            exponent = [0x80, ((0xff - exponent) & 0xff)]
        elif -32769 < exponent < 32768:
            exponent = ((0xffff - exponent) & 0xffff)
            exponent = [0x81, (exponent >> 8), exponent & 0xff]
        else:
            raise NotImplementedError(
                'REAL exponent {} out of range.'.format(exponent))

        data = bytearray(exponent) + mantissa

    return data


def decode_real(data):
    offset = 0

    if len(data) == 0:
        decoded = 0.0
    else:
        control = data[offset]

        if len(data) == 1:
            try:
                decoded = {
                    0x40: float('inf'),
                    0x41: float('-inf'),
                    0x42: float('nan')
                }[control]
            except KeyError:
                raise NotImplementedError(
                    'Unsupported REAL control word {}.'.format(control))
        else:
            if control == 0x80:
                exponent = data[offset + 1]

                if exponent & 0x80:
                    exponent -= 0x100

                offset += 2
            elif control == 0x81:
                exponent = ((data[offset + 1] << 8) | data[offset + 2])

                if exponent & 0x8000:
                    exponent -= 0x10000

                offset += 3
            else:
                raise NotImplementedError(
                    'Unsupported REAL control word {}.'.format(control))

            mantissa = 0

            for value in data[offset:]:
                mantissa <<= 8
                mantissa += value

            decoded = float(mantissa * 2 ** exponent)

    return decoded


class Type(object):

    def __init__(self, name, type_name, number, flags=0):
        self.name = name
        self.type_name = type_name

        if number is None:
            self.tag = None
        else:
            self.tag = encode_tag(number, flags)

        self.optional = False
        self.default = None

    def set_tag(self, number, flags):
        if not Class.APPLICATION & flags:
            flags |= Class.CONTEXT_SPECIFIC

        self.tag = encode_tag(number, flags)

    def decode_tag(self, data, offset):
        end_offset = offset + len(self.tag)

        if data[offset:end_offset] != self.tag:
            raise DecodeTagError(self.type_name,
                                 self.tag,
                                 data[offset:end_offset],
                                 offset)

        return end_offset


class PrimitiveOrConstructedType(object):

    def __init__(self, name, type_name, number, segment, flags=0):
        self.name = name
        self.type_name = type_name
        self.segment = segment

        if number is None:
            self.tag = None
            self.constructed_tag = None
        else:
            self.tag = encode_tag(number, flags)
            self.constructed_tag = copy(self.tag)
            self.constructed_tag[0] |= Encoding.CONSTRUCTED

        self.optional = False
        self.default = None

    def set_tag(self, number, flags):
        if not Class.APPLICATION & flags:
            flags |= Class.CONTEXT_SPECIFIC

        self.tag = encode_tag(number, flags)
        self.constructed_tag = copy(self.tag)
        self.constructed_tag[0] |= Encoding.CONSTRUCTED

    def decode_tag(self, data, offset):
        end_offset = offset + len(self.tag)
        tag = data[offset:end_offset]

        if tag == self.tag:
            return True, end_offset
        elif tag == self.constructed_tag:
            return False, end_offset
        else:
            raise DecodeTagError(self.type_name,
                                 self.tag,
                                 data[offset:end_offset],
                                 offset)

    def decode(self, data, offset):
        is_primitive, offset = self.decode_tag(data, offset)

        if is_primitive:
            length, offset = decode_length_definite(data, offset)
            end_offset = offset + length

            return self.decode_primitive_contents(data, offset, length), end_offset
        else:
            length, offset = decode_length_constructed(data, offset)
            segments = []

            if length is None:
                while data[offset:offset + 2] != b'\x00\x00':
                    decoded, offset = self.segment.decode(data, offset)
                    segments.append(decoded)

                end_offset = offset + 2
            else:
                end_offset = offset + length

                while offset < end_offset:
                    decoded, offset = self.segment.decode(data, offset)
                    segments.append(decoded)

            return self.decode_constructed_segments(segments), end_offset

    def decode_primitive_contents(self, data, offset, length):
        raise NotImplementedError()

    def decode_constructed_segments(self, segments):
        raise NotImplementedError()


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name,
                                      'INTEGER',
                                      Tag.INTEGER)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_signed_integer(data))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return decode_signed_integer(data[offset:end_offset]), end_offset

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Real(Type):

    def __init__(self, name):
        super(Real, self).__init__(name, 'REAL', Tag.REAL)

    def encode(self, data, encoded):
        data = encode_real(data)
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length
        decoded = decode_real(data[offset:end_offset])

        return decoded, end_offset

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name,
                                      'BOOLEAN',
                                      Tag.BOOLEAN)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(1)
        encoded.append(0xff * data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, contents_offset = decode_length_definite(data, offset)

        if length != 1:
            raise DecodeError(
                'expected BOOLEAN contents length 1 at offset {}, but '
                'got {}'.format(offset,
                                length))

        return bool(data[contents_offset]), contents_offset + length

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(IA5String, self).__init__(name,
                                        'IA5String',
                                        Tag.IA5_STRING,
                                        OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode_primitive_contents(self, data, offset, length):
        return data[offset:offset + length].decode('ascii')

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments).decode('ascii')

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(NumericString, self).__init__(name,
                                            'NumericString',
                                            Tag.NUMERIC_STRING,
                                            OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode_primitive_contents(self, data, offset, length):
        return data[offset:offset + length].decode('ascii')

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments).decode('ascii')

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class MembersType(Type):

    def __init__(self, name, tag_name, tag, members):
        super(MembersType, self).__init__(name,
                                          tag_name,
                                          tag,
                                          Encoding.CONSTRUCTED)
        self.members = members

    def set_tag(self, number, flags):
        super(MembersType, self).set_tag(number,
                                         flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        encoded_members = bytearray()

        for member in self.members:
            name = member.name

            if name in data:
                value = data[name]

                if isinstance(member, AnyDefinedBy):
                    member.encode(value, encoded_members, data)
                elif member.default != value or isinstance(member, Null):
                    member.encode(value, encoded_members)
            elif member.optional:
                pass
            elif member.default is None:
                raise EncodeError(
                    "member '{}' not found in {}".format(
                        name,
                        data))

        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(encoded_members)))
        encoded.extend(encoded_members)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)

        if data[offset] == 0x80:
            raise NotImplementedError(
                'decode until an end-of-contents tag is found')
        else:
            length, offset = decode_length_definite(data, offset)

        end_offset = offset + length
        values = {}

        for member in self.members:
            try:
                if offset < end_offset:
                    if isinstance(member, AnyDefinedBy):
                        value, offset = member.decode(data, offset, values)
                    else:
                        value, offset = member.decode(data, offset)
                else:
                    raise IndexError
            except (DecodeError, IndexError) as e:
                if member.optional:
                    continue

                if member.default is None:
                    if isinstance(e, IndexError):
                        e = DecodeError('out of data at offset {}'.format(offset))

                    e.location.append(member.name)
                    raise e

                value = member.default

            values[member.name] = value

        return values, offset

    def __repr__(self):
        return '{}({}, [{}])'.format(
            self.__class__.__name__,
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Sequence(MembersType):

    def __init__(self, name, members):
        super(Sequence, self).__init__(name, 'SEQUENCE', Tag.SEQUENCE, members)


class Set(MembersType):

    def __init__(self, name, members):
        super(Set, self).__init__(name, 'SET', Tag.SET, members)


class ArrayType(Type):

    def __init__(self, name, tag_name, tag, element_type):
        super(ArrayType, self).__init__(name,
                                        tag_name,
                                        tag,
                                        Encoding.CONSTRUCTED)
        self.element_type = element_type

    def set_tag(self, number, flags):
        super(ArrayType, self).set_tag(number,
                                       flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        encoded_elements = bytearray()

        for entry in data:
            self.element_type.encode(entry, encoded_elements)

        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(encoded_elements)))
        encoded.extend(encoded_elements)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)

        if data[offset] == 0x80:
            raise NotImplementedError(
                'decode until an end-of-contents tag is found')
        else:
            length, offset = decode_length_definite(data, offset)

        decoded = []
        start_offset = offset

        while (offset - start_offset) < length:
            decoded_element, offset = self.element_type.decode(data, offset)
            decoded.append(decoded_element)

        return decoded, offset

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.name,
                                   self.element_type)


class SequenceOf(ArrayType):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name,
                                         'SEQUENCE OF',
                                         Tag.SEQUENCE,
                                         element_type)


class SetOf(ArrayType):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name,
                                    'SET OF',
                                    Tag.SET,
                                    element_type)


class BitString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(BitString, self).__init__(name,
                                        'BIT STRING',
                                        Tag.BIT_STRING,
                                        self)

    def encode(self, data, encoded):
        number_of_unused_bits = (8 - (data[1] % 8))

        if number_of_unused_bits == 8:
            number_of_unused_bits = 0

        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data[0]) + 1))
        encoded.append(number_of_unused_bits)
        encoded.extend(data[0])

    def decode_primitive_contents(self, data, offset, length):
        length -= 1
        number_of_bits = 8 * length - data[offset]
        offset += 1

        return (bytearray(data[offset:offset + length]), number_of_bits)

    def decode_constructed_segments(self, segments):
        decoded = bytearray()
        number_of_bits = 0

        for data, length in segments:
            decoded.extend(data)
            number_of_bits += length

        return (decoded, number_of_bits)

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(OctetString, self).__init__(name,
                                          'OCTET STRING',
                                          Tag.OCTET_STRING,
                                          self)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data)

    def decode_primitive_contents(self, data, offset, length):
        return bytearray(data[offset:offset + length])

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments)

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(PrintableString, self).__init__(name,
                                              'PrintableString',
                                              Tag.PRINTABLE_STRING,
                                              OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode_primitive_contents(self, data, offset, length):
        return data[offset:offset + length].decode('ascii')

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments).decode('ascii')

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(UniversalString, self).__init__(name,
                                              'UniversalString',
                                              Tag.UNIVERSAL_STRING,
                                              OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode_primitive_contents(self, data, offset, length):
        return data[offset:offset + length].decode('ascii')

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments).decode('ascii')

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(VisibleString, self).__init__(name,
                                            'VisibleString',
                                            Tag.VISIBLE_STRING,
                                            OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode_primitive_contents(self, data, offset, length):
        return data[offset:offset + length].decode('ascii')

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments).decode('ascii')

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class GeneralString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(GeneralString, self).__init__(name,
                                            'GeneralString',
                                            Tag.GENERAL_STRING,
                                            OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode_primitive_contents(self, data, offset, length):
        return data[offset:offset + length].decode('ascii')

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments).decode('ascii')

    def __repr__(self):
        return 'GeneralString({})'.format(self.name)


class UTF8String(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(UTF8String, self).__init__(name,
                                         'UTF8String',
                                         Tag.UTF8_STRING,
                                         OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('utf-8'))

    def decode_primitive_contents(self, data, offset, length):
        return data[offset:offset + length].decode('utf-8')

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments).decode('utf-8')

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(BMPString, self).__init__(name,
                                        'BMPString',
                                        Tag.BMP_STRING,
                                        OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data)

    def decode_primitive_contents(self, data, offset, length):
        return bytearray(data[offset:offset + length])

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments)

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name,
                                      'UTCTime',
                                      Tag.UTC_TIME)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(13)
        encoded.extend(bytearray((data).encode('ascii')))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name,
                                              'GeneralizedTime',
                                              Tag.GENERALIZED_TIME)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class TeletexString(PrimitiveOrConstructedType):

    def __init__(self, name):
        super(TeletexString, self).__init__(name,
                                            'TeletexString',
                                            Tag.T61_STRING,
                                            OctetString(name))

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data)

    def decode_primitive_contents(self, data, offset, length):
        return bytearray(data[offset:offset + length])

    def decode_constructed_segments(self, segments):
        return bytearray().join(segments)

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name,
                                               'OBJECT IDENTIFIER',
                                               Tag.OBJECT_IDENTIFIER)

    def encode(self, data, encoded):
        identifiers = [int(identifier) for identifier in data.split('.')]

        first_subidentifier = (40 * identifiers[0] + identifiers[1])
        encoded_subidentifiers = self.encode_subidentifier(
            first_subidentifier)

        for identifier in identifiers[2:]:
            encoded_subidentifiers += self.encode_subidentifier(identifier)

        encoded.extend(self.tag)
        encoded.append(len(encoded_subidentifiers))
        encoded.extend(encoded_subidentifiers)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        subidentifier, offset = self.decode_subidentifier(data, offset)
        decoded = [subidentifier // 40, subidentifier % 40]

        while offset < end_offset:
            subidentifier, offset = self.decode_subidentifier(data, offset)
            decoded.append(subidentifier)

        return '.'.join([str(v) for v in decoded]), end_offset

    def encode_subidentifier(self, subidentifier):
        encoded = [subidentifier & 0x7f]
        subidentifier >>= 7

        while subidentifier > 0:
            encoded.append(0x80 | (subidentifier & 0x7f))
            subidentifier >>= 7

        return encoded[::-1]

    def decode_subidentifier(self, data, offset):
        decoded = 0

        while data[offset] & 0x80:
            decoded += (data[offset] & 0x7f)
            decoded <<= 7
            offset += 1

        decoded += data[offset]

        return decoded, offset + 1

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name, 'CHOICE', None)
        self.members = members

    def set_tag(self, number, flags):
        super(Choice, self).set_tag(number,
                                    flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        if not isinstance(data, tuple):
            raise EncodeError("expected tuple, but got '{}'".format(data))

        for member in self.members:
            if member.name == data[0]:
                member.encode(data[1], encoded)

                return

        raise EncodeError(
            "expected choices are {}, but got '{}'".format(
                [member.name for member in self.members],
                data[0]))

    def decode(self, data, offset):
        for member in self.members:
            if (isinstance(member, Choice)
                or member.tag == data[offset:offset + len(member.tag)]):
                try:
                    decoded, offset = member.decode(data, offset)
                except DecodeChoiceError:
                    pass
                else:
                    return (member.name, decoded), offset

        raise DecodeChoiceError()

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL', Tag.NULL)

    def encode(self, _, encoded):
        encoded.extend(self.tag)
        encoded.append(0)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)

        return None, offset + 1

    def __repr__(self):
        return 'Null({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY', None)

    def encode(self, data, encoded):
        encoded.extend(data)

    def decode(self, data, offset):
        start = offset
        _, _, offset = decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[start:end_offset], end_offset

    def __repr__(self):
        return 'Any({})'.format(self.name)


class AnyDefinedBy(Type):

    def __init__(self, name, type_member, choices):
        super(AnyDefinedBy, self).__init__(name,
                                           'ANY DEFINED BY',
                                           None,
                                           None)
        self.type_member = type_member
        self.choices = choices

    def encode(self, data, encoded, values):
        if self.choices:
            try:
                self.choices[values[self.type_member]].encode(data, encoded)
            except KeyError:
                raise EncodeError('bad AnyDefinedBy choice {}'.format(values[self.type_member]))
        else:
            encoded.extend(data)

    def decode(self, data, offset, values):
        if self.choices:
            try:
                return self.choices[values[self.type_member]].decode(data,
                                                                     offset)
            except KeyError:
                raise DecodeError('bad AnyDefinedBy choice {}'.format(values[self.type_member]))
        else:
            start = offset
            _, _, offset = decode_tag(data, offset)
            length, offset = decode_length_definite(data, offset)
            end_offset = offset + length

            return data[start:end_offset], end_offset

    def __repr__(self):
        return 'AnyDefinedBy({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name,
                                         'ENUMERATED',
                                         Tag.ENUMERATED)
        self.values = enum_values_as_dict(values)

    def encode(self, data, encoded):
        for value, name in self.values.items():
            if data == name:
                encoded.extend(self.tag)
                encoded.extend(encode_signed_integer(value))
                return

        raise EncodeError(
            "enumeration value '{}' not found in {}".format(
                data,
                [value for value in self.values.values()]))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length
        value = decode_signed_integer(data[offset:end_offset])

        return self.values[value], end_offset

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class ExplicitTag(Type):

    def __init__(self, name, inner):
        super(ExplicitTag, self).__init__(name, 'Tag', None)
        self.inner = inner

    def set_tag(self, number, flags):
        super(ExplicitTag, self).set_tag(number,
                                         flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        encoded_inner = bytearray()
        self.inner.encode(data, encoded_inner)
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(encoded_inner)))
        encoded.extend(encoded_inner)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        _, offset = decode_length_definite(data, offset)
        return self.inner.decode(data, offset)

    def __repr__(self):
        return 'Tag()'


class Recursive(Type):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name, 'RECURSIVE', None)
        self.type_name = type_name
        self.module_name = module_name

    def encode(self, _data, _encoded):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def decode(self, _data, _offset):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def __repr__(self):
        return 'Recursive({})'.format(self.name)


class CompiledType(object):

    def __init__(self, type_):
        self._type = type_

    def encode(self, data):
        encoded = bytearray()
        self._type.encode(data, encoded)

        return encoded

    def decode(self, data):
        return self._type.decode(bytearray(data), 0)[0]

    def __repr__(self):
        return repr(self._type)


class Compiler(compiler.Compiler):

    def process_type(self, type_name, type_descriptor, module_name):
        return CompiledType(self.compile_type(type_name,
                                              type_descriptor,
                                              module_name))

    def compile_implicit_type(self, name, type_descriptor, module_name):
        type_name = type_descriptor['type']

        if type_name == 'SEQUENCE':
            compiled = Sequence(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_name == 'SEQUENCE OF':
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name))
        elif type_name == 'SET':
            compiled = Set(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_name == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_name == 'CHOICE':
            compiled = Choice(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_name == 'INTEGER':
            compiled = Integer(name)
        elif type_name == 'REAL':
            compiled = Real(name)
        elif type_name == 'ENUMERATED':
            compiled = Enumerated(name, type_descriptor['values'])
        elif type_name == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_name == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_name == 'OCTET STRING':
            compiled = OctetString(name)
        elif type_name == 'TeletexString':
            compiled = TeletexString(name)
        elif type_name == 'NumericString':
            compiled = NumericString(name)
        elif type_name == 'PrintableString':
            compiled = PrintableString(name)
        elif type_name == 'IA5String':
            compiled = IA5String(name)
        elif type_name == 'VisibleString':
            compiled = VisibleString(name)
        elif type_name == 'GeneralString':
            compiled = GeneralString(name)
        elif type_name == 'UTF8String':
            compiled = UTF8String(name)
        elif type_name == 'BMPString':
            compiled = BMPString(name)
        elif type_name == 'UTCTime':
            compiled = UTCTime(name)
        elif type_name == 'UniversalString':
            compiled = UniversalString(name)
        elif type_name == 'GeneralizedTime':
            compiled = GeneralizedTime(name)
        elif type_name == 'BIT STRING':
            compiled = BitString(name)
        elif type_name == 'ANY':
            compiled = Any(name)
        elif type_name == 'ANY DEFINED BY':
            choices = {}

            for key, value in type_descriptor['choices'].items():
                choices[key] = self.compile_type(key,
                                                 value,
                                                 module_name)

            compiled = AnyDefinedBy(name,
                                    type_descriptor['value'],
                                    choices)
        elif type_name == 'NULL':
            compiled = Null(name)
        else:
            if type_name in self.types_backtrace:
                compiled = Recursive(name,
                                     type_name,
                                     module_name)
            else:
                self.types_backtrace_push(type_name)
                compiled = self.compile_type(
                    name,
                    *self.lookup_type_descriptor(
                        type_name,
                        module_name))
                self.types_backtrace_pop()

        return compiled

    def compile_type(self, name, type_descriptor, module_name):
        compiled = self.compile_implicit_type(name,
                                              type_descriptor,
                                              module_name)

        if self.is_explicit_tag(type_descriptor):
            compiled = ExplicitTag(name, compiled)

        # Set any given tag.
        if 'tag' in type_descriptor:
            tag = type_descriptor['tag']
            class_ = tag.get('class', None)

            if class_ == 'APPLICATION':
                flags = Class.APPLICATION
            elif class_ == 'PRIVATE':
                flags = Class.PRIVATE
            else:
                flags = 0

            compiled.set_tag(tag['number'], flags)

        return compiled

    def compile_members(self, members, module_name):
        compiled_members = []

        for member in members:
            if member == '...':
                continue

            if isinstance(member, list):
                compiled_members.extend(self.compile_members(member,
                                                             module_name))
                continue

            compiled_member = self.compile_type(member['name'],
                                                member,
                                                module_name)

            if 'optional' in member:
                compiled_member.optional = member['optional']

            if 'default' in member:
                compiled_member.default = member['default']

            compiled_members.append(compiled_member)

        return compiled_members


def compile_dict(specification):
    return Compiler(specification).process()


def decode_length(data):
    try:
        return sum(decode_length_definite(bytearray(data), 1))
    except DecodeContentsLengthError as e:
        return (e.length + e.offset)
    except IndexError:
        raise DecodeError('not enough data to decode the length')
