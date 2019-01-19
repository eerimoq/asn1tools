"""ASN.1 constraints checker.

"""

import string
from copy import copy

from . import ConstraintsError
from . import compiler
from . import format_or
from .permitted_alphabet import NUMERIC_STRING
from .permitted_alphabet import PRINTABLE_STRING
from .permitted_alphabet import IA5_STRING
from .permitted_alphabet import VISIBLE_STRING


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

TIME_TYPES = [
    'UTCTime',
    'GeneralizedTime',
    'DATE',
    'TIME-OF-DAY',
    'DATE-TIME'
]


class Type(object):

    def __init__(self, name):
        self.name = name
        self.minimum = 'MIN'
        self.maximum = 'MAX'

    def set_range(self, minimum, maximum, has_extension_marker):
        if has_extension_marker:
            return

        if minimum is None:
            minimum = 'MIN'

        if maximum is None:
            maximum = 'MAX'

        self.minimum = minimum
        self.maximum = maximum

    def set_size_range(self, minimum, maximum, has_extension_marker):
        self.set_range(minimum, maximum, has_extension_marker)

    def set_restricted_to_range(self,
                                minimum,
                                maximum,
                                has_extension_marker):
        self.set_range(minimum, maximum, has_extension_marker)

    def is_in_range(self, value):
        minimum_ok = (not self.has_lower_bound()) or (value >= self.minimum)
        maximum_ok = (not self.has_upper_bound()) or (value <= self.maximum)

        return minimum_ok and maximum_ok

    def set_default(self, value):
        pass

    def has_lower_bound(self):
        return self.minimum != 'MIN'

    def has_upper_bound(self):
        return self.maximum != 'MAX'

    def is_bound(self):
        return self.has_lower_bound() and self.has_upper_bound()

    def encode(self, data):
        raise NotImplementedError('To be implemented by subclasses.')


class String(Type):

    PERMITTED_ALPHABET = None

    def __init__(self,
                 name,
                 permitted_alphabet,
                 minimum,
                 maximum,
                 has_extension_marker):
        super(String, self).__init__(name)
        self.set_size_range(minimum, maximum, has_extension_marker)

        if permitted_alphabet is None:
            permitted_alphabet = self.PERMITTED_ALPHABET

        self.permitted_alphabet = permitted_alphabet

    def encode(self, data):
        length = len(data)

        if not self.is_in_range(length):
            raise ConstraintsError(
                'Expected between {} and {} characters, but got {}.'.format(
                    self.minimum,
                    self.maximum,
                    length))

        if self.permitted_alphabet is None:
            return

        for character in data:
            if character not in self.permitted_alphabet:
                raise ConstraintsError(
                    "Expected a character in '{}', but got '{}' (0x{:02x}).".format(
                        ''.join([c if c in string.printable[:-5] else '.'
                                 for c in self.permitted_alphabet]),
                        character if character in string.printable else '.',
                        ord(character)))


class Boolean(Type):

    def encode(self, data):
        pass


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name)

    def encode(self, data):
        if not self.is_in_range(data):
            raise ConstraintsError(
                'Expected an integer between {} and {}, but got {}.'.format(
                    self.minimum,
                    self.maximum,
                    data))


class Float(Type):

    def encode(self, data):
        pass


class Null(Type):

    def encode(self, data):
        pass


class BitString(Type):

    def __init__(self, name, minimum, maximum, has_extension_marker):
        super(BitString, self).__init__(name)
        self.set_size_range(minimum, maximum, has_extension_marker)

    def encode(self, data):
        number_of_bits = data[1]

        if not self.is_in_range(number_of_bits):
            raise ConstraintsError(
                'Expected between {} and {} bits, but got {}.'.format(
                    self.minimum,
                    self.maximum,
                    number_of_bits))


class Enumerated(Type):

    def encode(self, data):
        pass


