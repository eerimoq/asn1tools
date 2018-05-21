"""Packed Encoding Rules (PER) codec.

"""

import logging
from operator import attrgetter
from operator import itemgetter
import binascii
import string

from ..parser import EXTENSION_MARKER
from . import EncodeError
from . import DecodeError
from . import compiler
from .compiler import enum_values_split
from .ber import encode_real
from .ber import decode_real


LOGGER = logging.getLogger(__name__)


def integer_as_number_of_bits(size):
    """Returns the minimum number of bits needed to fit given positive
    integer.

    """

    if size == 0:
        return 0
    else:
        return size.bit_length()


def integer_as_number_of_bits_power_of_two(size):
    """Returns the minimum power of two number of bits needed to fit given
    positive integer.

    """

    if size == 0:
        return 0
    else:
        bit_length = integer_as_number_of_bits(size)
        bit_length_pow_2 = 1

        while bit_length > bit_length_pow_2:
            bit_length_pow_2 <<= 1

        return bit_length_pow_2


def size_as_number_of_bytes(size):
    """Returns the minimum number of bytes needed to fit given positive
    integer.

    """

    if size == 0:
        return 0
    else:
        number_of_bits = size.bit_length()
        rest = (number_of_bits % 8)

        if rest != 0:
            number_of_bits += (8 - rest)

        return number_of_bits // 8


CLASS_PRIO = {
    'UNIVERSAL': 0,
    'APPLICATION': 1,
    'CONTEXT_SPECIFIC': 2,
    'PRIVATE': 3
}


class OutOfDataError(DecodeError):

    def __init__(self, offset):
        super(OutOfDataError, self).__init__(
            'out of data at bit offset {} ({}.{} bytes)'.format(
                offset,
                *divmod(offset, 8)))


