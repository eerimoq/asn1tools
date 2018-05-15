"""Unaligned Packed Encoding Rules (UPER) codec.

"""

import logging
import string

from . import EncodeError
from . import DecodeError
from . import per
from .per import integer_as_number_of_bits
from .per import CLASS_PRIO
from .per import PermittedAlphabet
from .per import Encoder
from .per import Type
from .per import Boolean
from .per import Null
from .per import Any
from .per import Enumerated
from .per import Recursive
from .per import Real


LOGGER = logging.getLogger(__name__)


class KnownMultiplierStringType(Type):

    PERMITTED_ALPHABET = ''

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
        self.bits_per_character = integer_as_number_of_bits(
            len(permitted_alphabet) - 1)

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
            encoder.append_length_determinant(len(encoded))
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(encoded) - self.minimum,
                                                       self.number_of_bits)

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
            length = decoder.read_length_determinant()
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(self.number_of_bits)

        data = []

        for _ in range(length):
            value = decoder.read_non_negative_binary_integer(self.bits_per_character)
            data.append(self.permitted_alphabet.decode(value))

        return bytearray(data).decode('ascii')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)


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

    def encode(self, data, encoder):
        if self.has_extension_marker:
            encoder.append_bit(0)

        if self.number_of_bits is None:
            encoder.append_unconstrained_whole_number(data)
        else:
            encoder.append_non_negative_binary_integer(data - self.minimum,
                                                       self.number_of_bits)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                raise NotImplementedError('Extension is not implemented.')

        if self.number_of_bits is None:
            length = decoder.read_length_determinant()
            value = decoder.read_unconstrained_whole_number(length)
        else:
            value = decoder.read_non_negative_binary_integer(self.number_of_bits)
            value += self.minimum

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
            encoder.append_length_determinant(len(data))
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(
                len(data) - self.minimum,
                self.number_of_bits)

        for entry in data:
            self.element_type.encode(entry, encoder)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                raise NotImplementedError('Extension is not implemented.')

        if self.number_of_bits is None:
            length = decoder.read_length_determinant()
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(self.number_of_bits)

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
            encoder.append_length_determinant(data[1])
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(data[1] - self.minimum,
                                                       self.number_of_bits)

        encoder.append_bits(data[0], data[1])

    def decode(self, decoder):
        if self.number_of_bits is None:
            number_of_bits = decoder.read_length_determinant()
        else:
            number_of_bits = self.minimum

            if self.minimum != self.maximum:
                number_of_bits += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)

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
            self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_length_determinant(len(data))
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(data) - self.minimum,
                                                       self.number_of_bits)

        encoder.append_bytes(data)

    def decode(self, decoder):
        if self.number_of_bits is None:
            length = decoder.read_length_determinant()
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)

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
        raise NotImplementedError('UniversalString not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('UniversalString not yet implemented.')

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
        raise NotImplementedError('GeneralString not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('GeneralString not yet implemented.')

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
        raise NotImplementedError('BMPString not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('BMPString not yet implemented.')

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, _data, _encoder):
        raise NotImplementedError('TeletexString not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('TeletexString not yet implemented.')

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class UTCTime(VisibleString):
    pass


class GeneralizedTime(VisibleString):
    pass


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, _data, _encoder):
        raise NotImplementedError('OBJECT IDENTIFIER not yet implemented.')

    def decode(self, _decoder):
        raise NotImplementedError('OBJECT IDENTIFIER not yet implemented.')

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Choice(per.Choice):

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


class Compiler(per.Compiler):

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


def compile_dict(specification):
    return Compiler(specification).process()


def decode_length(_data):
    raise DecodeError('Decode length is not supported for this codec.')
