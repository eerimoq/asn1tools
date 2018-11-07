"""Python type checker.

"""

import sys
import datetime
from copy import copy

from . import EncodeError
from . import compiler
from . import format_or


STRING_TYPES = [
    'OBJECT IDENTIFIER',
    'TeletexString',
    'NumericString',
    'PrintableString',
    'IA5String',
    'VisibleString',
    'GeneralString',
    'UTF8String',
    'BMPString',
    'GraphicString',
    'UniversalString',
    'ObjectDescriptor'
]


class Type(object):

    TYPE = None

    def __init__(self, name):
        self.name = name

    def set_size_range(self, minimum, maximum, has_extension_marker):
        pass

    def encode(self, data):
        if not isinstance(data, self.TYPE):
            raise EncodeError(
                'Expected data of type {}, but got {}.'.format(self.TYPE.__name__,
                                                               data))


class Boolean(Type):

    TYPE = bool


class Integer(Type):

    def encode(self, data):
        if sys.version_info[0] > 2:
            if not isinstance(data, (int, str)):
                raise EncodeError(
                    'Expected data of type int or str, but got {}.'.format(
                        data))
        else:
            if not isinstance(data, (int, long, str, unicode)):
                raise EncodeError(
                    'Expected data of type int or str, but got {}.'.format(
                        data))


class Float(Type):

    def encode(self, data):
        if sys.version_info[0] > 2:
            if not isinstance(data, (float, int)):
                raise EncodeError(
                    'Expected data of type float or int, but got {}.'.format(
                        data))
        else:
            if not isinstance(data, (float, int, long)):
                raise EncodeError(
                    'Expected data of type float or int, but got {}.'.format(
                        data))


class Null(Type):

    def encode(self, data):
        if data is not None:
            raise EncodeError('Expected None, but got {}.'.format(data))


class BitString(Type):

    def encode(self, data):
        if (not isinstance(data, tuple)
            or len(data) != 2
            or not isinstance(data[0], (bytes, bytearray))
            or not isinstance(data[1], int)):
            raise EncodeError(
                'Expected data of type tuple(bytes, int), but got {}.'.format(
                    data))

        if 8 * len(data[0]) < data[1]:
            raise EncodeError(
                'Expected at least {} bit(s) data, but got {}.'.format(
                    data[1],
                    8 * len(data[0])))


class Bytes(Type):

    def encode(self, data):
        if not isinstance(data, (bytes, bytearray)):
            raise EncodeError(
                'Expected data of type bytes or bytearray, but got {}.'.format(
                    data))


class String(Type):

    def encode(self, data):
        if sys.version_info[0] > 2:
            if not isinstance(data, str):
                raise EncodeError(
                    'Expected data of type str, but got {}.'.format(data))
        else:
            if not isinstance(data, (str, unicode)):
                raise EncodeError(
                    'Expected data of type str, but got {}.'.format(data))


class Dict(Type):

    TYPE = dict

    def __init__(self, name, members):
        super(Dict, self).__init__(name)
        self.members = members

    def encode(self, data):
        super(Dict, self).encode(data)

        for member in self.members:
            name = member.name

            if name in data:
                try:
                    member.encode(data[name])
                except EncodeError as e:
                    e.location.append(member.name)
                    raise


class List(Type):

    TYPE = list

    def __init__(self, name, element_type):
        super(List, self).__init__(name)
        self.element_type = element_type

    def encode(self, data):
        super(List, self).encode(data)

        for entry in data:
            self.element_type.encode(entry)