class PermittedAlphabet(object):

    def __init__(self, encode_map, decode_map):
        self.encode_map = encode_map
        self.decode_map = decode_map

    def __len__(self):
        return len(self.encode_map)

    def encode(self, value):
        try:
            return self.encode_map[value]
        except KeyError:
            raise EncodeError(
                "expected a character in '{}', but got '{}' (0x{:02x})'".format(
                    ''.join(sorted([chr(v) for v in self.encode_map])),
                    chr(value) if chr(value) in string.printable else '.',
                    value))

    def decode(self, value):
        try:
            return self.decode_map[value]
        except KeyError:
            raise DecodeError(
                "expected a value in {}, but got {:d}".format(
                    list(self.decode_map),
                    value))


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

    def set_bit(self, pos):
        self.value |= (1 << (self.number_of_bits - pos - 1))

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

        value = int(binascii.hexlify(data), 16)
        number_of_alignment_bits = (8 - (number_of_bits % 8))

        if number_of_alignment_bits != 8:
            value >>= number_of_alignment_bits

        self.append_non_negative_binary_integer(value, number_of_bits)

    def append_non_negative_binary_integer(self, value, number_of_bits):
        """Append given integer value.

        """

        self.number_of_bits += number_of_bits
        self.value <<= number_of_bits
        self.value |= value

    def append_bytes(self, data):
        """Append given data.

        """

        if len(data) > 0:
            self.append_bits(data, 8 * len(data))

    def as_bytearray(self):
        """Return the bits as a bytearray.

        """

        if self.number_of_bits == 0:
            return bytearray()

        data = self.value
        number_of_bits = self.number_of_bits
        number_of_alignment_bits = (8 - (number_of_bits % 8))

        if number_of_alignment_bits != 8:
            data <<= number_of_alignment_bits
            number_of_bits += number_of_alignment_bits

        data |= (0x80 << number_of_bits)
        data = hex(data)[4:].rstrip('L')

        return bytearray(binascii.unhexlify(data))

    def append_length_determinant(self, length):
        if length < 128:
            encoded = bytearray([length])
        elif length < 16384:
            encoded = bytearray([(0x80 | (length >> 8)), (length & 0xff)])
        else:
            raise NotImplementedError(
                'Length determinant >=16384 is not yet supported.')

        self.append_bytes(encoded)

    def append_normally_small_non_negative_whole_number(self, value):
        if value < 64:
            self.append_non_negative_binary_integer(value, 7)
        else:
            self.append_bit(1)
            length = (value.bit_length() + 7) // 8
            self.append_length_determinant(length)
            self.append_non_negative_binary_integer(value, 8 * length)

    def append_normally_small_length(self, value):
        if value <= 64:
            self.append_non_negative_binary_integer(value - 1, 7)
        else:
            raise NotImplementedError(
                'Normally small length number >64 is not yet supported.')

    def append_constrained_whole_number(self,
                                        value,
                                        minimum,
                                        maximum,
                                        number_of_bits):
        _range = (maximum - minimum + 1)

        if _range <= 255:
            self.append_non_negative_binary_integer(value - minimum,
                                                    number_of_bits)
        elif _range == 256:
            self.align()
            self.append_non_negative_binary_integer(value - minimum, 8)
        elif _range <= 65536:
            self.align()
            self.append_non_negative_binary_integer(value - minimum, 16)
        else:
            number_of_bits = size_as_number_of_bytes(value) * 8
            self.align()
            self.append_non_negative_binary_integer(value - minimum,
                                                    number_of_bits)

    def append_unconstrained_whole_number(self, value):
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
        self.append_non_negative_binary_integer(value,
                                                8 * number_of_bytes)

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
        number_of_alignment_bits = (8 - (number_of_bits % 8))

        if number_of_alignment_bits != 8:
            value <<= number_of_alignment_bits

        return binascii.unhexlify(hex(value)[4:].rstrip('L'))

    def read_non_negative_binary_integer(self, number_of_bits):
        """Read an integer value of given number of bits.

        """

        if number_of_bits > self.number_of_bits:
            raise OutOfDataError(self.number_of_read_bits())

        self.number_of_bits -= number_of_bits
        mask = ((1 << number_of_bits) - 1)

        return ((self.value >> self.number_of_bits) & mask)

    def read_bytes_aligned(self, number_of_bytes):
        """Read given number of aligned bytes.

        """

        self.number_of_bits -= (self.number_of_bits % 8)

        return bytearray(self.read_bits(8 * number_of_bytes))

    def read_length_determinant(self):
        value = self.read_non_negative_binary_integer(8)

        if (value & 0x80) == 0x00:
            return value
        elif (value & 0xc0) == 0x80:
            return (((value & 0x7f) << 8)
                    | (self.read_non_negative_binary_integer(8)))
        else:
            try:
                value = {
                    0xc1: 16384,
                    0xc2: 32768,
                    0xc3: 49152,
                    0xc4: 65536
                }[value]
            except KeyError:
                raise DecodeError(
                    'Bad length determinant type 0x{:02x}.'.format(value))

            raise NotImplementedError(
                'Length determinant {} is not yet supported.'.format(
                    value))

    def read_normally_small_non_negative_whole_number(self):
        if not self.read_bit():
            decoded = self.read_non_negative_binary_integer(6)
        else:
            length = self.read_length_determinant()
            decoded = self.read_non_negative_binary_integer(8 * length)

        return decoded

    def read_normally_small_length(self):
        if not self.read_bit():
            return self.read_non_negative_binary_integer(6) + 1
        else:
            raise NotImplementedError(
                'Normally small length number >64 is not yet supported.')

    def read_constrained_whole_number(self,
                                      minimum,
                                      maximum,
                                      number_of_bits):
        _range = (maximum - minimum + 1)

        if _range <= 255:
            value = self.read_non_negative_binary_integer(number_of_bits)
        elif _range == 256:
            self.align()
            value = self.read_non_negative_binary_integer(8)
        elif _range <= 65536:
            self.align()
            value = self.read_non_negative_binary_integer(16)
        else:
            self.align()
            value = self.read_non_negative_binary_integer(number_of_bits)

        return value + minimum

    def read_unconstrained_whole_number(self, number_of_bytes):
        decoded = self.read_non_negative_binary_integer(8 * number_of_bytes)
        number_of_bits = (8 * number_of_bytes)

        if decoded & (1 << (number_of_bits - 1)):
            mask = ((1 << number_of_bits) - 1)
            decoded = (decoded - mask)
            decoded -= 1

        return decoded


class Type(object):

    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
        self.optional = False
        self.default = None
        self.tag = None

    def set_size_range(self, minimum, maximum, has_extension_marker):
        pass


