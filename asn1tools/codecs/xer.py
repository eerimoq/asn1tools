"""XML Encoding Rules (XER) codec.

"""

from xml.etree import ElementTree

from . import EncodeError, DecodeError
from . import compiler


class Type(object):

    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
        self.optional = None
        self.default = None


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
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN')

    def encode(self, data):
        element = ElementTree.Element(self.name)
        ElementTree.SubElement(element, 'true' if data else 'false')

        return element

    def decode(self, element):
        return element.find('true') is not None

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name):
        super(IA5String, self).__init__(name, 'IA5String')

    def encode(self, data):
        element = ElementTree.Element(self.name)
        element.text = data

        return element

    def decode(self, element):
        return element.text

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name, 'NumericString')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class Sequence(Type):

    def __init__(self, name, members):
        super(Sequence, self).__init__(name, 'SEQUENCE')
        self.members = members

    def encode(self, data):
        element = ElementTree.Element(self.name)

        for member in self.members:
            name = member.name

            if name in data:
                member_element = member.encode(data[name])
            elif member.optional or member.default is not None:
                continue
            else:
                raise EncodeError(
                    "Sequence member '{}' not found in {}.".format(
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
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Set(Type):

    def __init__(self, name, members):
        super(Set, self).__init__(name, 'SET')
        self.members = members

    def encode(self, data):
        element = ElementTree.Element(self.name)

        for member in self.members:
            name = member.name

            if name in data:
                member_element = member.encode(data[name])
            elif member.optional or member.default is not None:
                continue
            else:
                raise EncodeError(
                    "Set member '{}' not found in {}.".format(
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
        return 'Set({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class SequenceOf(Type):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name, 'SEQUENCE OF')
        self.element_type = element_type

    def encode(self, data):
        element = ElementTree.Element(self.name)

        for entry in data:
            element.append(self.element_type.encode(entry))

        return element

    def decode(self, element):
        values = []

        for member_element in list(element):
            value = self.element_type.decode(member_element)
            values.append(value)

        return values

    def __repr__(self):
        return 'SequenceOf({}, {})'.format(self.name,
                                           self.element_type)


class SetOf(Type):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name, 'SET OF')
        self.element_type = element_type

    def encode(self, data):
        element = ElementTree.Element(self.name)

        for entry in data:
            element.append(self.element_type.encode(entry))

        return element

    def decode(self, element):
        values = []

        for member_element in list(element):
            value = self.element_type.decode(member_element)
            values.append(value)

        return values

    def __repr__(self):
        return 'SetOf({}, {})'.format(self.name,
                                      self.element_type)


class BitString(Type):

    def __init__(self, name, minimum, maximum):
        super(BitString, self).__init__(name, 'BIT STRING')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name, 'OCTET STRING')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name, 'PrintableString')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name, 'UniversalString')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name):
        super(VisibleString, self).__init__(name, 'VisibleString')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name, 'UTF8String')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name, 'BMPString')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name, 'UTCTime')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name, 'GeneralizedTime')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, data):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name, 'CHOICE')
        self.members = members

    def encode(self, data):
        for member in self.members:
            if member.name in data:
                return {member.name: member.encode(data[member.name])}

        raise EncodeError(
            "Expected choices are {}, but got '{}'.".format(
                [member.name for member in self.members],
                ''.join([name for name in data])))

    def decode(self, data):
        for member in self.members:
            if member.name in data:
                return {member.name: member.decode(data[member.name])}

        raise DecodeError('')

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL')

    def encode(self, data):
        return data

    def decode(self, data):
        return data

    def __repr__(self):
        return 'Null({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY')

    def encode(self, _, encoder):
        raise NotImplementedError()

    def decode(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return 'Any({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name, 'ENUMERATED')
        self.values = values

    def encode(self, data):
        for name in self.values.values():
            if data == name:
                return data

        raise EncodeError(
            "Enumeration value '{}' not found in {}.".format(
                data,
                [value for value in self.values.values()]))

    def decode(self, data):
        if data in self.values.values():
            return data

        raise DecodeError(
            "Enumeration value '{}' not found in {}.".format(
                data,
                [value for value in self.values.values()]))

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class CompiledType(object):

    def __init__(self, type_):
        self._type = type_

    def encode(self, data):
        return ElementTree.tostring(self._type.encode(data))

    def decode(self, data):
        element = ElementTree.fromstring(data.decode('utf-8'))

        return self._type.decode(element)

    def __repr__(self):
        return repr(self._type)


class Compiler(compiler.Compiler):

    def process(self):
        return {
            module_name: {
                type_name: CompiledType(self.compile_type(
                    type_name,
                    type_descriptor,
                    module_name))
                for type_name, type_descriptor
                in self._specification[module_name]['types'].items()
            }
            for module_name in self._specification
        }

    def compile_implicit_type(self, name, type_descriptor, module_name):
        if type_descriptor['type'] == 'SEQUENCE':
            members, _ = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Sequence(name, members)
        elif type_descriptor['type'] == 'SEQUENCE OF':
            minimum, maximum = self.get_size_range(type_descriptor,
                                                   module_name)
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name))
        elif type_descriptor['type'] == 'SET':
            members, _ = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Set(name, members)
        elif type_descriptor['type'] == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_descriptor['type'] == 'CHOICE':
            members, _ = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Choice(name, members)
        elif type_descriptor['type'] == 'INTEGER':
            compiled = Integer(name)
        elif type_descriptor['type'] == 'REAL':
            compiled = Real(name)
        elif type_descriptor['type'] == 'ENUMERATED':
            compiled = Enumerated(name, type_descriptor['values'])
        elif type_descriptor['type'] == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_descriptor['type'] == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_descriptor['type'] == 'OCTET STRING':
            minimum, maximum =self.get_size_range(type_descriptor,
                                                  module_name)
            compiled = OctetString(name)
        elif type_descriptor['type'] == 'TeletexString':
            compiled = TeletexString(name)
        elif type_descriptor['type'] == 'NumericString':
            compiled = NumericString(name)
        elif type_descriptor['type'] == 'PrintableString':
            compiled = PrintableString(name)
        elif type_descriptor['type'] == 'IA5String':
            compiled = IA5String(name)
        elif type_descriptor['type'] == 'VisibleString':
            compiled = VisibleString(name)
        elif type_descriptor['type'] == 'UTF8String':
            compiled = UTF8String(name)
        elif type_descriptor['type'] == 'BMPString':
            compiled = BMPString(name)
        elif type_descriptor['type'] == 'UTCTime':
            compiled = UTCTime(name)
        elif type_descriptor['type'] == 'UniversalString':
            compiled = UniversalString(name)
        elif type_descriptor['type'] == 'GeneralizedTime':
            compiled = GeneralizedTime(name)
        elif type_descriptor['type'] == 'BIT STRING':
            minimum, maximum =self.get_size_range(type_descriptor,
                                                  module_name)
            compiled = BitString(name, minimum, maximum)
        elif type_descriptor['type'] == 'ANY':
            compiled = Any(name)
        elif type_descriptor['type'] == 'ANY DEFINED BY':
            compiled = Any(name)
        elif type_descriptor['type'] == 'NULL':
            compiled = Null(name)
        else:
            compiled = self.compile_type(
                name,
                *self.lookup_type_descriptor(
                    type_descriptor['type'],
                    module_name))

        return compiled

    def compile_type(self, name, type_descriptor, module_name):
        compiled = self.compile_implicit_type(name,
                                              type_descriptor,
                                              module_name)

        return compiled

    def compile_members(self, members, module_name):
        compiled_members = []
        extension = None

        for member in members:
            if member['name'] == '...':
                extension = []
                continue

            if extension is not None:
                raise NotImplementedError()

            compiled_member = self.compile_type(member['name'],
                                                member,
                                                module_name)
            compiled_member.optional = member['optional']

            if 'default' in member:
                compiled_member.default = member['default']

            compiled_members.append(compiled_member)

        return compiled_members, extension


def compile_dict(specification):
    return Compiler(specification).process()
