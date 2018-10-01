"""Basic Octet Encoding Rules (OER) codec.

"""

import binascii
from copy import copy
import struct
from operator import attrgetter

from ..parser import EXTENSION_MARKER
from . import EncodeError
from . import DecodeError
from . import OutOfDataError
from . import format_or
from . import compiler
from . import utc_time_to_datetime
from . import utc_time_from_datetime
from . import generalized_time_to_datetime
from . import generalized_time_from_datetime
from .compiler import enum_values_as_dict
from .ber import Class
from .ber import Tag
from .ber import encode_object_identifier
from .ber import decode_object_identifier
from . import der


def encode_tag(number, flags):
    if number < 63:
        tag = bytearray([flags | number])
    else:
        tag = bytearray([flags | 0x3f])
        encoded = bytearray()

        while number > 0:
            encoded.append(0x80 | (number & 0x7f))
            number >>= 7

        encoded[0] &= 0x7f
        encoded.reverse()
        tag.extend(encoded)

    return bytes(tag)


class Encoder(object):

    def __init__(self):
        self.number_of_bits = 0
        self.value = 0

    def __iadd__(self, other):
        self.append_non_negative_binary_integer(other.value,
                                                other.number_of_bits)

        return self

    def number_of_bytes(self):
        return (self.number_of_bits + 7) // 8

    def set_bit(self, offset):
        self.value |= (1 << (self.number_of_bits - offset - 1))

    def align(self):
        width = (8 * self.number_of_bytes() - self.number_of_bits)
        self.number_of_bits += width
        self.value <<= width

    def append_bit(self, bit):
        """Append given bit.

        """

        self.number_of_bits += 1
        self.value <<= 1
        self.value |= bit

    def append_bits(self, data, number_of_bits):
        """Append given bits.

        """

        if number_of_bits == 0:
            return

        value = int(binascii.hexlify(data), 16)
        value >>= (8 * len(data) - number_of_bits)

        self.append_non_negative_binary_integer(value, number_of_bits)

    def append_u8(self, value):
        return self.append_non_negative_binary_integer(value, 8)

    def append_bytes(self, data):
        """Append given data.

        """

        self.append_bits(data, 8 * len(data))

    def as_bytearray(self):
        """Return the bits as a bytearray.

        """

        if self.number_of_bits == 0:
            return bytearray()

        data = self.value
        data |= (0x80 << self.number_of_bits)
        data = hex(data)[4:].rstrip('L')

        return bytearray(binascii.unhexlify(data))

    def append_length_determinant(self, value):
        if value < 128:
            self.append_non_negative_binary_integer(value, 8)
        else:
            encoded = bytearray()

            while value > 0:
                encoded.append(value & 0xff)
                value >>= 8

            length = len(encoded)

            if length > 127:
                raise EncodeError('Length determinant {} is too big.'.format(value))

            self.append_u8(0x80 | length)
            self.append_bytes(encoded[::-1])

    def append_non_negative_binary_integer(self, value, number_of_bits):
        """Append given integer value.

        """

        self.number_of_bits += number_of_bits
        self.value <<= number_of_bits
        self.value |= value

    def append_integer(self, value):
        number_of_bits = value.bit_length()

        if value < 0:
            number_of_bytes = ((number_of_bits + 7) // 8)
            value = ((1 << (8 * number_of_bytes)) + value)

            if (value & (1 << (8 * number_of_bytes - 1))) == 0:
                value |= (0xff << (8 * number_of_bytes))
                number_of_bytes += 1
        elif value > 0:
            number_of_bytes = ((number_of_bits + 7) // 8)

            if number_of_bits == (8 * number_of_bytes):
                number_of_bytes += 1
        else:
            number_of_bytes = 1

        self.append_length_determinant(number_of_bytes)
        self.append_non_negative_binary_integer(value, 8 * number_of_bytes)

    def __repr__(self):
        return binascii.hexlify(self.as_bytearray()).decode('ascii')


class Decoder(object):

    def __init__(self, encoded):
        self.number_of_bits = (8 * len(encoded))
        self.total_number_of_bits = self.number_of_bits

        if len(encoded) > 0:
            self.value = int(binascii.hexlify(encoded), 16)
        else:
            self.value = 0

    def align(self):
        width = (self.number_of_bits & 0x7)
        self.number_of_bits -= width

    def number_of_read_bits(self):
        return self.total_number_of_bits - self.number_of_bits

    def skip_bits(self, number_of_bits):
        if number_of_bits > self.number_of_bits:
            raise OutOfDataError(self.number_of_read_bits())

        self.number_of_bits -= number_of_bits

    def peek_bit(self):
        return ((self.value >> (self.number_of_bits - 1)) & 1)

    def clear_bit(self):
        self.value &= (1 << (self.number_of_bits - 1)) - 1

    def read_bit(self):
        """Read a bit.

        """

        if self.number_of_bits == 0:
            raise OutOfDataError(self.number_of_read_bits())

        self.number_of_bits -= 1

        return ((self.value >> self.number_of_bits) & 1)

    def read_bits(self, number_of_bits):
        """Read given number of bits.

        """

        if number_of_bits > self.number_of_bits:
            raise OutOfDataError(self.number_of_read_bits())

        self.number_of_bits -= number_of_bits
        mask = ((1 << number_of_bits) - 1)
        value = ((self.value >> self.number_of_bits) & mask)
        value &= mask
        value |= (0x80 << number_of_bits)

        return binascii.unhexlify(hex(value)[4:].rstrip('L'))

    def read_byte(self):
        return self.read_non_negative_binary_integer(8)

    def read_bytes(self, number_of_bytes):
        return self.read_bits(8 * number_of_bytes)

    def read_non_negative_binary_integer(self, number_of_bits):
        """Read an integer value of given number of bits.

        """

        if number_of_bits > self.number_of_bits:
            raise OutOfDataError(self.number_of_read_bits())

        self.number_of_bits -= number_of_bits
        mask = ((1 << number_of_bits) - 1)

        return ((self.value >> self.number_of_bits) & mask)

    def read_length_determinant(self):
        value = self.read_byte()

        if value & 0x80:
            length = (value & 0x7f)
            value = self.read_non_negative_binary_integer(8 * length)
        else:
            value &= 0x7f

        return value

    def read_integer(self):
        number_of_bytes = self.read_length_determinant()
        number_of_bits = 8 * number_of_bytes
        value = self.read_non_negative_binary_integer(number_of_bits)

        if value & (1 << (number_of_bits - 1)):
            value -= (1 << number_of_bits) - 1
            value -= 1

        return value

    def read_tag(self):
        byte = self.read_byte()
        tag = bytearray([byte])

        if byte & 0x3f == 0x3f:
            while True:
                byte = self.read_byte()
                tag.append(byte)

                if byte & 0x80 == 0:
                    break

        return bytes(tag)


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

    def set_size_range(self, minimum, maximum, has_extension_marker):
        pass

    def set_restricted_to_range(self, minimum, maximum, has_extension_marker):
        pass

    def is_default(self, value):
        return value == self.default


class KnownMultiplierStringType(Type):

    TAG = None
    ENCODING = None

    def __init__(self,
                 name,
                 minimum=None,
                 maximum=None,
                 has_extension_marker=False):
        super(KnownMultiplierStringType, self).__init__(name,
                                                        self.__class__.__name__,
                                                        self.TAG)
        self.number_of_bytes = None

        if minimum is not None or maximum is not None:
            if not has_extension_marker:
                if minimum == maximum:
                    self.number_of_bytes = minimum

    def encode(self, data, encoder):
        encoded = data.encode(self.ENCODING)

        if self.number_of_bytes is None:
            encoder.append_length_determinant(len(encoded))
            encoder.append_bytes(encoded)
        else:
            encoder.append_bytes(encoded)

    def decode(self, decoder):
        if self.number_of_bytes is None:
            number_of_bytes = decoder.read_length_determinant()
        else:
            number_of_bytes = self.number_of_bytes

        return decoder.read_bytes(number_of_bytes).decode(self.ENCODING)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)


class MembersType(Type):

    def __init__(self, name, type_name, tag, root_members, additions):
        super(MembersType, self).__init__(name,
                                          type_name,
                                          tag)
        self.root_members = root_members
        self.additions = additions
        self.optionals = [
            member
            for member in root_members
            if member.optional or member.default is not None
        ]

    def encode(self, data, encoder):
        if self.additions is not None:
            offset = encoder.number_of_bits
            encoder.append_bit(0)
            self.encode_root(data, encoder)

            if len(self.additions) > 0:
                if self.encode_additions(data, encoder):
                    encoder.set_bit(offset)
        else:
            self.encode_root(data, encoder)

    def encode_root(self, data, encoder):
        for optional in self.optionals:
            if optional.optional:
                encoder.append_bit(optional.name in data)
            elif optional.name in data:
                encoder.append_bit(not optional.is_default(data[optional.name]))
            else:
                encoder.append_bit(0)

        encoder.align()

        for member in self.root_members:
            self.encode_member(member, data, encoder)

    def encode_additions(self, data, encoder):
        # Encode extension additions.
        presence_bits = 0
        addition_encoders = []

        try:
            for addition in self.additions:
                presence_bits <<= 1
                addition_encoder = Encoder()
                self.encode_member(addition,
                                   data,
                                   addition_encoder,
                                   encode_default=True)

                if addition_encoder.number_of_bits > 0:
                    addition_encoders.append(addition_encoder)
                    presence_bits |= 1
        except EncodeError:
            pass

        # Return false if no extension additions are present.
        if not addition_encoders:
            return False

        # Presence bit field.
        number_of_additions = len(self.additions)
        number_of_unused_bits = (8 - (number_of_additions % 8))
        encoder.append_length_determinant(number_of_additions + 1)
        encoder.append_non_negative_binary_integer(number_of_unused_bits, 8)
        encoder.append_non_negative_binary_integer(presence_bits,
                                                   number_of_additions)
        encoder.align()

        for addition_encoder in addition_encoders:
            encoder.append_length_determinant(addition_encoder.number_of_bytes())
            encoder += addition_encoder

        return True

    def encode_member(self, member, data, encoder, encode_default=False):
        name = member.name

        if name in data:
            try:
                if member.default is None:
                    member.encode(data[name], encoder)
                elif not member.is_default(data[name]) or encode_default:
                    member.encode(data[name], encoder)
            except EncodeError as e:
                e.location.append(member.name)
                raise
        elif member.optional or member.default is not None:
            pass
        else:
            raise EncodeError(
                "{} member '{}' not found in {}.".format(
                    self.__class__.__name__,
                    name,
                    data))

    def decode(self, decoder):
        if self.additions is not None:
            if decoder.read_bit():
                decoded = self.decode_root(decoder)
                decoded.update(self.decode_additions(decoder))

                return decoded
            else:
                return self.decode_root(decoder)
        else:
            return self.decode_root(decoder)

    def decode_root(self, decoder):
        values = {}
        optionals = {
            optional: decoder.read_bit()
            for optional in self.optionals
        }

        decoder.align()

        for member in self.root_members:
            try:
                if optionals.get(member, True):
                    value = member.decode(decoder)
                    values[member.name] = value
                elif member.default is not None:
                    values[member.name] = member.default
            except DecodeError as e:
                e.location.append(member.name)
                raise

        return values

    def decode_additions(self, decoder):
        # Presence bit field.
        length = decoder.read_length_determinant()
        decoder.read_byte()
        presence_bits = decoder.read_non_negative_binary_integer(length)
        decoder.align()
        decoded = {}

        for i in range(length):
            if presence_bits & (1 << (length - i - 1)):
                member_length = decoder.read_length_determinant()

                if i < len(self.additions):
                    addition = self.additions[i]

                    try:
                        decoded[addition.name] = addition.decode(decoder)
                    except DecodeError as e:
                        e.location.append(addition.name)
                        raise
                else:
                    decoder.skip_bits(8 * member_length)

        return decoded

    def __repr__(self):
        return '{}({}, [{}])'.format(
            self.__class__.__name__,
            self.name,
            ', '.join([repr(member) for member in self.root_members]))


class ArrayType(Type):

    def __init__(self, name, type_name, tag, element_type):
        super(ArrayType, self).__init__(name,
                                        type_name,
                                        tag)
        self.element_type = element_type

    def encode(self, data, encoder):
        encoder.append_integer(len(data))

        for entry in data:
            self.element_type.encode(entry, encoder)

    def decode(self, decoder):
        length = decoder.read_integer()
        decoded = []

        for _ in range(length):
            decoded_element = self.element_type.decode(decoder)
            decoded.append(decoded_element)

        return decoded

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.name,
                                   self.element_type)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name,
                                      'BOOLEAN',
                                      Tag.BOOLEAN)

    def encode(self, data, encoder):
        encoder.append_non_negative_binary_integer(0xff * data, 8)

    def decode(self, decoder):
        return bool(decoder.read_byte())

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name,
                                      'INTEGER',
                                      Tag.INTEGER)
        self.has_extension_marker = False
        self.length = None
        self.fmt = None

    def set_restricted_to_range(self, minimum, maximum, has_extension_marker):
        self.has_extension_marker = has_extension_marker

        if minimum == 'MIN' or maximum == 'MAX':
            return

        if minimum >= 0:
            if maximum < 256:
                self.length = 1
                self.fmt = '>B'
            elif maximum < 65536:
                self.length = 2
                self.fmt = '>H'
            elif maximum < 4294967296:
                self.length = 4
                self.fmt = '>I'
            elif maximum < 18446744073709551616:
                self.length = 8
                self.fmt = '>Q'
        elif minimum >= -128 and maximum < 128:
            self.length = 1
            self.fmt = '>b'
        elif minimum >= -32768 and maximum < 32768:
            self.length = 2
            self.fmt = '>h'
        elif minimum >= -2147483648 and maximum < 2147483648:
            self.length = 4
            self.fmt = '>i'
        elif minimum >= -9223372036854775808 and maximum < 9223372036854775808:
            self.length = 8
            self.fmt = '>q'

    def encode(self, data, encoder):
        if self.fmt:
            encoder.append_bytes(struct.pack(self.fmt, data))
        else:
            encoder.append_integer(data)

    def decode(self, decoder):
        if self.fmt:
            return struct.unpack(self.fmt, decoder.read_bytes(self.length))[0]
        else:
            return decoder.read_integer()

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Real(Type):

    def __init__(self, name, with_components):
        super(Real, self).__init__(name, 'REAL', Tag.REAL)

        if with_components is None:
            self.length = None
            self.fmt = None
        else:
            mantissa, base, exponent = self.unpack_with_components(with_components)

            if all([mantissa, base, exponent]):
                if self.is_binary32(mantissa, base, exponent):
                    self.length = 4
                    self.fmt = '>f'
                elif self.is_binary64(mantissa, base, exponent):
                    self.length = 8
                    self.fmt = '>d'
                else:
                    self.length = None
                    self.fmt = None
            else:
                self.length = None
                self.fmt = None

    def unpack_with_components(self, with_components):
        with_components = dict(with_components)

        try:
            mantissa = with_components['mantissa']
            base = with_components['base']
            exponent = with_components['exponent']
        except KeyError:
            mantissa = None
            base = None
            exponent = None

        return (mantissa, base, exponent)

    def is_binary32(self, mantissa, base, exponent):
        return (-16777215 <= mantissa[0] <= mantissa[1] <= 16777215
                and base == 2
                and -149 <= exponent[0] <= exponent[1] <= 104)

    def is_binary64(self, mantissa, base, exponent):
        return (-9007199254740991 <= mantissa[0] <= mantissa[1] <= 9007199254740991
                and base == 2
                and -1074 <= exponent[0] <= exponent[1] <= 971)

    def encode(self, data, encoder):
        if self.fmt is None:
            encoded = der.encode_real(data)
            encoder.append_length_determinant(len(encoded))
            encoder.append_bytes(encoded)
        else:
            try:
                encoder.append_bytes(struct.pack(self.fmt, data))
            except (struct.error, OverflowError):
                raise EncodeError(
                    'Expected an IEEE 754 {} bits floating point number, but '
                    'got {}.'.format(8 * self.length,
                                     data))

    def decode(self, decoder):
        if self.fmt is None:
            length = decoder.read_length_determinant()

            return der.decode_real(bytearray(decoder.read_bytes(length)))
        else:
            return struct.unpack(self.fmt, decoder.read_bytes(self.length))[0]

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL', Tag.NULL)

    def encode(self, _data, _encoder):
        return

    def decode(self, _decoder):
        return

    def __repr__(self):
        return 'Null({})'.format(self.name)


