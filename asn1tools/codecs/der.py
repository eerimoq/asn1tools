"""Basic Encoding Rules (DER) codec.

"""

from . import EncodeError, DecodeError, DecodeTagError
from . import compiler


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
    value = 0
    is_negative = (data[0] & 0x80)

    for byte in data:
        value <<= 8
        value += byte

    if is_negative:
        value -= (1 << (8 * len(data)))

    return value


def decode_tag(_data, offset):
    return 0, 0, offset + 1


class Type(object):

    def __init__(self, name, type_name, number, flags=0):
        self.name = name
        self.type_name = type_name

        if number is None:
            self.tag = None
        elif number < 31:
            self.tag = bytearray([flags | number])
        else:
            self.tag = bytearray([flags | 0x1f]) + encode_length_definite(number)

        self.optional = None
        self.default = None

    def set_tag(self, number, flags):
        if not Class.APPLICATION & flags:
            flags |= Class.CONTEXT_SPECIFIC

        if number < 31:
            self.tag = bytearray([flags | number])
        else:
            self.tag = bytearray([flags | 0x1f]) + encode_length_definite(number)

    def decode_tag(self, data, offset):
        end = offset + len(self.tag)

        if data[offset:end] != self.tag:
            raise DecodeTagError(self.type_name,
                                 self.tag,
                                 data[offset:end],
                                 offset)

        return end


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name,
                                      'INTEGER',
                                      Tag.INTEGER)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_signed_integer(data))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return decode_signed_integer(data[offset:end]), end

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Real(Type):

    def __init__(self, name):
        super(Real, self).__init__(name, 'REAL', Tag.REAL)

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        raise NotImplementedError()

    def __repr__(self):
        return 'Real({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name,
                                      'BOOLEAN',
                                      Tag.BOOLEAN)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(1)
        encoded.append(bool(data))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)

        if length != 1:
            raise DecodeError(
                'expected one byte data but got {} at offset {}'.format(
                    length,
                    offset))

        return (data[offset] != 0), offset + length

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name):
        super(IA5String, self).__init__(name,
                                        'IA5String',
                                        Tag.IA5_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return data[offset:end].decode('ascii'), end

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name,
                                            'NumericString',
                                            Tag.NUMERIC_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return data[offset:end].decode('ascii'), end

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class MembersType(Type):

    def __init__(self, name, tag_name, tag, members):
        super(MembersType, self).__init__(name,
                                          tag_name,
                                          tag,
                                          Encoding.CONSTRUCTED)
        self.members = members

    def set_tag(self, number, flags):
        super(MembersType, self).set_tag(number,
                                         flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        encoded_members = bytearray()

        for memder in self.members:
            name = memder.name

            if name in data:
                if isinstance(memder, AnyDefinedBy):
                    memder.encode(data[name], encoded_members, data)
                else:
                    memder.encode(data[name], encoded_members)
            elif memder.optional:
                pass
            elif memder.default is None:
                raise EncodeError(
                    "memder '{}' not found in {}".format(
                        name,
                        data))

        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(encoded_members)))
        encoded.extend(encoded_members)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)

        if data[offset] == 0x80:
            raise NotImplementedError(
                'decode until an end-of-contents tag is found')
        else:
            _, offset = decode_length_definite(data, offset)

        values = {}

        for memder in self.members:
            try:
                if isinstance(memder, AnyDefinedBy):
                    value, offset = memder.decode(data, offset, values)
                else:
                    value, offset = memder.decode(data, offset)
            except (DecodeError, IndexError) as e:
                if memder.optional:
                    continue

                if memder.default is None:
                    if isinstance(e, IndexError):
                        e = DecodeError('out of data at offset {}'.format(offset))

                    e.location.append(memder.name)
                    raise e

                value = memder.default

            values[memder.name] = value

        return values, offset

    def __repr__(self):
        return '{}({}, [{}])'.format(
            self.__class__.__name__,
            self.name,
            ', '.join([repr(memder) for memder in self.members]))


class Sequence(MembersType):

    def __init__(self, name, members):
        super(Sequence, self).__init__(name, 'SEQUENCE', Tag.SEQUENCE, members)


class Set(MembersType):

    def __init__(self, name, members):
        super(Set, self).__init__(name, 'SET', Tag.SET, members)


