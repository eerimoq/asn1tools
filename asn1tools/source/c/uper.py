"""Unaligned Packed Encoding Rules (UPER) C source code codec generator.

"""

from .utils import ENCODER_AND_DECODER_STRUCTS
from .utils import ENCODER_ABORT
from .utils import DECODER_ABORT
from .utils import Generator
from .utils import camel_to_snake_case
from .utils import is_user_type
from .utils import indent_lines
from .utils import dedent_lines
from ...codecs import uper


ENCODER_INIT = '''\
static void encoder_init(struct encoder_t *self_p,
                         uint8_t *buf_p,
                         size_t size)
{
    self_p->buf_p = buf_p;
    self_p->size = (8 * (ssize_t)size);
    self_p->pos = 0;
}\
'''

ENCODER_GET_RESULT = '''
static ssize_t encoder_get_result(struct encoder_t *self_p)
{
    if (self_p->size >= 0) {
        return ((self_p->pos + 7) / 8);
    } else {
        return (self_p->pos);
    }
}\
'''

ENCODER_ALLOC = '''
static ssize_t encoder_alloc(struct encoder_t *self_p,
                             size_t size)
{
    ssize_t pos;

    if (self_p->pos + (ssize_t)size <= self_p->size) {
        pos = self_p->pos;
        self_p->pos += (ssize_t)size;
    } else {
        pos = -ENOMEM;
        encoder_abort(self_p, ENOMEM);
    }

    return (pos);
}\
'''

ENCODER_APPEND_BIT = '''
static void encoder_append_bit(struct encoder_t *self_p,
                               int value)
{
    ssize_t pos;

    pos = encoder_alloc(self_p, 1);

    if (pos < 0) {
        return;
    }

    if ((pos % 8) == 0) {
        self_p->buf_p[pos / 8] = 0;
    }

    self_p->buf_p[pos / 8] |= (value << (7 - (pos % 8)));
}\
'''

ENCODER_APPEND_BYTES = '''
static void encoder_append_bytes(struct encoder_t *self_p,
                                 const uint8_t *buf_p,
                                 size_t size)
{
    size_t i;
    ssize_t pos;
    size_t byte_pos;
    size_t pos_in_byte;

    pos = encoder_alloc(self_p, 8 * size);

    if (pos < 0) {
        return;
    }

    byte_pos = ((size_t)pos / 8);
    pos_in_byte = ((size_t)pos % 8);

    if (pos_in_byte == 0) {
        memcpy(&self_p->buf_p[byte_pos], buf_p, size);
    } else {
        for (i = 0; i < size; i++) {
            self_p->buf_p[byte_pos + i] |= (buf_p[i] >> pos_in_byte);
            self_p->buf_p[byte_pos + i + 1] = (buf_p[i] << (8 - pos_in_byte));
        }
    }
}\
'''

ENCODER_APPEND_UINT8 = '''
static void encoder_append_uint8(struct encoder_t *self_p,
                                 uint8_t value)
{
    uint8_t buf[1];

    buf[0] = (uint8_t)value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}\
'''

ENCODER_APPEND_UINT16 = '''
static void encoder_append_uint16(struct encoder_t *self_p,
                                  uint16_t value)
{
    uint8_t buf[2];

    buf[0] = (value >> 8);
    buf[1] = value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}\
'''

ENCODER_APPEND_UINT32 = '''
static void encoder_append_uint32(struct encoder_t *self_p,
                                  uint32_t value)
{
    uint8_t buf[4];

    buf[0] = (value >> 24);
    buf[1] = (value >> 16);
    buf[2] = (value >> 8);
    buf[3] = value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}\
'''

ENCODER_APPEND_UINT64 = '''
static void encoder_append_uint64(struct encoder_t *self_p,
                                  uint64_t value)
{
    uint8_t buf[8];

    buf[0] = (value >> 56);
    buf[1] = (value >> 48);
    buf[2] = (value >> 40);
    buf[3] = (value >> 32);
    buf[4] = (value >> 24);
    buf[5] = (value >> 16);
    buf[6] = (value >> 8);
    buf[7] = value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}\
'''