class KnownMultiplierStringType(Type):

    PERMITTED_ALPHABET = PermittedAlphabet({}, {})

    def __init__(self,
                 name,
                 minimum=None,
                 maximum=None,
                 has_extension_marker=None,
                 permitted_alphabet=None):
        super(KnownMultiplierStringType, self).__init__(name,
                                                        self.__class__.__name__)
        self.set_size_range(minimum, maximum, has_extension_marker)

        if permitted_alphabet is None:
            permitted_alphabet = self.PERMITTED_ALPHABET

        self.permitted_alphabet = permitted_alphabet
        self.bits_per_character = integer_as_number_of_bits_power_of_two(
            len(permitted_alphabet) - 1)

        if len(self.PERMITTED_ALPHABET) < 2 ** self.bits_per_character:
            self.permitted_alphabet = self.PERMITTED_ALPHABET

    def set_size_range(self, minimum, maximum, has_extension_marker):
        self.minimum = minimum
        self.maximum = maximum
        self.has_extension_marker = has_extension_marker

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = maximum - minimum
            self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        encoded = data.encode('ascii')

        if self.has_extension_marker:
            encoder.append_bit(0)

        if self.number_of_bits is None:
            encoder.align()
            encoder.append_length_determinant(len(encoded))
        elif self.minimum != self.maximum:
            encoder.append_constrained_whole_number(len(encoded),
                                                    self.minimum,
                                                    self.maximum,
                                                    self.number_of_bits)

            if self.maximum > 1:
                encoder.align()
        elif self.maximum * self.bits_per_character > 16:
            encoder.align()

        for value in bytearray(encoded):
            encoder.append_non_negative_binary_integer(
                self.permitted_alphabet.encode(value),
                self.bits_per_character)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                raise NotImplementedError('Extension is not implemented.')

        if self.number_of_bits is None:
            decoder.align()
            length = decoder.read_length_determinant()
        else:
            if self.minimum != self.maximum:
                length = decoder.read_constrained_whole_number(self.minimum,
                                                               self.maximum,
                                                               self.number_of_bits)

                if self.maximum > 1:
                    decoder.align()
            elif self.maximum * self.bits_per_character > 16:
                decoder.align()
                length = self.minimum
            else:
                length = self.minimum

        data = []

        for _ in range(length):
            value = decoder.read_non_negative_binary_integer(self.bits_per_character)
            data.append(self.permitted_alphabet.decode(value))

        return bytearray(data).decode('ascii')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)