class ArrayType(Type):

    def __init__(self, name, tag_name, tag, element_type):
        super(ArrayType, self).__init__(name,
                                        tag_name,
                                        tag,
                                        Encoding.CONSTRUCTED)
        self.element_type = element_type

    def set_tag(self, number, flags):
        super(ArrayType, self).set_tag(number,
                                       flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        encoded_elements = bytearray()

        for entry in data:
            self.element_type.encode(entry, encoded_elements)

        encoded.extend(self.tag)
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
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.name,
                                   self.element_type)


class SequenceOf(ArrayType):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name,
                                         'SEQUENCE OF',
                                         Tag.SEQUENCE,
                                         element_type)


class SetOf(ArrayType):

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name,
                                    'SET OF',
                                    Tag.SET,
                                    element_type)


class BitString(Type):

    def __init__(self, name):
        super(BitString, self).__init__(name,
                                        'BIT STRING',
                                        Tag.BIT_STRING)

    def encode(self, data, encoded):
        number_of_unused_bits = (8 - (data[1] % 8))

        if number_of_unused_bits == 8:
            number_of_unused_bits = 0

        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data[0]) + 1))
        encoded.append(number_of_unused_bits)
        encoded.extend(data[0])

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length
        number_of_bits = 8 * (length - 1) - data[offset]
        offset += 1

        return (bytearray(data[offset:end]), number_of_bits), end

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name,
                                          'OCTET STRING',
                                          Tag.OCTET_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return bytearray(data[offset:end]), end

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name,
                                              'PrintableString',
                                              Tag.PRINTABLE_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return data[offset:end].decode('ascii'), end

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name,
                                              'UniversalString',
                                              Tag.UNIVERSAL_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return data[offset:end].decode('ascii'), end

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name):
        super(VisibleString, self).__init__(name,
                                            'VisibleString',
                                            Tag.VISIBLE_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return data[offset:end].decode('ascii'), end

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name,
                                         'UTF8String',
                                         Tag.UTF8_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('utf-8'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return data[offset:end].decode('utf-8'), end

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name,
                                        'BMPString',
                                        Tag.BMP_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return bytearray(data[offset:end]), end

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name,
                                      'UTCTime',
                                      Tag.UTC_TIME)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(13)
        encoded.extend(bytearray((data + 'Z').encode('ascii')))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return data[offset:end][:-1].decode('ascii'), end

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name,
                                              'GeneralizedTime',
                                              Tag.GENERALIZED_TIME)

    def encode(self, data, encoded):
        raise NotImplementedError()

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)

        raise NotImplementedError()

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name,
                                            'TeletexString',
                                            Tag.T61_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return bytearray(data[offset:end]), end

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name):
        super(ObjectIdentifier, self).__init__(name,
                                               'OBJECT IDENTIFIER',
                                               Tag.OBJECT_IDENTIFIER)

    def encode(self, data, encoded):
        identifiers = [int(identifier) for identifier in data.split('.')]

        first_subidentifier = (40 * identifiers[0] + identifiers[1])
        encoded_subidentifiers = self.encode_subidentifier(
            first_subidentifier)

        for identifier in identifiers[2:]:
            encoded_subidentifiers += self.encode_subidentifier(identifier)

        encoded.extend(self.tag)
        encoded.append(len(encoded_subidentifiers))
        encoded.extend(encoded_subidentifiers)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        subidentifier, offset = self.decode_subidentifier(data, offset)
        decoded = [subidentifier // 40, subidentifier % 40]

        while offset < end:
            subidentifier, offset = self.decode_subidentifier(data, offset)
            decoded.append(subidentifier)

        return '.'.join([str(v) for v in decoded]), end

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
        super(Choice, self).__init__(name, 'CHOICE', None)
        self.members = members

    def set_tag(self, number, flags):
        super(Choice, self).set_tag(number,
                                    flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        for memder in self.members:
            if memder.name in data:
                if self.tag is None:
                    memder.encode(data[memder.name], encoded)
                else:
                    encoded_members = bytearray()
                    memder.encode(data[memder.name], encoded_members)
                    encoded.extend(self.tag)
                    encoded.extend(encode_length_definite(len(encoded_members)))
                    encoded.extend(encoded_members)

                return

        raise EncodeError(
            "expected choices are {}, but got '{}'".format(
                [memder.name for memder in self.members],
                ''.join([name for name in data])))

    def decode(self, data, offset):
        if self.tag is not None:
            offset = self.decode_tag(data, offset)
            _, offset = decode_length_definite(data, offset)

        for memder in self.members:
            if (isinstance(memder, Choice)
                or memder.tag == data[offset:offset + len(memder.tag)]):
                try:
                    decoded, offset = memder.decode(data, offset)
                except DecodeChoiceError:
                    pass
                else:
                    return {memder.name: decoded}, offset

        raise DecodeChoiceError()

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(memder) for memder in self.members]))


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL', Tag.NULL)

    def encode(self, _, encoded):
        encoded.extend(self.tag)
        encoded.append(0)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)

        return None, offset + 1

    def __repr__(self):
        return 'Null({})'.format(self.name)


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY', None)

    def encode(self, data, encoded):
        encoded.extend(data)

    def decode(self, data, offset):
        start = offset
        _, _, offset = decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length

        return data[start:end], end

    def __repr__(self):
        return 'Any({})'.format(self.name)


