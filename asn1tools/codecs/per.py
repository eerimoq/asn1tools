"""Aligned Packed Encoding Rules (PER) codec.

"""

from operator import attrgetter
from operator import itemgetter
import binascii
import string

from ..parser import EXTENSION_MARKER
from . import EncodeError
from . import DecodeError
from . import OutOfDataError
from . import compiler
from . import format_or
from . import restricted_utc_time_to_datetime
from . import restricted_utc_time_from_datetime
from . import restricted_generalized_time_to_datetime
from . import restricted_generalized_time_from_datetime
from .compiler import enum_values_split
from .compiler import clean_bit_string_value
from .compiler import rstrip_bit_string_zeros
from .ber import encode_real
from .ber import decode_real
from .ber import encode_object_identifier
from .ber import decode_object_identifier
from .permitted_alphabet import NUMERIC_STRING
from .permitted_alphabet import PRINTABLE_STRING
from .permitted_alphabet import IA5_STRING
from .permitted_alphabet import VISIBLE_STRING


def is_unbound(minimum, maximum):
    return minimum in [None, 'MIN'] or maximum in [None, 'MAX']


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
        return 1
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
                "Expected a character in '{}', but got '{}' (0x{:02x})'.".format(
                    ''.join(sorted([chr(v) for v in self.encode_map])),
                    chr(value) if chr(value) in string.printable else '.',
                    value))

    def decode(self, value):
        try:
            return self.decode_map[value]
        except KeyError:
            raise DecodeError(
                "Expected a value in {}, but got {:d}.".format(
                    list(self.decode_map),
                    value))