ENCODER_APPEND_INT8 = '''
static void encoder_append_int8(struct encoder_t *self_p,
                                int8_t value)
{
    value += 128;
    encoder_append_uint8(self_p, (uint8_t)value);
}\
'''

ENCODER_APPEND_INT16 = '''
static void encoder_append_int16(struct encoder_t *self_p,
                                 int16_t value)
{
    value += 32768;
    encoder_append_uint16(self_p, (uint16_t)value);
}\
'''

ENCODER_APPEND_INT32 = '''
static void encoder_append_int32(struct encoder_t *self_p,
                                 int32_t value)
{
    value += 2147483648;
    encoder_append_uint32(self_p, (uint32_t)value);
}\
'''

ENCODER_APPEND_INT64 = '''
static void encoder_append_int64(struct encoder_t *self_p,
                                 int64_t value)
{
    uint64_t u64_value;

    u64_value = (uint64_t)value;
    u64_value += 9223372036854775808ul;

    encoder_append_uint64(self_p, u64_value);
}\
'''

ENCODER_APPEND_BOOL = '''
static void encoder_append_bool(struct encoder_t *self_p, bool value)
{
    encoder_append_bit(self_p, value ? 1 : 0);
}\
'''

ENCODER_APPEND_NON_NEGATIVE_BINARY_INTEGER = '''
static void encoder_append_non_negative_binary_integer(struct encoder_t *self_p,
                                                       uint64_t value,
                                                       size_t size)
{
    size_t i;

    for (i = 0; i < size; i++) {
        encoder_append_bit(self_p, (value >> (size - i - 1)) & 1);
    }
}\
'''

DECODER_INIT = '''
static void decoder_init(struct decoder_t *self_p,
                         const uint8_t *buf_p,
                         size_t size)
{
    self_p->buf_p = buf_p;
    self_p->size = (8 * (ssize_t)size);
    self_p->pos = 0;
}\
'''

DECODER_GET_RESULT = '''
static ssize_t decoder_get_result(struct decoder_t *self_p)
{
    if (self_p->size >= 0) {
        return ((self_p->pos + 7) / 8);
    } else {
        return (self_p->pos);
    }
}\
'''

DECODER_FREE = '''
static ssize_t decoder_free(struct decoder_t *self_p,
                            size_t size)
{
    ssize_t pos;

    if (self_p->pos + (ssize_t)size <= self_p->size) {
        pos = self_p->pos;
        self_p->pos += (ssize_t)size;
    } else {
        pos = -EOUTOFDATA;
        decoder_abort(self_p, EOUTOFDATA);
    }

    return (pos);
}\
'''

DECODER_READ_BIT = '''
static int decoder_read_bit(struct decoder_t *self_p)
{
    ssize_t pos;
    int value;

    pos = decoder_free(self_p, 1);

    if (pos >= 0) {
        value = ((self_p->buf_p[pos / 8] >> (7 - (pos % 8))) & 1);
    } else {
        value = 0;
    }

    return (value);
}\
'''

DECODER_READ_BYTES = '''
static void decoder_read_bytes(struct decoder_t *self_p,
                               uint8_t *buf_p,
                               size_t size)
{
    size_t i;
    ssize_t pos;
    size_t byte_pos;
    size_t pos_in_byte;

    pos = decoder_free(self_p, 8 * size);

    if (pos < 0) {
        return;
    }

    byte_pos = ((size_t)pos / 8);
    pos_in_byte = ((size_t)pos % 8);

    if (pos_in_byte == 0) {
        memcpy(buf_p, &self_p->buf_p[byte_pos], size);
    } else {
        for (i = 0; i < size; i++) {
            buf_p[i] = (self_p->buf_p[byte_pos + i] << pos_in_byte);
            buf_p[i] |= (self_p->buf_p[byte_pos + i + 1] >> (8 - pos_in_byte));
        }
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

    return ((buf[0] << 8) | buf[1]);
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
    int8_t value;

    value = (int8_t)decoder_read_uint8(self_p);
    value -= 128;

    return (value);
}\
'''

