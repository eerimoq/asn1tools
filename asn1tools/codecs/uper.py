"""Unaligned Packed Encoding Rules (UPER) codec.

"""

import logging
from operator import attrgetter
from operator import itemgetter
import binascii

from . import EncodeError
from . import DecodeError
from . import compiler
from .compiler import enum_values_split
from .per import encode_signed_integer
from .per import decode_signed_integer
from .ber import encode_real
from .ber import decode_real


LOGGER = logging.getLogger(__name__)


class DecodeChoiceError(Exception):
    pass


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
        return self.encode_map[value]

    def decode(self, value):
        return self.decode_map[value]


class Encoder(object):

    def __init__(self):
        self.number_of_bits = 0
        self.value = 0

    def __iadd__(self, other):
        self.append_integer(other.value, other.number_of_bits)

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

        self.append_integer(value, number_of_bits)

    def append_integer(self, value, number_of_bits):
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
            raise NotImplementedError()

        self.append_bytes(encoded)

    def append_normally_small_non_negative_whole_number(self, value):
        if value < 64:
            self.append_integer(value, 7)
        else:
            self.append_bit(1)
            length = (value.bit_length() + 7) // 8
            self.append_length_determinant(length)
            self.append_integer(value, 8 * length)

    def append_normally_small_length(self, value):
        if value <= 64:
            self.append_integer(value - 1, 7)
        else:
            raise NotImplementedError()

    def __repr__(self):
        return binascii.hexlify(self.as_bytearray()).decode('ascii')


class Decoder(object):

    def __init__(self, encoded):
        self.number_of_bits = (8 * len(encoded))

        if len(encoded) > 0:
            self.value = int(binascii.hexlify(encoded), 16)
        else:
            self.value = 0

    def skip_bits(self, number_of_bits):
        self.number_of_bits -= number_of_bits

    def read_bit(self):
        """Read a bit.

        """

        self.number_of_bits -= 1

        return ((self.value >> self.number_of_bits) & 1)

    def read_bits(self, number_of_bits):
        """Read given number of bits.

        """

        self.number_of_bits -= number_of_bits
        mask = ((1 << number_of_bits) - 1)
        value = ((self.value >> self.number_of_bits) & mask)
        value &= mask
        value |= (0x80 << number_of_bits)
        number_of_alignment_bits = (8 - (number_of_bits % 8))

        if number_of_alignment_bits != 8:
            value <<= number_of_alignment_bits

        return binascii.unhexlify(hex(value)[4:].rstrip('L'))

    def read_integer(self, number_of_bits):
        """Read an integer value of given number of bits.

        """

        self.number_of_bits -= number_of_bits
        mask = ((1 << number_of_bits) - 1)

        return ((self.value >> self.number_of_bits) & mask)

    def read_bytes(self, number_of_bytes):
        """Read given number of aligned bytes.

        """

        self.number_of_bits -= (self.number_of_bits % 8)

        return bytearray(self.read_bits(8 * number_of_bytes))

    def read_length_determinant(self):
        value = self.read_integer(8)

        if (value & 0x80) == 0x00:
            return value
        elif (value & 0xc0) == 0x80:
            return (((value & 0x7f) << 8) | (self.read_integer(8)))
        else:
            raise NotImplementedError()

    def read_normally_small_non_negative_whole_number(self):
        if not self.read_bit():
            decoded = self.read_integer(6)
        else:
            length = self.read_length_determinant()
            decoded = self.read_integer(8 * length)

        return decoded

    def read_normally_small_length(self):
        if not self.read_bit():
            return self.read_integer(6) + 1
        else:
            raise NotImplementedError()


def size_as_number_of_bits(size):
    """Returns the minimum number of bits needed to fit given positive
    integer.

    """

    return len('{:b}'.format(size))


class Type(object):

    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
        self.optional = False
        self.default = None
        self.tag = None

    def set_size_range(self, minimum, maximum):
        pass


