"""Basic Octet Encoding Rules (OER) C source code codec generator.

"""
from operator import itemgetter

import bitstruct
import textwrap

from .utils import ENCODER_AND_DECODER_STRUCTS
from .utils import ENCODER_ABORT
from .utils import DECODER_ABORT
from .utils import Generator
from .utils import camel_to_snake_case
from .utils import is_user_type
from .utils import indent_lines
from .utils import dedent_lines
from .utils import canonical
from .utils import format_default
from ...codecs import oer


LENGTH_DETERMINANT_LENGTH = '''
static uint32_t length_determinant_length(uint32_t value)
{
    uint32_t length;

    if (value < 128u) {
        length = 1;
    } else if (value < 256u) {
        length = 2;
    } else if (value < 65536u) {
        length = 3;
    } else if (value < 16777216u) {
        length = 4;
    } else {
        length = 5;
    }

    return (length);
}\
'''

MINIMUM_UINT_LENGTH = '''
static uint8_t minimum_uint_length(uint32_t value)
{
    uint8_t length;

    if (value < 256u) {
        length = 1;
    } else if (value < 65536u) {
        length = 2;
    } else if (value < 16777216u) {
        length = 3;
    } else {
        length = 4;
    }

    return (length);
}\
'''

ENCODER_INIT = '''\
static void encoder_init(struct encoder_t *self_p,
                         uint8_t *buf_p,
                         size_t size)
{
    self_p->buf_p = buf_p;
    self_p->size = (ssize_t)size;
    self_p->pos = 0;
}\
'''

ENCODER_GET_RESULT = '''
static ssize_t encoder_get_result(const struct encoder_t *self_p)
{
    return (self_p->pos);
}\
'''

ENCODER_ALLOC = '''
static ssize_t encoder_alloc(struct encoder_t *self_p,
                             size_t size)
{
    ssize_t pos;

    if ((self_p->pos + (ssize_t)size) <= self_p->size) {
        pos = self_p->pos;
        self_p->pos += (ssize_t)size;
    } else {
        pos = -ENOMEM;
        encoder_abort(self_p, ENOMEM);
    }

    return (pos);
}\
'''

ENCODER_APPEND_BYTES = '''
static void encoder_append_bytes(struct encoder_t *self_p,
                                 const uint8_t *buf_p,
                                 size_t size)
{
    ssize_t pos;

    pos = encoder_alloc(self_p, size);

    if (pos < 0) {
        return;
    }

    (void)memcpy(&self_p->buf_p[pos], buf_p, size);
}\
'''

ENCODER_APPEND_UINT8 = '''
static void encoder_append_uint8(struct encoder_t *self_p,
                                 uint8_t value)
{
    encoder_append_bytes(self_p, &value, sizeof(value));
}\
'''

ENCODER_APPEND_UINT16 = '''
static void encoder_append_uint16(struct encoder_t *self_p,
                                  uint16_t value)
{
    uint8_t buf[2];

    buf[0] = (uint8_t)(value >> 8);
    buf[1] = (uint8_t)value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}\
'''

ENCODER_APPEND_UINT32 = '''
static void encoder_append_uint32(struct encoder_t *self_p,
                                  uint32_t value)
{
    uint8_t buf[4];

    buf[0] = (uint8_t)(value >> 24);
    buf[1] = (uint8_t)(value >> 16);
    buf[2] = (uint8_t)(value >> 8);
    buf[3] = (uint8_t)value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}\
'''

ENCODER_APPEND_UINT64 = '''
static void encoder_append_uint64(struct encoder_t *self_p,
                                  uint64_t value)
{
    uint8_t buf[8];

    buf[0] = (uint8_t)(value >> 56);
    buf[1] = (uint8_t)(value >> 48);
    buf[2] = (uint8_t)(value >> 40);
    buf[3] = (uint8_t)(value >> 32);
    buf[4] = (uint8_t)(value >> 24);
    buf[5] = (uint8_t)(value >> 16);
    buf[6] = (uint8_t)(value >> 8);
    buf[7] = (uint8_t)value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}\
'''

ENCODER_APPEND_INT8 = '''
static void encoder_append_int8(struct encoder_t *self_p,
                                int8_t value)
{
    encoder_append_uint8(self_p, (uint8_t)value);
}\
'''

ENCODER_APPEND_INT16 = '''
static void encoder_append_int16(struct encoder_t *self_p,
                                 int16_t value)
{
    encoder_append_uint16(self_p, (uint16_t)value);
}\
'''

ENCODER_APPEND_INT32 = '''
static void encoder_append_int32(struct encoder_t *self_p,
                                 int32_t value)
{
    encoder_append_uint32(self_p, (uint32_t)value);
}\
'''

ENCODER_APPEND_INT64 = '''
static void encoder_append_int64(struct encoder_t *self_p,
                                 int64_t value)
{
    encoder_append_uint64(self_p, (uint64_t)value);
}\
'''

ENCODER_APPEND_UINT = '''
static void encoder_append_uint(struct encoder_t *self_p,
                                uint32_t value,
                                uint8_t number_of_bytes)
{
    switch (number_of_bytes) {

    case 1:
        encoder_append_uint8(self_p, (uint8_t)value);
        break;

    case 2:
        encoder_append_uint16(self_p, (uint16_t)value);
        break;

    case 3:
        encoder_append_uint8(self_p, (uint8_t)(value >> 16));
        encoder_append_uint16(self_p, (uint16_t)value);
        break;

    default:
        encoder_append_uint32(self_p, value);
        break;
    }
}\
'''

ENCODER_APPEND_FLOAT = '''
static void encoder_append_float(struct encoder_t *self_p,
                                 float value)
{
    uint32_t i32;

    (void)memcpy(&i32, &value, sizeof(i32));

    encoder_append_uint32(self_p, i32);
}\
'''

ENCODER_APPEND_DOUBLE = '''
static void encoder_append_double(struct encoder_t *self_p,
                                  double value)
{
    uint64_t i64;

    (void)memcpy(&i64, &value, sizeof(i64));

    encoder_append_uint64(self_p, i64);
}\
'''

