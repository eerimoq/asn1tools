"""Distinguished Encoding Rules (DER) codec.

"""

from . import EncodeError
from . import DecodeError
from . import DecodeTagError
from . import DecodeContentsLengthError
from . import compiler
from .compiler import enum_values_as_dict
from .ber import Class
from .ber import Encoding
from .ber import Tag
from .ber import encode_length_definite
from .ber import decode_length_definite
from .ber import encode_signed_integer
from .ber import decode_signed_integer
from .ber import encode_tag
from .ber import decode_tag
from .ber import Boolean
from .ber import Enumerated
from .ber import Null
from .ber import ObjectIdentifier


class DecodeChoiceError(Exception):
    pass


class Type(object):

    def __init__(self, name, type_name, number, flags=0):
        self.name = name
        self.type_name = type_name

        if number is None:
            self.tag = None
        else:
            self.tag = encode_tag(number, flags)

        self.optional = False
        self.default = None

    def set_tag(self, number, flags):
        if not Class.APPLICATION & flags:
            flags |= Class.CONTEXT_SPECIFIC

        self.tag = encode_tag(number, flags)

    def decode_tag(self, data, offset):
        end_offset = offset + len(self.tag)

        if data[offset:end_offset] != self.tag:
            raise DecodeTagError(self.type_name,
                                 self.tag,
                                 data[offset:end_offset],
                                 offset)

        return end_offset


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
        end_offset = offset + length

        return decode_signed_integer(data[offset:end_offset]), end_offset

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


class IA5String(Type):

    def __init__(self, name):
        super(IA5String, self).__init__(name,
                                        'IA5String',
                                        Tag.IA5_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

    def __repr__(self):
        return 'IA5String({})'.format(self.name)


class NumericString(Type):

    def __init__(self, name):
        super(NumericString, self).__init__(name,
                                            'NumericString',
                                            Tag.NUMERIC_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

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

        for member in self.members:
            name = member.name

            if name in data:
                value = data[name]

                if isinstance(member, AnyDefinedBy):
                    member.encode(value, encoded_members, data)
                elif member.default != value or isinstance(member, Null):
                    member.encode(value, encoded_members)
            elif member.optional:
                pass
            elif member.default is None:
                raise EncodeError(
                    "member '{}' not found in {}".format(
                        name,
                        data))

        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(encoded_members)))
        encoded.extend(encoded_members)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length
        values = {}

        for member in self.members:
            try:
                if offset < end_offset:
                    if isinstance(member, AnyDefinedBy):
                        value, offset = member.decode(data, offset, values)
                    else:
                        value, offset = member.decode(data, offset)
                else:
                    raise IndexError
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
        return '{}({}, [{}])'.format(
            self.__class__.__name__,
            self.name,
            ', '.join([repr(member) for member in self.members]))


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
        offset = self.decode_tag(data, offset)
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
        end_offset = offset + length
        number_of_bits = 8 * (length - 1) - data[offset]
        offset += 1

        return (bytearray(data[offset:end_offset]), number_of_bits), end_offset

    def __repr__(self):
        return 'BitString({})'.format(self.name)


