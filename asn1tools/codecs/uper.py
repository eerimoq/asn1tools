"""Unaligned Packed Encoding Rules (UPER) codec.

"""

from . import DecodeError
from . import per
from . import restricted_utc_time_to_datetime
from . import restricted_utc_time_from_datetime
from . import restricted_generalized_time_to_datetime
from . import restricted_generalized_time_from_datetime
from .per import integer_as_number_of_bits
from .per import PermittedAlphabet
from .per import Type
from .per import Boolean
from .per import Real
from .per import Null
from .per import Enumerated
from .per import ObjectIdentifier
from .per import Sequence
from .per import Set
from .per import UTF8String
from .per import GeneralString
from .per import BMPString
from .per import GraphicString
from .per import TeletexString
from .per import UniversalString
from .per import ObjectDescriptor
from .per import Any
from .per import Recursive
from .permitted_alphabet import NUMERIC_STRING
from .permitted_alphabet import PRINTABLE_STRING
from .permitted_alphabet import IA5_STRING
from .permitted_alphabet import VISIBLE_STRING


class Encoder(per.Encoder):

    def align(self):
        pass


class Decoder(per.Decoder):

    def align(self):
        pass


class KnownMultiplierStringType(per.KnownMultiplierStringType):

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

    def encode(self, data, encoder):
        encoded = bytearray(data.encode('ascii'))

        if self.has_extension_marker:
            encoder.append_bit(0)

        if self.number_of_bits is None:
            return self.encode_unbound(encoded, encoder)
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(encoded) - self.minimum,
                                                       self.number_of_bits)

        for value in encoded:
            encoder.append_non_negative_binary_integer(
                self.permitted_alphabet.encode(value),
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
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(self.number_of_bits)

        data = []

        for _ in range(length):
            value = decoder.read_non_negative_binary_integer(self.bits_per_character)
            data.append(self.permitted_alphabet.decode(value))

        return bytearray(data).decode('ascii')


class ArrayType(per.ArrayType):

    def encode(self, data, encoder):
        if self.has_extension_marker:
            if self.minimum <= len(data) <= self.maximum:
                encoder.append_bit(0)
            else:
                encoder.append_bit(1)
                encoder.append_length_determinant(len(data))

                for entry in data:
                    self.element_type.encode(entry, encoder)

                return

        if self.number_of_bits is None:
            return self.encode_unbound(data, encoder)
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(data) - self.minimum,
                                                       self.number_of_bits)

        for entry in data:
            self.element_type.encode(entry, encoder)

    def decode(self, decoder):
        length = None

        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                length = decoder.read_length_determinant()

        if length is not None:
            pass
        elif self.number_of_bits is None:
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


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER')
        self.minimum = None
        self.maximum = None
        self.has_extension_marker = None
        self.number_of_bits = None

    def set_restricted_to_range(self, minimum, maximum, has_extension_marker):
        self.has_extension_marker = has_extension_marker

        if minimum == 'MIN' or maximum == 'MAX':
            return

        self.minimum = minimum
        self.maximum = maximum
        size = self.maximum - self.minimum
        self.number_of_bits = integer_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.has_extension_marker:
            if self.minimum <= data <= self.maximum:
                encoder.append_bit(0)
            else:
                encoder.append_bit(1)
                encoder.append_unconstrained_whole_number(data)
                return

        if self.number_of_bits is None:
            encoder.append_unconstrained_whole_number(data)
        else:
            encoder.append_non_negative_binary_integer(data - self.minimum,
                                                       self.number_of_bits)

    def decode(self, decoder):
        if self.has_extension_marker:
            if decoder.read_bit():
                return decoder.read_unconstrained_whole_number()

        if self.number_of_bits is None:
            return decoder.read_unconstrained_whole_number()
        else:
            value = decoder.read_non_negative_binary_integer(self.number_of_bits)

            return value + self.minimum

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class BitString(per.BitString):

    def encode(self, data, encoder):
        data, number_of_bits = data

        if self.has_extension_marker:
            if self.minimum <= number_of_bits <= self.maximum:
                encoder.append_bit(0)
            else:
                raise NotImplementedError(
                    'BIT STRING extension is not yet implemented.')

        if self.has_named_bits:
            data, number_of_bits = self.rstrip_zeros(data, number_of_bits)

        if self.number_of_bits is None:
            return self.encode_unbound(data, number_of_bits, encoder)
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(
                number_of_bits - self.minimum,
                self.number_of_bits)

        encoder.append_bits(data, number_of_bits)

    def decode(self, decoder):
        if self.has_extension_marker:
            if decoder.read_bit():
                raise NotImplementedError(
                    'BIT STRING extension is not yet implemented.')

        if self.number_of_bits is None:
            return self.decode_unbound(decoder)
        else:
            number_of_bits = self.minimum

            if self.minimum != self.maximum:
                number_of_bits += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)

        value = decoder.read_bits(number_of_bits)

        return (value, number_of_bits)