class Enumerated(Type):

    def __init__(self, name, numeric_enums):
        super(Enumerated, self).__init__(name)
        self._numeric_enums = numeric_enums

    def encode(self, data):
        if self._numeric_enums:
            self.encode_integer(data)
        else:
            self.encode_string(data)

    def encode_integer(self, data):
        if sys.version_info[0] > 2:
            if not isinstance(data, int):
                raise EncodeError(
                    'Expected data of type int, but got {}.'.format(
                        data))
        else:
            if not isinstance(data, (int, long)):
                raise EncodeError(
                    'Expected data of type int, but got {}.'.format(
                        data))

    def encode_string(self, data):
        if sys.version_info[0] > 2:
            if not isinstance(data, str):
                raise EncodeError(
                    'Expected data of type str, but got {}.'.format(data))
        else:
            if not isinstance(data, (str, unicode)):
                raise EncodeError(
                    'Expected data of type str, but got {}.'.format(data))


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name)
        self.members = members
        self.name_to_member = {member.name: member for member in self.members}

    def format_names(self):
        return format_or(sorted([member.name for member in self.members]))

    def encode(self, data):
        if sys.version_info[0] > 2:
            if (not isinstance(data, tuple)
                or len(data) != 2
                or not isinstance(data[0], str)):
                raise EncodeError(
                    'Expected data of type tuple(str, object), but got {}.'.format(
                        data))
        else:
            if (not isinstance(data, tuple)
                or len(data) != 2
                or not isinstance(data[0], (str, unicode))):
                raise EncodeError(
                    'Expected data of type tuple(str, object), but got {}.'.format(
                        data))

        try:
            member = self.name_to_member[data[0]]
        except KeyError:
            raise EncodeError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    data[0]))

        try:
            member.encode(data[1])
        except EncodeError as e:
            e.location.append(member.name)
            raise


class Date(Type):

    def encode(self, data):
        if not isinstance(data, datetime.date):
            raise EncodeError(
                'Expected data of type datetime.date, but got {}.'.format(
                    data))


class TimeOfDay(Type):

    def encode(self, data):
        if not isinstance(data, datetime.time):
            raise EncodeError(
                'Expected data of type datetime.time, but got {}.'.format(
                    data))


class DateTime(Type):

    def encode(self, data):
        if not isinstance(data, datetime.datetime):
            raise EncodeError(
                'Expected data of type datetime.datetime, but got {}.'.format(
                    data))


class Skip(Type):

    def encode(self, data):
        pass


class Recursive(Type, compiler.Recursive):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name)
        self.type_name = type_name
        self.module_name = module_name
        self.inner = None

    def set_inner_type(self, inner):
        self.inner = copy(inner)

    def encode(self, data):
        self.inner.encode(data)


class CompiledType(compiler.CompiledType):

    def __init__(self, type_):
        super(CompiledType, self).__init__()
        self._type = type_

    @property
    def type(self):
        return self._type

    def encode(self, data):
        self._type.encode(data)


class Compiler(compiler.Compiler):

    def process_type(self, type_name, type_descriptor, module_name):
        compiled_type = self.compile_type(type_name,
                                          type_descriptor,
                                          module_name)

        return CompiledType(compiled_type)

    def compile_type(self, name, type_descriptor, module_name):
        type_name = type_descriptor['type']

        if type_name in ['SEQUENCE', 'SET']:
            members, _ = self.compile_members(type_descriptor['members'],
                                              module_name)
            compiled = Dict(name, members)
        elif type_name in ['SEQUENCE OF', 'SET OF']:
            element_type = self.compile_type('',
                                             type_descriptor['element'],
                                             module_name)
            compiled = List(name, element_type)
        elif type_name == 'CHOICE':
            members, _ = self.compile_members(type_descriptor['members'],
                                              module_name)
            compiled = Choice(name, members)
        elif type_name == 'INTEGER':
            compiled = Integer(name)
        elif type_name == 'REAL':
            compiled = Float(name)
        elif type_name == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_name == 'OCTET STRING':
            compiled = Bytes(name)
        elif type_name in ['UTCTime', 'GeneralizedTime', 'DATE-TIME']:
            compiled = DateTime(name)
        elif type_name == 'TIME-OF-DAY':
            compiled = TimeOfDay(name)
        elif type_name == 'DATE':
            compiled = Date(name)
        elif type_name == 'BIT STRING':
            compiled = BitString(name)
        elif type_name in STRING_TYPES:
            compiled = String(name)
        elif type_name == 'ENUMERATED':
            compiled = Enumerated(name, self._numeric_enums)
        elif type_name in ['ANY', 'ANY DEFINED BY', 'OpenType']:
            compiled = Skip(name)
        elif type_name == 'NULL':
            compiled = Null(name)
        elif type_name == 'EXTERNAL':
            members, _ = self.compile_members(
                self.external_type_descriptor()['members'],
                module_name)
            compiled = Dict(name, members)
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
