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

    def __init__(self, name, type_name, tag):
        self.name = name
        self.type_name = type_name
        self.tag = tag
        self.optional = None
        self.default = None

    def set_tag(self, tag):
        if Class.APPLICATION & tag:
            self.tag = tag
        else:
            self.tag = (Class.CONTEXT_SPECIFIC | tag)

    def decode_tag(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeTagError(self.type_name,
                                 self.tag,
                                 data[offset],
                                 offset)

        return offset + 1


class Integer(Type):

    def __init__(self, name):
        super(Integer, self).__init__(name, 'INTEGER', Tag.INTEGER)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.extend(encode_signed_integer(data))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return decode_signed_integer(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN', Tag.BOOLEAN)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(1)
        encoded.append(bool(data))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
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

    def __init__(self, name):
        super(IA5String, self).__init__(name,
                                        'IA5String',
                                        Tag.IA5_STRING)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name,
                                            'NumericString',
                                            Tag.NUMERIC_STRING)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'NumericString({})'.format(self.name)


class Sequence(Type):

    def __init__(self, name, members):
        super(Sequence, self).__init__(name,
                                       'SEQUENCE',
                                       Encoding.CONSTRUCTED | Tag.SEQUENCE)
        self.members = members

    def set_tag(self, tag):
        super(Sequence, self).set_tag(Encoding.CONSTRUCTED | tag)

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
        offset = self.decode_tag(data, offset)

        if data[offset] == 0x80:
            raise NotImplementedError(
                'Decode until an end-of-contents tag is found.')
        else:
            _, offset = decode_length_definite(data, offset)

        values = {}

        for member in self.members:
            try:
                value, offset = member.decode(data, offset)

            except (DecodeError, IndexError) as e:
                if member.optional:
                    continue

                if member.default is None:
                    if isinstance(e, IndexError):
                        e = DecodeError('out of data at offset {}'.format(offset))

                    e.location.append(member.name)
                    raise e

                value = member.default

            values[member.name] = value

        return values, offset

    def __repr__(self):
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Set(Type):

    def __init__(self, name, members):
        super(Set, self).__init__(name, 'SET', Encoding.CONSTRUCTED | Tag.SET)
        self.members = members

    def set_tag(self, tag):
        super(Set, self).set_tag(Encoding.CONSTRUCTED | tag)

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
                    "Set member '{}' not found in {}.".format(
                        name,
                        data))

        encoded.append(self.tag)
        encoded.extend(encode_length_definite(len(encoded_members)))
        encoded.extend(encoded_members)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)

        if data[offset] == 0x80:
            raise NotImplementedError(
                'Decode until an end-of-contents tag is found.')
        else:
            _, offset = decode_length_definite(data, offset)

        values = {}

        for member in self.members:
            try:
                value, offset = member.decode(data, offset)

            except (DecodeError, IndexError) as e:
                if member.optional:
                    continue

                if member.default is None:
                    if isinstance(e, IndexError):
                        e = DecodeError('out of data at offset {}'.format(offset))

                    e.location.append(member.name)
                    raise e

                value = member.default

            values[member.name] = value

        return values, offset

    def __repr__(self):
        return 'Set({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class SequenceOf(Type):

    def __init__(self, name, element_type):
        super(SequenceOf, self).__init__(name,
                                         'SEQUENCE OF',
                                         Encoding.CONSTRUCTED | Tag.SEQUENCE)
        self.element_type = element_type

    def set_tag(self, tag):
        super(SequenceOf, self).set_tag(Encoding.CONSTRUCTED | tag)

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

    def __init__(self, name, element_type):
        super(SetOf, self).__init__(name,
                                    'SET OF',
                                    Encoding.CONSTRUCTED | Tag.SET)
        self.element_type = element_type

    def set_tag(self, tag):
        super(SetOf, self).set_tag(Encoding.CONSTRUCTED | tag)

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

    def __init__(self, name):
        super(BitString, self).__init__(name, 'BIT STRING', Tag.BIT_STRING)

    def encode(self, data, encoded):
        number_of_unused_bits = (8 - (data[1] % 8))

        if number_of_unused_bits == 8:
            number_of_unused_bits = 0

        encoded.append(self.tag)
        encoded.append(len(data[0]) + 1)
        encoded.append(number_of_unused_bits)
        encoded.extend(data[0])

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length
        number_of_bits = 8 * (length - 1) - data[offset]
        offset += 1

        return (bytearray(data[offset:offset_end]), number_of_bits), offset_end

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name,
                                          'OCTET STRING',
                                          Tag.OCTET_STRING)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name,
                                              'PrintableString',
                                              Tag.PRINTABLE_STRING)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name,
                                              'UniversalString',
                                              Tag.UNIVERSAL_STRING)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name):
        super(VisibleString, self).__init__(name,
                                            'VisibleString',
                                            Tag.VISIBLE_STRING)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name,
                                         'UTF8String',
                                         Tag.UTF8_STRING)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('utf-8'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('utf-8'), offset_end

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name,
                                        'BMPString',
                                        Tag.BMP_STRING)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'BMPString({})'.format(self.name)