class AnyDefinedBy(Type):

    def __init__(self, name, type_memder, choices):
        super(AnyDefinedBy, self).__init__(name,
                                           'ANY DEFINED BY',
                                           None,
                                           None)
        self.type_memder = type_memder
        self.choices = choices

    def encode(self, data, encoded, values):
        if self.choices:
            self.choices[values[self.type_memder]].encode(data, encoded)
        else:
            encoded.extend(data)

    def decode(self, data, offset, values):
        if self.choices:
            return self.choices[values[self.type_memder]].decode(data,
                                                                 offset)
        else:
            start = offset
            _, _, offset = decode_tag(data, offset)
            length, offset = decode_length_definite(data, offset)
            end = offset + length

            return data[start:end], end

    def __repr__(self):
        return 'AnyDefinedBy({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name,
                                         'ENUMERATED',
                                         Tag.ENUMERATED)
        self.values = values

    def encode(self, data, encoded):
        for value, name in self.values.items():
            if data == name:
                encoded.extend(self.tag)
                encoded.extend(encode_signed_integer(value))
                return

        raise EncodeError(
            "enumeration value '{}' not found in {}".format(
                data,
                [value for value in self.values.values()]))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end = offset + length
        value = decode_signed_integer(data[offset:end])

        return self.values[value], end

    def __repr__(self):
        return 'Enumerated({})'.format(self.name)


class ExplicitTag(Type):

    def __init__(self, name, inner):
        super(ExplicitTag, self).__init__(name, 'Tag', None)
        self.inner = inner

    def set_tag(self, number, flags):
        super(ExplicitTag, self).set_tag(number,
                                         flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        encoded_inner = bytearray()
        self.inner.encode(data, encoded_inner)
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(encoded_inner)))
        encoded.extend(encoded_inner)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        _, offset = decode_length_definite(data, offset)
        return self.inner.decode(data, offset)

    def __repr__(self):
        return 'Tag()'


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
        elif type_descriptor['type'] == 'REAL':
            compiled = Real(name)
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
            choices = {}

            for key, value in type_descriptor['choices'].items():
                choices[key] = self.compile_type(key,
                                                 value,
                                                 module_name)

            compiled = AnyDefinedBy(name,
                                    type_descriptor['value'],
                                    choices)
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

        if self.is_explicit_tag(type_descriptor, module_name):
            compiled = ExplicitTag(name, compiled)

        # Set any given tag.
        if 'tag' in type_descriptor:
            tag = type_descriptor['tag']
            class_ = tag.get('class', None)

            if class_ == 'APPLICATION':
                flags = Class.APPLICATION
            elif class_ == 'PRIVATE':
                flags = Class.PRIVATE
            else:
                flags = 0

            compiled.set_tag(tag['number'], flags)

        return compiled

    def compile_members(self, members, module_name):
        compiled_members = []

        tags = self._specification[module_name].get('tags', None)

        if tags == 'AUTOMATIC':
            tag = 0
        else:
            tag = None

        for memder in members:
            if memder['name'] == '...':
                continue

            compiled_memder = self.compile_type(memder['name'],
                                                memder,
                                                module_name)
            compiled_memder.optional = memder['optional']

            if 'default' in memder:
                compiled_memder.default = memder['default']

            if tag is not None:
                compiled_memder.set_tag(tag, 0)
                tag += 1

            compiled_members.append(compiled_memder)

        return compiled_members


def compile_dict(specification):
    return Compiler(specification).process()