class Real(Type):

    def __init__(self, name):
        super(Real, self).__init__(name, 'REAL')

    def encode(self, data, encoder):
        encoded = encode_real(data)
        encoder.append_length_determinant(len(encoded))
        encoder.append_bytes(encoded)

    def decode(self, decoder):
        length = decoder.read_length_determinant()

        return decode_real(decoder.read_bytes_aligned(length))

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN')

    def encode(self, data, encoder):
        encoder.append_bit(bool(data))

    def decode(self, decoder):
        return bool(decoder.read_bit())

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class Integer(Type):

    def __init__(self, name, minimum, maximum, has_extension_marker):
        super(Integer, self).__init__(name, 'INTEGER')
        self.minimum = minimum
        self.maximum = maximum
        self.has_extension_marker = has_extension_marker

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = integer_as_number_of_bits(size)

            if size <= 65535:
                self.number_of_indefinite_bits = None
            else:
                number_of_bits = ((self.number_of_bits + 7) // 8).bit_length()
                self.number_of_indefinite_bits = number_of_bits

    def encode(self, data, encoder):
        if self.has_extension_marker:
            encoder.append_bit(0)

        if self.number_of_bits is None:
            encoder.align()
            encoder.append_unconstrained_whole_number(data)
        else:
            if self.number_of_indefinite_bits is None:
                number_of_bits = self.number_of_bits
            else:
                number_of_bytes = size_as_number_of_bytes(data)
                number_of_bits = 8 * number_of_bytes
                encoder.append_constrained_whole_number(
                    number_of_bytes - 1,
                    0,
                    self.number_of_indefinite_bits,
                    self.number_of_indefinite_bits)

            encoder.append_constrained_whole_number(data,
                                                    self.minimum,
                                                    self.maximum,
                                                    number_of_bits)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                raise NotImplementedError('Extension is not implemented.')

        if self.number_of_bits is None:
            decoder.align()
            length = decoder.read_length_determinant()
            value = decoder.read_unconstrained_whole_number(length)
        else:
            if self.number_of_indefinite_bits is None:
                number_of_bits = self.number_of_bits
            else:
                number_of_bits = decoder.read_constrained_whole_number(
                    0,
                    self.number_of_indefinite_bits,
                    self.number_of_indefinite_bits)
                number_of_bits += 1
                number_of_bits *= 8

            value = decoder.read_constrained_whole_number(self.minimum,
                                                          self.maximum,
                                                          number_of_bits)

        return value

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class MembersType(Type):

    def __init__(self,
                 name,
                 root_members,
                 additions,
                 type_name):
        super(MembersType, self).__init__(name, type_name)
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
                encoder.append_bit(data[optional.name] != optional.default)
            else:
                encoder.append_bit(0)

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

                if isinstance(addition, AdditionGroup):
                    addition.encode_addition_group(data, addition_encoder)
                else:
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
        encoder.append_normally_small_length(number_of_additions)
        encoder.append_non_negative_binary_integer(presence_bits,
                                                   number_of_additions)

        # Embed each encoded extension addition in an open type (add a
        # length field and multiple of 8 bits).
        encoder.align()

        for addition_encoder in addition_encoders:
            addition_encoder.align()
            encoder.append_length_determinant(addition_encoder.number_of_bytes())
            encoder += addition_encoder

        return True

    def encode_addition_group(self, data, encoder):
        self.encode_root(data, encoder)

        if ((encoder.value == 0)
            and (encoder.number_of_bits == len(self.optionals))):
            encoder.number_of_bits = 0

    def encode_member(self, member, data, encoder, encode_default=False):
        name = member.name

        if name in data:
            if member.default is None:
                member.encode(data[name], encoder)
            elif data[name] != member.default or encode_default:
                member.encode(data[name], encoder)
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
        length = decoder.read_normally_small_length()
        presence_bits = decoder.read_non_negative_binary_integer(length)
        decoder.align()
        decoded = {}

        for i in range(length):
            if presence_bits & (1 << (length - i - 1)):
                # Open type decoding.
                open_type_length = decoder.read_length_determinant()
                offset = decoder.number_of_bits

                if i < len(self.additions):
                    addition = self.additions[i]

                    if isinstance(addition, AdditionGroup):
                        decoded.update(addition.decode(decoder))
                    else:
                        try:
                            decoded[addition.name] = addition.decode(decoder)
                        except DecodeError as e:
                            e.location.append(addition.name)
                            raise
                else:
                    decoder.skip_bits(8 * open_type_length)

                alignment_bits = (offset - decoder.number_of_bits) % 8

                if alignment_bits != 0:
                    decoder.skip_bits(8 - alignment_bits)

        return decoded

    def __repr__(self):
        return '{}({}, [{}])'.format(
            self.__class__.__name__,
            self.name,
            ', '.join([repr(member) for member in self.root_members]))


class Sequence(MembersType):

    def __init__(self,
                 name,
                 root_members,
                 additions):
        super(Sequence, self).__init__(name,
                                       root_members,
                                       additions,
                                       'SEQUENCE')


class Set(MembersType):

    def __init__(self,
                 name,
                 root_members,
                 additions):
        super(Set, self).__init__(name,
                                  root_members,
                                  additions,
                                  'SET')


class AdditionGroup(Sequence):
    pass


class ArrayType(Type):

    def __init__(self,
                 name,
                 element_type,
                 minimum,
                 maximum,
                 has_extension_marker,
                 type_name):
        super(ArrayType, self).__init__(name, type_name)
        self.element_type = element_type
        self.minimum = minimum
        self.maximum = maximum
        self.has_extension_marker = has_extension_marker

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = maximum - minimum
            self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.has_extension_marker:
            encoder.append_bit(0)

        if self.number_of_bits is None:
            encoder.align()
            encoder.append_length_determinant(len(data))
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(data) - self.minimum,
                                                       self.number_of_bits)

        for entry in data:
            self.element_type.encode(entry, encoder)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                raise NotImplementedError('Extension is not implemented.')

        if self.number_of_bits is None:
            decoder.align()
            length = decoder.read_length_determinant()
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)

        decoded = []

        for _ in range(length):
            decoded_element = self.element_type.decode(decoder)
            decoded.append(decoded_element)

        return decoded

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.name,
                                   self.element_type)


class SequenceOf(ArrayType):

    def __init__(self,
                 name,
                 element_type,
                 minimum,
                 maximum,
                 has_extension_marker):
        super(SequenceOf, self).__init__(name,
                                         element_type,
                                         minimum,
                                         maximum,
                                         has_extension_marker,
                                         'SEQUENCE OF')


