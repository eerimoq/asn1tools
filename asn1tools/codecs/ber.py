"""BER (Basic Encoding Rules) codec.

"""

import struct
import math

import bitstruct

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
        return bytearray([length])
    else:
        encoded = []

        while length > 0:
            encoded.append(length & 0xff)
            length >>= 8

        encoded.append(0x80 | len(encoded))

        return bytearray(encoded[::-1])


def _decode_integer(data):
    value = 0

    for byte in data:
        value <<= 8
        value += byte

    return value


def _decode_length_definite(encoded):
    length = encoded[0]

    if length & 0x80:
        number_of_bytes = (length & 0x7f)
        length = _decode_integer(encoded[:number_of_bytes])
    else:
        number_of_bytes = 0

    return length, encoded[1 + number_of_bytes:]


class Type(object):

    def __init__(self, tag=None, optional=False, default=None):
        self.tag = tag
        self.optional = optional
        self.default = default

    def set_tag(self, tag):
        self.tag = struct.pack('B', (Class.CONTEXT_SPECIFIC
                                     | Encoding.CONSTRUCTED
                                     | tag))


class Integer(Type):

    def __init__(self, name, **kwargs):
        super(Integer, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = struct.pack('B', Tag.INTEGER)

    def encode(self, data):
        if data == 0:
            bits = 8
        else:
            bits = int(8 * math.ceil((math.log(abs(data), 2) + 1) / 8))

        return bitstruct.pack('u8u8s' + str(bits),
                              Tag.INTEGER,
                              bits / 8,
                              data)

    def decode(self, data):
        if data[0:1] != self.tag:
            raise DecodeError()

        length, data = _decode_length_definite(data[1:])

        return _decode_integer(data[:length]), data[length:]

    def __repr__(self):
        return 'Integer({})'.format(self.name)


class Boolean(Type):

    def __init__(self, name, **kwargs):
        super(Boolean, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = struct.pack('B', Tag.BOOLEAN)

    def encode(self, data):
        return self.tag + bitstruct.pack('u8b8', 1, data)

    def decode(self, data):
        if data[0:1] != self.tag:
            raise DecodeError()

        length, data = _decode_length_definite(data[1:])

        if length != 1:
            raise DecodeError()

        return (data[0] != 0), data[length:]

    def __repr__(self):
        return 'Boolean({})'.format(self.name)


class IA5String(Type):

    def __init__(self, name, **kwargs):
        super(IA5String, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = struct.pack('B', Tag.IA5_STRING)

    def encode(self, data):
        return (self.tag
                + bitstruct.pack('u8', len(data))
                + data.encode('ascii'))

    def decode(self, data):
        if data[0:1] != self.tag:
            raise DecodeError()

        length, data = _decode_length_definite(data[1:])

        return data[:length].decode('ascii'), data[length:]

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class Sequence(Type):

    def __init__(self, name, members, **kwargs):
        super(Sequence, self).__init__(**kwargs)
        self.name = name
        self.members = members

        if self.tag is None:
            self.tag = struct.pack('B', (Encoding.CONSTRUCTED
                                         | Tag.SEQUENCE))

    def encode(self, data):
        encoded = b''

        for member in self.members:
            name = member.name

            if name in data:
                encoded += member.encode(data[name])
            elif member.optional:
                pass
            elif member.default is not None:
                encoded += member.encode(member.default)
            else:
                raise EncodeError(
                    "Value missing for sequence member '{}'.".format(
                        name))

        return (self.tag
                + _encode_length_definite(len(encoded))
                + encoded)

    def decode(self, data):
        if data[0:1] != self.tag:
            raise DecodeError()

        data = data[1:]

        if data[0:1] == b'\x80':
            # Decode until an end-of-contents tag is found.
            raise NotImplementedError()
        else:
            length, data = _decode_length_definite(data)

        if length > len(data):
            raise DecodeError()

        values = {}

        for member in self.members:
            try:
                value, data = member.decode(data)

            except DecodeError:
                if member.optional:
                    continue

                if member.default is None:
                    raise

                value = member.default

            values[member.name] = value

        return values, data

    def __repr__(self):
        return 'Sequence({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class SequenceOf(Type):

    def __init__(self, name, element_type, **kwargs):
        super(SequenceOf, self).__init__(**kwargs)
        self.name = name
        self.element_type = element_type

        if self.tag is None:
            self.tag = bytearray([Encoding.CONSTRUCTED
                                  | Tag.SEQUENCE])

    def encode(self, data):
        encoded = b''

        for entry in data:
            encoded += self.element_type.encode(entry)

        return (self.tag
                + _encode_length_definite(len(encoded))
                + encoded)

    def decode(self, data):
        length, data = _decode_length_definite(data[1:])
        decoded = []
        start_length = len(data)

        while (start_length - len(data)) < length:
            decoded_element, data = self.element_type.decode(data)
            decoded.append(decoded_element)

        return decoded, data

    def __repr__(self):
        return 'SequenceOf({}, {})'.format(self.name,
                                           self.element_type)


class OctetString(Type):

    def __init__(self, name, **kwargs):
        super(OctetString, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = bytearray([Tag.OCTET_STRING])

    def set_tag(self, tag):
        self.tag = struct.pack('B', tag)

    def encode(self, data):
        return self.tag + struct.pack('B', len(data)) + data

    def decode(self, data):
        if data[0:1] != self.tag:
            raise DecodeError()

        length, data = _decode_length_definite(data[1:])

        return bytes(data[:length]), data[length:]

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class ObjectIdentifier(Type):

    def __init__(self, name, **kwargs):
        super(ObjectIdentifier, self).__init__(**kwargs)
        self.name = name

        if self.tag is None:
            self.tag = struct.pack('B', Tag.OBJECT_IDENTIFIER)

    def encode(self, data):
        identifiers = [int(identifier) for identifier in data.split('.')]

        first_subidentifier = (40 * identifiers[0] + identifiers[1])
        encoded = self._encode_subidentifier(first_subidentifier)

        for identifier in identifiers[2:]:
            encoded += self._encode_subidentifier(identifier)

        return self.tag + bytearray([len(encoded)] + encoded)

    def decode(self, data):
        if data[0:1] != self.tag:
            raise DecodeError()

        length, data = _decode_length_definite(data[1:])
        rest = data[length:]
        data = data[:length]

        subidentifier, data = self._decode_subidentifier(data)
        decoded = [subidentifier // 40, subidentifier % 40]

        while len(data) > 0:
            subidentifier, data = self._decode_subidentifier(data)
            decoded.append(subidentifier)

        return '.'.join([str(v) for v in decoded]), rest

    def _encode_subidentifier(self, subidentifier):
        encoded = [subidentifier & 0x7f]
        subidentifier >>= 7

        while subidentifier > 0:
            encoded.append(0x80 | (subidentifier & 0x7f))
            subidentifier >>= 7

        return encoded[::-1]

    def _decode_subidentifier(self, data):
        i = 0
        decoded = 0

        while data[i] & 0x80:
            decoded += (data[i] & 0x7f)
            decoded <<= 7
            i += 1

        decoded += data[i]

        return decoded, data[i + 1:]

    def __repr__(self):
        return 'ObjectIdentifier({})'.format(self.name)


class Choice(Type):

    def __init__(self, name, members, **kwargs):
        super(Choice, self).__init__(**kwargs)
        self.name = name
        self.members = members

    def encode(self, data):
        for member in self.members:
            if member.name in data:
                return member.encode(data[member.name])

        raise EncodeError("No choice found.")

    def decode(self, data):
        for member in self.members:
            if isinstance(member, Choice):
                try:
                    decoded, data = member.decode(data)
                    return {member.name: decoded}, data
                except DecodeChoiceError:
                    pass
            elif member.tag == data[0:1]:
                decoded, data = member.decode(data)
                return {member.name: decoded}, data

        raise DecodeChoiceError()

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Null(Type):

    def __init__(self, name, **kwargs):
        super(Null, self).__init__(**kwargs)
        self.name = name

    def encode(self, _):
        return b''

    def decode(self, data):
        return None, data

    def __repr__(self):
        return 'Null({})'.format(self.name)


class CompiledType(object):

    def __init__(self, type_):
        self._type = type_

    def encode(self, data):
        return self._type.encode(data)

    def decode(self, data):
        return self._type.decode(bytearray(data))[0]

    def __repr__(self):
        return repr(self._type)


class Compiler(object):

    def __init__(self, specification):
        self._specification = specification

    def process(self):
        compiled_types = {
            module_name: {
                type_name: CompiledType(self.compile_type(type_name,
                                                          type_descriptor,
                                                          module_name))
                for type_name, type_descriptor
                in self._specification[module_name]['types'].items()
            }
            for module_name in self._specification
        }

        return compiled_types

    def compile_type(self, name, type_descriptor, module_name):
        """Convert type with given name to an encode/decode object and return
        it.

        """

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
            compiled = type_descriptor
        else:
            compiled = self.compile_type(
                name,
                *self.lookup_type_descriptor(
                    type_descriptor['type'],
                    module_name))

        # Set any given tag.
        if 'tag' in type_descriptor:
            tag = type_descriptor['tag']

            if isinstance(tag[0], tuple):
                if tag[0][0] != 'APPLICATION':
                    raise Exception()

                tag = (Class.APPLICATION | tag[0][1])
            else:
                tag = tag[0]

            compiled.set_tag(tag)

        return compiled

    def compile_members(self, members, module_name):
        """Convert a list of values from tokens to classes. Each value has a
        name and a data part.

        """

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
                compiled_member = member
            elif member['type'] == 'OCTET STRING':
                compiled_member = OctetString(member['name'],
                                              optional=member['optional'])
            elif member['type'] == 'INTEGER':
                compiled_member = member
            elif member['type'] == 'OBJECT IDENTIFIER':
                compiled_member = ObjectIdentifier(
                    member['name'],
                    optional=member['optional'])
            elif member['type'] == 'NULL':
                compiled_member = Null(member['name'])
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