class Encoder(object):

    def __init__(self):
        self.number_of_bits = 0
        self.value = 0
        self.chunks_number_of_bits = 0
        self.chunks = []

    def __iadd__(self, other):
        for value, number_of_bits in other.chunks:
            self.append_non_negative_binary_integer(value, number_of_bits)

        self.append_non_negative_binary_integer(other.value,
                                                other.number_of_bits)

        return self

    def reset(self):
        self.number_of_bits = 0
        self.value = 0
        self.chunks_number_of_bits = 0
        self.chunks = []

    def are_all_bits_zero(self):
        return not (any([value for value, _ in self.chunks]) or self.value)

    def number_of_bytes(self):
        return (self.chunks_number_of_bits + self.number_of_bits + 7) // 8

    def offset(self):
        return (len(self.chunks), self.number_of_bits)

    def set_bit(self, offset):
        chunk_offset, bit_offset = offset

        if len(self.chunks) == chunk_offset:
            self.value |= (1 << (self.number_of_bits - bit_offset - 1))
        else:
            chunk = self.chunks[chunk_offset]
            chunk[0] |= (1 << (chunk[1] - bit_offset - 1))

    def align(self):
        self.align_always()

    def align_always(self):
        width = 8 * self.number_of_bytes()
        width -= self.chunks_number_of_bits
        width -= self.number_of_bits
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

    def append_non_negative_binary_integer(self, value, number_of_bits):
        """Append given integer value.

        """

        if self.number_of_bits > 4096:
            self.chunks.append([self.value, self.number_of_bits])
            self.chunks_number_of_bits += self.number_of_bits
            self.number_of_bits = 0
            self.value = 0

        self.number_of_bits += number_of_bits
        self.value <<= number_of_bits
        self.value |= value

    def append_bytes(self, data):
        """Append given data.

        """

        self.append_bits(data, 8 * len(data))

    def as_bytearray(self):
        """Return the bits as a bytearray.

        """

        value = 0
        number_of_bits = 0

        for chunk_value, chunk_number_of_bits in self.chunks:
            value <<= chunk_number_of_bits
            value |= chunk_value
            number_of_bits += chunk_number_of_bits

        value <<= self.number_of_bits
        value |= self.value
        number_of_bits += self.number_of_bits

        if number_of_bits == 0:
            return bytearray()

        number_of_alignment_bits = (8 - (number_of_bits % 8))

        if number_of_alignment_bits != 8:
            value <<= number_of_alignment_bits
            number_of_bits += number_of_alignment_bits

        value |= (0x80 << number_of_bits)
        value = hex(value)[4:].rstrip('L')

        return bytearray(binascii.unhexlify(value))

    def append_length_determinant(self, length):
        if length < 128:
            encoded = bytearray([length])
        elif length < 16384:
            encoded = bytearray([(0x80 | (length >> 8)), (length & 0xff)])
        elif length < 32768:
            encoded = b'\xc1'
            length = 16384
        elif length < 49152:
            encoded = b'\xc2'
            length = 32768
        elif length < 65536:
            encoded = b'\xc3'
            length = 49152
        else:
            encoded = b'\xc4'
            length = 65536

        self.append_bytes(encoded)

        return length

    def append_length_determinant_chunks(self, length):
        offset = 0
        chunk_length = length

        while True:
            chunk_length = self.append_length_determinant(chunk_length)

            yield offset, chunk_length

            if chunk_length < 16384:
                break

            offset += chunk_length
            chunk_length = length - offset

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
        elif value <= 127:
            self.append_non_negative_binary_integer(0x100 | value, 9)
        else:
            raise NotImplementedError(
                'Normally small length number >127 is not yet supported.')

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
            self.align_always()
            self.append_non_negative_binary_integer(value - minimum, 8)
        elif _range <= 65536:
            self.align_always()
            self.append_non_negative_binary_integer(value - minimum, 16)
        else:
            number_of_bits = size_as_number_of_bytes(value) * 8
            self.align_always()
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
            value = int(binascii.hexlify(encoded), 16)
            value |= (0x80 << self.number_of_bits)
            self.value = bin(value)[10:]
        else:
            self.value = ''

    def align(self):
        self.align_always()

    def align_always(self):
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

        bit = int(self.value[self.number_of_read_bits()])
        self.number_of_bits -= 1

        return bit

    def read_bits(self, number_of_bits):
        """Read given number of bits.

        """

        if number_of_bits > self.number_of_bits:
            raise OutOfDataError(self.number_of_read_bits())

        offset = self.number_of_read_bits()
        value = self.value[offset:offset + number_of_bits]
        self.number_of_bits -= number_of_bits
        value = '10000000' + value
        number_of_alignment_bits = (8 - (number_of_bits % 8))

        if number_of_alignment_bits != 8:
            value += '0' * number_of_alignment_bits

        return binascii.unhexlify(hex(int(value, 2))[4:].rstrip('L'))

    def read_bytes(self, number_of_bytes):
        return self.read_bits(8 * number_of_bytes)

    def read_bytes_aligned(self, number_of_bytes):
        """Read given number of aligned bytes.

        """

        self.number_of_bits -= (self.number_of_bits % 8)

        return bytearray(self.read_bytes(number_of_bytes))

    def read_non_negative_binary_integer(self, number_of_bits):
        """Read an integer value of given number of bits.

        """

        if number_of_bits > self.number_of_bits:
            raise OutOfDataError(self.number_of_read_bits())

        if number_of_bits == 0:
            return 0

        offset = self.number_of_read_bits()
        value = self.value[offset:offset + number_of_bits]
        self.number_of_bits -= number_of_bits

        return int(value, 2)

    def read_length_determinant(self):
        value = self.read_non_negative_binary_integer(8)

        if (value & 0x80) == 0x00:
            return value
        elif (value & 0xc0) == 0x80:
            return (((value & 0x7f) << 8)
                    | (self.read_non_negative_binary_integer(8)))
        else:
            try:
                return {
                    0xc1: 16384,
                    0xc2: 32768,
                    0xc3: 49152,
                    0xc4: 65536
                }[value]
            except KeyError:
                raise DecodeError(
                    'Bad length determinant fragmentation value 0x{:02x}.'.format(
                        value))

    def read_length_determinant_chunks(self):
        while True:
            length = self.read_length_determinant()

            yield length

            if length < 16384:
                break

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
        elif not self.read_bit():
            return self.read_non_negative_binary_integer(7)
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
            self.align_always()
            value = self.read_non_negative_binary_integer(8)
        elif _range <= 65536:
            self.align_always()
            value = self.read_non_negative_binary_integer(16)
        else:
            self.align_always()
            value = self.read_non_negative_binary_integer(number_of_bits)

        return value + minimum

    def read_unconstrained_whole_number(self):
        length = self.read_length_determinant()
        decoded = self.read_non_negative_binary_integer(8 * length)
        number_of_bits = (8 * length)

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

    def set_restricted_to_range(self, minimum, maximum, has_extension_marker):
        pass

    def is_default(self, value):
        return value == self.default