ENCODER_APPEND_BOOL = '''
static void encoder_append_bool(struct encoder_t *self_p, bool value)
{
    encoder_append_uint8(self_p, value ? 255u : 0u);
}\
'''

ENCODER_APPEND_LENGTH_DETERMINANT = '''
static void encoder_append_length_determinant(struct encoder_t *self_p,
                                              uint32_t length)
{
    if (length < 128u) {
        encoder_append_int8(self_p, (int8_t)length);
    } else if (length < 256u) {
        encoder_append_uint8(self_p, 0x81u);
        encoder_append_uint8(self_p, (uint8_t)length);
    } else if (length < 65536u) {
        encoder_append_uint8(self_p, 0x82u);
        encoder_append_uint16(self_p, (uint16_t)length);
    } else if (length < 16777216u) {
        encoder_append_uint32(self_p, length | (0x83u << 24u));
    } else {
        encoder_append_uint8(self_p, 0x84u);
        encoder_append_uint32(self_p, length);
    }
}\
'''

DECODER_INIT = '''
static void decoder_init(struct decoder_t *self_p,
                         const uint8_t *buf_p,
                         size_t size)
{
    self_p->buf_p = buf_p;
    self_p->size = (ssize_t)size;
    self_p->pos = 0;
}\
'''

DECODER_GET_RESULT = '''
static ssize_t decoder_get_result(const struct decoder_t *self_p)
{
    return (self_p->pos);
}\
'''

DECODER_FREE = '''
static ssize_t decoder_free(struct decoder_t *self_p,
                            size_t size)
{
    ssize_t pos;

    if ((self_p->pos + (ssize_t)size) <= self_p->size) {
        pos = self_p->pos;
        self_p->pos += (ssize_t)size;
    } else {
        pos = -EOUTOFDATA;
        decoder_abort(self_p, EOUTOFDATA);
    }

    return (pos);
}\
'''

DECODER_READ_BYTES = '''
static void decoder_read_bytes(struct decoder_t *self_p,
                               uint8_t *buf_p,
                               size_t size)
{
    ssize_t pos;

    pos = decoder_free(self_p, size);

    if (pos >= 0) {
        (void)memcpy(buf_p, &self_p->buf_p[pos], size);
    } else {
        (void)memset(buf_p, 0, size);
    }
}\
'''

DECODER_READ_UINT8 = '''
static uint8_t decoder_read_uint8(struct decoder_t *self_p)
{
    uint8_t value;

    decoder_read_bytes(self_p, &value, sizeof(value));

    return (value);
}\
'''

DECODER_READ_UINT16 = '''
static uint16_t decoder_read_uint16(struct decoder_t *self_p)
{
    uint8_t buf[2];

    decoder_read_bytes(self_p, &buf[0], sizeof(buf));

    return (uint16_t)(((uint16_t)buf[0] << 8) | (uint16_t)buf[1]);
}\
'''

DECODER_READ_UINT32 = '''
static uint32_t decoder_read_uint32(struct decoder_t *self_p)
{
    uint8_t buf[4];

    decoder_read_bytes(self_p, &buf[0], sizeof(buf));

    return (((uint32_t)buf[0] << 24)
            | ((uint32_t)buf[1] << 16)
            | ((uint32_t)buf[2] << 8)
            | (uint32_t)buf[3]);
}\
'''

DECODER_READ_UINT64 = '''
static uint64_t decoder_read_uint64(struct decoder_t *self_p)
{
    uint8_t buf[8];

    decoder_read_bytes(self_p, &buf[0], sizeof(buf));

    return (((uint64_t)buf[0] << 56)
            | ((uint64_t)buf[1] << 48)
            | ((uint64_t)buf[2] << 40)
            | ((uint64_t)buf[3] << 32)
            | ((uint64_t)buf[4] << 24)
            | ((uint64_t)buf[5] << 16)
            | ((uint64_t)buf[6] << 8)
            | (uint64_t)buf[7]);
}\
'''

DECODER_READ_INT8 = '''
static int8_t decoder_read_int8(struct decoder_t *self_p)
{
    return ((int8_t)decoder_read_uint8(self_p));
}\
'''

DECODER_READ_INT16 = '''
static int16_t decoder_read_int16(struct decoder_t *self_p)
{
    return ((int16_t)decoder_read_uint16(self_p));
}\
'''

DECODER_READ_INT32 = '''
static int32_t decoder_read_int32(struct decoder_t *self_p)
{
    return ((int32_t)decoder_read_uint32(self_p));
}\
'''

DECODER_READ_INT64 = '''
static int64_t decoder_read_int64(struct decoder_t *self_p)
{
    return ((int64_t)decoder_read_uint64(self_p));
}\
'''

DECODER_READ_UINT = '''
static uint32_t decoder_read_uint(struct decoder_t *self_p,
                                  uint8_t number_of_bytes)
{
    uint32_t value;

    switch (number_of_bytes) {

    case 1:
        value = decoder_read_uint8(self_p);
        break;

    case 2:
        value = decoder_read_uint16(self_p);
        break;

    case 3:
        value = (((uint32_t)decoder_read_uint8(self_p) << 16)
                 | decoder_read_uint16(self_p));
        break;

    case 4:
        value = decoder_read_uint32(self_p);
        break;

    default:
        value = 0xffffffffu;
        break;
    }

    return (value);
}\
'''

DECODER_READ_FLOAT = '''
static float decoder_read_float(struct decoder_t *self_p)
{
    float value;
    uint32_t i32;

    i32 = decoder_read_uint32(self_p);

    (void)memcpy(&value, &i32, sizeof(value));

    return (value);
}\
'''

DECODER_READ_DOUBLE = '''
static double decoder_read_double(struct decoder_t *self_p)
{
    double value;
    uint64_t i64;

    i64 = decoder_read_uint64(self_p);

    (void)memcpy(&value, &i64, sizeof(value));

    return (value);
}\
'''

DECODER_READ_BOOL = '''
static bool decoder_read_bool(struct decoder_t *self_p)
{
    return (decoder_read_uint8(self_p) != 0u);
}\
'''