class SetOf(ArrayType):

    def __init__(self,
                 name,
                 element_type,
                 minimum,
                 maximum,
                 has_extension_marker):
        super(SetOf, self).__init__(name,
                                    element_type,
                                    minimum,
                                    maximum,
                                    has_extension_marker,
                                    'SET OF')


class BitString(Type):

    def __init__(self, name, minimum, maximum):
        super(BitString, self).__init__(name, 'BIT STRING')
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.align()
            encoder.append_length_determinant(data[1])
        elif self.minimum != self.maximum:
            encoder.align()
            encoder.append_non_negative_binary_integer(data[1] - self.minimum,
                                                       self.number_of_bits)
            encoder.align()
        elif self.minimum > 16:
            encoder.align()

        encoder.append_bits(data[0], data[1])

    def decode(self, decoder):
        if self.number_of_bits is None:
            decoder.align()
            number_of_bits = decoder.read_length_determinant()
        else:
            number_of_bits = self.minimum

            if self.minimum != self.maximum:
                decoder.align()
                number_of_bits += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)
                decoder.align()
            elif self.minimum > 16:
                decoder.align()

        value = decoder.read_bits(number_of_bits)

        return (value, number_of_bits)

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name, minimum, maximum):
        super(OctetString, self).__init__(name, 'OCTET STRING')
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum

            if size == 0 and self.maximum >= 65536:
                self.number_of_bits = None
            else:
                self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        align = True

        if self.number_of_bits is None:
            encoder.align()
            encoder.append_length_determinant(len(data))
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(data) - self.minimum,
                                                       self.number_of_bits)
        elif self.maximum <= 2:
            align = False

        if align:
            encoder.align()

        encoder.append_bytes(data)

    def decode(self, decoder):
        align = True

        if self.number_of_bits is None:
            decoder.align()
            length = decoder.read_length_determinant()
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)
            elif self.maximum <= 2:
                align = False

        if align:
            decoder.align()

        return decoder.read_bits(8 * length)

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class IA5String(KnownMultiplierStringType):

    ENCODE_DECODE_MAP = {v: v for v in range(128)}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class NumericString(KnownMultiplierStringType):

    ALPHABET = bytearray(b' 0123456789')
    ENCODE_MAP = {v: i for i, v in enumerate(ALPHABET)}
    DECODE_MAP = {i: v for i, v in enumerate(ALPHABET)}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_MAP,
                                           DECODE_MAP)