class BitString(Type):

    def __init__(self, name, minimum, maximum, has_extension_marker):
        super(BitString, self).__init__(name,
                                        'BIT STRING',
                                        Tag.BIT_STRING)
        self.number_of_bits = None

        if minimum is not None or maximum is not None:
            if not has_extension_marker:
                if minimum == maximum:
                    self.number_of_bits = minimum

    def encode(self, data, encoder):
        number_of_bytes, number_of_rest_bits = divmod(data[1], 8)
        data = bytearray(data[0])

        if number_of_rest_bits == 0:
            data = data[:number_of_bytes]
            number_of_unused_bits = 0
        else:
            last_byte = data[number_of_bytes]
            last_byte &= ((0xff >> number_of_rest_bits) ^ 0xff)
            data = data[:number_of_bytes]
            data.append(last_byte)
            number_of_unused_bits = (8 - number_of_rest_bits)
            number_of_bytes += 1

        if self.number_of_bits is None:
            encoder.append_length_determinant(number_of_bytes + 1)
            encoder.append_non_negative_binary_integer(number_of_unused_bits,
                                                       8)
            encoder.append_bytes(data)
        else:
            encoder.append_bytes(data)

    def decode(self, decoder):
        if self.number_of_bits is None:
            number_of_bytes = decoder.read_length_determinant()
            number_of_unused_bits = decoder.read_byte()
            number_of_bytes -= 1
            number_of_bits = (8 * number_of_bytes - number_of_unused_bits)
        else:
            number_of_bytes = (self.number_of_bits + 7) // 8
            number_of_bits = self.number_of_bits

        return (decoder.read_bytes(number_of_bytes), number_of_bits)

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name, minimum, maximum, has_extension_marker):
        super(OctetString, self).__init__(name,
                                          'OCTET STRING',
                                          Tag.OCTET_STRING)
        self.number_of_bytes = None

        if minimum is not None or maximum is not None:
            if not has_extension_marker:
                if minimum == maximum:
                    self.number_of_bytes = minimum

    def encode(self, data, encoder):
        if self.number_of_bytes is None:
            encoder.append_length_determinant(len(data))
            encoder.append_bytes(data)
        else:
            encoder.append_bytes(data)

    def decode(self, decoder):
        if self.number_of_bytes is None:
            number_of_bytes = decoder.read_length_determinant()
        else:
            number_of_bytes = self.number_of_bytes

        return decoder.read_bytes(number_of_bytes)

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name,
                                               'OBJECT IDENTIFIER',
                                               Tag.OBJECT_IDENTIFIER)

    def encode(self, data, encoder):
        encoded_subidentifiers = encode_object_identifier(data)
        encoder.append_length_determinant(len(encoded_subidentifiers))
        encoder.append_bytes(bytearray(encoded_subidentifiers))

    def decode(self, decoder):
        length = decoder.read_length_determinant()
        data = decoder.read_bytes(length)

        return decode_object_identifier(bytearray(data), 0, len(data))

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name,
                                         'ENUMERATED',
                                         Tag.ENUMERATED)
        self.value_to_name = enum_values_as_dict(values)
        self.name_to_value = {v: k for k, v in self.value_to_name.items()}

    def format_names(self):
        return format_or(list(self.value_to_name.values()))

    def format_values(self):
        return format_or(list(self.value_to_name))

    def encode(self, data, encoder):
        try:
            value = self.name_to_value[data]
        except KeyError:
            raise EncodeError(
                "Expected enumeration value {}, but got '{}'.".format(
                    self.format_names(),
                    data))

        if 0 <= value <= 127:
            encoder.append_non_negative_binary_integer(value, 8)
        else:
            offset = encoder.number_of_bits
            encoder.append_integer(value)
            encoder.set_bit(offset)

    def decode(self, decoder):
        if decoder.peek_bit():
            decoder.clear_bit()
            value = decoder.read_integer()
        else:
            value = decoder.read_byte()

        try:
            return self.value_to_name[value]
        except KeyError:
            raise DecodeError(
                'Expected enumeration value {}, but got {}.'.format(
                    self.format_values(),
                    value))

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class Sequence(MembersType):

    def __init__(self, name, root_members, additions):
        super(Sequence, self).__init__(name,
                                       'SEQUENCE',
                                       Tag.SEQUENCE,
                                       root_members,
                                       additions)