class KnownMultiplierStringType(Type):

    PERMITTED_ALPHABET = PermittedAlphabet({}, {})

    def __init__(self,
                 name,
                 minimum=None,
                 maximum=None,
                 has_extension_marker=False,
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

        if is_unbound(minimum, maximum):
            self.number_of_bits = None
        else:
            size = maximum - minimum
            self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        encoded = bytearray(data.encode('ascii'))

        if self.has_extension_marker:
            if self.minimum <= len(encoded) <= self.maximum:
                encoder.append_bit(0)
            else:
                raise NotImplementedError(
                    'String size extension is not yet implemented.')

        if self.number_of_bits is None:
            return self.encode_unbound(encoded, encoder)
        elif self.minimum != self.maximum:
            encoder.append_constrained_whole_number(len(encoded),
                                                    self.minimum,
                                                    self.maximum,
                                                    self.number_of_bits)

            if self.maximum > 1:
                encoder.align()
        elif self.maximum * self.bits_per_character > 16:
            encoder.align()

        for value in encoded:
            encoder.append_non_negative_binary_integer(
                self.permitted_alphabet.encode(value),
                self.bits_per_character)

    def encode_unbound(self, encoded, encoder):
        encoder.align()

        for offset, length in encoder.append_length_determinant_chunks(len(encoded)):
            for entry in encoded[offset:offset + length]:
                encoder.append_non_negative_binary_integer(
                    self.permitted_alphabet.encode(entry),
                    self.bits_per_character)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                raise NotImplementedError(
                    'String size extension is not yet implemented.')

        if self.number_of_bits is None:
            return self.decode_unbound(decoder)
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

    def decode_unbound(self, decoder):
        decoder.align()
        decoded = []

        for length in decoder.read_length_determinant_chunks():
            for _ in range(length):
                value = decoder.read_non_negative_binary_integer(
                    self.bits_per_character)
                decoded.append(self.permitted_alphabet.decode(value))

        return bytearray(decoded).decode('ascii')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)


