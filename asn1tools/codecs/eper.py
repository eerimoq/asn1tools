"""Efficient Packed Encoding Rules (EPER) codec. (Patent 5,638,066)

"""

from operator import attrgetter
from operator import itemgetter
import binascii
import string
import datetime

from ..parser import EXTENSION_MARKER
from . import BaseType, format_bytes, ErrorWithLocation
from . import EncodeError
from . import DecodeError
from . import OutOfDataError
from . import compiler
from . import format_or
from . import restricted_utc_time_to_datetime
from . import restricted_utc_time_from_datetime
from . import restricted_generalized_time_to_datetime
from . import restricted_generalized_time_from_datetime
from .compiler import enum_values_split
from .compiler import enum_values_as_dict
from .compiler import clean_bit_string_value
from .compiler import rstrip_bit_string_zeros
from .ber import encode_real
from .ber import decode_real
from .ber import encode_object_identifier
from .ber import decode_object_identifier
from .permitted_alphabet import NUMERIC_STRING
from .permitted_alphabet import PRINTABLE_STRING
from .permitted_alphabet import IA5_STRING
from .permitted_alphabet import BMP_STRING
from .permitted_alphabet import VISIBLE_STRING
from .per import PermittedAlphabet

class Type(BaseType):

    def __init__(self, name, type_name):
        super().__init__(name, type_name)
        self.module_name = None
        self.tag = None

    def set_size_range(self, minimum, maximum, has_extension_marker):
        pass

    def set_restricted_to_range(self, minimum, maximum, has_extension_marker):
        pass

class KnownMultiplierStringType(Type):

    ENCODING = 'ascii'

    def __init__(self,
                 name,
                 minimum=None,
                 maximum=None,
                 has_extension_marker=False,
                 permitted_alphabet=None):
        raise NotImplemented

class Decoder(object):

    def __init__(self, encoded):
        raise NotImplemented

class MembersType(Type):

    def __init__(self,
                 name,
                 root_members,
                 additions,
                 type_name):
        raise NotImplemented

class ArrayType(Type):

    def __init__(self,
                 name,
                 element_type,
                 minimum,
                 maximum,
                 has_extension_marker,
                 type_name):
        raise NotImplemented

class Boolean(Type):

    def __init__(self, name):
        super(Boolean, self).__init__(name, 'BOOLEAN')
        raise NotImplemented

class Integer(Type):

    def __init__(self, name):
        raise NotImplemented
    
class Null(Type):

    def __init__(self, name):
        raise NotImplemented

class BitString(Type):

    def __init__(self,
                 name,
                 named_bits,
                 minimum,
                 maximum,
                 has_extension_marker):
        NotImplemented

class OctetString(Type):

    def __init__(self, name, minimum, maximum, has_extension_marker):
        raise NotImplemented
    
class Enumerated(Type):

    def __init__(self, name, values, numeric):
        raise NotImplemented
    
class Sequence(MembersType):

    def __init__(self,
                 name,
                 root_members,
                 additions):
        raise NotImplemented

class SequenceOf(ArrayType):

    def __init__(self,
                 name,
                 element_type,
                 minimum,
                 maximum,
                 has_extension_marker):
        raise NotImplemented

class Set(MembersType):

    def __init__(self,
                 name,
                 root_members,
                 additions):
        raise NotImplemented
    
class SetOf(ArrayType):

    def __init__(self,
                 name,
                 element_type,
                 minimum,
                 maximum,
                 has_extension_marker):
        raise NotImplemented
    

class UTF8String(Type):

    def __init__(self, name):
        raise NotImplemented
    
class NumericString(KnownMultiplierStringType):

    ALPHABET = bytearray(NUMERIC_STRING.encode('ascii'))
    ENCODE_MAP = {v: i for i, v in enumerate(ALPHABET)}
    DECODE_MAP = {i: v for i, v in enumerate(ALPHABET)}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_MAP,
                                           DECODE_MAP)
    
class PrintableString(KnownMultiplierStringType):

    ALPHABET = bytearray(PRINTABLE_STRING.encode('ascii'))
    ENCODE_MAP = {v: v for v in ALPHABET}
    DECODE_MAP = {v: v for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_MAP,
                                           DECODE_MAP)
    

class IA5String(KnownMultiplierStringType):

    ALPHABET = bytearray(IA5_STRING.encode('ascii'))
    ENCODE_DECODE_MAP = {v: v for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class BMPString(KnownMultiplierStringType):

    ENCODING = 'utf-16-be'
    ALPHABET = BMP_STRING
    ENCODE_DECODE_MAP = {ord(v): ord(v) for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class VisibleString(KnownMultiplierStringType):

    ALPHABET = bytearray(VISIBLE_STRING.encode('ascii'))
    ENCODE_DECODE_MAP = {v: v for v in ALPHABET}
    PERMITTED_ALPHABET = PermittedAlphabet(ENCODE_DECODE_MAP,
                                           ENCODE_DECODE_MAP)


class StringType(Type):
    def __init__(self, name):
        raise NotImplemented
class GeneralString(StringType):

    ENCODING = 'latin-1'


class GraphicString(StringType):

    ENCODING = 'latin-1'


class TeletexString(StringType):

    ENCODING = 'iso-8859-1'


class UniversalString(StringType):

    ENCODING = 'utf-32-be'
    LENGTH_MULTIPLIER = 4

class Compiler(compiler.Compiler):
    def process_type(self, type_name, type_descriptor, module_name):
        raise NotImplemented

    def compile_type(self, name, type_descriptor, module_name):
        raise NotImplemented

    def set_compiled_tag(self, compiled, type_descriptor):
        raise NotImplemented
    
    def compile_members(self,
                        members,
                        module_name,
                        sort_by_tag=False,
                        flat_additions=False):
        raise NotImplemented
    def compile_extension_member(self,
                                 member,
                                 module_name,
                                 additions,
                                 flat_additions):
        raise NotImplemented
    def get_permitted_alphabet(self, type_descriptor):
        raise NotImplemented

def compile_dict(specification, numeric_enums=False):
    raise NotImplemented

def decode_full_length(_data):
    raise NotImplemented