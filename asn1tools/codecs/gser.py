"""General String Encoding Rules (GSER).

"""

import time
import binascii
import math
from copy import copy
import datetime

from . import EncodeError
from . import DecodeError
from . import compiler
from . import format_or
from . import utc_time_from_datetime
from . import generalized_time_from_datetime
from .compiler import enum_values_as_dict


class Type(object):

    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
        self.optional = False
        self.default = None

    def set_size_range(self, minimum, maximum, has_extension_marker):
        pass


class MembersType(Type):

    def __init__(self, name, members, type_name):
        super(MembersType, self).__init__(name, type_name)
        self.members = members

    def encode(self, data, separator, indent):
        encoded_members = []
        member_separator = separator + ' ' * indent

        for member in self.members:
            name = member.name

            if name in data:
                try:
                    encoded_member = member.encode(data[name],
                                                   member_separator,
                                                   indent)
                except EncodeError as e:
                    e.location.append(member.name)
                    raise

                encoded_member = u'{}{} {}'.format(member_separator,
                                                   member.name,
                                                   encoded_member)
                encoded_members.append(encoded_member)
            elif member.optional:
                pass
            elif member.default is None:
                raise EncodeError(
                    "{} member '{}' not found in {}.".format(
                        self.__class__.__name__,
                        name,
                        data))

        encoded_members = ','.join(encoded_members)

        return separator.join(['{' + encoded_members, '}'])

    def __repr__(self):
        return '{}({}, [{}])'.format(
            self.__class__.__name__,
            self.name,
            ', '.join([repr(member) for member in self.members]))


class ArrayType(Type):

    def __init__(self, name, type_name, element_type):
        super(ArrayType, self).__init__(name, type_name)
        self.element_type = element_type

    def encode(self, data, separator, indent):
        encoded_elements = []
        element_separator = separator + ' ' * indent

        for entry in data:
            encoded_element = self.element_type.encode(entry,
                                                       element_separator,
                                                       indent)
            encoded_element = u'{}{}'.format(element_separator,
                                             encoded_element)
            encoded_elements.append(encoded_element)

        encoded_elements = ','.join(encoded_elements)

        return separator.join(['{' + encoded_elements, '}'])

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.name,
                                   self.element_type)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN')

    def encode(self, data, _separator, _indent):
        return 'TRUE' if data else 'FALSE'

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER')

    def encode(self, data, _separator, _indent):
        return str(data)

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Real(Type):

    def __init__(self, name):
        super(Real, self).__init__(name, 'REAL')

    def encode(self, data, _separator, _indent):
        if data == float('inf'):
            data = 'PLUS-INFINITY'
        elif data == float('-inf'):
            data = 'MINUS-INFINITY'
        elif math.isnan(data):
            raise EncodeError('Cannot encode floating point number NaN.')
        elif data == 0.0:
            data = '0'
        else:
            data = '{}E0'.format(data)

        return data

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL')

    def encode(self, _data, _separator, _indent):
        return 'NULL'

    def __repr__(self):
        return 'Null({})'.format(self.name)


class BitString(Type):

    def __init__(self, name):
        super(BitString, self).__init__(name, 'BIT STRING')

    def encode(self, data, _separator, _indent):
        encoded = int(binascii.hexlify(data[0]), 16)
        encoded |= (0x80 << (8 * len(data[0])))

        return "'{}'B".format(bin(encoded)[10:10 + data[1]]).upper()

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name, 'OCTET STRING')

    def encode(self, data, _separator, _indent):
        return "'{}'H".format(binascii.hexlify(data).decode('ascii')).upper()

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, data, _separator, _indent):
        return data

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values, numeric):
        super(Enumerated, self).__init__(name, 'ENUMERATED')

        if numeric:
            self.data_to_value = enum_values_as_dict(values)
        else:
            self.data_to_value = {
                v: v for v in enum_values_as_dict(values).values()
            }

    def encode(self, data, _separator, _indent):
        return self.data_to_value[data]

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class Sequence(MembersType):

    def __init__(self, name, members):
        super(Sequence, self).__init__(name, members, 'SEQUENCE')


class SequenceOf(ArrayType):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name,
                                         'SEQUENCE OF',
                                         element_type)


class Set(MembersType):

    def __init__(self, name, members):
        super(Set, self).__init__(name, members, 'SET')