DECODER_READ_LENGTH_DETERMINANT = '''
static uint32_t decoder_read_length_determinant(struct decoder_t *self_p)
{
    uint32_t length;

    length = decoder_read_uint8(self_p);

    if ((length & 0x80u) != 0u) {
        switch (length & 0x7fu) {

        case 1:
            length = decoder_read_uint8(self_p);
            break;

        case 2:
            length = decoder_read_uint16(self_p);
            break;

        case 3:
            length = (((uint32_t)decoder_read_uint8(self_p) << 16)
                      | decoder_read_uint16(self_p));
            break;

        case 4:
            length = decoder_read_uint32(self_p);
            break;

        default:
            length = 0xffffffffu;
            break;
        }
    }

    return (length);
}\
'''

DECODER_READ_TAG = '''
static uint32_t decoder_read_tag(struct decoder_t *self_p)
{
    uint32_t tag;

    tag = decoder_read_uint8(self_p);

    if ((tag & 0x3fu) == 0x3fu) {
        do {
            tag <<= 8;
            tag |= (uint32_t)decoder_read_uint8(self_p);
        } while ((tag & 0x80u) == 0x80u);
    }

    return (tag);
}\
'''


def get_encoded_real_lengths(type_):
    return [4] if type_.fmt == '>f' else [8]


def get_sequence_optionals(type_):
    return [
        member
        for member in type_.root_members
        if member.optional or member.default is not None
    ]


def get_sequence_extension_bit(type_):
    return 1 if type_.additions is not None else 0


def get_sequence_present_mask_length(optionals, extension_bit):
    return (len(optionals) + extension_bit + 7) // 8


def get_length_determinant_length(length):
    if length < 128:
        return 1
    elif length < 256:
        return 2
    elif length < 65536:
        return 3
    elif length < 1677726:
        return 4
    else:
        return 5


def sum_encoded_lengths(lengths):
    length = 0
    length_strings = []

    for length_part in lengths:

        if isinstance(length_part, int):
            length += length_part
        else:
            length_strings.append(length_part)

    if length > 0 or len(length_strings) == 0:
        length_strings.append(str(length))

    return ' + '.join(length_strings)


def get_sequence_additions_mask_length(additions):
    return (len(additions) + 7) // 8


def format_null_inner():
    return (
        [
            '(void)encoder_p;',
            '(void)src_p;'
        ],
        [
            '(void)decoder_p;',
            '(void)dst_p;'
        ]
    )