class PrintableString(KnownMultiplierStringType):

    ALPHABET = bytearray((string.ascii_uppercase
                          + string.ascii_lowercase
                          + string.digits
                          + " '()+,-./:=?").encode('ascii'))
    ENCODE_MAP = {v: v for v in ALPHABET}
    DECODE_MAP = {v: v for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_MAP,
                                           DECODE_MAP)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name, 'UniversalString')

    def encode(self, _data, _encoder):
        raise NotImplementedError('UniversalString is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('UniversalString is not yet implemented.')

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(KnownMultiplierStringType):

    ENCODE_DECODE_MAP = {v: v for v in range(32, 127)}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class GeneralString(Type):

    def __init__(self, name):
        super(GeneralString, self).__init__(name, 'GeneralString')

    def encode(self, _data, _encoder):
        raise NotImplementedError('GeneralString is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('GeneralString is not yet implemented.')

    def __repr__(self):
        return 'GeneralString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name, 'UTF8String')

    def encode(self, data, encoder):
        encoded = data.encode('utf-8')
        encoder.align()
        encoder.append_length_determinant(len(encoded))
        encoder.append_bytes(bytearray(encoded))

    def decode(self, decoder):
        decoder.align()
        length = decoder.read_length_determinant()
        encoded = decoder.read_bits(8 * length)

        return encoded.decode('utf-8')

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class GraphicString(Type):

    def __init__(self, name):
        super(GraphicString, self).__init__(name, 'GraphicString')

    def encode(self, data, encoder):
        encoded = data.encode('latin-1')
        encoder.append_length_determinant(len(encoded))
        encoder.append_bytes(bytearray(encoded))

    def decode(self, decoder):
        length = decoder.read_length_determinant()
        encoded = decoder.read_bits(8 * length)

        return encoded.decode('latin-1')

    def __repr__(self):
        return 'GraphicString({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name, 'BMPString')

    def encode(self, _data, _encoder):
        raise NotImplementedError('BMPString is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('BMPString is not yet implemented.')

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, _data, _encoder):
        raise NotImplementedError('TeletexString is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('TeletexString is not yet implemented.')

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class UTCTime(VisibleString):
    pass


class GeneralizedTime(VisibleString):
    pass


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, data, encoder):
        identifiers = [int(identifier) for identifier in data.split('.')]

        first_subidentifier = (40 * identifiers[0] + identifiers[1])
        encoded_subidentifiers = self.encode_subidentifier(
            first_subidentifier)

        for identifier in identifiers[2:]:
            encoded_subidentifiers += self.encode_subidentifier(identifier)

        encoder.append_bytes(bytearray([len(encoded_subidentifiers)]))
        encoder.append_bytes(bytearray(encoded_subidentifiers))

    def decode(self, decoder):
        length = decoder.read_bytes(1)[0]
        data = decoder.read_bytes(length)
        offset = 0
        subidentifier, offset = self.decode_subidentifier(data, offset)
        decoded = [subidentifier // 40, subidentifier % 40]

        while offset < length:
            subidentifier, offset = self.decode_subidentifier(data, offset)
            decoded.append(subidentifier)

        return '.'.join([str(v) for v in decoded])

    def encode_subidentifier(self, subidentifier):
        encoder = [subidentifier & 0x7f]
        subidentifier >>= 7

        while subidentifier > 0:
            encoder.append(0x80 | (subidentifier & 0x7f))
            subidentifier >>= 7

        return encoder[::-1]

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

    def __init__(self, name, root_members, additions):
        super(Choice, self).__init__(name, 'CHOICE')

        # Root.
        index_to_member, name_to_index = self.create_maps(root_members)
        self.root_index_to_member = index_to_member
        self.root_name_to_index = name_to_index
        self.root_number_of_bits = integer_as_number_of_bits(len(root_members) - 1)

        # Optional additions.
        if additions is None:
            index_to_member = None
            name_to_index = None
        else:
            index_to_member, name_to_index = self.create_maps(additions)

        self.additions_index_to_member = index_to_member
        self.additions_name_to_index = name_to_index

    def create_maps(self, members):
        index_to_member = {
            index: member
            for index, member in enumerate(members)
        }
        name_to_index = {
            member.name: index
            for index, member in enumerate(members)
        }

        return index_to_member, name_to_index

    def all_members(self):
        return (list(self.root_index_to_member.values())
                + list(self.additions_index_to_member.values()))

    def encode(self, data, encoder):
        if not isinstance(data, tuple):
            raise EncodeError("expected tuple, but got '{}'".format(data))

        if self.additions_index_to_member is not None:
            if data[0] in self.root_name_to_index:
                encoder.append_bit(0)
                self.encode_root(data, encoder)
            else:
                encoder.append_bit(1)
                self.encode_additions(data, encoder)
        else:
            self.encode_root(data, encoder)

    def encode_root(self, data, encoder):
        try:
            index = self.root_name_to_index[data[0]]
        except KeyError:
            raise EncodeError(
                "Expected choices are {}, but got '{}'.".format(
                    [member.name for member in self.all_members()],
                    data[0]))

        if len(self.root_index_to_member) > 1:
            encoder.append_non_negative_binary_integer(index,
                                                       self.root_number_of_bits)

        member = self.root_index_to_member[index]
        member.encode(data[1], encoder)

    def encode_additions(self, data, encoder):
        try:
            index = self.additions_name_to_index[data[0]]
        except KeyError:
            raise EncodeError(
                "Expected choices are {}, but got '{}'.".format(
                    [member.name for member in self.all_members()],
                    data[0]))

        addition_encoder = Encoder()
        addition = self.additions_index_to_member[index]
        addition.encode(data[1], addition_encoder)

        # Embed encoded extension addition in an open type (add a
        # length field and multiple of 8 bits).
        addition_encoder.align()
        encoder.append_normally_small_non_negative_whole_number(index)
        encoder.align()
        encoder.append_length_determinant(addition_encoder.number_of_bytes())
        encoder += addition_encoder

    def decode(self, decoder):
        if self.additions_index_to_member is not None:
            if decoder.read_bit():
                return self.decode_additions(decoder)
            else:
                return self.decode_root(decoder)
        else:
            return self.decode_root(decoder)

    def decode_root(self, decoder):
        if len(self.root_index_to_member) > 1:
            index = decoder.read_non_negative_binary_integer(
                self.root_number_of_bits)
        else:
            index = 0

        member = self.root_index_to_member[index]

        return (member.name, member.decode(decoder))

    def decode_additions(self, decoder):
        index = decoder.read_normally_small_non_negative_whole_number()
        addition = self.additions_index_to_member[index]

        # Open type decoding.
        decoder.align()
        decoder.read_length_determinant()
        offset = decoder.number_of_bits
        decoded = addition.decode(decoder)
        alignment_bits = (offset - decoder.number_of_bits) % 8

        if alignment_bits != 0:
            decoder.skip_bits(8 - alignment_bits)

        return (addition.name, decoded)

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member)
                       for member in self.root_name_to_index]))


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL')

    def encode(self, _, _encoder):
        pass

    def decode(self, _):
        return None

    def __repr__(self):
        return 'Null({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY')

    def encode(self, _, _encoder):
        raise NotImplementedError('ANY is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('ANY is not yet implemented.')

    def __repr__(self):
        return 'Any({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name, 'ENUMERATED')
        root, additions = enum_values_split(values)
        root = sorted(root, key=itemgetter(1))

        # Root.
        index_to_name, name_to_index = self.create_maps(root)
        self.root_index_to_name = index_to_name
        self.root_name_to_index = name_to_index
        self.root_number_of_bits = integer_as_number_of_bits(len(index_to_name) - 1)

        # Optional additions.
        if additions is None:
            index_to_name = None
            name_to_index = None
        else:
            index_to_name, name_to_index = self.create_maps(additions)

        self.additions_index_to_name = index_to_name
        self.additions_name_to_index = name_to_index

    def create_maps(self, items):
        index_to_name = {
            index: value[0]
            for index, value in enumerate(items)
        }
        name_to_index = {
            name: index
            for index, name in index_to_name.items()
        }

        return index_to_name, name_to_index

    def encode(self, data, encoder):
        if self.additions_index_to_name is None:
            index = self.root_name_to_index[data]
            encoder.append_non_negative_binary_integer(index,
                                                       self.root_number_of_bits)
        else:
            if data in self.root_name_to_index:
                encoder.append_bit(0)
                index = self.root_name_to_index[data]
                encoder.append_non_negative_binary_integer(index,
                                                           self.root_number_of_bits)
            else:
                encoder.append_bit(1)
                index = self.additions_name_to_index[data]
                encoder.append_normally_small_non_negative_whole_number(index)

    def decode(self, decoder):
        if self.additions_index_to_name is None:
            return self.decode_root(decoder)
        else:
            additions = decoder.read_bit()

            if additions == 0:
                return self.decode_root(decoder)
            else:
                index = decoder.read_normally_small_non_negative_whole_number()

                try:
                    return self.additions_index_to_name[index]
                except KeyError:
                    raise DecodeError(
                        'expected enumeration index in {}, but got {}'.format(
                            list(self.additions_index_to_name),
                            index))

    def decode_root(self, decoder):
        index = decoder.read_non_negative_binary_integer(self.root_number_of_bits)

        try:
            name = self.root_index_to_name[index]
        except KeyError:
            raise DecodeError(
                'expected enumeration index in {}, but got {}'.format(
                    list(self.root_index_to_name),
                    index))

        return name

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class Recursive(Type):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name, 'RECURSIVE')
        self.type_name = type_name
        self.module_name = module_name
        self._inner = None

    def set_inner_type(self, inner):
        self._inner = inner

    def encode(self, data, encoder):
        self._inner.encode(data, encoder)

    def decode(self, decoder):
        return self._inner.decode(decoder)

    def __repr__(self):
        return 'Recursive({})'.format(self.name)