class UTCTime(Type):

    def __init__(self, name):
        super(UTCTime, self).__init__(name,
                                      'UTCTime',
                                      Tag.UTC_TIME)

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(13)
        encoded.extend(bytearray((data + 'Y').encode('ascii')))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end][:-1].decode('ascii'), offset_end

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
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

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

        encoded.append(self.tag)
        encoded.append(len(encoded_subidentifiers))
        encoded.extend(encoded_subidentifiers)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
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

    def __init__(self, name, members):
        super(Choice, self).__init__(name, 'CHOICE', None)
        self.members = members

    def set_tag(self, tag):
        super(Choice, self).set_tag(Encoding.CONSTRUCTED | tag)

    def encode(self, data, encoded):
        for member in self.members:
            if member.name in data:
                if self.tag is None:
                    member.encode(data[member.name], encoded)
                else:
                    encoded_members = bytearray()
                    member.encode(data[member.name], encoded_members)
                    encoded.append(self.tag)
                    encoded.extend(encode_length_definite(len(encoded_members)))
                    encoded.extend(encoded_members)

                return

        raise EncodeError(
            "Expected choices are {}, but got '{}'.".format(
                [member.name for member in self.members],
                ''.join([name for name in data])))

    def decode(self, data, offset):
        if self.tag is not None:
            offset = self.decode_tag(data, offset)
            _, offset = decode_length_definite(data, offset)

        for member in self.members:
            if member.tag == data[offset] or isinstance(member, Choice):
                try:
                    decoded, offset = member.decode(data, offset)
                except DecodeChoiceError:
                    pass
                else:
                    return {member.name: decoded}, offset

        raise DecodeChoiceError()

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Null(Type):

    def __init__(self, name):
        super(Null, self).__init__(name, 'NULL', Tag.NULL)

    def encode(self, _, encoded):
        encoded.append(self.tag)
        encoded.append(0)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)

        return None, offset + 1

    def __repr__(self):
        return 'Null({})'.format(self.name)


ANY_CLASSES = {
    Tag.NULL: Null('any'),
    Tag.PRINTABLE_STRING: PrintableString('any'),
    Tag.IA5_STRING: IA5String('any'),
    Tag.UTF8_STRING: UTF8String('any')
}


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY', None)

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

    def __init__(self, name, values):
        super(Enumerated, self).__init__(name,
                                         'ENUMERATED',
                                         Tag.ENUMERATED)
        self.values = values

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
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        offset_end = offset + length
        value = decode_signed_integer(data[offset:offset_end])

        return self.values[value], offset_end

    def __repr__(self):
        return 'Null({})'.format(self.name)


class ExplicitTag(Type):

    def __init__(self, name, inner):
        super(ExplicitTag, self).__init__(name, 'Tag', None)
        self.inner = inner

    def set_tag(self, tag):
        super(ExplicitTag, self).set_tag(Encoding.CONSTRUCTED | tag)

    def encode(self, data, encoded):
        encoded_inner = bytearray()
        self.inner.encode(data, encoded_inner)
        encoded.append(self.tag)
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

        if self.is_explicit_tag(type_descriptor, module_name):
            compiled = ExplicitTag(name, compiled)

        # Set any given tag.
        if 'tag' in type_descriptor:
            tag = type_descriptor['tag']
            value = 0

            class_ = tag.get('class', None)

            if class_ == 'APPLICATION':
                value = Class.APPLICATION
            elif class_ == 'PRIVATE':
                value = Class.PRIVATE

            value |= tag['number']
            compiled.set_tag(value)

        return compiled

    def compile_members(self, members, module_name):
        compiled_members = []

        tags = self._specification[module_name].get('tags', None)

        if tags == 'AUTOMATIC':
            tag = 0
        else:
            tag = None

        for member in members:
            if member['name'] == '...':
                continue

            compiled_member = self.compile_type(member['name'],
                                                member,
                                                module_name)
            compiled_member.optional = member['optional']

            if 'default' in member:
                compiled_member.default = member['default']

            if tag is not None:
                compiled_member.set_tag(tag)
                tag += 1

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


def compile_dict(specification):
    return Compiler(specification).process()
