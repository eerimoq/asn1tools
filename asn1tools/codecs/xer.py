"""XML Encoding Rules (XER) codec.

"""

import sys
from xml.etree import ElementTree
import binascii

from . import EncodeError
from . import DecodeError
from . import compiler
from . import format_or
from . import utc_time_to_datetime
from . import utc_time_from_datetime
from . import generalized_time_to_datetime
from . import generalized_time_from_datetime
from .compiler import enum_values_as_dict


def indent_xml(element, indent, level=0):
    i = "\n" + level * indent

    if len(element):
        if not element.text or not element.text.strip():
            element.text = i + indent

        if not element.tail or not element.tail.strip():
            element.tail = i

        for element in element:
            indent_xml(element, indent, level + 1)

        if not element.tail or not element.tail.strip():
            element.tail = i
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = i


class Type(object):

    def __init__(self, name, type_name):
        self.name = name.replace(' ', '_')
        self.type_name = type_name
        self.optional = False
        self.default = None

    def set_size_range(self, minimum, maximum, has_extension_marker):
        pass

    def encode(self, data):
        raise NotImplementedError('To be implemented by subclasses.')

    def encode_of(self, data):
        return self.encode(data)

    def decode(self, element):
        raise NotImplementedError('To be implemented by subclasses.')

    def decode_of(self, element):
        return self.decode(element)


class StringType(Type):

    def __init__(self, name, type_name=None):
        if type_name is None:
            type_name = self.__class__.__name__

        super(StringType, self).__init__(name, type_name)

    def encode(self, data):
        element = ElementTree.Element(self.name)

        if len(data) > 0:
            element.text = data

        return element

    def decode(self, element):
        if element.text is None:
            return u''
        else:
            if sys.version_info[0] > 2:
                return element.text
            else:
                return unicode(element.text)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.name)


class MembersType(Type):

    def __init__(self, name, members, type_name):
        super(MembersType, self).__init__(name, type_name)
        self.members = members

    def encode(self, data):
        element = ElementTree.Element(self.name)

        for member in self.members:
            name = member.name

            if name in data:
                try:
                    member_element = member.encode(data[name])
                except EncodeError as e:
                    e.location.append(member.name)
                    raise
            elif member.optional or member.default is not None:
                continue
            else:
                raise EncodeError(
                    "{} member '{}' not found in {}.".format(
                        self.__class__.__name__,
                        name,
                        data))

            element.append(member_element)

        return element

    def decode(self, element):
        values = {}

        for member in self.members:
            name = member.name
            member_element = element.find(name)

            if member_element is not None:
                value = member.decode(member_element)
                values[name] = value
            elif member.optional:
                pass
            elif member.default is not None:
                values[name] = member.default

        return values

    def __repr__(self):
        return '{}({}, [{}])'.format(
            self.__class__.__name__,
            self.name,
            ', '.join([repr(member) for member in self.members]))


class ArrayType(Type):

    def __init__(self, name, element_type, type_name):
        super(ArrayType, self).__init__(name, type_name)
        self.element_type = element_type

    def encode(self, data):
        element = ElementTree.Element(self.name)

        for entry in data:
            element.append(self.element_type.encode_of(entry))

        return element

    def decode(self, element):
        values = []

        for member_element in list(element):
            value = self.element_type.decode_of(member_element)
            values.append(value)

        return values

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.name,
                                   self.element_type)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN')

    def encode(self, data):
        element = ElementTree.Element(self.name)
        ElementTree.SubElement(element, 'true' if data else 'false')

        return element

    def decode(self, element):
        return element.find('true') is not None

    def encode_of(self, data):
        return ElementTree.Element('true' if data else 'false')

    def decode_of(self, element):
        return element.tag == 'true'

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER')

    def encode(self, data):
        element = ElementTree.Element(self.name)
        element.text = str(data)

        return element

    def decode(self, element):
        return int(element.text)

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Real(Type):

    def __init__(self, name):
        super(Real, self).__init__(name, 'REAL')

    def encode(self, data):
        data = float(data)
        exponent = 0

        while abs(data) >= 10:
            data /= 10
            exponent += 1

        element = ElementTree.Element(self.name)
        element.text = '{}E{}'.format(data, exponent)

        return element

    def decode(self, element):
        return float(element.text)

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL')

    def encode(self, data):
        return ElementTree.Element(self.name)

    def decode(self, element):
        return None

    def __repr__(self):
        return 'Null({})'.format(self.name)


