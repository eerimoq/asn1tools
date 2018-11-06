"""Distinguished Encoding Rules (DER) codec.

"""

from . import DecodeTagError
from . import ber
from . import restricted_utc_time_to_datetime
from . import restricted_utc_time_from_datetime
from . import restricted_generalized_time_to_datetime
from . import restricted_generalized_time_from_datetime
from .compiler import clean_bit_string_value
from .ber import Class
from .ber import Encoding
from .ber import Tag
from .ber import encode_length_definite
from .ber import decode_length_definite
from .ber import encode_signed_integer
from .ber import decode_signed_integer
from .ber import encode_tag
from .ber import Boolean
from .ber import Real
from .ber import Null
from .ber import ObjectIdentifier
from .ber import Enumerated
from .ber import Sequence
from .ber import Set
from .ber import Choice
from .ber import Any
from .ber import AnyDefinedBy
from .ber import Recursive
from .ber import ObjectDescriptor
from .ber import Date
from .ber import TimeOfDay
from .ber import DateTime
from .ber import decode_length
from .ber import encode_real
from .ber import decode_real


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

    def decode_tag(self, data, offset):
        end_offset = offset + len(self.tag)

        if data[offset:end_offset] != self.tag:
            raise DecodeTagError(self.type_name,
                                 self.tag,
                                 data[offset:end_offset],
                                 offset)

        return end_offset

    def is_default(self, value):
        return value == self.default


class StringType(Type):

    TAG = None
    ENCODING = None

    def __init__(self, name):
        super(StringType, self).__init__(name,
                                         self.__class__.__name__,
                                         self.TAG)

    def encode(self, data, encoded):
        data = data.encode(self.ENCODING)
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode(self.ENCODING), end_offset

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)


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


class BitString(Type):

    def __init__(self, name, has_named_bits):
        super(BitString, self).__init__(name,
                                        'BIT STRING',
                                        Tag.BIT_STRING)
        self.has_named_bits = has_named_bits

    def is_default(self, value):
        if self.default is None:
            return False

        clean_value = clean_bit_string_value(value,
                                             self.has_named_bits)
        clean_default = clean_bit_string_value(self.default,
                                               self.has_named_bits)

        return clean_value == clean_default

    def encode(self, data, encoded):
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

        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data) + 1))
        encoded.append(number_of_unused_bits)
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length
        number_of_bits = 8 * (length - 1) - data[offset]
        offset += 1

        return (bytes(data[offset:end_offset]), number_of_bits), end_offset

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name,
                                          'OCTET STRING',
                                          Tag.OCTET_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return bytes(data[offset:end_offset]), end_offset

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


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


class UTF8String(StringType):

    TAG = Tag.UTF8_STRING
    ENCODING = 'utf-8'


class NumericString(StringType):

    TAG = Tag.NUMERIC_STRING
    ENCODING = 'ascii'


class PrintableString(StringType):

    TAG = Tag.PRINTABLE_STRING
    ENCODING = 'ascii'


class IA5String(StringType):

    TAG = Tag.IA5_STRING
    ENCODING = 'ascii'


class VisibleString(StringType):

    TAG = Tag.VISIBLE_STRING
    ENCODING = 'ascii'


class GeneralString(StringType):

    TAG = Tag.GENERAL_STRING
    ENCODING = 'latin-1'


class BMPString(StringType):

    TAG = Tag.BMP_STRING
    ENCODING = 'utf-16-be'


class UniversalString(StringType):

    TAG = Tag.UNIVERSAL_STRING
    ENCODING = 'utf-32-be'


class GraphicString(StringType):

    TAG = Tag.GRAPHIC_STRING
    ENCODING = 'latin-1'


class TeletexString(StringType):

    TAG = Tag.T61_STRING
    ENCODING = 'iso-8859-1'


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name,
                                      'UTCTime',
                                      Tag.UTC_TIME)

    def encode(self, data, encoded):
        data = restricted_utc_time_from_datetime(data).encode('ascii')
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length
        decoded = data[offset:end_offset].decode('ascii')

        return restricted_utc_time_to_datetime(decoded), end_offset

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name,
                                              'GeneralizedTime',
                                              Tag.GENERALIZED_TIME)

    def encode(self, data, encoded):
        data = restricted_generalized_time_from_datetime(data).encode('ascii')
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length
        decoded = data[offset:end_offset].decode('ascii')

        return restricted_generalized_time_to_datetime(decoded), end_offset

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class Compiler(ber.Compiler):

    def compile_implicit_type(self, name, type_descriptor, module_name):
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
                                                    module_name))
        elif type_name == 'SET':
            compiled = Set(
                name,
                *self.compile_members(type_descriptor['members'],
                                      module_name))
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
        elif type_name == 'GraphicString':
            compiled = GraphicString(name)
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
            compiled = BitString(name, has_named_bits)
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

        return compiled


def compile_dict(specification, numeric_enums=False):
    return Compiler(specification, numeric_enums).process()