class SequenceOf(ArrayType):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name,
                                         'SEQUENCE OF',
                                         Tag.SEQUENCE,
                                         element_type)


class Set(MembersType):

    def __init__(self, name, root_members, additions):
        super(Set, self).__init__(name,
                                  'SET',
                                  Tag.SET,
                                  root_members,
                                  additions)


class SetOf(ArrayType):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name,
                                    'SET OF',
                                    Tag.SET,
                                    element_type)


class Choice(Type):

    def __init__(self, name, root_members, additions):
        super(Choice, self).__init__(name, 'CHOICE', None)
        self.root_members = root_members
        self.name_to_root_member = {
            member.name: member for member in root_members
        }
        self.tag_to_root_member = {}
        self.add_tags(self.tag_to_root_member, root_members)

        if additions is None:
            additions = []

        self.additions = additions

        self.name_to_addition = {
            member.name: member for member in additions
        }
        self.tag_to_addition = {}
        self.add_tags(self.tag_to_addition, additions)

    @property
    def members(self):
        return self.root_members + self.additions

    def add_tags(self, tag_to_member, members):
        for member in members:
            tag_to_member[member.tag] = member

    def format_tag(self, tag):
        return binascii.hexlify(tag).decode('ascii')

    def format_tags(self):
        return format_or(
            sorted([self.format_tag(member.tag) for member in self.members]))

    def format_names(self):
        return format_or(sorted([member.name for member in self.members]))

    def encode(self, data, encoder):
        name = data[0]

        if name in self.name_to_root_member:
            member = self.name_to_root_member[name]
            encoder.append_bytes(member.tag)
            self.encode_member(member, data[1], encoder)
        elif name in self.name_to_addition:
            member = self.name_to_addition[name]
            encoder.append_bytes(member.tag)
            addition_encoder = Encoder()
            self.encode_member(member, data[1], addition_encoder)
            encoder.append_length_determinant(addition_encoder.number_of_bytes())
            encoder += addition_encoder
        else:
            raise EncodeError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    data[0]))

    def encode_member(self, member, data, encoder):
        try:
            member.encode(data, encoder)
        except EncodeError as e:
            e.location.append(member.name)
            raise

    def decode(self, decoder):
        tag = decoder.read_tag()

        if tag in self.tag_to_root_member:
            member = self.tag_to_root_member[tag]
            decoded = member.decode(decoder)
        elif tag in self.tag_to_addition:
            member = self.tag_to_addition[tag]
            decoder.read_length_determinant()
            decoded = member.decode(decoder)
        else:
            raise DecodeError(
                "Expected choice member tag {}, but got '{}'.".format(
                    self.format_tags(),
                    self.format_tag(tag)))

        return (member.name, decoded)

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class UTF8String(KnownMultiplierStringType):

    TAG = Tag.UTF8_STRING
    ENCODING = 'utf-8'


