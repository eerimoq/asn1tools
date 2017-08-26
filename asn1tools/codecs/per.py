"""PER (Packed Encoding Rules) codec.

"""

from . import EncodeError, DecodeError


class DecodeChoiceError(Exception):
    pass


class Encoded(object):

    def __init__(self):
        self.byte = 0
        self.index = 7
        self.buf = bytearray()

    def append_bit(self, bit):
        '''Append given bit.

        '''

        self.byte |= (bit << self.index)
        self.index -= 1

        if self.index == -1:
            self.buf.append(self.byte)
            self.byte = 0
            self.index = 7

    def append_bytes(self, data):
        '''Append given data aligned to a byte boundary.

        '''

        if self.index != 7:
            self.buf.append(self.byte)
            self.byte = 0
            self.index = 7

        self.buf.extend(data)

    def as_bytearray(self):
        '''Return the bits as a bytearray.

        '''

        if self.index < 7:
            return self.buf + bytearray([self.byte])
        else:
            return self.buf

    def __repr__(self):
        return str(self.as_bytearray())


def encode_length_definite(length):
    if length <= 127:
        encoded = bytearray([length])
    else:
        encoded = bytearray()

        while length > 0:
            encoded.append(length & 0xff)
            length >>= 8

        encoded.append(0x80 | len(encoded))
        encoded.reverse()

    return encoded


def decode_length_definite(encoded, offset):
    length = encoded[offset]
    offset += 1

    if length <= 127:
        return length, offset
    else:
        number_of_bytes = (length & 0x7f)
        length = decode_integer(encoded[offset:number_of_bytes + offset])

        return length, offset + number_of_bytes


def decode_integer(data):
    value = 0

    for byte in data:
        value <<= 8
        value += byte

    return value


def encode_signed_integer(data):
    encoded = bytearray()

    if data < 0:
        data *= -1

        while data > 0:
            encoded.append(256 - (data & 0xff))
            data >>= 8
    elif data > 0:
        while data > 0:
            encoded.append(data & 0xff)
            data >>= 8

        if encoded[-1] & 0x80:
            encoded.append(0)
    else:
        encoded.append(0)

    encoded.append(len(encoded))
    encoded.reverse()

    return encoded


def decode_signed_integer(data):
    value = 0
    is_negative = (data[0] & 0x80)

    for byte in data:
        value <<= 8
        value += byte

    if is_negative:
        value -= (1 << (8 * len(data)))

    return value


class Type(object):

    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
        self.optional = None
        self.default = None


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER')

    def encode(self, data, encoded):
        encoded.append_bytes(encode_signed_integer(data))

    def decode(self, data, offset):
        length = data[0]
        offset += 1
        offset_end = offset + length

        return decode_signed_integer(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN')

    def encode(self, data, encoded):
        encoded.append_bit(bool(data))

    def decode(self, data, offset):
        return (bool(data[offset])), offset + 1

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name):
        super(IA5String, self).__init__(name, 'IA5String')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name, 'NumericString')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class Sequence(Type):

    def __init__(self, name, members):
        super(Sequence, self).__init__(name, 'SEQUENCE')
        self.members = members
        self.optionals = [member.name
                          for member in members
                          if member.optional]

    def encode(self, data, encoded):
        for optional in self.optionals:
            encoded.append_bit(optional in data)

        for member in self.members:
            name = member.name

            if name in data:
                member.encode(data[name], encoded)
            elif member.optional:
                pass
            elif member.default is not None:
                member.encode(member.default, encoded)
            else:
                raise EncodeError(
                    "Sequence member '{}' not found in {}.".format(
                        name,
                        data))

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Set(Type):

    def __init__(self, name, members):
        super(Set, self).__init__(name, 'SET')
        self.members = members

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'Set({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class SequenceOf(Type):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name, 'SEQUENCE OF')
        self.element_type = element_type

    def encode(self, data, encoded):
        encoded.append_bytes(bytearray([len(data)]))

        for entry in data:
            self.element_type.encode(entry, encoded)

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'SequenceOf({}, {})'.format(self.name,
                                           self.element_type)


class SetOf(Type):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name, 'SET OF')
        self.element_type = element_type

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'SetOf({}, {})'.format(self.name,
                                      self.element_type)