class OctetString(Type):

    def __init__(self, name):
        super(OctetString, self).__init__(name,
                                          'OCTET STRING',
                                          Tag.OCTET_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return bytearray(data[offset:end_offset]), end_offset

    def __repr__(self):
        return 'OctetString({})'.format(self.name)


class PrintableString(Type):

    def __init__(self, name):
        super(PrintableString, self).__init__(name,
                                              'PrintableString',
                                              Tag.PRINTABLE_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

    def __repr__(self):
        return 'PrintableString({})'.format(self.name)


class UniversalString(Type):

    def __init__(self, name):
        super(UniversalString, self).__init__(name,
                                              'UniversalString',
                                              Tag.UNIVERSAL_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

    def __repr__(self):
        return 'UniversalString({})'.format(self.name)


class VisibleString(Type):

    def __init__(self, name):
        super(VisibleString, self).__init__(name,
                                            'VisibleString',
                                            Tag.VISIBLE_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

    def __repr__(self):
        return 'VisibleString({})'.format(self.name)


class GeneralString(Type):

    def __init__(self, name):
        super(GeneralString, self).__init__(name,
                                            'GeneralString',
                                            Tag.GENERAL_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

    def __repr__(self):
        return 'GeneralString({})'.format(self.name)


class UTF8String(Type):

    def __init__(self, name):
        super(UTF8String, self).__init__(name,
                                         'UTF8String',
                                         Tag.UTF8_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data.encode('utf-8'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('utf-8'), end_offset

    def __repr__(self):
        return 'UTF8String({})'.format(self.name)


class BMPString(Type):

    def __init__(self, name):
        super(BMPString, self).__init__(name,
                                        'BMPString',
                                        Tag.BMP_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return bytearray(data[offset:end_offset]), end_offset

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
        end_offset = offset + length

        return data[offset:end_offset][:-1].decode('ascii'), end_offset

    def __repr__(self):
        return 'UTCTime({})'.format(self.name)


class GeneralizedTime(Type):

    def __init__(self, name):
        super(GeneralizedTime, self).__init__(name,
                                              'GeneralizedTime',
                                              Tag.GENERALIZED_TIME)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.append(len(data))
        encoded.extend(data.encode('ascii'))

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[offset:end_offset].decode('ascii'), end_offset

    def __repr__(self):
        return 'GeneralizedTime({})'.format(self.name)


class TeletexString(Type):

    def __init__(self, name):
        super(TeletexString, self).__init__(name,
                                            'TeletexString',
                                            Tag.T61_STRING)

    def encode(self, data, encoded):
        encoded.extend(self.tag)
        encoded.extend(encode_length_definite(len(data)))
        encoded.extend(data)

    def decode(self, data, offset):
        offset = self.decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return bytearray(data[offset:end_offset]), end_offset

    def __repr__(self):
        return 'TeletexString({})'.format(self.name)


class Choice(Type):

    def __init__(self, name, members):
        super(Choice, self).__init__(name, 'CHOICE', None)
        self.members = members

    def set_tag(self, number, flags):
        super(Choice, self).set_tag(number,
                                    flags | Encoding.CONSTRUCTED)

    def encode(self, data, encoded):
        for member in self.members:
            if member.name == data[0]:
                member.encode(data[1], encoded)

                return

        raise EncodeError(
            "expected choices are {}, but got '{}'".format(
                [member.name for member in self.members],
                data[0]))

    def decode(self, data, offset):
        for member in self.members:
            if (isinstance(member, Choice)
                or member.tag == data[offset:offset + len(member.tag)]):
                try:
                    decoded, offset = member.decode(data, offset)
                except DecodeChoiceError:
                    pass
                else:
                    return (member.name, decoded), offset

        raise DecodeChoiceError()

    def __repr__(self):
        return 'Choice({}, [{}])'.format(
            self.name,
            ', '.join([repr(member) for member in self.members]))


class Any(Type):

    def __init__(self, name):
        super(Any, self).__init__(name, 'ANY', None)

    def encode(self, data, encoded):
        encoded.extend(data)

    def decode(self, data, offset):
        start = offset
        _, _, offset = decode_tag(data, offset)
        length, offset = decode_length_definite(data, offset)
        end_offset = offset + length

        return data[start:end_offset], end_offset

    def __repr__(self):
        return 'Any({})'.format(self.name)


class AnyDefinedBy(Type):

    def __init__(self, name, type_member, choices):
        super(AnyDefinedBy, self).__init__(name,
                                           'ANY DEFINED BY',
                                           None,
                                           None)
        self.type_member = type_member
        self.choices = choices

    def encode(self, data, encoded, values):
        if self.choices:
            self.choices[values[self.type_member]].encode(data, encoded)
        else:
            encoded.extend(data)

    def decode(self, data, offset, values):
        if self.choices:
            return self.choices[values[self.type_member]].decode(data,
                                                                 offset)
        else:
            start = offset
            _, _, offset = decode_tag(data, offset)
            length, offset = decode_length_definite(data, offset)
            end_offset = offset + length

            return data[start:end_offset], end_offset

    def __repr__(self):
        return 'AnyDefinedBy({})'.format(self.name)


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


class Recursive(Type):

    def __init__(self, name, type_name, module_name):
        super(Recursive, self).__init__(name, 'RECURSIVE', None)
        self.type_name = type_name
        self.module_name = module_name

    def encode(self, _data, _encoded):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def decode(self, _data, _offset):
        raise NotImplementedError(
            "Recursive types are not yet implemented (type '{}').".format(
                self.type_name))

    def __repr__(self):
        return 'Recursive({})'.format(self.name)


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

    def process_type(self, type_name, type_descriptor, module_name):
        return CompiledType(self.compile_type(type_name,
                                              type_descriptor,
                                              module_name))

    def compile_implicit_type(self, name, type_descriptor, module_name):
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
            compiled = BitString(name)
        elif type_name == 'ANY':
            compiled = Any(name)
        elif type_name == 'ANY DEFINED BY':
            choices = {}

            for key, value in type_descriptor['choices'].items():
                choices[key] = self.compile_type(key,
                                                 value,
                                                 module_name)

            compiled = AnyDefinedBy(name,
                                    type_descriptor['value'],
                                    choices)
        elif type_name == 'NULL':
            compiled = Null(name)
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

    def compile_type(self, name, type_descriptor, module_name):
        compiled = self.compile_implicit_type(name,
                                              type_descriptor,
                                              module_name)

        if self.is_explicit_tag(type_descriptor):
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


def decode_length(data):
    try:
        return sum(decode_length_definite(bytearray(data), 1))
    except DecodeContentsLengthError as e:
        return (e.length + e.offset)
    except IndexError:
        raise DecodeError('not enough data to decode the length')
