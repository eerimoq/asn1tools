"""UPER (Unaligned Packed Encoding Rules) codec.

"""

from . import EncodeError, DecodeError


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

        self.append_bits(data, 8 * len(data))

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
        self.index = -1
        self.offset = 0
        self.buf = encoded

    def read_bit(self):
        """Read a bit.

        """

        if self.index == -1:
            self.byte = self.buf[self.offset]
            self.index = 7
            self.offset += 1

        bit = ((self.byte >> self.index) & 0x1)
        self.index -= 1

        return bit

    def read_bits(self, number_of_bits):
        """Read given number of bits.

        """

        value = bytearray()
        byte = 0

        for i in range(number_of_bits):
            index = i % 8
            byte |= (self.read_bit() << (7 - index))

            if index == 7:
                value.append(byte)
                byte = 0

        if number_of_bits % 8 != 0:
            value.append(byte)

        return bytes(value)

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

        self.index = -1
        data = self.buf[self.offset:self.offset + number_of_bytes]
        self.offset += number_of_bytes
        return data


def size_as_number_of_bits(size):
    """Returns the minimum number of bits needed to fit given positive
    integer.

    """

    return len('{:b}'.format(size))


def encode_signed_integer(value):
    """Encode given integer value into a bytearray and return it.

    """

    encoded = bytearray()

    if value < 0:
        value *= -1
        value -= 1
        carry = not value

        while value > 0:
            encoded.append((value & 0xff) ^ 0xff)
            carry = (value & 0x80)
            value >>= 8

        if carry:
            encoded.append(0xff)
    elif value > 0:
        while value > 0:
            encoded.append(value & 0xff)
            value >>= 8

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
        self.optional = None
        self.default = None