class CompiledType(compiler.CompiledType):

    def __init__(self, type_, constraints):
        super(CompiledType, self).__init__(constraints)
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
        constraints = self.compile_constraints(type_name,
                                               type_descriptor,
                                               module_name)

        return CompiledType(compiled_type, constraints)

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
                                                    module_name),
                                  *self.get_size_range(type_descriptor,
                                                       module_name))
        elif type_name == 'SET':
            compiled = Set(name,
                           *self.compile_members(
                               type_descriptor['members'],
                               module_name,
                               sort_by_tag=True))
        elif type_name == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name),
                             *self.get_size_range(type_descriptor,
                                                  module_name))
        elif type_name == 'CHOICE':
            compiled = Choice(name,
                              *self.compile_members(
                                  type_descriptor['members'],
                                  module_name,
                                  flat_additions=True))
        elif type_name == 'INTEGER':
            compiled = Integer(name,
                               *self.get_restricted_to_range(type_descriptor,
                                                             module_name))
        elif type_name == 'REAL':
            compiled = Real(name)
        elif type_name == 'ENUMERATED':
            compiled = Enumerated(name, type_descriptor['values'])
        elif type_name == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_name == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_name == 'OCTET STRING':
            minimum, maximum, _ = self.get_size_range(type_descriptor,
                                                      module_name)
            compiled = OctetString(name, minimum, maximum)
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
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = VisibleString(name,
                                     *self.get_size_range(type_descriptor,
                                                          module_name),
                                     permitted_alphabet=permitted_alphabet)
        elif type_name == 'GeneralString':
            compiled = GeneralString(name)
        elif type_name == 'UTF8String':
            compiled = UTF8String(name)
        elif type_name == 'GraphicString':
            compiled = GraphicString(name)
        elif type_name == 'BMPString':
            compiled = BMPString(name)
        elif type_name == 'UTCTime':
            compiled = UTCTime(name)
        elif type_name == 'UniversalString':
            compiled = UniversalString(name)
        elif type_name == 'GeneralizedTime':
            compiled = GeneralizedTime(name)
        elif type_name == 'BIT STRING':
            minimum, maximum, _ = self.get_size_range(type_descriptor,
                                                      module_name)
            compiled = BitString(name, minimum, maximum)
        elif type_name == 'ANY':
            compiled = Any(name)
        elif type_name == 'ANY DEFINED BY':
            compiled = Any(name)
        elif type_name == 'NULL':
            compiled = Null(name)
        else:
            if type_name in self.types_backtrace:
                compiled = Recursive(name,
                                     type_name,
                                     module_name)
                self.recurvise_types.append(compiled)
            else:
                self.types_backtrace_push(type_name)
                compiled = self.compile_type(
                    name,
                    *self.lookup_type_descriptor(
                        type_name,
                        module_name))
                self.types_backtrace_pop()

        # Set any given tag.
        if 'tag' in type_descriptor:
            tag = type_descriptor['tag']
            class_prio = CLASS_PRIO[tag.get('class', 'CONTEXT_SPECIFIC')]
            class_number = tag['number']
            compiled.tag = (class_prio, class_number)

        return compiled

    def compile_members(self,
                        members,
                        module_name,
                        sort_by_tag=False,
                        flat_additions=False):
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
                                              additions,
                                              flat_additions)
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
                                 additions,
                                 flat_additions):
        if isinstance(member, list):
            if flat_additions:
                for memb in member:
                    compiled_member = self.compile_member(memb,
                                                          module_name)
                    additions.append(compiled_member)
            else:
                compiled_member, _ = self.compile_members(member,
                                                          module_name)
                compiled_group = AdditionGroup('ExtensionAddition',
                                               compiled_member,
                                               None)
                additions.append(compiled_group)
        else:
            compiled_member = self.compile_member(member,
                                                  module_name)
            additions.append(compiled_member)

    def compile_root_member(self, member, module_name, compiled_members):
        compiled_member = self.compile_member(member,
                                              module_name)
        compiled_members.append(compiled_member)

    def compile_member(self, member, module_name):
        compiled_member = self.compile_type(member['name'],
                                            member,
                                            module_name)

        if 'optional' in member:
            compiled_member.optional = member['optional']

        if 'default' in member:
            compiled_member.default = member['default']

        if 'size' in member:
            compiled_member.set_size_range(*self.get_size_range(member,
                                                                module_name))

        return compiled_member

    def get_permitted_alphabet(self, type_descriptor):
        def char_range(begin, end):
            return ''.join([chr(char)
                            for char in range(ord(begin), ord(end) + 1)])

        if 'from' not in type_descriptor:
            return

        permitted_alphabet = type_descriptor['from']
        value = ''

        for item in permitted_alphabet:
            if isinstance(item, tuple):
                value += char_range(item[0], item[1])
            else:
                value += item

        value = sorted(value)
        encode_map = {ord(v): i for i, v in enumerate(value)}
        decode_map = {i: ord(v) for i, v in enumerate(value)}

        return PermittedAlphabet(encode_map, decode_map)


def compile_dict(specification):
    return Compiler(specification).process()


def decode_length(_data):
    raise DecodeError('Decode length is not supported for this codec.')
