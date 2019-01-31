"""Unaligned Packed Encoding Rules (UPER) Rust source code codec generator.

"""

from .utils import ENCODER_AND_DECODER_STRUCTS
from .utils import ENCODER_ABORT
from .utils import DECODER_ABORT
from .utils import Generator
from .utils import is_user_type
from .utils import indent_lines
from .utils import dedent_lines
from .utils import make_camel_case
from ...codecs import uper


ENCODER_INIT = '''\
    fn new(dst: &'a mut [u8]) -> Encoder {
        Encoder {
            size: 8 * dst.len(),
            buf: dst,
            pos: 0,
            error: None
        }
    }\
'''

ENCODER_GET_RESULT = '''
    fn get_result(&self) -> Result<usize, Error> {
        if self.error.is_none() {
            return Ok((self.pos + 7) / 8);
        } else {
            return Err(self.error.unwrap());
        }
    }\
'''

ENCODER_ALLOC = '''
    fn alloc(&mut self, size: usize) -> Result<usize, ()> {
        if self.pos + size <= self.size {
            let pos = self.pos;
            self.pos += size;
            Ok(pos)
        } else {
            self.abort(Error::OutOfMemory);
            Err(())
        }
    }\
'''

ENCODER_APPEND_BIT = '''
    fn append_bit(&mut self, value: u8) {
        if let Ok(pos) = self.alloc(1) {
            if pos % 8 == 0 {
                self.buf[pos / 8] = 0;
            }

            self.buf[pos / 8] |= value << (7 - (pos % 8));
        }
    }\
'''

ENCODER_APPEND_BYTES = '''
    fn append_bytes(&mut self, buf: &[u8]) {
        if let Ok(pos) = self.alloc(8 * buf.len()) {
            let byte_pos = pos / 8;
            let pos_in_byte = pos % 8;

            if pos_in_byte == 0 {
                self.buf.get_mut(byte_pos..byte_pos + buf.len())
                    .unwrap()
                    .copy_from_slice(buf.get(0..buf.len()).unwrap());
            } else {
                for i in 0..buf.len() {
                    self.buf[byte_pos + i] |= buf[i] >> pos_in_byte;
                    self.buf[byte_pos + i + 1] = buf[i] << (8 - pos_in_byte);
                }
            }
        }
    }\
'''

ENCODER_APPEND_U8 = '''
    fn append_u8(&mut self, value: u8) {
        self.append_bytes(&value.to_be_bytes());
    }\
'''

ENCODER_APPEND_U16 = '''
    fn append_u16(&mut self, value: u16) {
        self.append_bytes(&value.to_be_bytes());
    }\
'''

ENCODER_APPEND_U32 = '''
    fn append_u32(&mut self, value: u32) {
        self.append_bytes(&value.to_be_bytes());
    }\
'''

ENCODER_APPEND_U64 = '''
    fn append_u64(&mut self, value: u64) {
        self.append_bytes(&value.to_be_bytes());
    }\
'''

ENCODER_APPEND_I8 = '''
    fn append_i8(&mut self, value: i8) {
        self.append_u8((value as u8).wrapping_add(128));
    }\
'''

ENCODER_APPEND_I16 = '''
    fn append_i16(&mut self, value: i16) {
        self.append_u16((value as u16).wrapping_add(32768));
    }\
'''

ENCODER_APPEND_I32 = '''
    fn append_i32(&mut self, value: i32) {
        self.append_u32((value as u32).wrapping_add(2147483648));
    }\
'''

ENCODER_APPEND_I64 = '''
    fn append_i64(&mut self, value: i64) {
        self.append_u64((value as u64).wrapping_add(9223372036854775808));
    }\
'''

ENCODER_APPEND_BOOL = '''
    fn append_bool(&mut self, value: bool) {
        self.append_bit(value as u8);
    }\
'''

ENCODER_APPEND_NON_NEGATIVE_BINARY_INTEGER = '''
    fn append_non_negative_binary_integer(&mut self, value: u64, size: usize) {
        for i in 0..size {
            self.append_bit((value >> (size - i - 1)) as u8 & 1);
        }
    }\
'''

DECODER_INIT = '''
    fn new(src: &'a[u8]) -> Decoder {
        Decoder {
            buf: src,
            size: 8 * src.len(),
            pos: 0,
            error: None
        }
    }\
'''

DECODER_GET_RESULT = '''
    fn get_result(&self) -> Result<usize, Error> {
        if self.error.is_none() {
            Ok((self.pos + 7) / 8)
        } else {
            Err(self.error.unwrap())
        }
    }\
'''