class OctetString(per.OctetString):

    def encode(self, data, encoder):
        if self.has_extension_marker:
            if self.minimum <= len(data) <= self.maximum:
                encoder.append_bit(0)
            else:
                encoder.append_bit(1)
                encoder.align()
                encoder.append_length_determinant(len(data))
                encoder.append_bytes(data)

                return

        if self.number_of_bits is None:
            return self.encode_unbound(data, encoder)
        elif self.minimum != self.maximum:
            encoder.append_non_negative_binary_integer(len(data) - self.minimum,
                                                       self.number_of_bits)

        encoder.append_bytes(data)

    def decode(self, decoder):
        if self.has_extension_marker:
            bit = decoder.read_bit()

            if bit:
                length = decoder.read_length_determinant()

                return decoder.read_bytes(length)

        if self.number_of_bits is None:
            return self.decode_unbound(decoder)
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_non_negative_binary_integer(
                    self.number_of_bits)

        return decoder.read_bytes(length)


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


class Choice(per.Choice):

    def encode_root_index(self, index, encoder):
        encoder.append_non_negative_binary_integer(index, self.root_number_of_bits)

    def decode_root_index(self, decoder):
        return decoder.read_non_negative_binary_integer(self.root_number_of_bits)


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


class Date(per.Date):

    def __init__(self, name):
        super(Date, self).__init__(name)
        immediate = Integer('immediate')
        near_future = Integer('near_future')
        near_past = Integer('near_past')
        reminder = Integer('reminder')
        immediate.set_restricted_to_range(2005, 2020, False)
        near_future.set_restricted_to_range(2021, 2276, False)
        near_past.set_restricted_to_range(1749, 2004, False)
        reminder.set_restricted_to_range('MIN', 1748, False)
        year = Choice('year',
                      [immediate, near_future, near_past, reminder],
                      None)
        month = Integer('month')
        day = Integer('day')
        month.set_restricted_to_range(1, 12, False)
        day.set_restricted_to_range(1, 31, False)
        self._inner = Sequence('DATE-ENCODING',
                               [year, month, day],
                               None)


class TimeOfDay(per.TimeOfDay):

    def __init__(self, name):
        super(TimeOfDay, self).__init__(name)
        hours = Integer('hours')
        minutes = Integer('minutes')
        seconds = Integer('seconds')
        hours.set_restricted_to_range(0, 24, False)
        minutes.set_restricted_to_range(0, 59, False)
        seconds.set_restricted_to_range(0, 60, False)
        self._inner = Sequence('TIME-OF-DAY-ENCODING',
                               [hours, minutes, seconds],
                               None)


class DateTime(per.DateTime):

    def __init__(self, name):
        super(DateTime, self).__init__(name)
        self._inner = Sequence('DATE-TIME-ENCODING',
                               [Date('date'), TimeOfDay('time')],
                               None)


class CompiledType(per.CompiledType):

    def encode(self, data):
        encoder = Encoder()
        self._type.encode(data, encoder)

        return encoder.as_bytearray()

    def decode(self, data):
        decoder = Decoder(bytearray(data))

        return self._type.decode(decoder)


class Compiler(per.Compiler):

    def process_type(self, type_name, type_descriptor, module_name):
        compiled_type = self.compile_type(type_name,
                                          type_descriptor,
                                          module_name)

        return CompiledType(compiled_type)

    def compile_type(self, name, type_descriptor, module_name):
        module_name = type_descriptor.get('module-name', module_name)
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
            compiled = Enumerated(name,
                                  type_descriptor['values'],
                                  self._numeric_enums)
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
        elif type_name == 'DATE':
            compiled = Date(name)
        elif type_name == 'TIME-OF-DAY':
            compiled = TimeOfDay(name)
        elif type_name == 'DATE-TIME':
            compiled = DateTime(name)
        elif type_name == 'BIT STRING':
            has_named_bits = ('named-bits' in type_descriptor)
            compiled = BitString(name,
                                 has_named_bits,
                                 *self.get_size_range(type_descriptor,
                                                      module_name))
        elif type_name == 'ANY':
            compiled = Any(name)
        elif type_name == 'ANY DEFINED BY':
            compiled = Any(name)
        elif type_name == 'NULL':
            compiled = Null(name)
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


def compile_dict(specification, numeric_enums=False):
    return Compiler(specification, numeric_enums).process()


def decode_length(_data):
    raise DecodeError('Decode length is not supported for this codec.')