class KnownMultiplierStringType(Type):

    def __init__(self, name, string_type, minimum, maximum):
        super(KnownMultiplierStringType, self).__init__(name, string_type)
        self.set_size_range(minimum, maximum)

    def set_size_range(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = maximum - minimum
            self.number_of_bits = size_as_number_of_bits(size)

    def encode_length(self, encoder, length):
        if self.number_of_bits is None:
            encoder.append_length_determinant(length)
        elif self.minimum != self.maximum:
            encoder.append_integer(length - self.minimum,
                                   self.number_of_bits)

    def decode_length(self, decoder):
        if self.number_of_bits is None:
            length = decoder.read_length_determinant()
        elif self.minimum != self.maximum:
            length = decoder.read_integer(self.number_of_bits)
            length += self.minimum
        else:
            length = self.minimum

        return length


class Integer(Type):

    def __init__(self, name, minimum, maximum):
        super(Integer, self).__init__(name, 'INTEGER')
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = size_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_bytes(encode_signed_integer(data))
        else:
            encoder.append_integer(data - self.minimum, self.number_of_bits)

    def decode(self, decoder):
        if self.number_of_bits is None:
            length = decoder.read_integer(8)
            value = decode_signed_integer(bytearray(decoder.read_bits(8 * length)))
        else:
            value = decoder.read_integer(self.number_of_bits)
            value += self.minimum

        return value

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

        return decode_real(decoder.read_bytes(length))

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


class IA5String(KnownMultiplierStringType):

    def __init__(self, name, minimum, maximum):
        super(IA5String, self).__init__(name,
                                        'IA5String',
                                        minimum,
                                        maximum)

    def encode(self, data, encoder):
        encoded = data.encode('ascii')
        self.encode_length(encoder, len(encoded))

        for byte in bytearray(encoded):
            encoder.append_bits(bytearray([(byte << 1) & 0xff]), 7)

    def decode(self, decoder):
        length = self.decode_length(decoder)
        data = []

        for _ in range(length):
            data.append(decoder.read_integer(7))

        return bytearray(data).decode('ascii')

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name, 'NumericString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class Sequence(Type):

    def __init__(self,
                 name,
                 root_members,
                 additions):
        super(Sequence, self).__init__(name, 'SEQUENCE')
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

                if isinstance(addition, Sequence):
                    addition.encode_addition_group(data, addition_encoder)
                else:
                    self.encode_member(addition, data, addition_encoder)

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
        encoder.append_integer(presence_bits, number_of_additions)

        # Embed each encoded extension addition in an open type (add a
        # length field and multiple of 8 bits).
        for addition_encoder in addition_encoders:
            addition_encoder.align()
            encoder.append_length_determinant(addition_encoder.number_of_bytes())
            encoder += addition_encoder

        return True

    def encode_addition_group(self, data, encoder):
        self.encode_root(data, encoder)

        if (encoder.value == 0
            and encoder.number_of_bits == len(self.optionals)):
            encoder.number_of_bits = 0

    def encode_member(self, member, data, encoder):
        name = member.name

        if name in data:
            if member.default is None:
                member.encode(data[name], encoder)
            elif data[name] != member.default:
                member.encode(data[name], encoder)
        elif member.optional or member.default is not None:
            pass
        else:
            raise EncodeError(
                "Sequence member '{}' not found in {}.".format(
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
            if optionals.get(member, True):
                value = member.decode(decoder)
                values[member.name] = value
            elif member.default is not None:
                values[member.name] = member.default

        return values

    def decode_additions(self, decoder):
        # Presence bit field.
        length = decoder.read_normally_small_length()
        presence_bits = decoder.read_integer(length)
        decoded = {}

        for i in range(length):
            if presence_bits & (1 << (length - i - 1)):
                addition = self.additions[i]

                # Open type decoding.
                decoder.read_length_determinant()
                offset = decoder.number_of_bits

                if isinstance(addition, Sequence):
                    decoded.update(addition.decode(decoder))
                else:
                    decoded[addition.name] = addition.decode(decoder)

                alignment_bits = (offset - decoder.number_of_bits) % 8

                if alignment_bits != 0:
                    decoder.skip_bits(8 - alignment_bits)

        return decoded

    def __repr__(self):
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.root_members]))