class Bytes(Type):

    def __init__(self, name, minimum, maximum, has_extension_marker):
        super(Bytes, self).__init__(name)
        self.set_size_range(minimum, maximum, has_extension_marker)

    def encode(self, data):
        length = len(data)

        if not self.is_in_range(length):
            raise ConstraintsError(
                'Expected between {} and {} bytes, but got {}.'.format(
                    self.minimum,
                    self.maximum,
                    length))


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

    def __init__(self, name, element_type, minimum, maximum, has_extension_marker):
        super(List, self).__init__(name)
        self.element_type = element_type
        self.set_size_range(minimum, maximum, has_extension_marker)

    def encode(self, data):
        length = len(data)

        if not self.is_in_range(length):
            raise ConstraintsError(
                'Expected a list of between {} and {} elements, but got {}.'.format(
                    self.minimum,
                    self.maximum,
                    length))

        for entry in data:
            self.element_type.encode(entry)


class Choice(Type):

    def __init__(self, name, members, has_extension_marker):
        super(Choice, self).__init__(name)
        self.members = members
        self.name_to_member = {member.name: member for member in self.members}
        self.has_extension_marker = has_extension_marker

    def format_names(self):
        return format_or(sorted(self.name_to_member))

    def encode(self, data):
        value = data[0]

        if value in self.name_to_member:
            member = self.name_to_member[value]
        elif self.has_extension_marker:
            return
        else:
            raise ConstraintsError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    value))

        try:
            member.encode(data[1])
        except ConstraintsError as e:
            e.location.append(member.name)
            raise


class NumericString(String):

    PERMITTED_ALPHABET = NUMERIC_STRING


class PrintableString(String):

    PERMITTED_ALPHABET = PRINTABLE_STRING


class IA5String(String):

    PERMITTED_ALPHABET = IA5_STRING


class VisibleString(String):

    PERMITTED_ALPHABET = VISIBLE_STRING


class Time(Type):

    def encode(self, data):
        pass


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
        module_name = type_descriptor.get('module-name', module_name)
        type_name = type_descriptor['type']

        if type_name in ['SEQUENCE', 'SET']:
            members, _ = self.compile_members(type_descriptor['members'],
                                              module_name)
            compiled = Dict(name, members)
        elif type_name in ['SEQUENCE OF', 'SET OF']:
            element_type = self.compile_type('',
                                             type_descriptor['element'],
                                             module_name)
            compiled = List(name,
                            element_type,
                            *self.get_size_range(
                                type_descriptor,
                                module_name))
        elif type_name == 'CHOICE':
            compiled = Choice(name,
                              *self.compile_members(type_descriptor['members'],
                                                    module_name))
        elif type_name == 'INTEGER':
            compiled = Integer(name)
        elif type_name == 'REAL':
            compiled = Float(name)
        elif type_name == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_name == 'OCTET STRING':
            compiled = Bytes(name,
                             *self.get_size_range(type_descriptor,
                                                  module_name))
        elif type_name == 'ENUMERATED':
            compiled = Enumerated(name)
        elif type_name in TIME_TYPES:
            compiled = Time(name)
        elif type_name == 'BIT STRING':
            compiled = BitString(name,
                                 *self.get_size_range(type_descriptor,
                                                      module_name))
        elif type_name == 'NumericString':
            compiled = NumericString(name,
                                     self.get_permitted_alphabet(type_descriptor),
                                     *self.get_size_range(type_descriptor,
                                                          module_name))
        elif type_name == 'PrintableString':
            compiled = PrintableString(name,
                                       self.get_permitted_alphabet(type_descriptor),
                                       *self.get_size_range(type_descriptor,
                                                            module_name))
        elif type_name == 'IA5String':
            compiled = IA5String(name,
                                 self.get_permitted_alphabet(type_descriptor),
                                 *self.get_size_range(type_descriptor,
                                                      module_name))
        elif type_name == 'VisibleString':
            compiled = VisibleString(name,
                                     self.get_permitted_alphabet(type_descriptor),
                                     *self.get_size_range(type_descriptor,
                                                          module_name))
        elif type_name in STRING_TYPES:
            compiled = String(name,
                              self.get_permitted_alphabet(type_descriptor),
                              *self.get_size_range(type_descriptor,
                                                   module_name))
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

        if 'restricted-to' in type_descriptor:
            compiled = self.set_compiled_restricted_to(compiled,
                                                       type_descriptor,
                                                       module_name)

        return compiled

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

        return ''.join(sorted(value))


def compile_dict(specification, numeric_enums=False):
    return Compiler(specification, numeric_enums).process()