class NumericString(KnownMultiplierStringType):

    TAG = Tag.NUMERIC_STRING
    ENCODING = 'ascii'


class PrintableString(KnownMultiplierStringType):

    TAG = Tag.PRINTABLE_STRING
    ENCODING = 'ascii'


class IA5String(KnownMultiplierStringType):

    TAG = Tag.IA5_STRING
    ENCODING = 'ascii'


class VisibleString(KnownMultiplierStringType):

    TAG = Tag.VISIBLE_STRING
    ENCODING = 'ascii'


class GeneralString(KnownMultiplierStringType):

    TAG = Tag.GENERAL_STRING
    ENCODING = 'latin-1'


class BMPString(KnownMultiplierStringType):

    TAG = Tag.BMP_STRING
    ENCODING = 'utf-16-be'


class GraphicString(KnownMultiplierStringType):

    TAG = Tag.GENERAL_STRING
    ENCODING = 'latin-1'


class UniversalString(KnownMultiplierStringType):

    TAG = Tag.UNIVERSAL_STRING
    ENCODING = 'utf-32-be'


class TeletexString(KnownMultiplierStringType):

    TAG = Tag.T61_STRING
    ENCODING = 'iso-8859-1'


class ObjectDescriptor(GraphicString):

    TAG = Tag.OBJECT_DESCRIPTOR