class Set(Type):

    def __init__(self, name, members, additions):
        super(Set, self).__init__(name, 'SET')
        self.members = members
        self.additions = additions
        self.optionals = [
            member
            for member in members
            if member.optional or member.default is not None
        ]

    def encode(self, data, encoder):
        if self.additions is not None:
            encoder.append_bit(0)

        for optional in self.optionals:
            if optional.optional:
                encoder.append_bit(optional.name in data)
            elif optional.name in data:
                encoder.append_bit(data[optional.name] != optional.default)
            else:
                encoder.append_bit(0)

        for member in self.members:
            name = member.name

            if name in data:
                if member.default is None:
                    member.encode(data[name], encoder)
                elif data[name] != member.default:
                    member.encode(data[name], encoder)
            elif member.optional or member.default is not None:
                pass
            else:
                raise EncodeError(
                    "Set member '{}' not found in {}.".format(
                        name,
                        data))

    def decode(self, decoder):
        if self.additions is not None:
            decoder.read_bit()

        values = {}
        optionals = {
            optional: decoder.read_bit()
            for optional in self.optionals
        }

        for member in self.members:
            if optionals.get(member, True):
                value = member.decode(decoder)
                values[member.name] = value
            elif member.default is not None:
                values[member.name] = member.default

        return values

    def __repr__(self):
        return 'Set({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class SequenceOf(Type):

    def __init__(self, name, element_type, minimum, maximum):
        super(SequenceOf, self).__init__(name, 'SEQUENCE OF')
        self.element_type = element_type
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = maximum - minimum
            self.number_of_bits = size_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_length_determinant(len(data))
        elif self.minimum != self.maximum:
            encoder.append_integer(len(data) - self.minimum,
                                   self.number_of_bits)

        for entry in data:
            self.element_type.encode(entry, encoder)

    def decode(self, decoder):
        if self.number_of_bits is None:
            length = decoder.read_length_determinant()
        elif self.minimum != self.maximum:
            length = decoder.read_integer(self.number_of_bits)
            length += self.minimum
        else:
            length = self.minimum

        decoded = []

        for _ in range(length):
            decoded_element = self.element_type.decode(decoder)
            decoded.append(decoded_element)

        return decoded

    def __repr__(self):
        return 'SequenceOf({}, {})'.format(self.name,
                                           self.element_type)


class SetOf(Type):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name, 'SET OF')
        self.element_type = element_type

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'SetOf({}, {})'.format(self.name,
                                      self.element_type)


