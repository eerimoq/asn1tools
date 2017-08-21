"""BER (Basic Encoding Rules) codec.

"""

from . import EncodeError, DecodeError, DecodeTagError


class Class(object):
    UNIVERSAL        = 0x00
    APPLICATION      = 0x40
    CONTEXT_SPECIFIC = 0x80
    PRIVATE          = 0xc0


class Encoding(object):
    PRIMITIVE   = 0x00
    CONSTRUCTED = 0x20


class Tag(object):
    END_OF_CONTENTS   = 0x00
    BOOLEAN           = 0x01
    INTEGER           = 0x02
    BIT_STRING        = 0x03
    OCTET_STRING      = 0x04
    NULL              = 0x05
    OBJECT_IDENTIFIER = 0x06
    OBJECT_DESCRIPTOR = 0x07
    EXTERNAL          = 0x08
    REAL              = 0x09
    ENUMERATED        = 0x0a
    EMBEDDED_PDV      = 0x0b
    UTF8_STRING       = 0x0c
    RELATIVE_OID      = 0x0d
    SEQUENCE          = 0x10
    SET               = 0x11
    NUMERIC_STRING    = 0x12
    PRINTABLE_STRING  = 0x13
    T61_STRING        = 0x14
    VIDEOTEX_STRING   = 0x15
    IA5_STRING        = 0x16
    UTC_TIME          = 0x17
    GENERALIZED_TIME  = 0x18
    GRAPHIC_STRING    = 0x19
    VISIBLE_STRING    = 0x1a
    GENERAL_STRING    = 0x1b
    UNIVERSAL_STRING  = 0x1c
    CHARACTER_STRING  = 0x1d
    BMP_STRING        = 0x1e


class DecodeChoiceError(Exception):
    pass


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

    def __init__(self, tag=None, optional=False, default=None):
        self.tag = tag
        self.optional = optional
        self.default = default

    def set_tag(self, tag):
        self.tag = tag