class StringType(Type):

    ENCODING = None
    LENGTH_MULTIPLIER = 1

    def __init__(self, name):
        super(StringType, self).__init__(name, self.__class__.__name__)

    def encode(self, data, encoder):
        encoded = data.encode(self.ENCODING)
        encoder.align()

        for offset, length in encoder.append_length_determinant_chunks(len(data)):
            offset *= self.LENGTH_MULTIPLIER
            data = encoded[offset:offset + self.LENGTH_MULTIPLIER * length]
            encoder.append_bytes(data)

    def decode(self, decoder):
        decoder.align()
        encoded = []

        for length in decoder.read_length_determinant_chunks():
            encoded.append(decoder.read_bytes(self.LENGTH_MULTIPLIER * length))

        return b''.join(encoded).decode(self.ENCODING)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)


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
            offset = encoder.offset()
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

        for member in self.root_members:
            self.encode_member(member, data, encoder)

    def encode_additions(self, data, encoder):
        # Encode extension additions.
        presence_bits = 0
        addition_encoders = []
        number_of_precence_bits = 0

        try:
            for addition in self.additions:
                presence_bits <<= 1
                addition_encoder = encoder.__class__()
                number_of_precence_bits += 1

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
        presence_bits <<= (number_of_additions - number_of_precence_bits)
        encoder.append_normally_small_length(number_of_additions)
        encoder.append_non_negative_binary_integer(presence_bits,
                                                   number_of_additions)

        # Embed each encoded extension addition in an open type (add a
        # length field and multiple of 8 bits).
        encoder.align()

        for addition_encoder in addition_encoders:
            addition_encoder.align_always()
            encoder.append_length_determinant(addition_encoder.number_of_bytes())
            encoder += addition_encoder

        return True

    def encode_addition_group(self, data, encoder):
        self.encode_root(data, encoder)

        if (encoder.are_all_bits_zero()
            and (encoder.number_of_bits == len(self.optionals))):
            encoder.reset()

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
            else:
                decoded = self.decode_root(decoder)
        else:
            decoded = self.decode_root(decoder)

        return decoded

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

        if is_unbound(minimum, maximum):
            self.number_of_bits = None
        else:
            size = maximum - minimum
            self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.has_extension_marker:
            if self.minimum <= len(data) <= self.maximum:
                encoder.append_bit(0)
            else:
                raise NotImplementedError('Extension is not yet implemented.')

        if self.number_of_bits is None:
            return self.encode_unbound(data, encoder)
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(data) - self.minimum,
                                                       self.number_of_bits)

        for entry in data:
            self.element_type.encode(entry, encoder)

    def encode_unbound(self, data, encoder):
        encoder.align()

        for offset, length in encoder.append_length_determinant_chunks(len(data)):
            for entry in data[offset:offset + length]:
                self.element_type.encode(entry, encoder)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                raise NotImplementedError('Extension is not yet implemented.')

        if self.number_of_bits is None:
            return self.decode_unbound(decoder)
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

    def decode_unbound(self, decoder):
        decoder.align()
        decoded = []

        for length in decoder.read_length_determinant_chunks():
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
        super(Boolean, self).__init__(name, 'BOOLEAN')

    def encode(self, data, encoder):
        encoder.append_bit(bool(data))

    def decode(self, decoder):
        return bool(decoder.read_bit())

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER')
        self.minimum = None
        self.maximum = None
        self.has_extension_marker = False
        self.number_of_bits = None
        self.number_of_indefinite_bits = None

    def set_restricted_to_range(self, minimum, maximum, has_extension_marker):
        self.has_extension_marker = has_extension_marker

        if minimum == 'MIN' or maximum == 'MAX':
            return

        self.minimum = minimum
        self.maximum = maximum
        size = self.maximum - self.minimum
        self.number_of_bits = integer_as_number_of_bits(size)

        if size <= 65535:
            self.number_of_indefinite_bits = None
        else:
            number_of_bits = ((self.number_of_bits + 7) // 8 - 1).bit_length()
            self.number_of_indefinite_bits = number_of_bits

    def encode(self, data, encoder):
        if self.has_extension_marker:
            if self.minimum <= data <= self.maximum:
                encoder.append_bit(0)
            else:
                encoder.append_bit(1)
                encoder.align()
                encoder.append_unconstrained_whole_number(data)
                return

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
            if decoder.read_bit():
                decoder.align()

                return decoder.read_unconstrained_whole_number()

        if self.number_of_bits is None:
            decoder.align()

            return decoder.read_unconstrained_whole_number()
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

            return decoder.read_constrained_whole_number(self.minimum,
                                                         self.maximum,
                                                         number_of_bits)

    def __repr__(self):
        return 'Integer({})'.format(self.name)


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


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL')

    def encode(self, _, _encoder):
        pass

    def decode(self, _):
        return None

    def __repr__(self):
        return 'Null({})'.format(self.name)


class BitString(Type):

    def __init__(self, name, minimum, maximum, has_named_bits):
        super(BitString, self).__init__(name, 'BIT STRING')
        self.minimum = minimum
        self.maximum = maximum
        self.has_named_bits = has_named_bits

        if is_unbound(minimum, maximum):
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = integer_as_number_of_bits(size)

    def is_default(self, value):
        clean_value = clean_bit_string_value(value,
                                             self.has_named_bits)
        clean_default = clean_bit_string_value(self.default,
                                               self.has_named_bits)

        return clean_value == clean_default

    def rstrip_zeros(self, data, number_of_bits):
        data, number_of_bits = rstrip_bit_string_zeros(bytearray(data))

        if self.minimum is not None:
            if number_of_bits < self.minimum:
                number_of_bits = self.minimum
                number_of_bytes = ((number_of_bits + 7) // 8)
                data += (number_of_bytes - len(data)) * b'\x00'

        return (data, number_of_bits)

    def encode(self, data, encoder):
        data, number_of_bits = data

        if self.has_named_bits:
            data, number_of_bits = self.rstrip_zeros(data, number_of_bits)

        if self.number_of_bits is None:
            return self.encode_unbound(data, number_of_bits, encoder)
        elif self.minimum != self.maximum:
            encoder.align()
            encoder.append_non_negative_binary_integer(
                number_of_bits - self.minimum,
                self.number_of_bits)
            encoder.align()
        elif self.minimum > 16:
            encoder.align()

        encoder.append_bits(data, number_of_bits)

    def encode_unbound(self, data, number_of_bits, encoder):
        encoder.align()

        for offset, length in encoder.append_length_determinant_chunks(number_of_bits):
            encoder.append_bits(data[offset // 8:(offset + length + 7) // 8], length)

    def decode(self, decoder):
        if self.number_of_bits is None:
            return self.decode_unbound(decoder)
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

    def decode_unbound(self, decoder):
        decoder.align()
        decoded = []
        number_of_bits = 0

        for length in decoder.read_length_determinant_chunks():
            decoded.append(decoder.read_bits(length))
            number_of_bits += length

        return (b''.join(decoded), number_of_bits)

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name, minimum, maximum):
        super(OctetString, self).__init__(name, 'OCTET STRING')
        self.minimum = minimum
        self.maximum = maximum

        if is_unbound(minimum, maximum):
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
            return self.encode_unbound(data, encoder)
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(data) - self.minimum,
                                                       self.number_of_bits)
        elif self.maximum <= 2:
            align = False

        if align:
            encoder.align()

        encoder.append_bytes(data)

    def encode_unbound(self, data, encoder):
        encoder.align()

        for offset, length in encoder.append_length_determinant_chunks(len(data)):
            encoder.align()
            encoder.append_bytes(data[offset:offset + length])

    def decode(self, decoder):
        align = True

        if self.number_of_bits is None:
            return self.decode_unbound(decoder)
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)
            elif self.maximum <= 2:
                align = False

        if align:
            decoder.align()

        return decoder.read_bytes(length)

    def decode_unbound(self, decoder):
        decoder.align()
        decoded = []

        for length in decoder.read_length_determinant_chunks():
            decoder.align()
            decoded.append(decoder.read_bytes(length))

        return b''.join(decoded)

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, data, encoder):
        encoded_subidentifiers = encode_object_identifier(data)
        encoder.align()
        encoder.append_length_determinant(len(encoded_subidentifiers))
        encoder.append_bytes(bytearray(encoded_subidentifiers))

    def decode(self, decoder):
        decoder.align()
        length = decoder.read_length_determinant()
        data = decoder.read_bytes(length)

        return decode_object_identifier(bytearray(data), 0, len(data))

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


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

    def format_root_indexes(self):
        return format_or(sorted(list(self.root_index_to_name)))

    def format_addition_indexes(self):
        return format_or(sorted(list(self.additions_index_to_name)))

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
                        'Expected enumeration index {}, but got {}.'.format(
                            self.format_addition_indexes(),
                            index))

    def decode_root(self, decoder):
        index = decoder.read_non_negative_binary_integer(self.root_number_of_bits)

        try:
            name = self.root_index_to_name[index]
        except KeyError:
            raise DecodeError(
                'Expected enumeration index {}, but got {}.'.format(
                    self.format_root_indexes(),
                    index))

        return name

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class Sequence(MembersType):

    def __init__(self,
                 name,
                 root_members,
                 additions):
        super(Sequence, self).__init__(name,
                                       root_members,
                                       additions,
                                       'SEQUENCE')


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