class BitString(Type):

    def __init__(self, name, minimum, maximum):
        super(BitString, self).__init__(name, 'BIT STRING')
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = size_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_bytes(bytearray([data[1]]) + data[0])
        else:
            if self.minimum != self.maximum:
                encoder.append_integer(data[1] - self.minimum,
                                       self.number_of_bits)

            encoder.append_bits(data[0], data[1])


    def decode(self, decoder):
        if self.number_of_bits is None:
            number_of_bits = decoder.read_bytes(1)[0]
            value = decoder.read_bytes((number_of_bits + 7) // 8)
        else:
            number_of_bits = self.minimum

            if self.minimum != self.maximum:
                number_of_bits += decoder.read_integer(self.number_of_bits)

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
            self.number_of_bits = size_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_length_determinant(len(data))
        else:
            if self.minimum != self.maximum:
                encoder.append_integer(len(data) - self.minimum,
                                       self.number_of_bits)

        encoder.append_bytes(data)

    def decode(self, decoder):
        if self.number_of_bits is None:
            length = decoder.read_length_determinant()
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_integer(self.number_of_bits)

        return decoder.read_bits(8 * length)

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name, 'PrintableString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name, 'UniversalString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(KnownMultiplierStringType):

    def __init__(self,
                 name,
                 minimum=None,
                 maximum=None,
                 permitted_alphabet=None):
        super(VisibleString, self).__init__(name,
                                            'VisibleString',
                                            minimum,
                                            maximum)
        self.permitted_alphabet = permitted_alphabet

        if permitted_alphabet is None:
            self.bits_per_character = 7
        else:
            self.bits_per_character = size_as_number_of_bits(
                len(permitted_alphabet))

    def encode(self, data, encoder):
        encoded = data.encode('ascii')
        self.encode_length(encoder, len(encoded))

        for value in bytearray(encoded):
            if self.permitted_alphabet is not None:
                value = self.permitted_alphabet.encode(value)

            encoder.append_bits(
                bytearray([(value << (8 - self.bits_per_character)) & 0xff]),
                self.bits_per_character)

    def decode(self, decoder):
        length = self.decode_length(decoder)
        data = []

        for _ in range(length):
            value = decoder.read_integer(self.bits_per_character)

            if self.permitted_alphabet is not None:
                value = self.permitted_alphabet.decode(value)

            data.append(value)

        return bytearray(data).decode('ascii')

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class GeneralString(Type):

    def __init__(self, name):
        super(GeneralString, self).__init__(name, 'GeneralString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'GeneralString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name, 'UTF8String')

    def encode(self, data, encoder):
        encoded = data.encode('utf-8')
        encoder.append_length_determinant(len(encoded))
        encoder.append_bytes(bytearray(encoded))

    def decode(self, decoder):
        length = decoder.read_length_determinant()
        encoded = decoder.read_bits(8 * length)

        return encoded.decode('utf-8')

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name, 'BMPString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(VisibleString):

    def __init__(self, name):
        super(UTCTime, self).__init__(name, 'UTCTime')

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(VisibleString):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name, 'GeneralizedTime')

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Choice(Type):

    def __init__(self, name, root_members, additions):
        super(Choice, self).__init__(name, 'CHOICE')

        # Root.
        index_to_member, name_to_index = self.create_maps(root_members)
        self.root_index_to_member = index_to_member
        self.root_name_to_index = name_to_index
        self.root_number_of_bits = size_as_number_of_bits(len(root_members) - 1)

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
            encoder.append_integer(index, self.root_number_of_bits)

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
            index = decoder.read_integer(self.root_number_of_bits)
        else:
            index = 0

        member = self.root_index_to_member[index]

        return (member.name, member.decode(decoder))

    def decode_additions(self, decoder):
        index = decoder.read_normally_small_non_negative_whole_number()
        addition = self.additions_index_to_member[index]

        # Open type decoding.
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
                       for member in self.root_members]))


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

    def encode(self, _, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

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
        self.root_number_of_bits = size_as_number_of_bits(
            len(index_to_name) - 1)

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
            encoder.append_integer(index, self.root_number_of_bits)
        else:
            if data in self.root_name_to_index:
                encoder.append_bit(0)
                index = self.root_name_to_index[data]
                encoder.append_integer(index, self.root_number_of_bits)
            else:
                encoder.append_bit(1)
                index = self.additions_name_to_index[data]
                encoder.append_normally_small_non_negative_whole_number(index)

    def decode(self, decoder):
        if self.additions_index_to_name is None:
            index = decoder.read_integer(self.root_number_of_bits)
            name = self.root_index_to_name[index]
        else:
            additions = decoder.read_bit()

            if additions == 0:
                index = decoder.read_integer(self.root_number_of_bits)
                name = self.root_index_to_name[index]
            else:
                index = decoder.read_normally_small_non_negative_whole_number()
                name = self.additions_index_to_name[index]

        return name

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class Recursive(Type):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name, 'RECURSIVE')
        self.type_name = type_name
        self.module_name = module_name

    def encode(self, _data, _encoder):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def decode(self, _decoder):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def __repr__(self):
        return 'Recursive({})'.format(self.name)