class BitString(Type):

    def __init__(self, name):
        super(BitString, self).__init__(name, 'BIT STRING')

    def encode(self, data):
        element = ElementTree.Element(self.name)

        if data[1] > 0:
            encoded = int(binascii.hexlify(data[0]), 16)
            encoded |= (0x80 << (8 * len(data[0])))
            element.text = bin(encoded)[10:10 + data[1]].upper()

        return element

    def decode(self, element):
        encoded = element.text

        if encoded is None:
            number_of_bits = 0
            decoded = b''
        else:
            number_of_bits = len(encoded)
            decoded = int(encoded, 2)
            decoded |= (0x80 << number_of_bits)
            rest = (number_of_bits % 8)

            if rest != 0:
                decoded <<= (8 - rest)

            decoded = binascii.unhexlify(hex(decoded).rstrip('L')[4:])

        return (decoded, number_of_bits)

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name, 'OCTET STRING')

    def encode(self, data):
        element = ElementTree.Element(self.name)

        if len(data) > 0:
            element.text = binascii.hexlify(data).decode('ascii').upper()

        return element

    def decode(self, element):
        if element.text is None:
            return b''
        else:
            return binascii.unhexlify(element.text)

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class ObjectIdentifier(StringType):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def decode(self, element):
        if element.text is None:
            raise DecodeError("Expected an OBJECT IDENTIFIER, but got ''.")

        return element.text


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name, 'ENUMERATED')
        self.values = set(enum_values_as_dict(values).values())

    def format_names(self):
        return format_or(sorted(self.values))

    def encode(self, data):
        if data not in self.values:
            raise EncodeError(
                "Expected enumeration value {}, but got '{}'.".format(
                    self.format_names(),
                    data))

        element = ElementTree.Element(self.name)
        element.append(ElementTree.Element(data))

        return element

    def decode(self, element):
        value = element[0].tag

        if value not in self.values:
            raise DecodeError(
                "Expected enumeration value {}, but got '{}'.".format(
                    self.format_names(),
                    value))

        return value

    def encode_of(self, data):
        if data not in self.values:
            raise EncodeError(
                "Expected enumeration value {}, but got '{}'.".format(
                    self.format_names(),
                    data))

        return ElementTree.Element(data)

    def decode_of(self, element):
        value = element.tag

        if value not in self.values:
            raise DecodeError(
                "Expected enumeration value {}, but got '{}'.".format(
                    self.format_names(),
                    value))

        return value

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class Sequence(MembersType):

    def __init__(self, name, members):
        super(Sequence, self).__init__(name, members, 'SEQUENCE')


class SequenceOf(ArrayType):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name,
                                         element_type,
                                         'SEQUENCE OF')


class Set(MembersType):

    def __init__(self, name, members):
        super(Set, self).__init__(name, members, 'SET')


class SetOf(ArrayType):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name,
                                    element_type,
                                    'SET OF')


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name, 'CHOICE')
        self.members = members
        self.name_to_member = {member.name: member for member in self.members}

    def format_names(self):
        return format_or(sorted([member.name for member in self.members]))

    def encode(self, data):
        try:
            member = self.name_to_member[data[0]]
        except KeyError:
            raise EncodeError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    data[0]))

        element = ElementTree.Element(self.name)

        try:
            element.append(member.encode(data[1]))
        except EncodeError as e:
            e.location.append(member.name)
            raise

        return element

    def decode(self, element):
        member_element = element[0]
        name = member_element.tag

        try:
            member = self.name_to_member[name]
        except KeyError:
            raise DecodeError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    name))

        return (name, member.decode(member_element))

    def encode_of(self, data):
        try:
            member = self.name_to_member[data[0]]
        except KeyError:
            raise EncodeError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    data[0]))

        return member.encode(data[1])

    def decode_of(self, element):
        name = element.tag

        try:
            member = self.name_to_member[name]
        except KeyError:
            raise DecodeError(
                "Expected choice {}, but got '{}'.".format(
                    self.format_names(),
                    name))

        return (name, member.decode(element))

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class UTF8String(StringType):
    pass


class NumericString(StringType):
    pass


class PrintableString(StringType):
    pass


class IA5String(StringType):
    pass


class VisibleString(StringType):
    pass


class GeneralString(StringType):
    pass


class BMPString(StringType):
    pass


class GraphicString(StringType):
    pass


class UniversalString(StringType):
    pass


class TeletexString(StringType):
    pass


class ObjectDescriptor(GraphicString):
    pass


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name, 'UTCTime')

    def encode(self, data):
        element = ElementTree.Element(self.name)
        element.text = utc_time_from_datetime(data)

        return element

    def decode(self, element):
        return utc_time_to_datetime(element.text)

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name, 'GeneralizedTime')

    def encode(self, data):
        element = ElementTree.Element(self.name)
        element.text = generalized_time_from_datetime(data)

        return element

    def decode(self, element):
        return generalized_time_to_datetime(element.text)

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY')

    def encode(self, data):
        raise NotImplementedError('ANY is not yet implemented.')

    def decode(self, element):
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

    def encode(self, data):
        encoded = self._inner.encode(data)
        encoded.tag = self.name

        return encoded

    def decode(self, element):
        return self._inner.decode(element)

    def __repr__(self):
        return 'Recursive({})'.format(self.name)


class CompiledType(compiler.CompiledType):

    def __init__(self, type_):
        super(CompiledType, self).__init__()
        self._type = type_

    @property
    def type(self):
        return self._type

    def encode(self, data, indent=None):
        element = self._type.encode(data)

        if indent is not None:
            indent_xml(element, indent * " ")

        return ElementTree.tostring(element)

    def decode(self, data):
        element = ElementTree.fromstring(data.decode('utf-8'))

        return self._type.decode(element)

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
            members = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Sequence(name, members)
        elif type_name == 'SEQUENCE OF':
            element = type_descriptor['element']
            compiled = SequenceOf(name,
                                  self.compile_type(element['type'],
                                                    element,
                                                    module_name))
        elif type_name == 'SET':
            members = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Set(name, members)
        elif type_name == 'SET OF':
            element = type_descriptor['element']
            compiled = SetOf(name,
                             self.compile_type(element['type'],
                                               element,
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
        elif type_name == 'GraphicString':
            compiled = GraphicString(name)
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
        elif type_name == 'EXTERNAL':
            compiled = Sequence(
                name,
                self.compile_members(self.external_type_descriptor()['members'],
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

        return compiled


def compile_dict(specification):
    return Compiler(specification).process()


def decode_length(_data):
    raise DecodeError('Decode length is not supported for this codec.')