class Set(MembersType):

    def __init__(self,
                 name,
                 root_members,
                 additions):
        super(Set, self).__init__(name,
                                  root_members,
                                  additions,
                                  'SET')


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

    def format_root_indexes(self):
        return format_or(sorted(list(self.root_index_to_member)))

    def format_addition_indexes(self):
        return format_or(sorted(list(self.additions_index_to_member)))

    def format_names(self):
        members = list(self.root_index_to_member.values())

        if self.additions_index_to_member is not None:
            members += list(self.additions_index_to_member.values())

        return format_or(sorted([member.name for member in members]))

    def encode(self, data, encoder):
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
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    data[0]))

        if len(self.root_index_to_member) > 1:
            encoder.append_non_negative_binary_integer(index,
                                                       self.root_number_of_bits)

        member = self.root_index_to_member[index]
        self.encode_member(member, data[1], encoder)

    def encode_additions(self, data, encoder):
        try:
            index = self.additions_name_to_index[data[0]]
        except KeyError:
            raise EncodeError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    data[0]))

        addition_encoder = Encoder()
        addition = self.additions_index_to_member[index]
        self.encode_member(addition, data[1], addition_encoder)

        # Embed encoded extension addition in an open type (add a
        # length field and multiple of 8 bits).
        addition_encoder.align()
        encoder.append_normally_small_non_negative_whole_number(index)
        encoder.align()
        encoder.append_length_determinant(addition_encoder.number_of_bytes())
        encoder += addition_encoder

    def encode_member(self, member, data, encoder):
        try:
            member.encode(data, encoder)
        except EncodeError as e:
            e.location.append(member.name)
            raise

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

        try:
            member = self.root_index_to_member[index]
        except KeyError:
            raise DecodeError(
                'Expected choice index {}, but got {}.'.format(
                    self.format_root_indexes(),
                    index))

        return (member.name, member.decode(decoder))

    def decode_additions(self, decoder):
        index = decoder.read_normally_small_non_negative_whole_number()

        try:
            addition = self.additions_index_to_member[index]
        except KeyError:
            raise DecodeError(
                'Expected choice index {}, but got {}.'.format(
                    self.format_addition_indexes(),
                    index))

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


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name, 'UTF8String')

    def encode(self, data, encoder):
        encoded = data.encode('utf-8')
        encoder.align()

        for offset, length in encoder.append_length_determinant_chunks(len(encoded)):
            encoder.append_bytes(encoded[offset:offset + length])

    def decode(self, decoder):
        decoder.align()
        encoded = []

        for length in decoder.read_length_determinant_chunks():
            encoded.append(decoder.read_bytes(length))

        return b''.join(encoded).decode('utf-8')

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class NumericString(KnownMultiplierStringType):

    ALPHABET = bytearray(NUMERIC_STRING.encode('ascii'))
    ENCODE_MAP = {v: i for i, v in enumerate(ALPHABET)}
    DECODE_MAP = {i: v for i, v in enumerate(ALPHABET)}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_MAP,
                                           DECODE_MAP)


