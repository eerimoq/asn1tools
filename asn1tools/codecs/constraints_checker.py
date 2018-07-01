"""Python type checker.

"""

import logging
from copy import copy

from . import ConstraintsError
from . import compiler


LOGGER = logging.getLogger(__name__)

STRING_TYPES = [
    'ENUMERATED',
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
    'UniversalString'
]


class Type(object):

    def __init__(self, name):
        self.name = name

    def set_size_range(self, minimum, maximum, has_extension_marker):
        pass

    def set_restricted_to_range(self, minimum, maximum, has_extension_marker):
        pass

    def encode(self, data):
        raise NotImplementedError


class Boolean(Type):

    def encode(self, data):
        raise NotImplementedError


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name)
        self.minimum = None
        self.maximum = None

    def set_restricted_to_range(self,
                                minimum,
                                maximum,
                                _has_extension_marker):
        self.minimum = minimum
        self.maximum = maximum

    def encode(self, data):
        if self.minimum is None:
            return

        if data < self.minimum or data > self.maximum:
            raise ConstraintsError(
                'Expected an integer between {} and {}, but got {}.'.format(
                    self.minimum,
                    self.maximum,
                    data))


class Float(Type):

    def encode(self, data):
        raise NotImplementedError


class Null(Type):

    def encode(self, data):
        raise NotImplementedError


class BitString(Type):

    def encode(self, data):
        raise NotImplementedError


class Bytes(Type):

    def encode(self, data):
        raise NotImplementedError


class String(Type):

    def encode(self, data):
        raise NotImplementedError


class Dict(Type):

    def __init__(self, name, members):
        super(Dict, self).__init__(name)
        self.members = members

    def encode(self, data):
        for member in self.members:
            name = member.name

            if name in data:
                try:
                    member.encode(data[name])
                except ConstraintsError as e:
                    e.location.append(member.name)
                    raise


class List(Type):

    def __init__(self, name, element_type):
        super(List, self).__init__(name)
        self.element_type = element_type

    def encode(self, data):
        for entry in data:
            self.element_type.encode(entry)


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name)
        self.members = members

    def encode(self, data):
        raise NotImplementedError


class Time(Type):

    def encode(self, data):
        raise NotImplementedError


class Skip(Type):

    def encode(self, data):
        raise NotImplementedError


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
            members = self.compile_members(type_descriptor['members'],
                                           module_name)
            compiled = Dict(name, members)
        elif type_name in ['SEQUENCE OF', 'SET OF']:
            element_type = self.compile_type('',
                                             type_descriptor['element'],
                                             module_name)
            compiled = List(name, element_type)
        elif type_name == 'CHOICE':
            members = self.compile_members(type_descriptor['members'],
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
        elif type_name in ['UTCTime', 'GeneralizedTime']:
            compiled = Time(name)
        elif type_name == 'BIT STRING':
            compiled = BitString(name)
        elif type_name in STRING_TYPES:
            compiled = String(name)
        elif type_name in ['ANY', 'ANY DEFINED BY', 'OpenType']:
            compiled = Skip(name)
        elif type_name == 'NULL':
            compiled = Null(name)
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

        if 'restricted-to' in type_descriptor:
            compiled = self.set_compiled_restricted_to(compiled,
                                                       type_descriptor,
                                                       module_name)

        return compiled


def compile_dict(specification):
    return Compiler(specification).process()