class Integer(Type):

    def __init__(self, name, **kwargs):
        super(Integer, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.INTEGER

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.extend(encode_signed_integer(data))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('INTEGER',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return decode_signed_integer(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name, **kwargs):
        super(Boolean, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.BOOLEAN

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(1)
        encoded.append(bool(data))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('BOOLEAN',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)

        if length != 1:
            raise DecodeError(
                'Expected one byte data but got {} at offset {}.'.format(
                    length,
                    offset))

        return (data[offset] != 0), offset + length

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name, **kwargs):
        super(IA5String, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.IA5_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('IA5String',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name, **kwargs):
        super(NumericString, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.NUMERIC_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('NumericString',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class Sequence(Type):

    def __init__(self, name, members, **kwargs):
        super(Sequence, self).__init__(**kwargs)
        self.name = name
        self.members = members
        self.tag = (Encoding.CONSTRUCTED | Tag.SEQUENCE)

    def set_tag(self, tag):
        self.tag = (Class.CONTEXT_SPECIFIC
                    | Encoding.CONSTRUCTED
                    | tag)

    def encode(self, data, encoded):
        encoded_members = bytearray()

        for member in self.members:
            name = member.name

            if name in data:
                member.encode(data[name], encoded_members)
            elif member.optional:
                pass
            elif member.default is not None:
                member.encode(member.default, encoded_members)
            else:
                raise EncodeError(
                    "Sequence member '{}' not found in {}.".format(
                        name,
                        data))

        encoded.append(self.tag)
        encoded.extend(encode_length_definite(len(encoded_members)))
        encoded.extend(encoded_members)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('SEQUENCE',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1

        if data[offset] == 0x80:
            raise NotImplementedError(
                'Decode until an end-of-contents tag is found.')
        else:
            length, offset = decode_length_definite(data, offset)

        if length > len(data) - offset:
            raise DecodeError(
                'Expected at least {} bytes data but got {} at offset {}.'.format(
                    length,
                    len(data) - offset,
                    offset))

        values = {}

        for member in self.members:
            try:
                value, offset = member.decode(data, offset)

            except DecodeError as e:
                if member.optional:
                    continue

                if member.default is None:
                    e.location.append(member.name)
                    raise

                value = member.default

            values[member.name] = value

        return values, offset

    def __repr__(self):
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Set(Sequence):
    pass


class SequenceOf(Type):

    def __init__(self, name, element_type, **kwargs):
        super(SequenceOf, self).__init__(**kwargs)
        self.name = name
        self.element_type = element_type
        self.tag = (Encoding.CONSTRUCTED | Tag.SEQUENCE)

    def encode(self, data, encoded):
        encoded_elements = bytearray()

        for entry in data:
            self.element_type.encode(entry, encoded_elements)

        encoded.append(self.tag)
        encoded.extend(encode_length_definite(len(encoded_elements)))
        encoded.extend(encoded_elements)

    def decode(self, data, offset):
        offset += 1
        length, offset = decode_length_definite(data, offset)
        decoded = []
        start_offset = offset

        while (offset - start_offset) < length:
            decoded_element, offset = self.element_type.decode(data, offset)
            decoded.append(decoded_element)

        return decoded, offset

    def __repr__(self):
        return 'SequenceOf({}, {})'.format(self.name,
                                           self.element_type)


class SetOf(Type):

    def __init__(self, name, element_type, **kwargs):
        super(SetOf, self).__init__(**kwargs)
        self.name = name
        self.element_type = element_type
        self.tag = (Encoding.CONSTRUCTED | Tag.SET)

    def encode(self, data, encoded):
        encoded_elements = bytearray()

        for entry in data:
            self.element_type.encode(entry, encoded_elements)

        encoded.append(self.tag)
        encoded.extend(encode_length_definite(len(encoded_elements)))
        encoded.extend(encoded_elements)

    def decode(self, data, offset):
        offset += 1
        length, offset = decode_length_definite(data, offset)
        decoded = []
        start_offset = offset

        while (offset - start_offset) < length:
            decoded_element, offset = self.element_type.decode(data, offset)
            decoded.append(decoded_element)

        return decoded, offset

    def __repr__(self):
        return 'SetOf({}, {})'.format(self.name,
                                      self.element_type)


class BitString(Type):

    def __init__(self, name, **kwargs):
        super(BitString, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.BIT_STRING

    def encode(self, data, encoded):
        number_of_unused_bits = (8 - (data[1] % 8))

        encoded.append(self.tag)
        encoded.append(len(data[0]) + 1)
        encoded.append(number_of_unused_bits)
        encoded.extend(data[0])

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('BIT STRING',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length
        number_of_bits = 8 * (length - 1) - data[offset]
        offset += 1

        return (bytearray(data[offset:offset_end]), number_of_bits), offset_end

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name, **kwargs):
        super(OctetString, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.OCTET_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('OCTET STRING',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name, **kwargs):
        super(PrintableString, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.PRINTABLE_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('PrintableString',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name, **kwargs):
        super(UniversalString, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.UNIVERSAL_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('UniversalString',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name, **kwargs):
        super(VisibleString, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.VISIBLE_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('VisibleString',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name, **kwargs):
        super(UTF8String, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.UTF8_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('UTF8String',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('utf-8'), offset_end

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name, **kwargs):
        super(BMPString, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.BMP_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('BMPString',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name, **kwargs):
        super(UTCTime, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.UTC_TIME

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('UTCTime',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end][:-1].decode('ascii'), offset_end

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name, **kwargs):
        super(GeneralizedTime, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.GENERALIZED_TIME

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('GeneralizedTime',
                                 self.tag,
                                 data[offset],
                                 offset)

        raise NotImplementedError()

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class T61String(Type):

    def __init__(self, name, **kwargs):
        super(T61String, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.T61_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('T61String',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'T61String({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name, **kwargs):
        super(ObjectIdentifier, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.OBJECT_IDENTIFIER

    def encode(self, data, encoded):
        identifiers = [int(identifier) for identifier in data.split('.')]

        first_subidentifier = (40 * identifiers[0] + identifiers[1])
        encoded_subidentifiers = self.encode_subidentifier(
            first_subidentifier)

        for identifier in identifiers[2:]:
            encoded_subidentifiers += self.encode_subidentifier(identifier)

        encoded.append(self.tag)
        encoded.append(len(encoded_subidentifiers))
        encoded.extend(encoded_subidentifiers)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('OBJECT IDENTIFIER',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        subidentifier, offset = self.decode_subidentifier(data, offset)
        decoded = [subidentifier // 40, subidentifier % 40]

        while offset < offset_end:
            subidentifier, offset = self.decode_subidentifier(data, offset)
            decoded.append(subidentifier)

        return '.'.join([str(v) for v in decoded]), offset_end

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

    def __init__(self, name, members, **kwargs):
        super(Choice, self).__init__(**kwargs)
        self.name = name
        self.members = members

    def encode(self, data, encoded):
        for member in self.members:
            if member.name in data:
                member.encode(data[member.name], encoded)
                return

        raise EncodeError(
            "Expected choices are {}, but got '{}'.".format(
                [member.name for member in self.members],
                ''.join([name for name in data])))

    def decode(self, data, offset):
        for member in self.members:
            if isinstance(member, Choice):
                try:
                    decoded, offset = member.decode(data, offset)
                    return {member.name: decoded}, offset
                except DecodeChoiceError:
                    pass
            elif member.tag == data[offset]:
                decoded, offset = member.decode(data, offset)
                return {member.name: decoded}, offset

        raise DecodeChoiceError()

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Null(Type):

    def __init__(self, name, **kwargs):
        super(Null, self).__init__(**kwargs)
        self.name = name
        self.tag = Tag.NULL

    def encode(self, _, encoded):
        encoded.append(self.tag)
        encoded.append(0)

    def decode(self, _, offset):
        return None, offset + 2

    def __repr__(self):
        return 'Null({})'.format(self.name)


ANY_CLASSES = {
    Tag.NULL: Null('any'),
    Tag.PRINTABLE_STRING: PrintableString('any'),
    Tag.IA5_STRING: IA5String('any'),
    Tag.UTF8_STRING: UTF8String('any')
}


class Any(Type):

    def __init__(self, name, **kwargs):
        super(Any, self).__init__(**kwargs)
        self.name = name

    def encode(self, _, encoded):
        pass

    def decode(self, data, offset):
        tag = data[offset]

        try:
            return ANY_CLASSES[tag].decode(data, offset)
        except KeyError:
            raise DecodeError('Any tag {} not supported'.format(tag))

    def __repr__(self):
        return 'Any({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values, **kwargs):
        super(Enumerated, self).__init__(**kwargs)
        self.name = name
        self.values = values
        self.tag = Tag.ENUMERATED

    def encode(self, data, encoded):
        for value, name in self.values.items():
            if data == name:
                encoded.append(self.tag)
                encoded.extend(encode_signed_integer(value))
                return

        raise EncodeError(
            "Enumeration value '{}' not found in {}.".format(
                data,
                [value for value in self.values.values()]))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError('ENUMERATED',
                                 self.tag,
                                 data[offset],
                                 offset)

        offset += 1
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length
        value = decode_signed_integer(data[offset:offset_end])

        return self.values[value], offset_end

    def __repr__(self):
        return 'Null({})'.format(self.name)


class CompiledType(object):

    def __init__(self, type_):
        self._type = type_

    def encode(self, data):
        encoded = bytearray()
        self._type.encode(data, encoded)
        return encoded

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

    def compile_type(self, name, type_descriptor, module_name):
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
            compiled = T61String(name)
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

        # Set any given tag.
        if 'tag' in type_descriptor:
            tag = type_descriptor['tag']
            value = 0

            if 'class' in tag:
                if tag['class'] != 'APPLICATION':
                    raise Exception()

                value = Class.APPLICATION

            value |= tag['number']
            compiled.set_tag(value)

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