class UTCTime(VisibleString):

    TAG = Tag.UTC_TIME

    def encode(self, data, encoder):
        encoded = utc_time_from_datetime(data)

        return super(UTCTime, self).encode(encoded, encoder)

    def decode(self, decoder):
        decoded = super(UTCTime, self).decode(decoder)

        return utc_time_to_datetime(decoded)


class GeneralizedTime(VisibleString):

    TAG = Tag.GENERALIZED_TIME

    def encode(self, data, encoder):
        encoded = generalized_time_from_datetime(data)

        return super(GeneralizedTime, self).encode(encoded, encoder)

    def decode(self, decoder):
        decoded = super(GeneralizedTime, self).decode(decoder)

        return generalized_time_to_datetime(decoded)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY', None)

    def encode(self, data, encoder):
        raise NotImplementedError('ANY is not yet implemented.')

    def decode(self, decoder):
        raise NotImplementedError('ANY is not yet implemented.')

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

    def encode(self, data, encoder):
        raise NotImplementedError('ANY DEFINED BY is not yet implemented.')

    def decode(self, decoder):
        raise NotImplementedError('ANY DEFINED BY is not yet implemented.')

    def __repr__(self):
        return 'AnyDefinedBy({})'.format(self.name)


class Recursive(Type, compiler.Recursive):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name, 'RECURSIVE', None)
        self.type_name = type_name
        self.module_name = module_name
        self.tag_number = None
        self.tag_flags = None
        self.inner = None

    def set_inner_type(self, inner):
        self.inner = copy(inner)

        if self.tag_number is not None:
            self.inner.set_tag(self.tag_number, self.tag_flags)

    def encode(self, data, encoder):
        self.inner.encode(data, encoder)

    def decode(self, decoder):
        return self.inner.decode(decoder)

    def __repr__(self):
        return 'Recursive({})'.format(self.type_name)