class Integer(Type):

    def __init__(self, name, minimum, maximum):
        super(Integer, self).__init__(name, 'INTEGER')
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = size_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_bytes(encode_signed_integer(data))
        else:
            encoder.append_integer(data - self.minimum, self.number_of_bits)

    def decode(self, decoder):
        if self.number_of_bits is None:
            length = decoder.read_bytes(1)[0]
            value = decode_signed_integer(decoder.read_bytes(length))
        else:
            value = decoder.read_integer(self.number_of_bits)
            value += self.minimum

        return value

    def __repr__(self):
        return 'Integer({})'.format(self.name)


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
        encoder.append_bytes(bytearray([len(data)]))

        for byte in bytearray(data.encode('ascii')):
            encoder.append_bits(bytearray([(byte << 1) & 0xff]), 7)

    def decode(self, decoder):
        length = decoder.read_bytes(1)[0]
        data = []

        for _ in range(length):
            data.append(decoder.read_integer(7))

        return bytearray(data).decode('ascii')

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

    def __init__(self, name, members, extension):
        super(Sequence, self).__init__(name, 'SEQUENCE')
        self.members = members
        self.extension = extension
        self.optionals = [
            member
            for member in members
            if member.optional or member.default is not None
        ]

    def encode(self, data, encoder):
        if self.extension is not None:
            if len(self.extension) == 0:
                encoder.append_bit(0)
            else:
                raise NotImplementedError()

        for optional in self.optionals:
            if optional.optional:
                encoder.append_bit(optional.name in data)
            elif optional.name in data:
                encoder.append_bit(data[optional.name] != optional.default)
            else:
                encoder.append_bit(0)

        for member in self.members:
            name = member.name

            if name in data:
                if member.default is None:
                    member.encode(data[name], encoder)
                elif data[name] != member.default:
                    member.encode(data[name], encoder)
            elif member.optional:
                pass
            else:
                raise EncodeError(
                    "Sequence member '{}' not found in {}.".format(
                        name,
                        data))

    def decode(self, decoder):
        if self.extension is not None:
            if len(self.extension) == 0:
                decoder.read_bit()
            else:
                raise NotImplementedError()

        values = {}
        optionals = {
            optional: decoder.read_bit()
            for optional in self.optionals
        }

        for member in self.members:
            if optionals.get(member, True):
                value = member.decode(decoder)
                values[member.name] = value
            elif member.default is not None:
                values[member.name] = member.default

        return values

    def __repr__(self):
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Set(Type):

    def __init__(self, name, members, extension):
        super(Set, self).__init__(name, 'SET')
        self.members = members
        self.extension = extension

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'Set({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class SequenceOf(Type):

    def __init__(self, name, element_type, minimum, maximum):
        super(SequenceOf, self).__init__(name, 'SEQUENCE OF')
        self.element_type = element_type
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = size_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            raise NotImplementedError()
        else:
            encoder.append_integer(len(data) - self.minimum,
                                   self.number_of_bits)

        for entry in data:
            self.element_type.encode(entry, encoder)

    def decode(self, decoder):
        if self.number_of_bits is None:
            raise NotImplementedError()
        else:
            number_of_elements = decoder.read_integer(self.number_of_bits)
            number_of_elements += self.minimum

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

    def __init__(self, name, minimum, maximum):
        super(BitString, self).__init__(name, 'BIT STRING')
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = size_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_bytes(bytearray([data[1]]) + data[0])
        else:
            if self.minimum != self.maximum:
                encoder.append_integer(data[1] - self.minimum,
                                       self.number_of_bits)

            encoder.append_bits(data[0], data[1])


    def decode(self, decoder):
        if self.number_of_bits is None:
            number_of_bits = decoder.read_bytes(1)[0]
            value = decoder.read_bytes((number_of_bits + 7) // 8)
        else:
            number_of_bits = self.minimum

            if self.minimum != self.maximum:
                number_of_bits += decoder.read_integer(self.number_of_bits)

            value = decoder.read_bits(number_of_bits)

        return (value, number_of_bits)

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name, minimum, maximum):
        super(OctetString, self).__init__(name, 'OCTET STRING')
        self.minimum = minimum
        self.maximum = maximum

        if minimum is None or maximum is None:
            self.number_of_bits = None
        else:
            size = self.maximum - self.minimum
            self.number_of_bits = size_as_number_of_bits(size)

    def encode(self, data, encoder):
        if self.number_of_bits is None:
            encoder.append_bytes(bytearray([len(data)]) + data)
        else:
            if self.minimum != self.maximum:
                encoder.append_integer(len(data) - self.minimum,
                                       self.number_of_bits)

            encoder.append_bytes(data)

    def decode(self, decoder):
        if self.number_of_bits is None:
            length = decoder.read_integer(8)
        else:
            length = self.minimum

            if self.minimum != self.maximum:
                length += decoder.read_integer(self.number_of_bits)

        return decoder.read_bits(8 * length)

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
        raise NotImplementedError()
        identifiers = [int(identifier) for identifier in data.split('.')]

        first_subidentifier = (40 * identifiers[0] + identifiers[1])
        encoded_subidentifiers = self.encode_subidentifier(
            first_subidentifier)

        for identifier in identifiers[2:]:
            encoded_subidentifiers += self.encode_subidentifier(identifier)

        encoder.append_bytes([len(encoded_subidentifiers)])
        encoder.append_bytes(encoded_subidentifiers)

    def decode(self, decoder):
        raise NotImplementedError()
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

    def __init__(self, name, members, extension):
        super(Choice, self).__init__(name, 'CHOICE')
        self.members = members
        self.extension = extension
        self.number_of_bits = size_as_number_of_bits(len(members) - 1)

    def encode(self, data, encoder):
        if self.extension is not None:
            if len(self.extension) == 0:
                encoder.append_bit(0)
            else:
                raise NotImplementedError()

        for i, member in enumerate(self.members):
            if member.name in data:
                if len(self.members) > 1:
                    encoder.append_integer(i, self.number_of_bits)

                member.encode(data[member.name], encoder)
                return

        raise EncodeError(
            "Expected choices are {}, but got '{}'.".format(
                [member.name for member in self.members],
                ''.join([name for name in data])))

    def decode(self, decoder):
        if self.extension is not None:
            if len(self.extension) == 0:
                decoder.read_bit()
            else:
                raise NotImplementedError()

        if len(self.members) > 1:
            index = decoder.read_integer(self.number_of_bits)
        else:
            index = 0

        member = self.members[index]

        return {member.name: member.decode(decoder)}

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


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name, 'ENUMERATED')
        self.values = values
        self.lowest_value = min(values)
        highest_value = max(values.keys()) - self.lowest_value
        self.number_of_bits = size_as_number_of_bits(highest_value)

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