class BitString(Type):

    def __init__(self, name):
        super(BitString, self).__init__(name, 'BIT STRING')

    def encode(self, data, encoded):
        encoded.append_bytes(bytearray([data[1]]) + data[0])

    def decode(self, data, offset):
        number_of_bits = data[0]
        offset += 1
        offset_end = offset + ((number_of_bits + 7) // 8)

        return (data[offset:offset_end], number_of_bits), offset_end

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name, 'OCTET STRING')

    def encode(self, data, encoded):
        encoded.append_bytes(bytearray([len(data)]) + data)

    def decode(self, data, offset):
        length = data[0]
        offset += 1
        offset_end = offset + length

        return data[offset:offset_end], offset_end

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name, 'PrintableString')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name, 'UniversalString')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name):
        super(VisibleString, self).__init__(name, 'VisibleString')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name, 'UTF8String')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name, 'BMPString')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name, 'UTCTime')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name, 'GeneralizedTime')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def encode_subidentifier(self, subidentifier):
        encoded = [subidentifier & 0x7f]
        subidentifier >>= 7

        while subidentifier > 0:
            encoded.append(0x80 | (subidentifier & 0x7f))
            subidentifier >>= 7

        return encoded[::-1]

    def decode_subidentifier(self, data, offset):
        decoded = 0

        while data[offset] & 0x80:
            decoded += (data[offset] & 0x7f)
            decoded <<= 7
            offset += 1

        decoded += data[offset]

        return decoded, offset + 1

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name, 'CHOICE')
        self.members = members

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL')

    def encode(self, _, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'Null({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY')

    def encode(self, _, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'Any({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name, 'ENUMERATED')
        self.values = values

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'Null({})'.format(self.name)


class ExplicitTag(Type):

    def __init__(self, name, inner):
        super(ExplicitTag, self).__init__(name, 'Tag')
        self.inner = inner

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'Tag()'


class CompiledType(object):

    def __init__(self, type_):
        self._type = type_

    def encode(self, data):
        encoded = Encoded()
        self._type.encode(data, encoded)
        return encoded.as_bytearray()

    def decode(self, data):
        return self._type.decode(bytearray(data), 0)[0]

    def __repr__(self):
        return repr(self._type)


class Compiler(object):

    def __init__(self, specification):
        self._specification = specification

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
            compiled = Sequence(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_descriptor['type'] == 'SEQUENCE OF':
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name))
        elif type_descriptor['type'] == 'SET':
            compiled = Set(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_descriptor['type'] == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_descriptor['type'] == 'CHOICE':
            compiled = Choice(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_descriptor['type'] == 'INTEGER':
            compiled = Integer(name)
        elif type_descriptor['type'] == 'ENUMERATED':
            compiled = Enumerated(name, type_descriptor['values'])
        elif type_descriptor['type'] == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_descriptor['type'] == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_descriptor['type'] == 'OCTET STRING':
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
            compiled = BitString(name)
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

    def is_explicit_tag(self, type_descriptor, module_name):
        try:
            return type_descriptor['tag']['kind'] == 'EXPLICIT'
        except KeyError:
            pass

        try:
            tags = self._specification[module_name].get('tags', None)
            return bool(type_descriptor['tag']) and (tags != 'IMPLICIT')
        except KeyError:
            pass

        return False

    def compile_type(self, name, type_descriptor, module_name):
        compiled = self.compile_implicit_type(name,
                                              type_descriptor,
                                              module_name)

        return compiled

    def compile_members(self, members, module_name):
        compiled_members = []

        for member in members:
            if member['name'] == '...':
                continue

            compiled_member = self.compile_type(member['name'],
                                                member,
                                                module_name)
            compiled_member.optional = member['optional']

            if 'default' in member:
                compiled_member.default = member['default']

            compiled_members.append(compiled_member)

        return compiled_members

    def lookup_type_descriptor(self, type_name, module_name):
        module = self._specification[module_name]
        type_descriptor = None

        if type_name in module['types']:
            type_descriptor = module['types'][type_name]
        else:
            for from_module_name, imports in module['imports'].items():
                if type_name in imports:
                    from_module = self._specification[from_module_name]
                    type_descriptor = from_module['types'][type_name]
                    module_name = from_module_name
                    break

        if type_descriptor is None:
            raise Exception("Type '{}' not found.".format(type_name))

        return type_descriptor, module_name


def compile_json(specification):
    return Compiler(specification).process()
