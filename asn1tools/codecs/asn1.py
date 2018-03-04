"""Basic ASN.1 notation codec.

"""

import binascii
import logging

from . import EncodeError
from . import DecodeError
from . import compiler
from .compiler import enum_values_as_dict


LOGGER = logging.getLogger(__name__)


class Type(object):

    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
        self.optional = False
        self.default = None


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER')

    def encode(self, data, _separator, _indent):
        return str(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Real(Type):

    def __init__(self, name):
        super(Real, self).__init__(name, 'REAL')

    def encode(self, data, separator, indent):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN')

    def encode(self, data, separator, indent):
        return 'TRUE' if data else 'FALSE'

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name):
        super(IA5String, self).__init__(name, 'IA5String')

    def encode(self, data, _separator, _indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name, 'NumericString')

    def encode(self, data, _separator, _indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class Sequence(Type):

    def __init__(self, name, members):
        super(Sequence, self).__init__(name, 'SEQUENCE')
        self.members = members

    def encode(self, data, separator, indent):
        encoded_members = []
        member_separator = separator + ' ' * indent

        for member in self.members:
            name = member.name

            if name in data:
                encoded_member = member.encode(data[name],
                                               member_separator,
                                               indent)
                encoded_member = '{}{} {}'.format(member_separator,
                                                  member.name,
                                                  encoded_member)
                encoded_members.append(encoded_member)
            elif member.optional:
                pass
            elif member.default is None:
                raise EncodeError(
                    "member '{}' not found in {}".format(
                        name,
                        data))

        encoded_members = ','.join(encoded_members)

        return separator.join(['{' + encoded_members, '}'])

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Set(Type):

    def __init__(self, name, members):
        super(Set, self).__init__(name, 'SET')
        self.members = members

    def encode(self, data, separator, indent):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Set({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class SequenceOf(Type):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name, 'SEQUENCE OF')
        self.element_type = element_type

    def encode(self, data, separator, indent):
        encoded_members = []
        member_separator = separator + ' ' * indent

        for entry in data:
            encoded_member = self.element_type.encode(entry,
                                                      member_separator,
                                                      indent)
            encoded_member = '{}{}'.format(member_separator,
                                           encoded_member)
            encoded_members.append(encoded_member)

        encoded_members = ','.join(encoded_members)

        return separator.join(['{' + encoded_members, '}'])

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'SequenceOf({}, {})'.format(self.name,
                                           self.element_type)


class SetOf(Type):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name, 'SET OF')
        self.element_type = element_type

    def encode(self, data, separator, indent):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'SetOf({}, {})'.format(self.name,
                                      self.element_type)


class BitString(Type):

    def __init__(self, name):
        super(BitString, self).__init__(name, 'BIT STRING')

    def encode(self, data, _separator, _indent):
        encoded = int(binascii.hexlify(data[0]), 16)
        encoded |= (0x80 << (8 * len(data[0])))

        return "'{}'B".format(bin(encoded)[10:10 + data[1]]).upper()

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name, 'OCTET STRING')

    def encode(self, data, _separator, _indent):
        return "'{}'H".format(binascii.hexlify(data).decode('ascii')).upper()

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name, 'PrintableString')

    def encode(self, data, _separator, _indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name, 'UniversalString')

    def encode(self, data, _separator, _indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name):
        super(VisibleString, self).__init__(name, 'VisibleString')

    def encode(self, data, _separator, _indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class GeneralString(Type):

    def __init__(self, name):
        super(GeneralString, self).__init__(name, 'GeneralString')

    def encode(self, data, separator, indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'GeneralString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name, 'UTF8String')

    def encode(self, data, _separator, _indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name, 'BMPString')

    def encode(self, data, separator, indent):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name, 'UTCTime')

    def encode(self, data, _separator, _indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name, 'GeneralizedTime')

    def encode(self, data, _separator, _indent):
        return '"{}"'.format(data)

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, data, separator, indent):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, data, separator, indent):
        return data

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name, 'CHOICE')
        self.members = members

    def encode(self, data, separator, indent):
        for member in self.members:
            if member.name == data[0]:
                encoded = '{} : {}'.format(data[0],
                                           member.encode(data[1],
                                                         separator,
                                                         indent))

                return encoded

        raise EncodeError(
            "expected choices are {}, but got '{}'".format(
                [member.name for member in self.members],
                data[0]))

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL')

    def encode(self, _data, _separator, _indent):
        return 'NULL'

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Null({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY')

    def encode(self, _, encoder):
        raise NotImplementedError

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Any({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name, 'ENUMERATED')
        self.values = enum_values_as_dict(values)

    def encode(self, data, separator, indent):
        return data

    def decode(self, data):
        raise NotImplementedError

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class Recursive(Type):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name, 'RECURSIVE')

    def encode(self, data, separator, indent):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def decode(self, data):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def __repr__(self):
        return 'Recursive({})'.format(self.name)


class CompiledType(object):

    def __init__(self, type_name, type_):
        type_.name = ''
        self._value_name = type_name.lower()
        self._value_type = type_name
        self._type = type_

    def encode(self, data, indent=None):
        if indent is None:
            encoded = self._type.encode(data, ' ', 0)
        else:
            encoded = self._type.encode(data, '\n', indent)

        encoded = '{} {} ::= {}'.format(self._value_name,
                                        self._value_type,
                                        encoded.lstrip(' '))

        return encoded.encode('utf-8')

    def decode(self, data):
        return self._type.decode(data)

    def __repr__(self):
        return repr(self._type)


class Compiler(compiler.Compiler):

    def process_type(self, type_name, type_descriptor, module_name):
        return CompiledType(type_name,
                            self.compile_type(type_name,
                                              type_descriptor,
                                              module_name))

    def compile_type(self, name, type_descriptor, module_name):
        type_name = type_descriptor['type']

        if type_name == 'SEQUENCE':
            members = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Sequence(name, members)
        elif type_name == 'SEQUENCE OF':
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name))
        elif type_name == 'SET':
            members = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Set(name, members)
        elif type_name == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_name == 'CHOICE':
            members = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Choice(name, members)
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
        elif type_name == 'UTCTime':
            compiled = UTCTime(name)
        elif type_name == 'UniversalString':
            compiled = UniversalString(name)
        elif type_name == 'GeneralizedTime':
            compiled = GeneralizedTime(name)
        elif type_name == 'BIT STRING':
            compiled = BitString(name)
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

        return compiled

    def compile_members(self, members, module_name):
        compiled_members = []

        for member in members:
            if member == '...':
                continue

            if isinstance(member, list):
                compiled_members.extend(self.compile_members(member,
                                                             module_name))
                continue

            compiled_member = self.compile_type(member['name'],
                                                member,
                                                module_name)

            if 'optional' in member:
                compiled_member.optional = member['optional']

            if 'default' in member:
                compiled_member.default = member['default']

            compiled_members.append(compiled_member)

        return compiled_members


def compile_dict(specification):
    return Compiler(specification).process()


def decode_length(_data):
    raise DecodeError('Decode length not supported for this codec.')
