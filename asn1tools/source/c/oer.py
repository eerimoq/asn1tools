"""Basic Octet Encoding Rules (OER) C source code codec generator.

"""

import bitstruct

from .utils import ENCODER_AND_DECODER_STRUCTS
from .utils import ENCODER_ABORT
from .utils import DECODER_ABORT
from .utils import Generator
from .utils import camel_to_snake_case
from .utils import is_user_type
from .utils import indent_lines
from .utils import dedent_lines
from ...codecs import oer


MINIMUM_UINT_LENGTH = '''
static uint8_t minimum_uint_length(uint32_t value)
{
    uint8_t length;

    if (value < 256) {
        length = 1;
    } else if (value < 65536) {
        length = 2;
    } else if (value < 16777216) {
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
static ssize_t encoder_get_result(struct encoder_t *self_p)
{
    return (self_p->pos);
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

    memcpy(&self_p->buf_p[pos], buf_p, size);
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
        encoder_append_uint8(self_p, value);
        break;

    case 2:
        encoder_append_uint16(self_p, value);
        break;

    case 3:
        encoder_append_uint8(self_p, value >> 16);
        encoder_append_uint16(self_p, value);
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

    memcpy(&i32, &value, sizeof(i32));

    encoder_append_uint32(self_p, i32);
}\
'''

ENCODER_APPEND_DOUBLE = '''
static void encoder_append_double(struct encoder_t *self_p,
                                  double value)
{
    uint64_t i64;

    memcpy(&i64, &value, sizeof(i64));

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
    if (length < 128) {
        encoder_append_int8(self_p, length);
    } else if (length < 256) {
        encoder_append_uint8(self_p, 0x81u);
        encoder_append_uint8(self_p, length);
    } else if (length < 65536) {
        encoder_append_uint8(self_p, 0x82u);
        encoder_append_uint16(self_p, length);
    } else if (length < 16777216) {
        length |= (0x83u << 24);
        encoder_append_uint32(self_p, length);
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
static ssize_t decoder_get_result(struct decoder_t *self_p)
{
    return (self_p->pos);
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

DECODER_READ_BYTES = '''
static void decoder_read_bytes(struct decoder_t *self_p,
                               uint8_t *buf_p,
                               size_t size)
{
    ssize_t pos;

    pos = decoder_free(self_p, size);

    if (pos >= 0) {
        memcpy(buf_p, &self_p->buf_p[pos], size);
    } else {
        memset(buf_p, 0, size);
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
        value = 0xffffffff;
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

    memcpy(&value, &i32, sizeof(value));

    return (value);
}\
'''

DECODER_READ_DOUBLE = '''
static double decoder_read_double(struct decoder_t *self_p)
{
    double value;
    uint64_t i64;

    i64 = decoder_read_uint64(self_p);

    memcpy(&value, &i64, sizeof(value));

    return (value);
}\
'''

DECODER_READ_BOOL = '''
static bool decoder_read_bool(struct decoder_t *self_p)
{
    return (decoder_read_uint8(self_p) != 0);
}\
'''

DECODER_READ_LENGTH_DETERMINANT = '''
static uint32_t decoder_read_length_determinant(struct decoder_t *self_p)
{
    uint32_t length;

    length = decoder_read_uint8(self_p);

    if (length & 0x80u) {
        switch (length & 0x7f) {

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
            length = 0xffffffff;
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


class _Generator(Generator):

    def format_real(self, type_):
        if type_.fmt is None:
            raise self.error('REAL not IEEE 754 binary32 or binary64.')

        if type_.fmt == '>f':
            return ['float']
        else:
            return ['double']

    def get_enumerated_values(self, type_):
        return type_.value_to_data.values()

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

        optionals = [
            member
            for member in type_.root_members
            if member.optional or member.default is not None
        ]

        present_mask_length = ((len(optionals) + 7) // 8)
        default_condition_by_member_name = {}

        if present_mask_length > 0:
            fmt = 'uint8_t {{}}[{}];'.format(present_mask_length)
            unique_present_mask = self.add_unique_variable(fmt, 'present_mask')

            for i in range(present_mask_length):
                encode_lines.append('{}[{}] = 0;'.format(unique_present_mask,
                                                         i))

            encode_lines.append('')

            decode_lines += [
                'decoder_read_bytes(decoder_p,',
                '                   &{}[0],'.format(unique_present_mask),
                '                   sizeof({}));'.format(unique_present_mask),
                ''
            ]

            for i, member in enumerate(optionals):
                byte, bit = divmod(i, 8)
                mask = '0x{:02x}'.format(1 << (7 - bit))
                present_mask = '{}[{}]'.format(unique_present_mask,
                                               byte)
                default_condition = '({0} & {1}) == {1}'.format(present_mask, mask)
                default_condition_by_member_name[member.name] = default_condition

                if member.optional:
                    encode_lines += [
                        'if (src_p->{}is_{}_present) {{'.format(
                            self.location_inner('', '.'),
                            member.name),
                        '    {} |= {};'.format(present_mask, mask),
                        '}',
                        ''
                    ]
                    decode_lines.append(
                        'dst_p->{0}is_{1}_present = (({2} & {3}) == {3});'.format(
                            self.location_inner('', '.'),
                            member.name,
                            present_mask,
                            mask))
                else:
                    encode_lines += [
                        'if (src_p->{}{} != {}) {{'.format(self.location_inner('', '.'),
                                                           member.name,
                                                           member.default),
                        '    {} |= {};'.format(present_mask, mask),
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

        return encode_lines, decode_lines

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
                'if (dst_p->{}length > {}) {{'.format(location, checker.maximum),
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
                'if (dst_p->{}length > {}) {{'.format(location, checker.maximum),
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

    def format_enumerated_inner(self):
        return (
            [
                'encoder_append_uint8(encoder_p, src_p->{});'.format(
                    self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_uint8(decoder_p);'.format(
                    self.location_inner())
            ]
        )

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
                'for ({ui} = 0; {ui} < {maximum}; {ui}++) {{'.format(
                    ui=unique_i,
                    maximum=checker.maximum),
            ] + indent_lines(encode_lines)
            decode_lines = [
                '{} = decoder_read_uint8(decoder_p);'.format(
                    unique_number_of_length_bytes),
                '{} = decoder_read_uint8(decoder_p);'.format(unique_length),
                '',
                'if (({} != 1) || ({} > {})) {{'.format(unique_number_of_length_bytes,
                                                        unique_length,
                                                        checker.maximum),
                '    decoder_abort(decoder_p, EBADLENGTH);',
                '',
                '    return;',
                '}',
                '',
                'for ({ui} = 0; {ui} < {maximum}; {ui}++) {{'.format(
                    ui=unique_i,
                    maximum=checker.maximum),
            ] + indent_lines(decode_lines)
        else:
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
                'dst_p->{}length = decoder_read_uint('.format(location),
                '    decoder_p,',
                '    {});'.format(unique_number_of_length_bytes),
                '',
                'if (dst_p->{}length > {}) {{'.format(location, checker.maximum),
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
            return self.format_enumerated_inner()
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
            return self.format_enumerated_inner()
        elif isinstance(type_, oer.Null):
            return self.format_null_inner()
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
            ('minimum_uint_length(', MINIMUM_UINT_LENGTH)
        ]

        for pattern, definition in functions:
            is_in_helpers = any([pattern in helper for helper in helpers])

            if pattern in definitions or is_in_helpers:
                helpers.insert(0, definition)

        return [ENCODER_AND_DECODER_STRUCTS] + helpers + ['']


def generate(compiled, namespace):
    return _Generator(namespace).generate(compiled)