class SetOf(ArrayType):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name,
                                    'SET OF',
                                    element_type)


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name, 'CHOICE')
        self.members = members
        self.name_to_member = {member.name: member for member in self.members}

    def format_names(self):
        return format_or(sorted([member.name for member in self.members]))

    def encode(self, data, separator, indent):
        try:
            member = self.name_to_member[data[0]]
        except KeyError:
            raise EncodeError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    data[0]))

        try:
            encoded = member.encode(data[1], separator, indent)
        except EncodeError as e:
            e.location.append(member.name)
            raise

        return u'{} : {}'.format(data[0], encoded)

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name, 'UTF8String')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name, 'NumericString')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name, 'PrintableString')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name):
        super(IA5String, self).__init__(name, 'IA5String')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name):
        super(VisibleString, self).__init__(name, 'VisibleString')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class GeneralString(Type):

    def __init__(self, name):
        super(GeneralString, self).__init__(name, 'GeneralString')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'GeneralString({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name, 'BMPString')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class GraphicString(Type):

    def __init__(self, name):
        super(GraphicString, self).__init__(name, 'GraphicString')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'GraphicString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name, 'UniversalString')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(data)

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class ObjectDescriptor(GraphicString):

    def __repr__(self):
        return 'ObjectDescriptor({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name, 'UTCTime')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(utc_time_from_datetime(data))

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name, 'GeneralizedTime')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(generalized_time_from_datetime(data))

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class Date(Type):

    def __init__(self, name):
        super(Date, self).__init__(name, 'DATE')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(str(data))


class TimeOfDay(Type):

    def __init__(self, name):
        super(TimeOfDay, self).__init__(name, 'TIME-OF-DAY')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(str(data))


class DateTime(Type):

    def __init__(self, name):
        super(DateTime, self).__init__(name, 'DATE-TIME')

    def encode(self, data, _separator, _indent):
        return u'"{}"'.format(str(data).replace(' ', 'T'))


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY')

    def encode(self, data, _separator, _indent):
        data = binascii.hexlify(data).decode('ascii').upper()

        return "'{}'H".format(data)

    def __repr__(self):
        return 'Any({})'.format(self.name)


class Recursive(Type, compiler.Recursive):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name, 'RECURSIVE')
        self.type_name = type_name
        self.module_name = module_name
        self.inner = None

    def set_inner_type(self, inner):
        self.inner = copy(inner)

    def encode(self, data, separator, indent):
        return self.inner.encode(data, separator, indent)

    def __repr__(self):
        return 'Recursive({})'.format(self.type_name)


class CompiledType(compiler.CompiledType):

    def __init__(self, type_name, compiled_type):
        super(CompiledType, self).__init__()
        self._value_name = type_name.lower()
        self._value_type = type_name
        self._type = compiled_type

    @property
    def type(self):
        return self._type

    def encode(self, data, indent=None):
        if indent is None:
            encoded = self._type.encode(data, ' ', 0)
        else:
            encoded = self._type.encode(data, '\n', indent)

        encoded = u'{} {} ::= {}'.format(self._value_name,
                                         self._value_type,
                                         encoded.lstrip(' '))

        return encoded.encode('utf-8')

    def decode(self, data):
        raise NotImplementedError('GSER decoding is not implemented.')

    def __repr__(self):
        return repr(self._type)


class Compiler(compiler.Compiler):

    def process_type(self, type_name, type_descriptor, module_name):
        compiled_type = self.compile_type(type_name,
                                          type_descriptor,
                                          module_name)

        return CompiledType(type_name, compiled_type)

    def compile_type(self, name, type_descriptor, module_name):
        type_name = type_descriptor['type']

        if type_name == 'SEQUENCE':
            members, _ = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Sequence(name, members)
        elif type_name == 'SEQUENCE OF':
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name))
        elif type_name == 'SET':
            members, _ = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Set(name, members)
        elif type_name == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_name == 'CHOICE':
            members, _ = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Choice(name, members)
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
            compiled = BitString(name)
        elif type_name == 'ANY':
            compiled = Any(name)
        elif type_name == 'ANY DEFINED BY':
            compiled = Any(name)
        elif type_name == 'NULL':
            compiled = Null(name)
        elif type_name == 'EXTERNAL':
            members, _ = self.compile_members(
                self.external_type_descriptor()['members'],
                module_name)
            compiled = Sequence(name, members)
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


def decode_length(_data):
    raise DecodeError('Decode length is not supported for this codec.')