class PrintableString(KnownMultiplierStringType):

    ALPHABET = bytearray(PRINTABLE_STRING.encode('ascii'))
    ENCODE_MAP = {v: v for v in ALPHABET}
    DECODE_MAP = {v: v for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_MAP,
                                           DECODE_MAP)


class IA5String(KnownMultiplierStringType):

    ALPHABET = bytearray(IA5_STRING.encode('ascii'))
    ENCODE_DECODE_MAP = {v: v for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class VisibleString(KnownMultiplierStringType):

    ALPHABET = bytearray(VISIBLE_STRING.encode('ascii'))
    ENCODE_DECODE_MAP = {v: v for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class GeneralString(StringType):

    ENCODING = 'latin-1'


class BMPString(StringType):

    ENCODING = 'utf-16-be'
    LENGTH_MULTIPLIER = 2


class GraphicString(StringType):

    ENCODING = 'latin-1'


class TeletexString(StringType):

    ENCODING = 'iso-8859-1'


class UniversalString(StringType):

    ENCODING = 'utf-32-be'
    LENGTH_MULTIPLIER = 4


class ObjectDescriptor(GraphicString):
    pass


class UTCTime(VisibleString):

    def encode(self, data, encoder):
        encoded = restricted_utc_time_from_datetime(data)

        return super(UTCTime, self).encode(encoded, encoder)

    def decode(self, decoder):
        decoded = super(UTCTime, self).decode(decoder)

        return restricted_utc_time_to_datetime(decoded)


class GeneralizedTime(VisibleString):

    def encode(self, data, encoder):
        enceded = restricted_generalized_time_from_datetime(data)

        return super(GeneralizedTime, self).encode(enceded, encoder)

    def decode(self, decoder):
        decoded = super(GeneralizedTime, self).decode(decoder)

        return restricted_generalized_time_to_datetime(decoded)


class OpenType(Type):

    def __init__(self, name):
        super(OpenType, self).__init__(name, 'OpenType')

    def encode(self, data, encoder):
        encoder.align()
        encoder.append_length_determinant(len(data))
        encoder.append_bytes(data)

    def decode(self, decoder):
        decoder.align()
        length = decoder.read_length_determinant()

        return decoder.read_bytes(length)

    def __repr__(self):
        return 'OpenType({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY')

    def encode(self, _, _encoder):
        raise NotImplementedError('ANY is not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('ANY is not yet implemented.')

    def __repr__(self):
        return 'Any({})'.format(self.name)


class Recursive(Type, compiler.Recursive):

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
        return 'Recursive({})'.format(self.type_name)


class AdditionGroup(Sequence):
    pass


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
            compiled = Sequence(
                name,
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
            compiled = Set(
                name,
                *self.compile_members(type_descriptor['members'],
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
            minimum, maximum, _ = self.get_size_range(type_descriptor,
                                                      module_name)
            compiled = OctetString(name, minimum, maximum)
        elif type_name == 'TeletexString':
            compiled = TeletexString(name)
        elif type_name == 'NumericString':
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = NumericString(name,
                                     *self.get_size_range(type_descriptor,
                                                          module_name),
                                     permitted_alphabet=permitted_alphabet)
        elif type_name == 'PrintableString':
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = PrintableString(name,
                                       *self.get_size_range(type_descriptor,
                                                            module_name),
                                       permitted_alphabet=permitted_alphabet)
        elif type_name == 'IA5String':
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = IA5String(name,
                                 *self.get_size_range(type_descriptor,
                                                      module_name),
                                 permitted_alphabet=permitted_alphabet)
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
            has_named_bits = ('named-bits' in type_descriptor)
            compiled = BitString(name,
                                 minimum,
                                 maximum,
                                 has_named_bits)
        elif type_name == 'ANY':
            compiled = Any(name)
        elif type_name == 'ANY DEFINED BY':
            compiled = Any(name)
        elif type_name == 'NULL':
            compiled = Null(name)
        elif type_name == 'OpenType':
            compiled = OpenType(name)
        elif type_name == 'EXTERNAL':
            compiled = Sequence(
                name,
                *self.compile_members(self.external_type_descriptor()['members'],
                                      module_name))
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
            compiled = self.set_compiled_tag(compiled, type_descriptor)

        if 'restricted-to' in type_descriptor:
            compiled = self.set_compiled_restricted_to(compiled,
                                                       type_descriptor,
                                                       module_name)

        return compiled

    def set_compiled_tag(self, compiled, type_descriptor):
        compiled = self.copy(compiled)
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