class _Generator(Generator):

    def __init__(self, namespace):
        super(_Generator, self).__init__(namespace)
        self.additional_helpers = {}

    def format_real(self, type_):
        if type_.fmt is None:
            raise self.error('REAL not IEEE 754 binary32 or binary64.')

        if type_.fmt == '>f':
            return ['float']
        else:
            return ['double']

    def get_enumerated_values(self, type_):
        return sorted([(canonical(data), value)
                       for data, value in type_.data_to_value.items()],
                      key=itemgetter(1))

    def get_choice_members(self, type_):
        return type_.root_members

    def format_type(self, type_, checker):
        if isinstance(type_, oer.Integer):
            return self.format_integer(checker)
        elif isinstance(type_, oer.Boolean):
            return self.format_boolean()
        elif isinstance(type_, oer.Real):
            return self.format_real(type_)
        elif isinstance(type_, oer.Null):
            return []
        elif is_user_type(type_):
            return self.format_user_type(type_.type_name,
                                         type_.module_name)
        elif isinstance(type_, oer.OctetString):
            return self.format_octet_string(checker)
        elif isinstance(type_, oer.Sequence):
            return self.format_sequence(type_, checker)
        elif isinstance(type_, oer.Choice):
            return self.format_choice(type_, checker)
        elif isinstance(type_, oer.SequenceOf):
            return self.format_sequence_of(type_, checker)
        elif isinstance(type_, oer.Enumerated):
            return self.format_enumerated(type_)
        else:
            raise self.error(
                "Unsupported type '{}'.".format(type_.type_name))

    def get_encoded_type_lengths(self, type_, checker):
        if isinstance(type_, oer.Integer):
            return self.get_encoded_integer_lengths(checker)
        elif isinstance(type_, oer.Boolean):
            return [1]
        elif isinstance(type_, oer.Real):
            return get_encoded_real_lengths(type_)
        elif isinstance(type_, oer.Null):
            return [0]
        elif isinstance(type_, oer.OctetString):
            return self.get_encoded_octet_string_lengths(type_, checker)
        elif isinstance(type_, oer.Sequence):
            return self.get_encoded_sequence_lengths(type_, checker)
        elif isinstance(type_, oer.Choice):
            return self.get_encoded_choice_lengths(type_, checker)
        elif isinstance(type_, oer.SequenceOf):
            return self.get_encoded_sequence_of_lengths(type_, checker)
        elif isinstance(type_, oer.Enumerated):
            return self.get_encoded_enumerated_length(type_)
        else:
            raise self.error(
                "Unsupported type '{}'.".format(type_.type_name))

    def generate_type_declaration_process(self, type_, checker):
        if isinstance(type_, oer.Integer):
            lines = self.format_integer(checker)
            lines[0] += ' value;'
        elif isinstance(type_, oer.Boolean):
            lines = self.format_boolean()
            lines[0] += ' value;'
        elif isinstance(type_, oer.Real):
            lines = self.format_real(type_)
            lines[0] += ' value;'
        elif isinstance(type_, oer.Enumerated):
            lines = self.format_enumerated(type_)
            lines[0] += ' value;'
        elif isinstance(type_, oer.Sequence):
            lines = self.format_sequence(type_, checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, oer.SequenceOf):
            lines = self.format_sequence_of(type_, checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, oer.Choice):
            lines = self.format_choice(type_, checker)
            lines = dedent_lines(lines[1:-1])
        elif isinstance(type_, oer.OctetString):
            lines = self.format_octet_string(checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, oer.Null):
            lines = []
        else:
            raise self.error(
                "Unsupported type '{}'.".format(type_.type_name))

        return lines

    def format_integer_inner(self, checker):
        type_name = self.format_type_name(checker.minimum, checker.maximum)[:-2]

        return (
            [
                'encoder_append_{}(encoder_p, src_p->{});'.format(
                    type_name,
                    self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_{}(decoder_p);'.format(
                    self.location_inner(),
                    type_name)
            ]
        )

    def get_encoded_integer_lengths(self, checker):
        return [self.type_length(checker.minimum, checker.maximum) // 8]

    def format_boolean_inner(self):
        return (
            [
                'encoder_append_bool(encoder_p, src_p->{});'.format(
                    self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_bool(decoder_p);'.format(
                    self.location_inner())
            ]
        )

    def format_real_inner(self, type_):
        if type_.fmt == '>f':
            c_type = 'float'
        else:
            c_type = 'double'

        return (
            [
                'encoder_append_{}(encoder_p, src_p->{});'.format(
                    c_type,
                    self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_{}(decoder_p);'.format(
                    self.location_inner(),
                    c_type)
            ]
        )

    def format_sequence_inner(self, type_, checker):
        encode_lines = []
        decode_lines = []

        optionals = get_sequence_optionals(type_)
        extension_bit = get_sequence_extension_bit(type_)

        present_mask_length = get_sequence_present_mask_length(optionals,
                                                               extension_bit)
        default_condition_by_member_name = {}

        if present_mask_length > 0:
            fmt = 'uint8_t {{}}[{}];'.format(present_mask_length)
            unique_present_mask = self.add_unique_variable(fmt, 'present_mask')

            start_set_byte = 0
            if extension_bit == 1 and len(type_.additions) > 0:
                if_line = 'if({}) {{'.format(self.get_addition_present_condition(type_))
                encode_lines.extend(textwrap.wrap(if_line, 120,
                                                  subsequent_indent=' ' * len('if(')))
                encode_lines.append('    {}[0] = 0x80;'.format(unique_present_mask))
                encode_lines.append('}')
                encode_lines.append('else {')
                encode_lines.append('    {}[0] = 0x0;'.format(unique_present_mask))
                encode_lines.append('}')
                start_set_byte = 1

            for i in range(start_set_byte, present_mask_length):
                encode_lines.append('{}[{}] = 0;'.format(unique_present_mask, i))

            encode_lines.append('')

            decode_lines += [
                'decoder_read_bytes(decoder_p,',
                '                   &{}[0],'.format(unique_present_mask),
                '                   sizeof({}));'.format(unique_present_mask),
                ''
            ]

            for i, member in enumerate(optionals, start=extension_bit):
                byte, bit = divmod(i, 8)
                mask = '0x{:02x}'.format(1 << (7 - bit))
                present_mask = '{}[{}]'.format(unique_present_mask,
                                               byte)
                default_condition = '({0} & {1}u) == {1}u'.format(present_mask, mask)
                default_condition_by_member_name[member.name] = default_condition

                if member.optional:
                    encode_lines += [
                        'if (src_p->{}is_{}_present) {{'.format(
                            self.location_inner('', '.'),
                            member.name),
                        '    {} |= {}u;'.format(present_mask, mask),
                        '}',
                        ''
                    ]
                    decode_lines.append(
                        'dst_p->{0}is_{1}_present = (({2} & {3}u) == {3}u);'.format(
                            self.location_inner('', '.'),
                            member.name,
                            present_mask,
                            mask))
                else:
                    encode_lines += [
                        'if (src_p->{}{} != {}) {{'.format(self.location_inner('', '.'),
                                                           member.name,
                                                           format_default(
                                                               member.default)),
                        '    {} |= {}u;'.format(present_mask, mask),
                        '}',
                        ''
                    ]

            encode_lines += [
                'encoder_append_bytes(encoder_p,',
                '                     &{}[0],'.format(unique_present_mask),
                '                     sizeof({}));'.format(unique_present_mask),
                ''
            ]
            decode_lines.append('')

        for member in type_.root_members:
            (member_encode_lines,
             member_decode_lines) = self.format_sequence_inner_member(
                 member,
                 checker,
                 default_condition_by_member_name)

            encode_lines += member_encode_lines
            decode_lines += member_decode_lines

        if type_.additions is not None and len(type_.additions) > 0:
            additions_encode_lines, additions_decode_lines = (
                self.format_sequence_additions(type_, checker))

            addition_condition = 'if(({}[0] & 0x80u) == 0x80u) {{'.format(
                unique_present_mask)
            encode_lines += [
                '',
                addition_condition
            ] + indent_lines(additions_encode_lines) + [
                '}'
            ]

            decode_lines += [
                '',
                addition_condition
            ] + indent_lines(additions_decode_lines) + [
                '}',
                'else {'
            ] + [
                '    dst_p->{}is_{}_addition_present = false;'.format(
                    self.location_inner('', '.'), addition.name)
                for addition in type_.additions] + [
                '}'
            ]

        return encode_lines, decode_lines

    def format_sequence_additions(self, type_, checker):
        encode_lines = ['']
        decode_lines = ['']

        addition_mask_length = get_sequence_additions_mask_length(type_.additions)
        addition_mask_unused_bits = (addition_mask_length * 8) - len(type_.additions)

        encode_lines.append('encoder_append_length_determinant(encoder_p, {});'.format(
            addition_mask_length + 1))
        unique_addition_length = self.add_unique_decode_variable(
            'uint32_t {};', 'addition_length')
        decode_lines += [
            '{} = decoder_read_length_determinant(decoder_p);'.format(
                unique_addition_length),
            '',
            'if({} <= 1u) {{'.format(unique_addition_length),
            '    decoder_abort(decoder_p, EBADLENGTH);',
            '',
            '    return;',
            '}',
            '{} -= 1u;'.format(unique_addition_length)]

        encode_lines.append('encoder_append_uint8(encoder_p, {});'.format(
            addition_mask_unused_bits))
        unique_addition_unused_bits = self.add_unique_decode_variable(
            'uint8_t {};', 'addition_unused_bits')
        unique_addition_bits = self.add_unique_decode_variable(
            'uint32_t {};', 'addition_bits')
        decode_lines += [
            '{} = decoder_read_uint8(decoder_p);'.format(unique_addition_unused_bits),
            '',
            'if ({} > 7u) {{'.format(unique_addition_unused_bits),
            '    decoder_abort(decoder_p, EBADLENGTH);',
            '',
            '    return;',
            '}',
            '{} = (({} * 8u) - {});'.format(unique_addition_bits, unique_addition_length,
                                            unique_addition_unused_bits)]

        fmt = 'uint8_t {{}}[{}];'.format(addition_mask_length)
        unique_addition_mask = self.add_unique_variable(
            fmt, 'addition_mask')

        for i in range(addition_mask_length):
            encode_lines.append('{}[{}] = 0;'.format(unique_addition_mask, i))

        for i, addition in enumerate(type_.additions):
            byte, bit = divmod(i, 8)
            mask = '0x{:02x}'.format(1 << (7 - bit))
            addition_mask = '{}[{}]'.format(unique_addition_mask,
                                            byte)
            encode_lines += [
                '',
                'if (src_p->{}is_{}_addition_present) {{'.format(
                    self.location_inner('', '.'), addition.name),
                '    {} |= {}u;'.format(addition_mask, mask),
                '}'
            ]
        encode_lines += [
            'encoder_append_bytes(encoder_p,',
            '                     &{}[0],'.format(unique_addition_mask),
            '                     sizeof({}));'.format(unique_addition_mask)]

        unique_i = self.add_unique_decode_variable('uint32_t {};', 'i')
        unique_tmp_addition_mask = self.add_unique_decode_variable('uint8_t {};',
                                                                   'tmp_addition_mask')
        unique_unknown_addition_bits = self.add_unique_decode_variable(
            'uint32_t {};', 'unknown_addition_bits')
        unique_mask = self.add_unique_decode_variable('uint8_t {};', 'mask')

        decode_lines += [
            'decoder_read_bytes(decoder_p,',
            '                   {mask},'.format(mask=unique_addition_mask),
            '                   ({read} < {defined}u) ? {read} : {defined}u);'.format(
                read=unique_addition_length, defined=addition_mask_length),
            '',
            '{} = {}[{}];'.format(unique_tmp_addition_mask, unique_addition_mask,
                                  addition_mask_length - 1),
            '{} = 0x{:02x};'.format(unique_mask, 0x80 >> (len(type_.additions) % 8)),
            '{} = 0;'.format(unique_unknown_addition_bits),
            '',
            'for (i = {}; i < {}; i++) {{'.format(len(type_.additions),
                                                  unique_addition_bits),
            '',
            '    if ({} == 0u) {{'.format(unique_mask),
            '        decoder_read_bytes(decoder_p, &{}, 1);'.format(
                unique_tmp_addition_mask),
            '',
            '        if (decoder_get_result(decoder_p) < 0) {',
            '',
            '            return;',
            '        }',
            '        {} = 0x80;'.format(unique_mask),
            '    }',
            '',
            '    if( ({tmp_addition} & {mask}) == {mask}) {{'.format(
                tmp_addition=unique_tmp_addition_mask, mask=unique_mask),
            '        {} += 1u;'.format(unique_unknown_addition_bits),
            '    };',
            '    {} >>= 1;'.format(unique_mask),
            '}'
        ]

        for i, addition in enumerate(type_.additions):
            byte, bit = divmod(i, 8)
            mask = '0x{:02x}'.format(1 << (7 - bit))

            (addition_encode_lines,
             addition_decode_lines) = self.format_sequence_inner_member(
                addition,
                checker,
                None,
                skip_when_not_present=False)

            member_checker = self.get_member_checker(checker, addition.name)
            encoded_lengths = self.get_encoded_type_lengths(addition, member_checker)
            encode_lines += [
                '',
                'if (src_p->{}is_{}_addition_present) {{'
                .format(self.location_inner('', '.'), addition.name),
                '    encoder_append_length_determinant(encoder_p, {});'
                .format(sum_encoded_lengths(encoded_lengths))
            ] + indent_lines(addition_encode_lines) + [
                '}'
            ]

            decode_lines += [
                'dst_p->{location}is_{name}_addition_present = '
                '(({addition_bits} > {current_bit}u) && '
                '(({addition_mask}[{index}] & {mask}u) == {mask}u));'.format(
                    location=self.location_inner('', '.'),
                    name=addition.name,
                    addition_bits=unique_addition_bits,
                    current_bit=i,
                    addition_mask=unique_addition_mask,
                    index=byte,
                    mask=mask),
                '',
                'if (dst_p->{location}is_{name}_addition_present) {{'.format(
                    location=self.location_inner('', '.'),
                    name=addition.name),
                '    (void)decoder_read_length_determinant(decoder_p);'
            ] + indent_lines(addition_decode_lines) + [
                '}',
                '']

        unique_tmp_length = self.add_unique_decode_variable('uint32_t {};', 'tmp_length')
        decode_lines += [
            'for ({i} = 0; {i} < {unique_unknown_addition_bits}; {i}++) {{'.format(
                i=unique_i,
                first_bit=len(type_.additions),
                unique_unknown_addition_bits=unique_unknown_addition_bits),
            '    {} = decoder_read_length_determinant(decoder_p);'.format(
                unique_tmp_length),
            '',
            '    if (decoder_free(decoder_p, {}) < 0) {{'.format(unique_tmp_length),
            '',
            '        return;',
            '    }',
            '}']

        return encode_lines, decode_lines

    def get_encoded_sequence_lengths(self, type_, checker):
        lengths = []
        optionals = get_sequence_optionals(type_)
        extension_bit = get_sequence_extension_bit(type_)

        lengths.append(get_sequence_present_mask_length(optionals,
                                                        extension_bit))
        for member in type_.root_members:
            lengths.extend(self.get_encoded_type_lengths(member, checker))

        if type_.additions is not None and len(type_.additions) > 0:
            additions_mask_length = (
                get_sequence_additions_mask_length(type_.additions))
            lengths.append(get_length_determinant_length(additions_mask_length))
            lengths.append(1)
            lengths.append(additions_mask_length)

            for addition in type_.additions:
                member_checker = self.get_member_checker(checker, addition.name)
                additions_lengths = self.get_encoded_type_lengths(addition,
                                                                  member_checker)
                addition_length = int(sum_encoded_lengths(additions_lengths))
                lengths.append(get_length_determinant_length(addition_length))
                lengths.extend(additions_lengths)

        return lengths

    def format_octet_string_inner(self, checker):
        location = self.location_inner('', '.')

        if checker.minimum == checker.maximum:
            encode_lines = [
                'encoder_append_bytes(encoder_p,',
                '                     &src_p->{}buf[0],'.format(location),
                '                     {});'.format(checker.maximum)
            ]
            decode_lines = [
                'decoder_read_bytes(decoder_p,',
                '                   &dst_p->{}buf[0],'.format(location),
                '                   {});'.format(checker.maximum)
            ]
        elif checker.maximum < 128:
            encode_lines = [
                'encoder_append_uint8(encoder_p, src_p->{}length);'.format(
                    location),
                'encoder_append_bytes(encoder_p,',
                '                     &src_p->{}buf[0],'.format(location),
                '                     src_p->{}length);'.format(location)
            ]
            decode_lines = [
                'dst_p->{}length = decoder_read_uint8(decoder_p);'.format(
                    location),
                '',
                'if (dst_p->{}length > {}u) {{'.format(location, checker.maximum),
                '    decoder_abort(decoder_p, EBADLENGTH);',
                '',
                '    return;',
                '}',
                '',
                'decoder_read_bytes(decoder_p,',
                '                   &dst_p->{}buf[0],'.format(location),
                '                   dst_p->{}length);'.format(location)
            ]
        else:
            encode_lines = [
                'encoder_append_length_determinant(encoder_p, src_p->{}length);'.format(
                    location),
                'encoder_append_bytes(encoder_p,',
                '                     &src_p->{}buf[0],'.format(location),
                '                     src_p->{}length);'.format(location)
            ]
            decode_lines = [
                'dst_p->{}length = decoder_read_length_determinant(decoder_p);'.format(
                    location),
                '',
                'if (dst_p->{}length > {}u) {{'.format(location, checker.maximum),
                '    decoder_abort(decoder_p, EBADLENGTH);',
                '',
                '    return;',
                '}',
                '',
                'decoder_read_bytes(decoder_p,',
                '                   &dst_p->{}buf[0],'.format(location),
                '                   dst_p->{}length);'.format(location)
            ]

        return encode_lines, decode_lines

    def get_encoded_octet_string_lengths(self, type_, checker):
        with self.members_backtrace_push(type_.name):
            if checker.minimum == checker.maximum:

                return [checker.maximum]
            else:
                location = self.location_inner('', '.')
                src_length = 'src_p->{}length'.format(location)

                return ['length_determinant_length({})'.format(src_length),
                        src_length]

    def get_user_type_prefix(self, type_name, module_name):
        module_name_snake = camel_to_snake_case(module_name)
        type_name_snake = camel_to_snake_case(type_name)

        return '{}_{}_{}'.format(self.namespace,
                                 module_name_snake,
                                 type_name_snake)

    def format_user_type_inner(self, type_name, module_name):
        prefix = self.get_user_type_prefix(type_name, module_name)
        encode_lines = [
            '{}_encode_inner(encoder_p, &src_p->{});'.format(
                prefix,
                self.location_inner())
        ]
        decode_lines = [
            '{}_decode_inner(decoder_p, &dst_p->{});'.format(
                prefix,
                self.location_inner())
        ]

        return encode_lines, decode_lines

    def format_choice_inner(self, type_, checker):
        encode_lines = []
        decode_lines = []
        unique_tag = self.add_unique_decode_variable('uint32_t {};', 'tag')
        choice = '{}choice'.format(self.location_inner('', '.'))

        for member in type_.root_members:
            member_checker = self.get_member_checker(checker,
                                                     member.name)

            with self.asn1_members_backtrace_push(member.name):
                with self.c_members_backtrace_push('value'):
                    with self.c_members_backtrace_push(member.name):
                        choice_encode_lines, choice_decode_lines = self.format_type_inner(
                            member,
                            member_checker)

            tag_length = len(member.tag)

            if tag_length > 4:
                raise self.error(
                    'CHOICE tags of more than four bytes are not yet supported.')

            tag = bitstruct.unpack('u{}'.format(8 * tag_length),
                                   member.tag)[0]
            tag = '0x{{:0{}x}}'.format(2 * tag_length).format(tag)

            choice_encode_lines = [
                'encoder_append_uint(encoder_p, {}, {});'.format(
                    tag,
                    tag_length)
            ] + choice_encode_lines + [
                'break;'
            ]
            encode_lines += [
                'case {}_choice_{}_e:'.format(self.location, member.name)
            ] + indent_lines(choice_encode_lines) + [
                ''
            ]

            choice_decode_lines = [
                'dst_p->{} = {}_choice_{}_e;'.format(choice,
                                                     self.location,
                                                     member.name)
            ] + choice_decode_lines + [
                'break;'
            ]
            decode_lines += [
                'case {}:'.format(tag)
            ] + indent_lines(choice_decode_lines) + [
                ''
            ]

        encode_lines = [
            '',
            'switch (src_p->{}) {{'.format(choice),
            ''
        ] + encode_lines + [
            'default:',
            '    encoder_abort(encoder_p, EBADCHOICE);',
            '    break;',
            '}',
            ''
        ]

        decode_lines = [
            '{} = decoder_read_tag(decoder_p);'.format(unique_tag),
            '',
            'switch ({}) {{'.format(unique_tag),
            ''
        ] + decode_lines + [
            'default:',
            '    decoder_abort(decoder_p, EBADCHOICE);',
            '    break;',
            '}',
            ''
        ]

        return encode_lines, decode_lines

    def get_encoded_choice_lengths(self, type_, checker):
        function_name = 'get_choice_{}_length'.format(camel_to_snake_case(type_.name))

        if function_name not in self.additional_helpers:
            with self.members_backtrace_push(type_.name):
                choice = '{}choice'.format(self.location_inner('', '.'))
                choice_length_lines = []

                for member in type_.root_members:
                    member_checker = self.get_member_checker(checker,
                                                             member.name)

                    with self.asn1_members_backtrace_push(member.name):
                        with self.c_members_backtrace_push('value'):
                            with self.c_members_backtrace_push(member.name):
                                choice_type_lengths = self.get_encoded_type_lengths(
                                    member,
                                    member_checker)

                    choice_type_lengths.append(len(member.tag))
                    choice_type_length = sum_encoded_lengths(choice_type_lengths)

                    choice_length_lines += [
                        'case {}_choice_{}_e:'.format(self.location, member.name),
                        '    length = {};'.format(choice_type_length),
                        '    break;',
                        '']

            length_lines = [
                'uint32_t length;',
                '',
                'switch (src_p->{}) {{'.format(choice),
                ''
            ] + choice_length_lines + [
                'default:',
                '    length = 0;'
                '    break;',
                '}',
                'return length;']

            length_lines = [
                'static uint32_t {}(const struct {}_t *src_p) {{'.format(
                    function_name, self.location)
            ] + indent_lines(length_lines) + [
                '}']
            self.additional_helpers[function_name] = length_lines

        return ['{}(src_p)'.format(function_name)]

    def format_enumerated_inner(self, type_):
        encode_lines = []
        decode_lines = []

        max_value = max(type_.value_to_data)
        min_value = min(type_.value_to_data)

        type_name = '{}_e'.format(self.location)
        type_length = self.type_length(0, max_value) // 8

        if min_value < 0:
            raise self.error('Negative enumerators are not supported.')

        unique_enum_length = self.add_unique_variable('uint8_t {};',
                                                      'enum_length')
        encode_lines += [
            '{} = minimum_uint_length(src_p->{});'.format(
                unique_enum_length, self.location_inner()),
            '',
            'if ((uint32_t)src_p->{0} > 127u) {{'.format(
                self.location_inner()),
            '    encoder_append_uint8(encoder_p, 0x80u | {});'.format(
                unique_enum_length),
            '}',
            'encoder_append_uint(encoder_p, (uint32_t)src_p->{}, {});'.format(
                self.location_inner(), unique_enum_length)]
        decode_lines += [
            '{} = decoder_read_uint8(decoder_p);'.format(unique_enum_length),
            '',
            'if (({} & 0x80u) == 0x80u) {{'.format(unique_enum_length),
            '    {} &= 0x7fu;'.format(unique_enum_length),
            '',
            '    if (({length} > {type_length}u) || ({length} == 0u)) {{'.format(
                type_length=type_length, length=unique_enum_length),
            '        decoder_abort(decoder_p, EBADLENGTH);',
            '',
            '        return;',
            '    }',
            '    dst_p->{} = (enum {})decoder_read_uint(decoder_p, {});'.format(
                self.location_inner(), type_name, unique_enum_length),
            '}',
            'else {',
            '    dst_p->{} = (enum {}){};'.format(self.location_inner(), type_name,
                                                  unique_enum_length),
            '}']

        return encode_lines, decode_lines

    def get_encoded_enumerated_length(self, type_):
        with self.members_backtrace_push(type_.name):
            return ['length_determinant_length((uint32_t)src_p->{})'.format(
                self.location_inner())]

    def format_sequence_of_inner(self, type_, checker):
        unique_number_of_length_bytes = self.add_unique_variable(
            'uint8_t {};',
            'number_of_length_bytes')
        unique_i = self.add_unique_variable(
            '{} {{}};'.format(self.format_type_name(0, checker.maximum)),
            'i')

        if checker.minimum == checker.maximum:
            unique_length = self.add_unique_decode_variable('uint8_t {};',
                                                            'length')

        with self.c_members_backtrace_push('elements[{}]'.format(unique_i)):
            encode_lines, decode_lines = self.format_type_inner(
                type_.element_type,
                checker.element_type)

        location = self.location_inner('', '.')

        if checker.minimum == checker.maximum:
            encode_lines = [
                '{} = minimum_uint_length({});'.format(
                    unique_number_of_length_bytes,
                    checker.maximum),
                'encoder_append_uint8(encoder_p, {});'.format(
                    unique_number_of_length_bytes),
                'encoder_append_uint(encoder_p,',
                '                    {},'.format(checker.maximum),
                '                    {});'.format(unique_number_of_length_bytes),
                '',
                'for ({ui} = 0; {ui} < {maximum}u; {ui}++) {{'.format(
                    ui=unique_i,
                    maximum=checker.maximum),
            ] + indent_lines(encode_lines)
            decode_lines = [
                '{} = decoder_read_uint8(decoder_p);'.format(
                    unique_number_of_length_bytes),
                '{} = decoder_read_uint8(decoder_p);'.format(unique_length),
                '',
                'if (({} != 1u) || ({} > {}u)) {{'.format(unique_number_of_length_bytes,
                                                          unique_length,
                                                          checker.maximum),
                '    decoder_abort(decoder_p, EBADLENGTH);',
                '',
                '    return;',
                '}',
                '',
                'for ({ui} = 0; {ui} < {maximum}u; {ui}++) {{'.format(
                    ui=unique_i,
                    maximum=checker.maximum),
            ] + indent_lines(decode_lines)
        else:
            if checker.maximum < 256:
                cast = '(uint8_t)'
            else:
                cast = ''
            encode_lines = [
                '{} = minimum_uint_length(src_p->{}length);'.format(
                    unique_number_of_length_bytes,
                    location),
                'encoder_append_uint8(encoder_p, {});'.format(
                    unique_number_of_length_bytes),
                'encoder_append_uint(encoder_p,',
                '                    src_p->{}length,'.format(location),
                '                    {});'.format(unique_number_of_length_bytes),
                '',
                'for ({ui} = 0; {ui} < src_p->{loc}length; {ui}++) {{'.format(
                    ui=unique_i,
                    loc=location),
            ] + indent_lines(encode_lines)
            decode_lines = [
                '{} = decoder_read_uint8(decoder_p);'.format(
                    unique_number_of_length_bytes),
                'dst_p->{}length = {}decoder_read_uint('.format(location, cast),
                '    decoder_p,',
                '    {});'.format(unique_number_of_length_bytes),
                '',
                'if (dst_p->{}length > {}u) {{'.format(location, checker.maximum),
                '    decoder_abort(decoder_p, EBADLENGTH);',
                '',
                '    return;',
                '}',
                '',
                'for ({ui} = 0; {ui} < dst_p->{loc}length; {ui}++) {{'.format(
                    loc=location,
                    ui=unique_i),
            ] + indent_lines(decode_lines)

        encode_lines += ['}', '']
        decode_lines += ['}', '']

        return encode_lines, decode_lines

    def get_encoded_sequence_of_lengths(self, type_, checker):
        inner_lengths = self.get_encoded_type_lengths(type_.element_type,
                                                      checker.element_type)
        inner_length = sum_encoded_lengths(inner_lengths)

        with self.c_members_backtrace_push(type_.name):

            return [1,
                    'minimum_uint_length(src_p->{loc}length)'.format(
                        loc=self.location_inner('', '.')),
                    '(uint32_t)(src_p->{loc}length * ({inner_length}))'.format(
                        loc=self.location_inner('', '.'), inner_length=inner_length)]

    def format_type_inner(self, type_, checker):
        if isinstance(type_, oer.Integer):
            return self.format_integer_inner(checker)
        elif isinstance(type_, oer.Real):
            return self.format_real_inner(type_)
        elif isinstance(type_, oer.Null):
            return [], []
        elif isinstance(type_, oer.Boolean):
            return self.format_boolean_inner()
        elif is_user_type(type_):
            return self.format_user_type_inner(type_.type_name,
                                               type_.module_name)
        elif isinstance(type_, oer.OctetString):
            return self.format_octet_string_inner(checker)
        elif isinstance(type_, oer.Sequence):
            return self.format_sequence_inner(type_, checker)
        elif isinstance(type_, oer.Choice):
            return self.format_choice_inner(type_, checker)
        elif isinstance(type_, oer.SequenceOf):
            return self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, oer.Enumerated):
            return self.format_enumerated_inner(type_)
        else:
            raise self.error(str(type_))

    def generate_definition_inner_process(self, type_, checker):
        if isinstance(type_, oer.Integer):
            return self.format_integer_inner(checker)
        elif isinstance(type_, oer.Boolean):
            return self.format_boolean_inner()
        elif isinstance(type_, oer.Real):
            return self.format_real_inner(type_)
        elif isinstance(type_, oer.Sequence):
            return self.format_sequence_inner(type_, checker)
        elif isinstance(type_, oer.SequenceOf):
            return self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, oer.Choice):
            return self.format_choice_inner(type_, checker)
        elif isinstance(type_, oer.OctetString):
            return self.format_octet_string_inner(checker)
        elif isinstance(type_, oer.Enumerated):
            return self.format_enumerated_inner(type_)
        elif isinstance(type_, oer.Null):
            return format_null_inner()
        else:
            return [], []

    def generate_helpers(self, definitions):
        helpers = []

        functions = [
            ('decoder_read_tag(', DECODER_READ_TAG),
            ('decoder_read_length_determinant(', DECODER_READ_LENGTH_DETERMINANT),
            ('decoder_read_bool(', DECODER_READ_BOOL),
            ('decoder_read_double(', DECODER_READ_DOUBLE),
            ('decoder_read_float(', DECODER_READ_FLOAT),
            ('decoder_read_uint(', DECODER_READ_UINT),
            ('decoder_read_int64(', DECODER_READ_INT64),
            ('decoder_read_int32(', DECODER_READ_INT32),
            ('decoder_read_int16(', DECODER_READ_INT16),
            ('decoder_read_int8(', DECODER_READ_INT8),
            ('decoder_read_uint64(', DECODER_READ_UINT64),
            ('decoder_read_uint32(', DECODER_READ_UINT32),
            ('decoder_read_uint16(', DECODER_READ_UINT16),
            ('decoder_read_uint8(', DECODER_READ_UINT8),
            ('decoder_read_bytes(', DECODER_READ_BYTES),
            ('decoder_free(', DECODER_FREE),
            ('decoder_abort(', DECODER_ABORT),
            ('decoder_get_result(', DECODER_GET_RESULT),
            ('decoder_init(', DECODER_INIT),
            ('encoder_append_length_determinant(', ENCODER_APPEND_LENGTH_DETERMINANT),
            ('encoder_append_bool(', ENCODER_APPEND_BOOL),
            ('encoder_append_double(', ENCODER_APPEND_DOUBLE),
            ('encoder_append_float(', ENCODER_APPEND_FLOAT),
            ('encoder_append_uint(', ENCODER_APPEND_UINT),
            ('encoder_append_int64(', ENCODER_APPEND_INT64),
            ('encoder_append_int32(', ENCODER_APPEND_INT32),
            ('encoder_append_int16(', ENCODER_APPEND_INT16),
            ('encoder_append_int8(', ENCODER_APPEND_INT8),
            ('encoder_append_uint64(', ENCODER_APPEND_UINT64),
            ('encoder_append_uint32(', ENCODER_APPEND_UINT32),
            ('encoder_append_uint16(', ENCODER_APPEND_UINT16),
            ('encoder_append_uint8(', ENCODER_APPEND_UINT8),
            ('encoder_append_bytes(', ENCODER_APPEND_BYTES),
            ('encoder_alloc(', ENCODER_ALLOC),
            ('encoder_abort(', ENCODER_ABORT),
            ('encoder_get_result(', ENCODER_GET_RESULT),
            ('encoder_init(', ENCODER_INIT),
            ('minimum_uint_length(', MINIMUM_UINT_LENGTH),
            ('length_determinant_length(', LENGTH_DETERMINANT_LENGTH)
        ]

        for pattern, definition in functions:
            is_in_helpers = any([pattern in helper for helper in helpers])

            if pattern in definitions or is_in_helpers:
                helpers.insert(0, definition)

        for additional_helpers in self.additional_helpers.values():
            helpers.extend(additional_helpers + [''])

        return [ENCODER_AND_DECODER_STRUCTS] + helpers + ['']


def generate(compiled, namespace):
    return _Generator(namespace).generate(compiled)