class CompiledType(compiler.CompiledType):

    def __init__(self, type_):
        super(CompiledType, self).__init__()
        self._type = type_

    @property
    def type(self):
        return self._type

    def encode(self, data):
        encoder = Encoder()
        self._type.encode(data, encoder)

        return encoder.as_bytearray()

    def decode(self, data):
        decoder = Decoder(bytearray(data))

        return self._type.decode(decoder)

    def __repr__(self):
        return repr(self._type)


class Compiler(compiler.Compiler):

    def process_type(self, type_name, type_descriptor, module_name):
        compiled_type = self.compile_type(type_name,
                                          type_descriptor,
                                          module_name)

        return CompiledType(compiled_type)

    def compile_type(self, name, type_descriptor, module_name):
        type_name = type_descriptor['type']

        if type_name == 'SEQUENCE':
            compiled = Sequence(name,
                                *self.compile_members(type_descriptor['members'],
                                                      module_name))
        elif type_name == 'SEQUENCE OF':
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name))
        elif type_name == 'SET':
            compiled = Set(name,
                           *self.compile_members(type_descriptor['members'],
                                                 module_name,
                                                 sort_by_tag=True))
        elif type_name == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_name == 'CHOICE':
            compiled = Choice(
                name,
                *self.compile_members(type_descriptor['members'],
                                      module_name))
        elif type_name == 'INTEGER':
            compiled = Integer(name)
        elif type_name == 'REAL':
            compiled = Real(name, self.get_with_components(type_descriptor))
        elif type_name == 'ENUMERATED':
            compiled = Enumerated(name, type_descriptor['values'])
        elif type_name == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_name == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_name == 'OCTET STRING':
            compiled = OctetString(name,
                                   *self.get_size_range(type_descriptor,
                                                        module_name))
        elif type_name == 'TeletexString':
            compiled = TeletexString(name)
        elif type_name == 'NumericString':
            compiled = NumericString(name,
                                     *self.get_size_range(type_descriptor,
                                                          module_name))
        elif type_name == 'PrintableString':
            compiled = PrintableString(name,
                                       *self.get_size_range(type_descriptor,
                                                            module_name))
        elif type_name == 'IA5String':
            compiled = IA5String(name,
                                 *self.get_size_range(type_descriptor,
                                                      module_name))
        elif type_name == 'VisibleString':
            compiled = VisibleString(name,
                                     *self.get_size_range(type_descriptor,
                                                          module_name))
        elif type_name == 'GeneralString':
            compiled = GeneralString(name)
        elif type_name == 'UTF8String':
            compiled = UTF8String(name,
                                  *self.get_size_range(type_descriptor,
                                                       module_name))
        elif type_name == 'BMPString':
            compiled = BMPString(name)
        elif type_name == 'GraphicString':
            compiled = GraphicString(name)
        elif type_name == 'UTCTime':
            compiled = UTCTime(name)
        elif type_name == 'UniversalString':
            compiled = UniversalString(name)
        elif type_name == 'GeneralizedTime':
            compiled = GeneralizedTime(name)
        elif type_name == 'BIT STRING':
            compiled = BitString(name,
                                 *self.get_size_range(type_descriptor,
                                                      module_name))
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
        elif type_name == 'EXTERNAL':
            compiled = Sequence(
                name,
                *self.compile_members(self.external_type_descriptor()['members'],
                                      module_name))
            compiled.set_tag(Tag.EXTERNAL, 0)
        elif type_name == 'ObjectDescriptor':
            compiled = ObjectDescriptor(name)
        else:
            if type_name in self.types_backtrace:
                compiled = Recursive(name,
                                     type_name,
                                     module_name)
                self.recursive_types.append(compiled)
            else:
                compiled = self.compile_user_type(name,
                                                  type_name,
                                                  module_name)

        if 'tag' in type_descriptor:
            compiled = self.copy(compiled)
            tag = type_descriptor['tag']
            class_ = tag.get('class', None)

            if class_ == 'APPLICATION':
                flags = Class.APPLICATION
            elif class_ == 'PRIVATE':
                flags = Class.PRIVATE
            else:
                flags = 0

            compiled.set_tag(tag['number'], flags)

        if 'restricted-to' in type_descriptor:
            compiled = self.set_compiled_restricted_to(compiled,
                                                       type_descriptor,
                                                       module_name)

        return compiled

    def compile_members(self,
                        members,
                        module_name,
                        sort_by_tag=False):
        compiled_members = []
        in_extension = False
        additions = None

        for member in members:
            if member == EXTENSION_MARKER:
                in_extension = not in_extension

                if in_extension:
                    additions = []
            elif in_extension:
                self.compile_extension_member(member,
                                              module_name,
                                              additions)
            else:
                self.compile_root_member(member,
                                         module_name,
                                         compiled_members)

        if sort_by_tag:
            compiled_members = sorted(compiled_members, key=attrgetter('tag'))

        return compiled_members, additions

    def compile_extension_member(self,
                                 member,
                                 module_name,
                                 additions):
        if isinstance(member, list):
            for memb in member:
                compiled_member = self.compile_member(memb,
                                                      module_name)
                additions.append(compiled_member)
        else:
            compiled_member = self.compile_member(member,
                                                  module_name)
            additions.append(compiled_member)


def compile_dict(specification):
    return Compiler(specification).process()


def decode_length(_data):
    raise DecodeError('Decode length is not supported for this codec.')
