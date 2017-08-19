"""BER (Basic Encoding Rules) codec.

"""

from . import EncodeError, DecodeError


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


def _encode_length_definite(length):
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


def _decode_integer(data):
    value = 0

    for byte in data:
        value <<= 8
        value += byte

    return value


def _encode_signed_integer(data):
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


def _decode_signed_integer(data):
    value = 0
    is_negative = (data[0] & 0x80)

    for byte in data:
        value <<= 8
        value += byte

    if is_negative:
        value -= (1 << (8 * len(data)))

    return value


def _decode_length_definite(encoded, offset):
    length = encoded[offset]
    offset += 1

    if length & 0x80:
        number_of_bytes = (length & 0x7f)
        length = _decode_integer(
            encoded[offset:number_of_bytes + offset])
    else:
        number_of_bytes = 0

    return length, offset + number_of_bytes


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

        if self.tag is None:
            self.tag = Tag.INTEGER

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.extend(_encode_signed_integer(data))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeError()

        offset += 1
        length, offset = _decode_length_definite(data, offset)
        offset_end = offset + length

        return _decode_signed_integer(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name, **kwargs):
        super(Boolean, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = Tag.BOOLEAN

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(1)
        encoded.append(bool(data))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeError()

        offset += 1
        length, offset = _decode_length_definite(data, offset)

        if length != 1:
            raise DecodeError()

        return (data[offset] != 0), offset + length

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name, **kwargs):
        super(IA5String, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = Tag.IA5_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeError()

        offset += 1
        length, offset = _decode_length_definite(data, offset)
        offset_end = offset + length

        return data[offset:offset_end].decode('ascii'), offset_end

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class Sequence(Type):

    def __init__(self, name, members, **kwargs):
        super(Sequence, self).__init__(**kwargs)
        self.name = name
        self.members = members

        if self.tag is None:
            self.tag = (Encoding.CONSTRUCTED
                        | Tag.SEQUENCE)

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
                    "Sequence member '{}' not found in '{}'.".format(
                        name,
                        data))

        encoded.append(self.tag)
        encoded.extend(_encode_length_definite(len(encoded_members)))
        encoded.extend(encoded_members)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeError()

        offset += 1

        if data[offset] == 0x80:
            # Decode until an end-of-contents tag is found.
            raise NotImplementedError()
        else:
            length, offset = _decode_length_definite(data, offset)

        if length > len(data) - offset:
            raise DecodeError()

        values = {}

        for member in self.members:
            try:
                value, offset = member.decode(data, offset)

            except DecodeError:
                if member.optional:
                    continue

                if member.default is None:
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

        if self.tag is None:
            self.tag = (Encoding.CONSTRUCTED
                        | Tag.SEQUENCE)

    def encode(self, data, encoded):
        encoded_elements = bytearray()

        for entry in data:
            self.element_type.encode(entry, encoded_elements)

        encoded.append(self.tag)
        encoded.extend(_encode_length_definite(len(encoded_elements)))
        encoded.extend(encoded_elements)

    def decode(self, data, offset):
        offset += 1
        length, offset = _decode_length_definite(data, offset)
        decoded = []
        start_offset = offset

        while (offset - start_offset) < length:
            decoded_element, offset = self.element_type.decode(data, offset)
            decoded.append(decoded_element)

        return decoded, offset

    def __repr__(self):
        return 'SequenceOf({}, {})'.format(self.name,
                                           self.element_type)