class ExplicitTag(Type):

    def __init__(self, name, inner):
        super(ExplicitTag, self).__init__(name, 'Tag')
        self.inner = inner

    def encode(self, data, encoder):
        raise NotImplementedError()

    def decode(self, decoder):
        raise NotImplementedError()

    def __repr__(self):
        return 'Tag()'


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

    def get_size_range(self, type_descriptor, module_name):
        """Returns a tuple of the minimum and maximum values allowed according
        the the ASN.1 specification SIZE parameter. Returns (None,
        None) if the type does not have a SIZE parameter.

        """

        size = type_descriptor.get('size', None)

        if size is None:
            minimum = None
            maximum = None
        elif isinstance(size, int):
            minimum = size
            maximum = size
        elif isinstance(size, list):
            if isinstance(size[0], tuple):
                minimum, maximum = size[0]
            else:
                minimum = size[0]
                maximum = size[0]
        else:
            raise NotImplementedError()

        try:
            minimum = self.lookup_value(minimum, module_name)[0]['value']
        except KeyError:
            pass

        try:
            maximum = self.lookup_value(maximum, module_name)[0]['value']
        except KeyError:
            pass

        return minimum, maximum

    def get_restricted_to_range(self, type_descriptor, module_name):
        restricted_to = type_descriptor.get('restricted-to', None)

        if restricted_to is None:
            minimum = None
            maximum = None
        elif isinstance(restricted_to, list):
            if isinstance(restricted_to[0], tuple):
                minimum, maximum = restricted_to[0]
            else:
                minimum = restricted_to[0]
                maximum = restricted_to[0]
        else:
            raise NotImplementedError()

        try:
            minimum = self.lookup_value(minimum, module_name)[0]['value']
        except KeyError:
            pass

        try:
            maximum = self.lookup_value(maximum, module_name)[0]['value']
        except KeyError:
            pass

        return minimum, maximum

    def compile_implicit_type(self, name, type_descriptor, module_name):
        if type_descriptor['type'] == 'SEQUENCE':
            members, extension = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Sequence(name,
                                members,
                                extension)
        elif type_descriptor['type'] == 'SEQUENCE OF':
            minimum, maximum = self.get_size_range(type_descriptor,
                                                   module_name)
            compiled = SequenceOf(name,
                                  self.compile_type('',
                                                    type_descriptor['element'],
                                                    module_name),
                                  minimum,
                                  maximum)
        elif type_descriptor['type'] == 'SET':
            members, extension = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Set(name,
                           members,
                           extension)
        elif type_descriptor['type'] == 'SET OF':
            compiled = SetOf(name,
                             self.compile_type('',
                                               type_descriptor['element'],
                                               module_name))
        elif type_descriptor['type'] == 'CHOICE':
            members, extension = self.compile_members(
                type_descriptor['members'],
                module_name)
            compiled = Choice(name,
                              members,
                              extension)
        elif type_descriptor['type'] == 'INTEGER':
            minimum, maximum = self.get_restricted_to_range(type_descriptor,
                                                            module_name)
            compiled = Integer(name, minimum, maximum)
        elif type_descriptor['type'] == 'ENUMERATED':
            compiled = Enumerated(name, type_descriptor['values'])
        elif type_descriptor['type'] == 'BOOLEAN':
            compiled = Boolean(name)
        elif type_descriptor['type'] == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_descriptor['type'] == 'OCTET STRING':
            minimum, maximum =self.get_size_range(type_descriptor,
                                                  module_name)
            compiled = OctetString(name, minimum, maximum)
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
            raise KeyError("Type '{}' not found.".format(type_name))

        return type_descriptor, module_name

    def lookup_value(self, value_name, module_name):
        module = self._specification[module_name]
        value = None

        if value_name in module['values']:
            value = module['values'][value_name]
        else:
            for from_module_name, imports in module['imports'].items():
                if value_name in imports:
                    from_module = self._specification[from_module_name]
                    value = from_module['values'][value_name]
                    module_name = from_module_name
                    break

        if value is None:
            raise KeyError("Value '{}' not found.".format(value_name))

        return value, module_name


def compile_dict(specification):
    return Compiler(specification).process()
