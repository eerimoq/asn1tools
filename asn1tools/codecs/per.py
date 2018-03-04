"""Packed Encoding Rules (PER) codec.

"""

from . import EncodeError
from . import DecodeError
from . import compiler
from .compiler import enum_values_as_dict


class DecodeChoiceError(Exception):
    pass


class Encoder(object):

    def __init__(self):
        self.byte = 0
        self.index = 7
        self.buf = bytearray()

    def append_bit(self, bit):
        """Append given bit.

        """

        self.byte |= (bit << self.index)
        self.index -= 1

        if self.index == -1:
            self.buf.append(self.byte)
            self.byte = 0
            self.index = 7

    def append_bits(self, data, number_of_bits):
        """Append given bits.

        """

        for i in range(number_of_bits):
            self.append_bit((bytearray(data)[i // 8] >> (7 - (i % 8))) & 0x1)

    def append_integer(self, value, number_of_bits):
        """Append given integer value.

        """

        for i in range(number_of_bits):
            self.append_bit((value >> (number_of_bits - i - 1)) & 0x1)

    def append_bytes(self, data):
        """Append given data aligned to a byte boundary.

        """

        if self.index != 7:
            self.buf.append(self.byte)
            self.byte = 0
            self.index = 7

        self.buf.extend(data)

    def as_bytearray(self):
        """Return the bits as a bytearray.

        """

        if self.index < 7:
            return self.buf + bytearray([self.byte])
        else:
            return self.buf

    def __repr__(self):
        return str(self.as_bytearray())


class Decoder(object):

    def __init__(self, encoded):
        self.byte = None
        self.index = 0
        self.offset = 0
        self.buf = encoded

    def read_bit(self):
        """Read a bit.

        """

        if self.index == 0:
            self.byte = self.buf[self.offset]
            self.index = 7
            self.offset += 1

        bit = ((self.byte >> self.index) & 0x1)
        self.index -= 1

        return bit

    def read_integer(self, number_of_bits):
        """Read an integer value of given number of bits.

        """

        value = 0

        for _ in range(number_of_bits):
            value <<= 1
            value |= self.read_bit()

        return value

    def read_bytes(self, number_of_bytes):
        """Read given number of bytes.

        """

        self.index = 0
        data = self.buf[self.offset:self.offset + number_of_bytes]
        self.offset += number_of_bytes

        return data


def encode_signed_integer(data):
    """Encode given integer value into a bytearray and return it.

    """

    encoded = bytearray()

    if data < 0:
        data *= -1
        data -= 1
        carry = not data

        while data > 0:
            encoded.append((data & 0xff) ^ 0xff)
            carry = (data & 0x80)
            data >>= 8

        if carry:
            encoded.append(0xff)
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
    """Decode given data bytes as a signed integer and return it.

    """

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
        self.optional = False
        self.default = None


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER')

    def encode(self, data, encoder):
        encoder.append_bytes(encode_signed_integer(data))

    def decode(self, decoder):
        length = decoder.read_bytes(1)[0]

        return decode_signed_integer(decoder.read_bytes(length))

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Real(Type):

    def __init__(self, name):
        super(Real, self).__init__(name, 'REAL')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN')

    def encode(self, data, encoder):
        encoder.append_bit(bool(data))

    def decode(self, decoder):
        return bool(decoder.read_bit())

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name):
        super(IA5String, self).__init__(name, 'IA5String')

    def encode(self, data, encoder):
        encoder.append_bytes(bytearray([len(data)]) + data.encode('ascii'))

    def decode(self, decoder):
        length = decoder.read_bytes(1)[0]

        return decoder.read_bytes(length).decode('ascii')

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name, 'NumericString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
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

    def encode(self, data, encoder):
        for optional in self.optionals:
            encoder.append_bit(optional in data)

        for member in self.members:
            name = member.name

            if name in data:
                member.encode(data[name], encoder)
            elif member.optional:
                pass
            elif member.default is not None:
                member.encode(member.default, encoder)
            else:
                raise EncodeError(
                    "Sequence member '{}' not found in {}.".format(
                        name,
                        data))

    def decode(self, decoder):
        values = {}

        optionals = {optional: decoder.read_bit()
                     for optional in self.optionals}

        for member in self.members:
            if not optionals.get(member.name, True):
                continue

            try:
                value = member.decode(decoder)
            except (DecodeError, IndexError) as e:
                if member.optional:
                    continue

                if member.default is None:
                    if isinstance(e, IndexError):
                        e = DecodeError('out of data at offset {}'.format(-1))

                    e.location.append(member.name)
                    raise e

                value = member.default

            values[member.name] = value

        return values

    def __repr__(self):
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Set(Type):

    def __init__(self, name, members):
        super(Set, self).__init__(name, 'SET')
        self.members = members

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'Set({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class SequenceOf(Type):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name, 'SEQUENCE OF')
        self.element_type = element_type

    def encode(self, data, encoder):
        encoder.append_bytes(bytearray([len(data)]))

        for entry in data:
            self.element_type.encode(entry, encoder)

    def decode(self, decoder):
        number_of_elements = decoder.read_bytes(1)[0]
        decoded = []

        for _ in range(number_of_elements):
            decoded_element = self.element_type.decode(decoder)
            decoded.append(decoded_element)

        return decoded

    def __repr__(self):
        return 'SequenceOf({}, {})'.format(self.name,
                                           self.element_type)


class SetOf(Type):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name, 'SET OF')
        self.element_type = element_type

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'SetOf({}, {})'.format(self.name,
                                      self.element_type)


class BitString(Type):

    def __init__(self, name, size):
        super(BitString, self).__init__(name, 'BIT STRING')
        self.size = size

    def encode(self, data, encoder):
        if self.size is None:
            encoder.append_bytes(bytearray([data[1]]) + data[0])
        else:
            encoder.append_bits(*data)

    def decode(self, decoder):
        number_of_bits = decoder.read_bytes(1)[0]

        return (decoder.read_bytes((number_of_bits + 7) // 8), number_of_bits)

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name, 'OCTET STRING')

    def encode(self, data, encoder):
        encoder.append_bytes(bytearray([len(data)]) + data)

    def decode(self, decoder):
        length = decoder.read_bytes(1)[0]

        return decoder.read_bytes(length)

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name, 'PrintableString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name, 'UniversalString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name):
        super(VisibleString, self).__init__(name, 'VisibleString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class GeneralString(Type):

    def __init__(self, name):
        super(GeneralString, self).__init__(name, 'GeneralString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'GeneralString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name, 'UTF8String')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name, 'BMPString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name, 'UTCTime')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name, 'GeneralizedTime')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name, 'TeletexString')

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name, 'OBJECT IDENTIFIER')

    def encode(self, data, encoder):
        identifiers = [int(identifier) for identifier in data.split('.')]

        first_subidentifier = (40 * identifiers[0] + identifiers[1])
        encoded_subidentifiers = self.encode_subidentifier(
            first_subidentifier)

        for identifier in identifiers[2:]:
            encoded_subidentifiers += self.encode_subidentifier(identifier)

        encoder.append_bytes([len(encoded_subidentifiers)])
        encoder.append_bytes(encoded_subidentifiers)

    def decode(self, decoder):
        length = decoder.read_bytes(1)[0]
        data = decoder.read_bytes(length)
        offset = 0
        subidentifier, offset = self.decode_subidentifier(data, offset)
        decoded = [subidentifier // 40, subidentifier % 40]

        while offset < length:
            subidentifier, offset = self.decode_subidentifier(data, offset)
            decoded.append(subidentifier)

        return '.'.join([str(v) for v in decoded])

    def encode_subidentifier(self, subidentifier):
        encoder = [subidentifier & 0x7f]
        subidentifier >>= 7

        while subidentifier > 0:
            encoder.append(0x80 | (subidentifier & 0x7f))
            subidentifier >>= 7

        return encoder[::-1]

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
        self.number_of_bits = len('{:b}'.format(len(members) - 1))

    def encode(self, data, encoder):
        if not isinstance(data, tuple):
            raise EncodeError("expected tuple, but got '{}'".format(data))

        for i, member in enumerate(self.members):
            if member.name == data[0]:
                if len(self.members) > 1:
                    encoder.append_integer(i, self.number_of_bits)

                member.encode(data[1], encoder)
                return

        raise EncodeError(
            "Expected choices are {}, but got '{}'.".format(
                [member.name for member in self.members],
                data[0]))

    def decode(self, data, offset):
        for member in self.members:
            if isinstance(member, Choice):
                try:
                    decoded, offset = member.decode(data, offset)
                    return (member.name, decoded), offset
                except DecodeChoiceError:
                    pass
            elif member.tag == data[offset]:
                decoded, offset = member.decode(data, offset)
                return (member.name, decoded), offset

        raise DecodeChoiceError()

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL')

    def encode(self, _, _encoder):
        pass

    def decode(self, _):
        return None

    def __repr__(self):
        return 'Null({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY')

    def encode(self, _, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'Any({})'.format(self.name)


class OpenType(Type):

    def __init__(self, name):
        super(OpenType, self).__init__(name, 'OpenType')

    def encode(self, data, encoder):
        encoder.append_bytes(bytearray([len(data)]) + data)

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'OpenType({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name, 'ENUMERATED')
        values = enum_values_as_dict(values)
        self.values = values
        self.lowest_value = min(values)
        highest_value = max(values.keys()) - self.lowest_value
        self.number_of_bits = len('{:b}'.format(highest_value))

    def encode(self, data, encoder):
        for value, name in self.values.items():
            if data == name:
                encoder.append_integer(value - self.lowest_value,
                                       self.number_of_bits)
                return

        raise EncodeError(
            "Enumeration value '{}' not found in {}.".format(
                data,
                [value for value in self.values.values()]))

    def decode(self, decoder):
        value = decoder.read_integer(self.number_of_bits)

        return self.values[value + self.lowest_value]

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class Recursive(Type):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name, 'RECURSIVE')
        self.type_name = type_name
        self.module_name = module_name

    def encode(self, _data, _encoder):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def decode(self, _decoder):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def __repr__(self):
        return 'Recursive({})'.format(self.name)


class CompiledType(object):

    def __init__(self, type_):
        self._type = type_

    def encode(self, data):
        encoder = Encoder()
        self._type.encode(data, encoder)
        return encoder.as_bytearray()

    def decode(self, data):
        decoder = Decoder(bytearray(data))
        return self._type.decode(decoder)

    def __repr__(self):
        return repr(self._type)


class Compiler(compiler.Compiler):

    def process_type(self, type_name, type_descriptor, module_name):
        return CompiledType(self.compile_type(type_name,
                                              type_descriptor,
                                              module_name))

    def compile_type(self, name, type_descriptor, module_name):
        if '.' in type_descriptor['type']:
            type_descriptor = self.convert_class_member_type(type_descriptor,
                                                             module_name)

        type_name = type_descriptor['type']

        if type_name == 'SEQUENCE':
            compiled = Sequence(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_name == 'SEQUENCE OF':
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name))
        elif type_name == 'SET':
            compiled = Set(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_name == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_name == 'CHOICE':
            compiled = Choice(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
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
            size = type_descriptor.get('size', None)
            compiled = BitString(name, size)
        elif type_name == 'ANY':
            compiled = Any(name)
        elif type_name == 'ANY DEFINED BY':
            compiled = Any(name)
        elif type_name == 'NULL':
            compiled = Null(name)
        elif type_name == 'OpenType':
            compiled = OpenType(name)
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