class BitString(Type):

    def __init__(self, name, **kwargs):
        super(BitString, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = Tag.BIT_STRING

    def encode(self, data, encoded):
        number_of_unused_bits = (8 - (data[1] % 8))

        encoded.append(self.tag)
        encoded.append(len(data[0]) + 1)
        encoded.append(number_of_unused_bits)
        encoded.extend(data[0])

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeError()

        offset += 1
        length, offset = _decode_length_definite(data, offset)
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

        if self.tag is None:
            self.tag = Tag.OCTET_STRING

    def encode(self, data, encoded):
        encoded.append(self.tag)
        encoded.append(len(data))
        encoded.extend(data)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeError()

        offset += 1
        length, offset = _decode_length_definite(data, offset)
        offset_end = offset + length

        return bytearray(data[offset:offset_end]), offset_end

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name, **kwargs):
        super(ObjectIdentifier, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = Tag.OBJECT_IDENTIFIER

    def encode(self, data, encoded):
        identifiers = [int(identifier) for identifier in data.split('.')]

        first_subidentifier = (40 * identifiers[0] + identifiers[1])
        encoded_subidentifiers = self._encode_subidentifier(
            first_subidentifier)

        for identifier in identifiers[2:]:
            encoded_subidentifiers += self._encode_subidentifier(identifier)

        encoded.append(self.tag)
        encoded.append(len(encoded_subidentifiers))
        encoded.extend(encoded_subidentifiers)

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeError()

        offset += 1
        length, offset = _decode_length_definite(data, offset)
        offset_end = offset + length

        subidentifier, offset = self._decode_subidentifier(data, offset)
        decoded = [subidentifier // 40, subidentifier % 40]

        while offset < offset_end:
            subidentifier, offset = self._decode_subidentifier(data, offset)
            decoded.append(subidentifier)

        return '.'.join([str(v) for v in decoded]), offset_end

    def _encode_subidentifier(self, subidentifier):
        encoded = [subidentifier & 0x7f]
        subidentifier >>= 7

        while subidentifier > 0:
            encoded.append(0x80 | (subidentifier & 0x7f))
            subidentifier >>= 7

        return encoded[::-1]

    def _decode_subidentifier(self, data, offset):
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

        if self.tag is None:
            self.tag = Tag.NULL

    def encode(self, _, encoded):
        encoded.append(self.tag)
        encoded.append(0)

    def decode(self, _, offset):
        return None, offset + 2

    def __repr__(self):
        return 'Null({})'.format(self.name)


class Enumerated(Type):

    def __init__(self, name, values, **kwargs):
        super(Enumerated, self).__init__(**kwargs)
        self.name = name
        self.values = values

        if self.tag is None:
            self.tag = Tag.ENUMERATED

    def encode(self, data, encoded):
        for value, name in self.values.items():
            if data == name:
                encoded.append(self.tag)
                encoded.extend(_encode_signed_integer(value))
                return

        raise EncodeError(
            "Enumeration value '{}' not found in {}.".format(
                data,
                [value for value in self.values.values()]))

    def decode(self, data, offset):
        if data[offset] != self.tag:
            raise DecodeError()

        offset += 1
        length, offset = _decode_length_definite(data, offset)
        offset_end = offset + length
        value = _decode_signed_integer(data[offset:offset_end])

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
        compiled_types = {
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

        return compiled_types

    def compile_type(self, name, type_descriptor, module_name):
        if type_descriptor['type'] == 'SEQUENCE':
            compiled = Sequence(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_descriptor['type'] == 'CHOICE':
            compiled = Choice(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
        elif type_descriptor['type'] == 'OCTET STRING':
            compiled = OctetString(name)
        elif type_descriptor['type'] == 'INTEGER':
            compiled = Integer(name)
        elif type_descriptor['type'] == 'OBJECT IDENTIFIER':
            compiled = ObjectIdentifier(name)
        elif type_descriptor['type'] == 'SEQUENCE OF':
            compiled = SequenceOf(name,
                                  self.compile_type(
                                      '',
                                      *self.lookup_type_descriptor(
                                          type_descriptor['element_type'],
                                          module_name)))
        elif type_descriptor['type'] == 'NULL':
            compiled = Null(name)
        elif type_descriptor['type'] == 'TeletexString':
            compiled = Null(name)
        elif type_descriptor['type'] == 'SET':
            compiled = Set(
                name,
                self.compile_members(type_descriptor['members'],
                                     module_name))
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
            if member['type'] == 'INTEGER':
                compiled_member = Integer(member['name'],
                                          optional=member['optional'])
            elif member['type'] == 'BOOLEAN':
                compiled_member = Boolean(member['name'],
                                          optional=member['optional'])
            elif member['type'] == 'IA5String':
                compiled_member = IA5String(member['name'],
                                            optional=member['optional'])
            elif member['type'] == 'BIT STRING':
                compiled_member = BitString(member['name'],
                                            optional=member['optional'])
            elif member['type'] == 'OCTET STRING':
                compiled_member = OctetString(member['name'],
                                              optional=member['optional'])
            elif member['type'] == 'OBJECT IDENTIFIER':
                compiled_member = ObjectIdentifier(
                    member['name'],
                    optional=member['optional'])
            elif member['type'] == 'NULL':
                compiled_member = Null(member['name'])
            elif member['type'] == 'ENUMERATED':
                compiled_member = Enumerated(member['name'],
                                             member['values'],
                                             optional=member['optional'])
            elif member['type'] == 'SEQUENCE':
                compiled_member = Sequence(
                    member['name'],
                    self.compile_members(member['members'],
                                         module_name),
                    optional=member['optional'])
            elif member['type'] == 'SEQUENCE OF':
                compiled_member = SequenceOf(member['name'],
                                             self.compile_type(
                                                 '',
                                                 *self.lookup_type_descriptor(
                                                     member['element_type'],
                                                     module_name)))
            else:
                compiled_member = self.compile_type(
                    member['name'],
                    *self.lookup_type_descriptor(
                        member['type'],
                        module_name))

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