DECODER_FREE = '''
    fn free(&mut self, size: usize) -> Result<usize, ()> {
        if self.pos + size <= self.size {
            let pos = self.pos;
            self.pos += size;
            Ok(pos)
        } else {
            self.abort(Error::OutOfData);
            Err(())
        }
    }\
'''

DECODER_READ_BIT = '''
    fn read_bit(&mut self) -> u8 {
        if let Ok(pos) = self.free(1) {
            (self.buf[pos / 8] >> (7 - (pos % 8))) & 1
        } else {
            0
        }
    }\
'''

DECODER_READ_BYTES = '''
    fn read_bytes(&mut self, buf: &mut [u8]) {
        if let Ok(pos) = self.free(8 * buf.len()) {
            let byte_pos = pos / 8;
            let pos_in_byte = pos % 8;

            if pos_in_byte == 0 {
                buf.copy_from_slice(
                    self.buf.get(byte_pos..byte_pos + buf.len()).unwrap());
            } else {
                for i in 0..buf.len() {
                    buf[i] = self.buf[byte_pos + i] << pos_in_byte;
                    buf[i] |= self.buf[byte_pos + i + 1] >> (8 - pos_in_byte);
                }
            }
        }
    }\
'''

DECODER_READ_U8 = '''
    fn read_u8(&mut self) -> u8 {
        let mut buf = [0; 1];

        self.read_bytes(&mut buf);

        u8::from_be_bytes(buf)
    }\
'''

DECODER_READ_U16 = '''
    fn read_u16(&mut self) -> u16 {
        let mut buf = [0; 2];

        self.read_bytes(&mut buf);

        u16::from_be_bytes(buf)
    }\
'''

DECODER_READ_U32 = '''
    fn read_u32(&mut self) -> u32 {
        let mut buf = [0; 4];

        self.read_bytes(&mut buf);

        u32::from_be_bytes(buf)
    }\
'''

DECODER_READ_U64 = '''
    fn read_u64(&mut self) -> u64 {
        let mut buf = [0; 8];

        self.read_bytes(&mut buf);

        u64::from_be_bytes(buf)
    }\
'''

DECODER_READ_I8 = '''
    fn read_i8(&mut self) -> i8 {
        self.read_u8().wrapping_sub(128) as i8
    }\
'''

DECODER_READ_I16 = '''
    fn read_i16(&mut self) -> i16 {
        self.read_u16().wrapping_sub(32768) as i16
    }\
'''

DECODER_READ_I32 = '''
    fn read_i32(&mut self) -> i32 {
        self.read_u32().wrapping_sub(2147483648) as i32
    }\
'''

DECODER_READ_I64 = '''
    fn read_i64(&mut self) -> i64 {
        self.read_u64().wrapping_sub(9223372036854775808) as i64
    }\
'''

DECODER_READ_BOOL = '''
    fn read_bool(&mut self) -> bool {
        self.read_bit() != 0
    }\
'''

DECODER_READ_NON_NEGATIVE_BINARY_INTEGER = '''
    fn read_non_negative_binary_integer(&mut self, size: usize) -> u64 {
        let mut value: u64 = 0;

        for _ in 0..size {
            value <<= 1;
            value |= self.read_bit() as u64;
        }

        value
    }\
'''


def does_bits_match_range(number_of_bits, minimum, maximum):
    return 2 ** number_of_bits == (maximum - minimum + 1)