class CompiledType(object):

    def __init__(self, type_):
        self._type = type_

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
        return CompiledType(self.compile_type(type_name,
                                              type_descriptor,
                                              module_name))

    def compile_type(self, name, type_descriptor, module_name):
        type_name = type_descriptor['type']

        if type_name == 'SEQUENCE':
            root_members, additions = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Sequence(name,
                                root_members,
                                additions)
        elif type_name == 'SEQUENCE OF':
            minimum, maximum = self.get_size_range(type_descriptor,
                                                   module_name)
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name),
                                  minimum,
                                  maximum)
        elif type_name == 'SET':
            members, additions = self.compile_members(
                type_descriptor['members'],
                module_name,
                sort_by_tag=True)
            compiled = Set(name,
                           members,
                           additions)
        elif type_name == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_name == 'CHOICE':
            members, additions = self.compile_members(
                type_descriptor['members'],
                module_name,
                flat_additions=True)
            compiled = Choice(name,
                              members,
                              additions)
        elif type_name == 'INTEGER':
            minimum, maximum = self.get_restricted_to_range(type_descriptor,
                                                            module_name)
            compiled = Integer(name, minimum, maximum)
        elif type_name == 'REAL':
            compiled = Real(name)
        elif type_name == 'ENUMERATED':
            compiled = Enumerated(name, type_descriptor['values'])
        elif type_name == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_name == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_name == 'OCTET STRING':
            minimum, maximum = self.get_size_range(type_descriptor,
                                                   module_name)
            compiled = OctetString(name, minimum, maximum)
        elif type_name == 'TeletexString':
            compiled = TeletexString(name)
        elif type_name == 'NumericString':
            compiled = NumericString(name)
        elif type_name == 'PrintableString':
            compiled = PrintableString(name)
        elif type_name == 'IA5String':
            minimum, maximum = self.get_size_range(type_descriptor,
                                                   module_name)
            compiled = IA5String(name, minimum, maximum)
        elif type_name == 'VisibleString':
            minimum, maximum = self.get_size_range(type_descriptor,
                                                   module_name)
            permitted_alphabet = self.get_permitted_alphabet(type_descriptor)
            compiled = VisibleString(name,
                                     minimum,
                                     maximum,
                                     permitted_alphabet)
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
            minimum, maximum = self.get_size_range(type_descriptor,
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
            if member == '...':
                in_extension = not in_extension

                if in_extension:
                    additions = []

                continue

            if in_extension:
                if isinstance(member, list):
                    if flat_additions:
                        for memb in member:
                            compiled_member = self.compile_member(memb,
                                                                  module_name)
                            additions.append(compiled_member)
                    else:
                        compiled_member, _ = self.compile_members(member,
                                                                  module_name)
                        compiled_member = Sequence('ExtensionAddition',
                                                   compiled_member,
                                                   None)
                        additions.append(compiled_member)
                else:
                    compiled_member = self.compile_member(member,
                                                          module_name)
                    additions.append(compiled_member)
            else:
                compiled_member = self.compile_member(member,
                                                      module_name)
                compiled_members.append(compiled_member)

        if sort_by_tag:
            compiled_members = sorted(compiled_members, key=attrgetter('tag'))

        return compiled_members, additions

    def compile_member(self, member, module_name):
        compiled_member = self.compile_type(member['name'],
                                            member,
                                            module_name)

        if 'optional' in member:
            compiled_member.optional = member['optional']

        if 'default' in member:
            compiled_member.default = member['default']

        if 'size' in member:
            minimum, maximum = self.get_size_range(member,
                                                   module_name)
            compiled_member.set_size_range(minimum, maximum)

        return compiled_member

    def get_permitted_alphabet(self, type_descriptor):
        def char_range(begin, end):
            return ''.join([chr(char)
                            for char in range(ord(begin), ord(end) + 1)])

        if 'permitted-alphabet' in type_descriptor:
            permitted_alphabet = type_descriptor['permitted-alphabet']
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
    raise DecodeError('Decode length not supported for this codec.')