DECODER_READ_INT16 = '''
static int16_t decoder_read_int16(struct decoder_t *self_p)
{
    int16_t value;

    value = (int16_t)decoder_read_uint16(self_p);
    value -= 32768;

    return (value);
}\
'''

DECODER_READ_INT32 = '''
static int32_t decoder_read_int32(struct decoder_t *self_p)
{
    int32_t value;

    value = (int32_t)decoder_read_uint32(self_p);
    value -= 2147483648;

    return (value);
}\
'''

DECODER_READ_INT64 = '''
static int64_t decoder_read_int64(struct decoder_t *self_p)
{
    uint64_t value;

    value = decoder_read_uint64(self_p);
    value -= 9223372036854775808ul;

    return ((int64_t)value);
}\
'''

DECODER_READ_BOOL = '''
static bool decoder_read_bool(struct decoder_t *self_p)
{
    return (decoder_read_bit(self_p) != 0);
}\
'''

DECODER_READ_NON_NEGATIVE_BINARY_INTEGER = '''
static uint64_t decoder_read_non_negative_binary_integer(struct decoder_t *self_p,
                                                         size_t size)
{
    size_t i;
    uint64_t value;

    value = 0;

    for (i = 0; i < size; i++) {
        value <<= 1;
        value |= (uint64_t)decoder_read_bit(self_p);
    }

    return (value);
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
            lines = self.format_sequence(type_, checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, uper.SequenceOf):
            lines = self.format_sequence_of(type_, checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, uper.Choice):
            lines = self.format_choice(type_, checker)
            lines = dedent_lines(lines[1:-1])
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
        suffix = type_name[:-2]
        location = self.location_inner()

        if (type_.number_of_bits % 8) == 0:
            return (
                [
                    'encoder_append_{}(encoder_p, src_p->{});'.format(
                        suffix,
                        location)
                ],
                [
                    'dst_p->{} = decoder_read_{}(decoder_p);'.format(location,
                                                                     suffix)
                ]
            )
        else:
            return (
                [
                    'encoder_append_non_negative_binary_integer(',
                    '    encoder_p,',
                    '    (uint64_t)(src_p->{} - {}),'.format(location, checker.minimum),
                    '    {});'.format(type_.number_of_bits)
                ],
                [
                    'dst_p->{} = decoder_read_non_negative_binary_integer('.format(
                        location),
                    '    decoder_p,',
                    '    {});'.format(type_.number_of_bits),
                    'dst_p->{} += {};'.format(location, checker.minimum)
                ]
            )

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
                    'encoder_append_bool(encoder_p, src_p->{});'.format(
                        name))
                decode_lines.append(
                    'dst_p->{} = decoder_read_bool(decoder_p);'.format(
                        name))
            elif member.default is not None:
                unique_is_present = self.add_unique_decode_variable('bool {};',
                                                                    'is_present')
                member_name_to_is_present[member.name] = unique_is_present
                encode_lines.append(
                    'encoder_append_bool(encoder_p, src_p->{}{} != {});'.format(
                        self.location_inner('', '.'),
                        member.name,
                        member.default))
                decode_lines.append(
                    '{} = decoder_read_bool(decoder_p);'.format(
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
                'encoder_append_bytes(encoder_p,',
                '                     &src_p->{}buf[0],'.format(location),
                '                     {});'.format(checker.maximum)
            ]
            decode_lines = [
                'decoder_read_bytes(decoder_p,',
                '                   &dst_p->{}buf[0],'.format(location),
                '                   {});'.format(checker.maximum)
            ]
        else:
            encode_lines = [
                'encoder_append_non_negative_binary_integer(',
                '    encoder_p,',
                '    src_p->{}length - {}u,'.format(location, checker.minimum),
                '    {});'.format(type_.number_of_bits),
                'encoder_append_bytes(encoder_p,',
                '                     &src_p->{}buf[0],'.format(location),
                '                     src_p->{}length);'.format(location)
            ]
            decode_lines = [
                'dst_p->{}length = decoder_read_non_negative_binary_integer('.format(
                    location),
                '    decoder_p,',
                '    {});'.format(type_.number_of_bits),
                'dst_p->{}length += {};'.format(location, checker.minimum)
            ]

            if not does_bits_match_range(type_.number_of_bits,
                                         checker.minimum,
                                         checker.maximum):
                decode_lines += [
                    '',
                    'if (dst_p->{}length > {}) {{'.format(location, checker.maximum),
                    '    decoder_abort(decoder_p, EBADLENGTH);',
                    '',
                    '    return;',
                    '}',
                    ''
                ]

            decode_lines += [
                'decoder_read_bytes(decoder_p,',
                '                   &dst_p->{}buf[0],'.format(location),
                '                   dst_p->{}length);'.format(location)
            ]

        return encode_lines, decode_lines

    def format_user_type_inner(self, type_name, module_name):
        module_name_snake = camel_to_snake_case(module_name)
        type_name_snake = camel_to_snake_case(type_name)
        prefix = '{}_{}_{}'.format(self.namespace,
                                   module_name_snake,
                                   type_name_snake)
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
        type_name = self.format_type_name(0, max(type_.root_index_to_member))
        unique_choice = self.add_unique_decode_variable(
            '{} {{}};'.format(type_name),
            'choice')
        choice = '{}choice'.format(self.location_inner('', '.'))

        for member in type_.root_index_to_member.values():
            member_checker = self.get_member_checker(checker,
                                                     member.name)

            with self.asn1_members_backtrace_push(member.name):
                with self.c_members_backtrace_push('value'):
                    with self.c_members_backtrace_push(member.name):
                        choice_encode_lines, choice_decode_lines = self.format_type_inner(
                            member,
                            member_checker)

            index = type_.root_name_to_index[member.name]

            choice_encode_lines = [
                'encoder_append_non_negative_binary_integer(encoder_p, {}, {});'.format(
                    index,
                    type_.root_number_of_bits)
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
                'case {}:'.format(index)
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
            '{} = decoder_read_non_negative_binary_integer(decoder_p, {});'.format(
                unique_choice,
                type_.root_number_of_bits),
            '',
            'switch ({}) {{'.format(unique_choice),
            ''
        ] + decode_lines + [
            'default:',
            '    decoder_abort(decoder_p, EBADCHOICE);',
            '    break;',
            '}',
            ''
        ]

        return encode_lines, decode_lines

    def format_enumerated_inner(self, type_):
        type_name = self.format_type_name(0, max(type_.root_index_to_data))
        unique_value = self.add_unique_decode_variable(
            '{} {{}};'.format(type_name),
            'value')
        location = self.location_inner()

        encode_lines = [
            'encoder_append_non_negative_binary_integer(encoder_p, '
            'src_p->{}, {});'.format(location,
                                     type_.root_number_of_bits)
        ]
        decode_lines = [
            '{} = decoder_read_non_negative_binary_integer('
            'decoder_p, {});'.format(unique_value,
                                     type_.root_number_of_bits)
        ]

        if bin(len(self.get_enumerated_values(type_))).count('1') != 1:
            decode_lines += [
                '',
                'if ({} > {}) {{'.format(unique_value,
                                         len(self.get_enumerated_values(type_)) - 1),
                '    decoder_abort(decoder_p, EBADENUM);',
                '',
                '    return;',
                '}',
                ''
            ]

        decode_lines += [
            'dst_p->{} = (enum {}_e){};'.format(location,
                                                self.location,
                                                unique_value)
        ]

        return encode_lines, decode_lines

    def format_null_inner(self):
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

    def format_sequence_of_inner(self, type_, checker):
        type_name = self.format_type_name(0, checker.maximum)
        unique_i = self.add_unique_variable('{} {{}};'.format(type_name),
                                            'i')

        with self.c_members_backtrace_push('elements[{}]'.format(unique_i)):
            encode_lines, decode_lines = self.format_type_inner(
                type_.element_type,
                checker.element_type)

        if checker.minimum == checker.maximum:
            first_encode_lines = first_decode_lines = [
                '',
                'for ({0} = 0; {0} < {1}; {0}++) {{'.format(
                    unique_i,
                    checker.maximum)
            ]
        else:
            location = self.location_inner('', '.')
            first_encode_lines = [
                'encoder_append_non_negative_binary_integer(',
                '    encoder_p,',
                '    src_p->{}length - {}u,'.format(location, checker.minimum),
                '    {});'.format(type_.number_of_bits),
                '',
                'for ({0} = 0; {0} < src_p->{1}length; {0}++) {{'.format(
                    unique_i,
                    location)
            ]
            first_decode_lines = [
                'dst_p->{}length = decoder_read_non_negative_binary_integer('.format(
                    location),
                '    decoder_p,',
                '    {});'.format(type_.number_of_bits),
                'dst_p->{}length += {};'.format(location, checker.minimum),
                ''
            ]

            if not does_bits_match_range(type_.number_of_bits,
                                         checker.minimum,
                                         checker.maximum):
                first_decode_lines += [
                    'if (dst_p->{}length > {}) {{'.format(location, checker.maximum),
                    '    decoder_abort(decoder_p, EBADLENGTH);',
                    '',
                    '    return;',
                    '}',
                    ''
                ]

            first_decode_lines += [
                'for ({0} = 0; {0} < dst_p->{1}length; {0}++) {{'.format(
                    unique_i,
                    location)
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
            return self.format_user_type_inner(type_.type_name,
                                               type_.module_name)
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

    def generate_helpers(self, definitions):
        helpers = []

        functions = [
            (
                'decoder_read_non_negative_binary_integer(',
                DECODER_READ_NON_NEGATIVE_BINARY_INTEGER
            ),
            ('decoder_read_bool(', DECODER_READ_BOOL),
            ('decoder_read_int64(', DECODER_READ_INT64),
            ('decoder_read_int32(', DECODER_READ_INT32),
            ('decoder_read_int16(', DECODER_READ_INT16),
            ('decoder_read_int8(', DECODER_READ_INT8),
            ('decoder_read_uint64(', DECODER_READ_UINT64),
            ('decoder_read_uint32(', DECODER_READ_UINT32),
            ('decoder_read_uint16(', DECODER_READ_UINT16),
            ('decoder_read_uint8(', DECODER_READ_UINT8),
            ('decoder_read_bytes(', DECODER_READ_BYTES),
            ('decoder_read_bit(', DECODER_READ_BIT),
            ('decoder_free(', DECODER_FREE),
            ('decoder_abort(', DECODER_ABORT),
            ('decoder_get_result(', DECODER_GET_RESULT),
            ('decoder_init(', DECODER_INIT),
            (
                'encoder_append_non_negative_binary_integer(',
                ENCODER_APPEND_NON_NEGATIVE_BINARY_INTEGER
            ),
            ('encoder_append_bool(', ENCODER_APPEND_BOOL),
            ('encoder_append_int64(', ENCODER_APPEND_INT64),
            ('encoder_append_int32(', ENCODER_APPEND_INT32),
            ('encoder_append_int16(', ENCODER_APPEND_INT16),
            ('encoder_append_int8(', ENCODER_APPEND_INT8),
            ('encoder_append_uint64(', ENCODER_APPEND_UINT64),
            ('encoder_append_uint32(', ENCODER_APPEND_UINT32),
            ('encoder_append_uint16(', ENCODER_APPEND_UINT16),
            ('encoder_append_uint8(', ENCODER_APPEND_UINT8),
            ('encoder_append_bytes(', ENCODER_APPEND_BYTES),
            ('encoder_append_bit(', ENCODER_APPEND_BIT),
            ('encoder_alloc(', ENCODER_ALLOC),
            ('encoder_abort(', ENCODER_ABORT),
            ('encoder_get_result(', ENCODER_GET_RESULT),
            ('encoder_init(', ENCODER_INIT)
        ]

        for pattern, definition in functions:
            is_in_helpers = any([pattern in helper for helper in helpers])

            if pattern in definitions or is_in_helpers:
                helpers.insert(0, definition)

        return [ENCODER_AND_DECODER_STRUCTS] + helpers + ['']


def generate(compiled, namespace):
    return _Generator(namespace).generate(compiled)