class _Generator(Generator):

    def format_real(self):
        return []

    def get_enumerated_values(self, type_):
        return sorted(type_.root_data_to_index)

    def get_choice_members(self, type_):
        return type_.root_index_to_member.values()

    def format_type(self, type_, checker):
        if isinstance(type_, uper.Integer):
            return self.format_integer(checker)
        elif isinstance(type_, uper.Boolean):
            return self.format_boolean()
        elif isinstance(type_, uper.Real):
            return self.format_real()
        elif isinstance(type_, uper.Null):
            return []
        elif is_user_type(type_):
            return self.format_user_type(type_.type_name,
                                         type_.module_name)
        elif isinstance(type_, uper.OctetString):
            return self.format_octet_string(checker)
        elif isinstance(type_, uper.Sequence):
            return self.format_sequence(type_, checker)
        elif isinstance(type_, uper.Choice):
            return self.format_choice(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            return self.format_sequence_of(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            return self.format_enumerated(type_)
        else:
            raise self.error(
                "Unsupported type '{}'.".format(type_.type_name))

    def generate_type_declaration_process(self, type_, checker):
        if isinstance(type_, uper.Integer):
            lines = self.format_integer(checker)
            lines[0] += ' value;'
        elif isinstance(type_, uper.Boolean):
            lines = self.format_boolean()
            lines[0] += ' value;'
        elif isinstance(type_, uper.Real):
            lines = self.format_real()
        elif isinstance(type_, uper.Enumerated):
            lines = self.format_enumerated(type_)
            lines[0] += ' value;'
        elif isinstance(type_, uper.Sequence):
            lines = self.format_sequence(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            lines = self.format_sequence_of(type_, checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, uper.Choice):
            lines = self.format_choice(type_, checker)
        elif isinstance(type_, uper.OctetString):
            lines = self.format_octet_string(checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, uper.Null):
            lines = []
        else:
            raise self.error(
                "Unsupported type '{}'.".format(type_.type_name))

        return lines

    def generate_definition_inner_process(self, type_, checker):
        if isinstance(type_, uper.Integer):
            return self.format_integer_inner(type_, checker)
        elif isinstance(type_, uper.Boolean):
            return self.format_boolean_inner()
        elif isinstance(type_, uper.Real):
            return self.format_real_inner()
        elif isinstance(type_, uper.Sequence):
            return self.format_sequence_inner(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            return self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, uper.Choice):
            return self.format_choice_inner(type_, checker)
        elif isinstance(type_, uper.OctetString):
            return self.format_octet_string_inner(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            return self.format_enumerated_inner(type_)
        elif isinstance(type_, uper.Null):
            return self.format_null_inner()
        else:
            return [], []

    def format_integer_inner(self, type_, checker):
        type_name = self.format_type_name(checker.minimum, checker.maximum)
        location = self.location_inner()

        if (type_.number_of_bits % 8) == 0:
            return (
                [
                    'encoder.append_{}(self.{});'.format(
                        type_name,
                        location)
                ],
                [
                    'self.{} = decoder.read_{}();'.format(location, type_name)
                ]
            )
        else:
            return (
                [
                    'encoder.append_non_negative_binary_integer(',
                    '    (self.{} - {}) as u64,'.format(location, checker.minimum),
                    '    {});'.format(type_.number_of_bits)
                ],
                [
                    'self.{} = '
                    'decoder.read_non_negative_binary_integer({}) as {};'.format(
                        location,
                        type_.number_of_bits,
                        type_name),
                    'self.{} += {};'.format(location, checker.minimum)
                ]
            )

    def format_boolean_inner(self):
        return (
            [
                'encoder.append_bool(self.{});'.format(
                    self.location_inner())
            ],
            [
                'self.{} = decoder.read_bool();'.format(
                    self.location_inner())
            ]
        )

    def format_real_inner(self):
        return [], []

    def format_sequence_inner(self, type_, checker):
        encode_lines = []
        decode_lines = []
        member_name_to_is_present = {}

        for member in type_.root_members:
            if member.optional:
                name = '{}is_{}_present'.format(self.location_inner('', '.'),
                                                member.name)
                encode_lines.append(
                    'encoder.append_bit(self.{} as u8);'.format(name))
                decode_lines.append(
                    'self.{} = decoder.read_bit() != 0;'.format(
                        name))
            elif member.default is not None:
                unique_is_present = self.add_unique_variable('is_present')
                member_name_to_is_present[member.name] = unique_is_present
                encode_lines.append(
                    'encoder.append_bit((self.{}{} != {}) as u8);'.format(
                        self.location_inner('', '.'),
                        member.name,
                        member.default))
                decode_lines.append(
                    '{} = decoder.read_bit() == 1;'.format(
                        unique_is_present))

        for member in type_.root_members:
            (member_encode_lines,
             member_decode_lines) = self.format_sequence_inner_member(
                 member,
                 checker,
                 member_name_to_is_present)

            encode_lines += member_encode_lines
            decode_lines += member_decode_lines

        return encode_lines, decode_lines

    def format_octet_string_inner(self, type_, checker):
        location = self.location_inner('', '.')

        if checker.minimum == checker.maximum:
            encode_lines = [
                'encoder.append_bytes(&self.{}buf);'.format(location)
            ]
            decode_lines = [
                'decoder.read_bytes(&mut self.{}buf);'.format(location)
            ]
        else:
            encode_lines = [
                'encoder.append_non_negative_binary_integer(',
                '    (self.{}length - {}) as u64,'.format(location,
                                                          checker.minimum),
                '    {});'.format(type_.number_of_bits),
                'encoder.append_bytes(&self.{}buf,'.format(location),
                '                     self.{}length);'.format(location)
            ]
            decode_lines = [
                'self.{}length = decoder.read_non_negative_binary_integer('.format(
                    location),
                '    {});'.format(type_.number_of_bits),
                'self.{}length += {};'.format(location, checker.minimum)
            ]

            if not does_bits_match_range(type_.number_of_bits,
                                         checker.minimum,
                                         checker.maximum):
                decode_lines += [
                    '',
                    'if self.{}length > {} {{'.format(location, checker.maximum),
                    '    decoder.abort(Error::BadLength);',
                    '',
                    '    return;',
                    '}',
                    ''
                ]

            decode_lines += [
                'decoder.read_bytes(&mut self.{}buf,'.format(location),
                '                   self.{}length);'.format(location)
            ]

        return encode_lines, decode_lines

    def format_user_type_inner(self):
        encode_lines = [
            'self.{}.encode_inner(&mut encoder);'.format(
                self.location_inner())
        ]
        decode_lines = [
            'self.{}.decode_inner(&mut decoder);'.format(
                self.location_inner())
        ]

        return encode_lines, decode_lines

    def format_choice_inner(self, type_, checker):
        encode_lines = []
        decode_lines = []
        unique_choice = self.add_unique_variable('choice')
        choice = '{}choice'.format(self.location_inner('', '.'))

        for member in type_.root_index_to_member.values():
            member_checker = self.get_member_checker(checker,
                                                     member.name)

            with self.asn1_members_backtrace_push(member.name):
                with self.c_members_backtrace_push(member.name):
                    choice_encode_lines, choice_decode_lines = self.format_type_inner(
                        member,
                        member_checker)

            index = type_.root_name_to_index[member.name]

            choice_encode_lines = [
                'encoder.append_non_negative_binary_integer({}, {});'.format(
                    index,
                    type_.root_number_of_bits)
            ] + choice_encode_lines
            encode_lines += [
                '    {}({}) => {{'.format(make_camel_case(member.name),
                                          unique_choice)
            ] + indent_lines(choice_encode_lines, 8) + [
                '    },'
            ]

            choice_decode_lines = [
                'self.{} = {}{};'.format(choice,
                                         self.location,
                                         make_camel_case(member.name))
            ] + choice_decode_lines
            decode_lines += [
                '    {} => {{'.format(index)
            ] + indent_lines(choice_decode_lines, 8) + [
                '    },'
            ]

        encode_lines = [
            '',
            'match self {'
        ] + encode_lines + [
            '    _ => encoder.abort(Error::BadChoice);',
            '}',
            ''
        ]

        decode_lines = [
            '',
            'match decoder.read_non_negative_binary_integer({}) {{'.format(
                type_.root_number_of_bits)
        ] + decode_lines + [
            '    _ => decoder.abort(Error::BadChoice);',
            '}',
            ''
        ]

        return encode_lines, decode_lines

    def format_enumerated_inner(self, type_):
        return (
            [
                'encoder.append_non_negative_binary_integer('
                'self.{}, {});'.format(self.location_inner(),
                                       type_.root_number_of_bits)
            ],
            [
                'self.{} = decoder.read_non_negative_binary_integer('
                '{});'.format(self.location_inner(),
                              type_.root_number_of_bits)
            ]
        )

    def format_null_inner(self):
        return (
            [
                '(void)src_p;'
            ],
            [
                '(void)dst_p;'
            ]
        )

    def format_sequence_of_inner(self, type_, checker):
        unique_i = self.add_unique_variable('i')

        with self.c_members_backtrace_push('elements[{}]'.format(unique_i)):
            encode_lines, decode_lines = self.format_type_inner(
                type_.element_type,
                checker.element_type)

        if checker.minimum == checker.maximum:
            first_encode_lines = first_decode_lines = [
                '',
                'for {} in 0..{} {{'.format(unique_i, checker.maximum)
            ]
        else:
            location = self.location_inner('', '.')
            first_encode_lines = [
                'encoder.append_non_negative_binary_integer(',
                '    (self.{}length - {}) as u64,'.format(location,
                                                          checker.minimum),
                '    {});'.format(type_.number_of_bits),
                '',
                'for {} in 0..self.{}length {{'.format(unique_i, location)
            ]
            first_decode_lines = [
                'self.{}length = '
                'decoder.read_non_negative_binary_integer({});'.format(
                    location,
                    type_.number_of_bits),
                'self.{}length += {};'.format(location, checker.minimum),
                ''
            ]

            if not does_bits_match_range(type_.number_of_bits,
                                         checker.minimum,
                                         checker.maximum):
                first_decode_lines += [
                    'if self.{}length > {} {{'.format(location, checker.maximum),
                    '    decoder.abort(Error::BadLength);',
                    '',
                    '    return;',
                    '}',
                    ''
                ]

            first_decode_lines += [
                'for {} in 0..self.{}length {{'.format(unique_i, location)
            ]

        encode_lines = first_encode_lines + indent_lines(encode_lines) + ['}', '']
        decode_lines = first_decode_lines + indent_lines(decode_lines) + ['}', '']

        return encode_lines, decode_lines

    def format_type_inner(self, type_, checker):
        if isinstance(type_, uper.Integer):
            return self.format_integer_inner(type_, checker)
        elif isinstance(type_, uper.Real):
            return self.format_real_inner()
        elif isinstance(type_, uper.Null):
            return [], []
        elif isinstance(type_, uper.Boolean):
            return self.format_boolean_inner()
        elif is_user_type(type_):
            return self.format_user_type_inner()
        elif isinstance(type_, uper.OctetString):
            return self.format_octet_string_inner(type_, checker)
        elif isinstance(type_, uper.Sequence):
            return self.format_sequence_inner(type_, checker)
        elif isinstance(type_, uper.Choice):
            return self.format_choice_inner(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            return self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            return self.format_enumerated_inner(type_)
        else:
            raise self.error(type_)

    def generate_encoder(self, definitions):
        functions = [
            ('encoder.init(', ENCODER_INIT),
            ('encoder.get_result(', ENCODER_GET_RESULT),
            ('encoder.abort(', ENCODER_ABORT),
            ('encoder.append_bit(', ENCODER_ALLOC),
            ('encoder.append_bit(', ENCODER_APPEND_BIT),
            ('encoder.append_bytes(', ENCODER_APPEND_BYTES),
            ('encoder.append_u8(', ENCODER_APPEND_U8),
            ('encoder.append_u16(', ENCODER_APPEND_U16),
            ('encoder.append_u32(', ENCODER_APPEND_U32),
            ('encoder.append_u64(', ENCODER_APPEND_U64),
            ('encoder.append_i8(', ENCODER_APPEND_I8),
            ('encoder.append_i16(', ENCODER_APPEND_I16),
            ('encoder.append_i32(', ENCODER_APPEND_I32),
            ('encoder.append_i64(', ENCODER_APPEND_I64),
            ('encoder.append_bool(', ENCODER_APPEND_BOOL),
            (
                'encoder.append_non_negative_binary_integer(',
                ENCODER_APPEND_NON_NEGATIVE_BINARY_INTEGER
            )
        ]

        helpers = [
            "impl<'a> Encoder<'a> {",
            "    fn new(dst: &'a mut [u8]) -> Encoder {",
            '        Encoder {',
            '            size: 8 * dst.len(),',
            '            buf: dst,',
            '            pos: 0,',
            '            error: None',
            '        }',
            '    }'
        ]

        for pattern, definition in functions:
            if pattern in definitions:
                helpers.append(definition)

        return helpers + ['}', '']

    def generate_decoder(self, definitions):
        functions = [
            ('decoder.init(', DECODER_INIT),
            ('decoder.get_result(', DECODER_GET_RESULT),
            ('decoder.abort(', DECODER_ABORT),
            ('decoder.read_bit(', DECODER_FREE),
            ('decoder.read_bit(', DECODER_READ_BIT),
            ('decoder.read_bytes(', DECODER_READ_BYTES),
            ('decoder.read_u8(', DECODER_READ_U8),
            ('decoder.read_u16(', DECODER_READ_U16),
            ('decoder.read_u32(', DECODER_READ_U32),
            ('decoder.read_u64(', DECODER_READ_U64),
            ('decoder.read_i8(', DECODER_READ_I8),
            ('decoder.read_i16(', DECODER_READ_I16),
            ('decoder.read_i32(', DECODER_READ_I32),
            ('decoder.read_i64(', DECODER_READ_I64),
            ('decoder.read_bool(', DECODER_READ_BOOL),
            (
                'decoder.read_non_negative_binary_integer(',
                DECODER_READ_NON_NEGATIVE_BINARY_INTEGER
            )
        ]

        helpers = [
            "impl<'a> Decoder<'a> {",
            "    fn new(src: &'a[u8]) -> Decoder {",
            '        Decoder {',
            '            buf: src,',
            '            size: 8 * src.len(),',
            '            pos: 0,',
            '            error: None',
            '        }',
            '    }'
        ]

        for pattern, definition in functions:
            if pattern in definitions:
                helpers.append(definition)

        return helpers + ['}']

    def generate_helpers(self, definitions):
        helpers = [ENCODER_AND_DECODER_STRUCTS]
        helpers += self.generate_encoder(definitions)
        helpers += self.generate_decoder(definitions)

        return helpers + ['']


def generate(compiled):
    return _Generator().generate(compiled)
