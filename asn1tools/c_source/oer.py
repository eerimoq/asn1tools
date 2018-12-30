"""Basic Octet Encoding Rules (OER) codec generator.

"""

import struct

from .utils import canonical
from .utils import camel_to_snake_case
from ..codecs import oer
from ..errors import Error


TYPE_DECLARATION_FMT = '''\
/**
 * Type {type_name} in module {module_name}.
 */
{helper_types}\
struct {namespace}_{module_name_snake}_{type_name_snake}_t {{
{members}
}};
'''

DECLARATION_FMT = '''\
/**
 * Encode type {type_name} defined in module {module_name}.
 *
 * @param[out] dst_p Buffer to encode into.
 * @param[in] size Size of dst_p.
 * @param[in] src_p Data to encode.
 *
 * @return Encoded data length or negative error code.
 */
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_encode(
    uint8_t *dst_p,
    size_t size,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p);

/**
 * Decode type {type_name} defined in module {module_name}.
 *
 * @param[out] dst_p Decoded data.
 * @param[in] src_p Data to decode.
 * @param[in] size Size of src_p.
 *
 * @return Number of bytes decoded or negative error code.
 */
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_decode(
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p,
    const uint8_t *src_p,
    size_t size);
'''

DEFINITION_INNER_FMT = '''\
static void {namespace}_{module_name_snake}_{type_name_snake}_encode_inner(
    struct encoder_t *encoder_p,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p)
{{
{encode_body}\
}}

static void {namespace}_{module_name_snake}_{type_name_snake}_decode_inner(
    struct decoder_t *decoder_p,
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p)
{{
{decode_body}\
}}
'''

DEFINITION_FMT = '''\
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_encode(
    uint8_t *dst_p,
    size_t size,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p)
{{
    struct encoder_t encoder;

    encoder_init(&encoder, dst_p, size);
    {namespace}_{module_name_snake}_{type_name_snake}_encode_inner(&encoder, src_p);

    return (encoder_get_result(&encoder));
}}

ssize_t {namespace}_{module_name_snake}_{type_name_snake}_decode(
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p,
    const uint8_t *src_p,
    size_t size)
{{
    struct decoder_t decoder;

    decoder_init(&decoder, src_p, size);
    {namespace}_{module_name_snake}_{type_name_snake}_decode_inner(&decoder, dst_p);

    return (decoder_get_result(&decoder));
}}
'''

ENCODER_AND_DECODER_STRUCTS = '''\
struct encoder_t {
    uint8_t *buf_p;
    ssize_t size;
    ssize_t pos;
};

struct decoder_t {
    const uint8_t *buf_p;
    ssize_t size;
    ssize_t pos;
};
'''

ENCODER_INIT = '''\
static void encoder_init(struct encoder_t *self_p,
                         uint8_t *buf_p,
                         size_t size)
{
    self_p->buf_p = buf_p;
    self_p->size = size;
    self_p->pos = 0;
}\
'''

ENCODER_GET_RESULT = '''
static ssize_t encoder_get_result(struct encoder_t *self_p)
{
    return (self_p->pos);
}\
'''

ENCODER_ABORT = '''
static void encoder_abort(struct encoder_t *self_p,
                          ssize_t error)
{
    if (self_p->size >= 0) {
        self_p->size = -error;
        self_p->pos = -error;
    }
}\
'''

ENCODER_ALLOC = '''
static size_t encoder_alloc(struct encoder_t *self_p,
                            size_t size)
{
    ssize_t pos;

    if (self_p->pos + (ssize_t)size <= self_p->size) {
        pos = self_p->pos;
        self_p->pos += size;
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

ENCODER_APPEND_INTEGER_8 = '''
static void encoder_append_integer_8(struct encoder_t *self_p,
                                     uint8_t value)
{
    encoder_append_bytes(self_p, &value, sizeof(value));
}\
'''

ENCODER_APPEND_INTEGER_16 = '''
static void encoder_append_integer_16(struct encoder_t *self_p,
                                      uint16_t value)
{
    uint8_t buf[2];

    buf[0] = (value >> 8);
    buf[1] = value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}\
'''

ENCODER_APPEND_INTEGER_32 = '''
static void encoder_append_integer_32(struct encoder_t *self_p,
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

ENCODER_APPEND_INTEGER_64 = '''
static void encoder_append_integer_64(struct encoder_t *self_p,
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

ENCODER_APPEND_FLOAT = '''
static void encoder_append_float(struct encoder_t *self_p,
                                 float value)
{
    uint32_t i32;

    memcpy(&i32, &value, sizeof(i32));

    encoder_append_integer_32(self_p, i32);
}\
'''

ENCODER_APPEND_DOUBLE = '''
static void encoder_append_double(struct encoder_t *self_p,
                                  double value)
{
    uint64_t i64;

    memcpy(&i64, &value, sizeof(i64));

    encoder_append_integer_64(self_p, i64);
}\
'''

ENCODER_APPEND_BOOL = '''
static void encoder_append_bool(struct encoder_t *self_p, bool value)
{
    encoder_append_integer_8(self_p, value ? 255 : 0);
}\
'''

ENCODER_APPEND_LENGTH_DETERMINANT = '''
static void encoder_append_length_determinant(struct encoder_t *self_p,
                                              uint32_t length)
{
    if (length < 128) {
        encoder_append_integer_8(self_p, length);
    } else if (length < 256) {
        encoder_append_integer_8(self_p, 0x80 | 1);
        encoder_append_integer_8(self_p, length);
    } else if (length < 65536) {
        encoder_append_integer_8(self_p, 0x80 | 2);
        encoder_append_integer_16(self_p, length);
    } else if (length < 16777216) {
        length |= ((0x80 | 3) << 24);
        encoder_append_integer_32(self_p, length);
    } else {
        encoder_append_integer_8(self_p, 0x80 | 4);
        encoder_append_integer_32(self_p, length);
    }
}\
'''

DECODER_INIT = '''
static void decoder_init(struct decoder_t *self_p,
                         const uint8_t *buf_p,
                         size_t size)
{
    self_p->buf_p = buf_p;
    self_p->size = size;
    self_p->pos = 0;
}\
'''

DECODER_GET_RESULT = '''
static ssize_t decoder_get_result(struct decoder_t *self_p)
{
    return (self_p->pos);
}\
'''

DECODER_ABORT = '''
static void decoder_abort(struct decoder_t *self_p,
                          ssize_t error)
{
    if (self_p->size >= 0) {
        self_p->size = -error;
        self_p->pos = -error;
    }
}\
'''

DECODER_FREE = '''
static size_t decoder_free(struct decoder_t *self_p,
                           size_t size)
{
    ssize_t pos;

    if (self_p->pos + (ssize_t)size <= self_p->size) {
        pos = self_p->pos;
        self_p->pos += size;
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

DECODER_READ_INTEGER_8 = '''
static uint8_t decoder_read_integer_8(struct decoder_t *self_p)
{
    uint8_t value;

    decoder_read_bytes(self_p, &value, sizeof(value));

    return (value);
}\
'''

DECODER_READ_INTEGER_16 = '''
static uint16_t decoder_read_integer_16(struct decoder_t *self_p)
{
    uint8_t buf[2];

    decoder_read_bytes(self_p, &buf[0], sizeof(buf));

    return ((buf[0] << 8) | buf[1]);
}\
'''

DECODER_READ_INTEGER_32 = '''
static uint32_t decoder_read_integer_32(struct decoder_t *self_p)
{
    uint8_t buf[4];

    decoder_read_bytes(self_p, &buf[0], sizeof(buf));

    return ((buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]);
}\
'''

DECODER_READ_INTEGER_64 = '''
static uint64_t decoder_read_integer_64(struct decoder_t *self_p)
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

DECODER_READ_FLOAT = '''
static float decoder_read_float(struct decoder_t *self_p)
{
    float value;
    uint32_t i32;

    i32 = decoder_read_integer_32(self_p);

    memcpy(&value, &i32, sizeof(value));

    return (value);
}\
'''

DECODER_READ_DOUBLE = '''
static double decoder_read_double(struct decoder_t *self_p)
{
    double value;
    uint64_t i64;

    i64 = decoder_read_integer_64(self_p);

    memcpy(&value, &i64, sizeof(value));

    return (value);
}\
'''

DECODER_READ_BOOL = '''
static bool decoder_read_bool(struct decoder_t *self_p)
{
    uint8_t value;

    value = decoder_read_integer_8(self_p);

    return (value != 0);
}\
'''

DECODER_READ_LENGTH_DETERMINANT = '''
static uint32_t decoder_read_length_determinant(struct decoder_t *self_p)
{
    uint32_t length;

    length = decoder_read_integer_8(self_p);

    if (length & 0x80) {
        switch (length & 0x7f) {

        case 1:
            length = decoder_read_integer_8(self_p);
            break;

        case 2:
            length = decoder_read_integer_16(self_p);
            break;

        case 3:
            length = ((decoder_read_integer_8(self_p) << 16)
                      | decoder_read_integer_16(self_p));
            break;

        case 4:
            length = decoder_read_integer_32(self_p);
            break;

        default:
            length = 0xffffffff;
            break;
        }
    }

    return (length);
}\
'''


class _MembersBacktracesContext(object):

    def __init__(self, backtraces, member_name):
        self.backtraces = backtraces
        self.member_name = member_name

    def __enter__(self):
        for backtrace in self.backtraces:
            backtrace.append(self.member_name)

    def __exit__(self, *args):
        for backtrace in self.backtraces:
            backtrace.pop()


def _join_lines(lines, suffix):
    return[line + suffix for line in lines[:-1]] + lines[-1:]


def _type_length(length):
    if length <= 8:
        return 8
    elif length <= 16:
        return 16
    elif length <= 32:
        return 32
    else:
        return 64


def _format_type_name(minimum, maximum):
    length = _type_length((maximum - minimum).bit_length())
    type_name = 'int{}_t'.format(length)

    if minimum >= 0:
        type_name = 'u' + type_name

    return type_name


def _is_user_type(type_):
    return type_.module_name is not None


def _strip_blank_lines(lines):
    try:
        while lines[0] == '':
            del lines[0]

        while lines[-1] == '':
            del lines[-1]
    except IndexError:
        pass

    stripped = []

    for line in lines:
        if line == '' and stripped[-1] == '':
            continue

        stripped.append(line)

    return stripped


def _indent_lines(lines):
    indented_lines = []

    for line in lines:
        if line:
            indented_line = 4 * ' ' + line
        else:
            indented_line = line

        indented_lines.append(indented_line)

    return _strip_blank_lines(indented_lines)


def _dedent_lines(lines):
    return [line[4:] for line in lines]


class _Generator(object):

    def __init__(self, namespace):
        self.namespace = canonical(namespace)
        self.asn1_members_backtrace = []
        self.c_members_backtrace = []
        self.module_name = None
        self.type_name = None
        self.helper_lines = []
        self.base_variables = set()
        self.used_suffixes_by_base_variables = {}
        self.encode_variable_lines = []
        self.decode_variable_lines = []

    @property
    def module_name_snake(self):
        return camel_to_snake_case(self.module_name)

    @property
    def type_name_snake(self):
        return camel_to_snake_case(self.type_name)

    @property
    def location(self):
        location = '{}_{}_{}'.format(self.namespace,
                                     self.module_name_snake,
                                     self.type_name_snake)

        if self.asn1_members_backtrace:
            location += '_{}'.format('_'.join(self.asn1_members_backtrace))

        return location

    def location_inner(self, default='value', end=''):
        if self.c_members_backtrace:
            return '.'.join(self.c_members_backtrace) + end
        else:
            return default

    def members_backtrace_push(self, member_name):
        backtraces = [
            self.asn1_members_backtrace,
            self.c_members_backtrace
        ]

        return _MembersBacktracesContext(backtraces, member_name)

    def asn1_members_backtrace_push(self, member_name):
        backtraces = [self.asn1_members_backtrace]

        return _MembersBacktracesContext(backtraces, member_name)

    def c_members_backtrace_push(self, member_name):
        backtraces = [self.c_members_backtrace]

        return _MembersBacktracesContext(backtraces, member_name)

    def get_member_checker(self, checker, name):
        for member in checker.members:
            if member.name == name:
                return member

        raise Error('No member checker found for {}.'.format(name))

    def add_unique_variable(self, fmt, name, variable_lines=None):
        if name in self.base_variables:
            try:
                suffix = self.used_suffixes_by_base_variables[name]
                suffix += 1
            except KeyError:
                suffix = 2

            self.used_suffixes_by_base_variables[name] = suffix
            unique_name = '{}_{}'.format(name, suffix)
        else:
            self.base_variables.add(name)
            unique_name = name

        line = fmt.format(unique_name)

        if variable_lines is None:
            self.encode_variable_lines.append(line)
            self.decode_variable_lines.append(line)
        elif variable_lines == 'encode':
            self.encode_variable_lines.append(line)
        else:
            self.decode_variable_lines.append(line)

        return unique_name

    def add_unique_encode_variable(self, fmt, name):
        return self.add_unique_variable(fmt, name, 'encode')

    def add_unique_decode_variable(self, fmt, name):
        return self.add_unique_variable(fmt, name, 'decode')

    def format_integer(self, checker):
        if not checker.is_bound():
            raise Error('INTEGER not fixed size.')

        type_name = _format_type_name(checker.minimum, checker.maximum)

        return [type_name]

    def format_real(self, type_):
        if type_.fmt is None:
            raise Error('REAL not IEEE 754.')

        if type_.fmt == '>f':
            return ['float']
        else:
            return ['double']

    def format_boolean(self):
        return ['bool']

    def format_octet_string(self, checker):
        if not checker.has_upper_bound():
            raise Error('OCTET STRING has no maximum length.')

        if checker.minimum == checker.maximum:
            lines = []
        elif checker.maximum < 256:
            lines = ['    uint8_t length;']
        elif checker.maximum < 65536:
            lines = ['    uint16_t length;']
        else:
            lines = ['    uint32_t length;']

        return [
            'struct {'
        ] + lines + [
            '    uint8_t buf[{}];'.format(checker.maximum),
            '}'
        ]

    def format_utf8_string(self, checker):
        if not checker.has_upper_bound():
            raise Error('UTF8String has no maximum length.')

        raise NotImplementedError

    def format_sequence(self, type_, checker):
        lines = []

        for member in type_.root_members:
            member_checker = self.get_member_checker(checker, member.name)

            if member.optional:
                lines += ['bool is_{}_present;'.format(member.name)]

            with self.members_backtrace_push(member.name):
                member_lines = self.format_type(member, member_checker)

            if member_lines:
                member_lines[-1] += ' {};'.format(member.name)

            lines += member_lines

        return ['struct {'] + _indent_lines(lines) + ['}']

    def format_sequence_of(self, type_, checker):
        if not checker.is_bound():
            raise Error('SEQUENCE OF has no maximum length.')

        lines = self.format_type(type_.element_type, checker.element_type)

        if lines:
            lines[-1] += ' elements[{}];'.format(checker.maximum)

        if checker.minimum != checker.maximum:
            lines = ['uint8_t length;'] + lines

        return ['struct {'] + _indent_lines(lines) + ['}']

    def format_enumerated(self, type_):
        lines = ['enum {}_e'.format(self.location)]

        values = [
            '    {}_{}_e'.format(self.location, value)
            for value in type_.value_to_data.values()
        ]
        self.helper_lines += [
            'enum {}_e {{'.format(self.location)
        ] + _join_lines(values, ',') + [
            '};',
            ''
        ]

        return lines

    def format_choice(self, type_, checker):
        lines = []
        choices = []

        for member in type_.root_members:
            member_checker = self.get_member_checker(checker,
                                                     member.name)

            with self.members_backtrace_push(member.name):
                choice_lines = self.format_type(member, member_checker)

            if choice_lines:
                choice_lines[-1] += ' {};'.format(member.name)

            lines += choice_lines
            choices.append('    {}_choice_{}_e'.format(self.location,
                                                       member.name))

        self.helper_lines += [
            'enum {}_choice_e {{'.format(self.location)
        ] + _join_lines(choices, ',') + [
            '};',
            ''
        ]

        lines = [
            'enum {}_choice_e choice;'.format(self.location),
            'union {'
        ] + _indent_lines(lines) + [
            '} value;'
        ]

        lines = ['struct {'] + _indent_lines(lines) + ['}']

        return lines

    def format_user_type(self, type_name, module_name):
        module_name_snake = camel_to_snake_case(module_name)
        type_name_snake = camel_to_snake_case(type_name)

        return ['struct {}_{}_{}_t'.format(self.namespace,
                                           module_name_snake,
                                           type_name_snake)]

    def format_type(self, type_, checker):
        if isinstance(type_, oer.Integer):
            lines = self.format_integer(checker)
        elif isinstance(type_, oer.Boolean):
            lines = self.format_boolean()
        elif isinstance(type_, oer.Real):
            lines = self.format_real(type_)
        elif isinstance(type_, oer.Null):
            lines = []
        elif isinstance(type_, oer.OctetString):
            lines = self.format_octet_string(checker)
        elif _is_user_type(type_):
            lines = self.format_user_type(type_.type_name,
                                          type_.module_name)
        elif isinstance(type_, oer.Sequence):
            lines = self.format_sequence(type_, checker)
        elif isinstance(type_, oer.Choice):
            lines = self.format_choice(type_, checker)
        elif isinstance(type_, oer.SequenceOf):
            lines = self.format_sequence_of(type_, checker)
        elif isinstance(type_, oer.Enumerated):
            lines = self.format_enumerated(type_)
        else:
            raise NotImplementedError(type_)

        return lines

    def reset(self):
        self.helper_lines = []
        self.base_variables = set()
        self.used_suffixes_by_base_variables = {}
        self.encode_variable_lines = []
        self.decode_variable_lines = []

    def generate_type_declaration(self, compiled_type):
        type_ = compiled_type.type
        checker = compiled_type.constraints_checker.type
        lines = []

        try:
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
            elif isinstance(type_, oer.UTF8String):
                lines = self.format_utf8_string(checker)
            elif isinstance(type_, oer.Sequence):
                lines = self.format_sequence(type_, checker)[1:-1]
                lines = _dedent_lines(lines)
            elif isinstance(type_, oer.SequenceOf):
                lines = self.format_sequence_of(type_, checker)[1:-1]
                lines = _dedent_lines(lines)
            elif isinstance(type_, oer.Choice):
                lines = self.format_choice(type_, checker)
                lines = _dedent_lines(lines[1:-1])
            elif isinstance(type_, oer.OctetString):
                lines = self.format_octet_string(checker)[1:-1]
                lines = _dedent_lines(lines)
            elif isinstance(type_, oer.Null):
                lines = []
            else:
                raise NotImplementedError(type_)
        except Error:
            return []

        if not lines:
            lines = ['uint8_t dummy;']

        lines = _indent_lines(lines)

        if self.helper_lines:
            self.helper_lines.append('')

        return [
            TYPE_DECLARATION_FMT.format(namespace=self.namespace,
                                        module_name=self.module_name,
                                        type_name=self.type_name,
                                        module_name_snake=self.module_name_snake,
                                        type_name_snake=self.type_name_snake,
                                        helper_types='\n'.join(self.helper_lines),
                                        members='\n'.join(lines))
        ]

    def generate_declaration(self):
        return DECLARATION_FMT.format(namespace=self.namespace,
                                      module_name=self.module_name,
                                      type_name=self.type_name,
                                      module_name_snake=self.module_name_snake,
                                      type_name_snake=self.type_name_snake)

    def format_integer_inner(self, checker):
        type_name = _format_type_name(checker.minimum, checker.maximum)

        length = {
            'int8_t': 8,
            'uint8_t': 8,
            'int16_t': 16,
            'uint16_t': 16,
            'int32_t': 32,
            'uint32_t': 32,
            'int64_t': 64,
            'uint64_t': 64
        }[type_name]

        return (
            [
                'encoder_append_integer_{}(encoder_p, src_p->{});'.format(
                    length,
                    self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_integer_{}(decoder_p);'.format(
                    self.location_inner(),
                    length)
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
        member_name_to_mask = {}
        member_name_to_present_mask = {}

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
                member_name_to_mask[member.name] = mask
                present_mask = '{}[{}]'.format(unique_present_mask,
                                               byte)
                member_name_to_present_mask[member.name] = present_mask

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
            member_checker = self.get_member_checker(checker, member.name)

            with self.members_backtrace_push(member.name):
                member_encode_lines, member_decode_lines = self.format_type_inner(
                    member,
                    member_checker)

            location = self.location_inner('', '.')

            if member.optional:
                is_present = '{}is_{}_present'.format(location, member.name)
                member_encode_lines = [
                    '',
                    'if (src_p->{}) {{'.format(is_present)
                ] + _indent_lines(member_encode_lines) + [
                    '}',
                    ''
                ]
                member_decode_lines = [
                    '',
                    'if (dst_p->{}) {{'.format(is_present)
                ] + _indent_lines(member_decode_lines) + [
                    '}',
                    ''
                ]
            elif member.default is not None:
                name = '{}{}'.format(location, member.name)
                member_encode_lines = [
                    '',
                    'if (src_p->{} != {}) {{'.format(name, member.default)
                ] + _indent_lines(member_encode_lines) + [
                    '}',
                    ''
                ]
                mask = member_name_to_mask[member.name]
                present_mask = member_name_to_present_mask[member.name]
                member_decode_lines = [
                    '',
                    'if (({0} & {1}) == {1}) {{'.format(present_mask, mask)
                ] + _indent_lines(member_decode_lines) + [
                    '} else {',
                    '    dst_p->{} = {};'.format(name, member.default),
                    '}',
                    ''
                ]

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
                'encoder_append_integer_8(encoder_p, src_p->{}length);'.format(
                    location),
                'encoder_append_bytes(encoder_p,',
                '                     &src_p->{}buf[0],'.format(location),
                '                     src_p->{}length);'.format(location)
            ]
            decode_lines = [
                'dst_p->{}length = decoder_read_integer_8(decoder_p);'.format(
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
        unique_tag = self.add_unique_decode_variable('uint8_t {};', 'tag')
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

            if len(member.tag) != 1:
                raise NotImplementedError(
                    'CHOICE tags of more than one byte are not yet supported.')

            tag = struct.unpack('B', member.tag)[0]

            choice_encode_lines = [
                'encoder_append_integer_8(encoder_p, 0x{:02x});'.format(tag)
            ] + choice_encode_lines + [
                'break;'
            ]
            encode_lines += [
                'case {}_choice_{}_e:'.format(self.location, member.name)
            ] + _indent_lines(choice_encode_lines) + [
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
                'case 0x{:02x}:'.format(tag)
            ] + _indent_lines(choice_decode_lines) + [
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
            '{} = decoder_read_integer_8(decoder_p);'.format(unique_tag),
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
                'encoder_append_integer_8(encoder_p, src_p->{});'.format(
                    self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_integer_8(decoder_p);'.format(
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
        unique_i = self.add_unique_variable('uint8_t {};', 'i')

        if checker.minimum == checker.maximum:
            unique_length = self.add_unique_decode_variable('uint8_t {};',
                                                            'length')

        with self.c_members_backtrace_push('elements[{}]'.format(unique_i)):
            encode_lines, decode_lines = self.format_type_inner(
                type_.element_type,
                checker.element_type)

        if checker.minimum == checker.maximum:
            encode_lines = [
                'encoder_append_integer_8(encoder_p, 1);',
                'encoder_append_integer_8(encoder_p, {});'.format(checker.maximum),
                '',
                'for ({ui} = 0; {ui} < {maximum}; {ui}++) {{'.format(
                    ui=unique_i,
                    maximum=checker.maximum),
            ] + _indent_lines(encode_lines)
            decode_lines = [
                'decoder_read_integer_8(decoder_p);',
                '{} = decoder_read_integer_8(decoder_p);'.format(unique_length),
                '',
                'if ({} > {}) {{'.format(unique_length, checker.maximum),
                '    decoder_abort(decoder_p, EBADLENGTH);',
                '',
                '    return;',
                '}',
                '',
                'for ({ui} = 0; {ui} < {maximum}; {ui}++) {{'.format(
                    ui=unique_i,
                    maximum=checker.maximum),
            ] + _indent_lines(decode_lines)
        else:
            encode_lines = [
                'encoder_append_integer_8(encoder_p, 1);',
                'encoder_append_integer_8(encoder_p, src_p->{}length);'.format(
                    self.location_inner('', '.')),
                '',
                'for ({ui} = 0; {ui} < src_p->{loc}length; {ui}++) {{'.format(
                    ui=unique_i,
                    loc=self.location_inner('', '.')),
            ] + _indent_lines(encode_lines)
            decode_lines = [
                'decoder_read_integer_8(decoder_p);',
                'dst_p->{}length = decoder_read_integer_8(decoder_p);'.format(
                    self.location_inner('', '.')),
                '',
                'if (dst_p->{}length > {}) {{'.format(self.location_inner('', '.'),
                                                      checker.maximum),
                '    decoder_abort(decoder_p, EBADLENGTH);',
                '',
                '    return;',
                '}',
                '',
                'for ({ui} = 0; {ui} < dst_p->{loc}length; {ui}++) {{'.format(
                    loc=self.location_inner('', '.'),
                    ui=unique_i),
            ] + _indent_lines(decode_lines)

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
        elif isinstance(type_, oer.OctetString):
            return self.format_octet_string_inner(checker)
        elif _is_user_type(type_):
            return self.format_user_type_inner(type_.type_name,
                                               type_.module_name)
        elif isinstance(type_, oer.Sequence):
            return self.format_sequence_inner(type_, checker)
        elif isinstance(type_, oer.Choice):
            return self.format_choice_inner(type_, checker)
        elif isinstance(type_, oer.SequenceOf):
            return self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, oer.Enumerated):
            return self.format_enumerated_inner()
        else:
            raise NotImplementedError(type_)

    def generate_definition_inner(self, compiled_type):
        type_ = compiled_type.type
        checker = compiled_type.constraints_checker.type

        if isinstance(type_, oer.Integer):
            encode_lines, decode_lines = self.format_integer_inner(checker)
        elif isinstance(type_, oer.Boolean):
            encode_lines, decode_lines = self.format_boolean_inner()
        elif isinstance(type_, oer.Real):
            encode_lines, decode_lines = self.format_real_inner(type_)
        elif isinstance(type_, oer.Sequence):
            encode_lines, decode_lines = self.format_sequence_inner(type_, checker)
        elif isinstance(type_, oer.SequenceOf):
            encode_lines, decode_lines = self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, oer.Choice):
            encode_lines, decode_lines = self.format_choice_inner(type_, checker)
        elif isinstance(type_, oer.OctetString):
            encode_lines, decode_lines = self.format_octet_string_inner(checker)
        elif isinstance(type_, oer.Enumerated):
            encode_lines, decode_lines = self.format_enumerated_inner()
        elif isinstance(type_, oer.Null):
            encode_lines, decode_lines = self.format_null_inner()
        else:
            encode_lines, decode_lines = [], []

        if self.encode_variable_lines:
            encode_lines = self.encode_variable_lines + [''] + encode_lines

        if self.decode_variable_lines:
            decode_lines = self.decode_variable_lines + [''] + decode_lines

        encode_lines = _indent_lines(encode_lines) + ['']
        decode_lines = _indent_lines(decode_lines) + ['']

        return DEFINITION_INNER_FMT.format(namespace=self.namespace,
                                           module_name_snake=self.module_name_snake,
                                           type_name_snake=self.type_name_snake,
                                           encode_body='\n'.join(encode_lines),
                                           decode_body='\n'.join(decode_lines))

    def generate_definition(self):
        return DEFINITION_FMT.format(namespace=self.namespace,
                                     module_name_snake=self.module_name_snake,
                                     type_name_snake=self.type_name_snake)

    def generate_helpers(self, definitions):
        helpers = [ENCODER_AND_DECODER_STRUCTS]

        functions = [
            ('encoder_init(', ENCODER_INIT),
            ('encoder_get_result(', ENCODER_GET_RESULT),
            ('encoder_abort(', ENCODER_ABORT),
            ('encoder_append_bytes(', ENCODER_ALLOC),
            ('encoder_append_bytes(', ENCODER_APPEND_BYTES),
            ('encoder_append_integer_8(', ENCODER_APPEND_INTEGER_8),
            ('encoder_append_integer_16(', ENCODER_APPEND_INTEGER_16),
            ('encoder_append_integer_32(', ENCODER_APPEND_INTEGER_32),
            ('encoder_append_integer_64(', ENCODER_APPEND_INTEGER_64),
            ('encoder_append_float(', ENCODER_APPEND_FLOAT),
            ('encoder_append_double(', ENCODER_APPEND_DOUBLE),
            ('encoder_append_bool(', ENCODER_APPEND_BOOL),
            ('encoder_append_length_determinant(', ENCODER_APPEND_LENGTH_DETERMINANT),
            ('decoder_init(', DECODER_INIT),
            ('decoder_get_result(', DECODER_GET_RESULT),
            ('decoder_abort(', DECODER_ABORT),
            ('decoder_read_bytes(', DECODER_FREE),
            ('decoder_read_bytes(', DECODER_READ_BYTES),
            ('decoder_read_integer_8(', DECODER_READ_INTEGER_8),
            ('decoder_read_integer_16(', DECODER_READ_INTEGER_16),
            ('decoder_read_integer_32(', DECODER_READ_INTEGER_32),
            ('decoder_read_integer_64(', DECODER_READ_INTEGER_64),
            ('decoder_read_float(', DECODER_READ_FLOAT),
            ('decoder_read_double(', DECODER_READ_DOUBLE),
            ('decoder_read_bool(', DECODER_READ_BOOL),
            ('decoder_read_length_determinant(', DECODER_READ_LENGTH_DETERMINANT)
        ]

        for pattern, definition in functions:
            if pattern in definitions:
                helpers.append(definition)

        return helpers + ['']

    def generate(self, compiled):
        type_declarations = []
        declarations = []
        definitions_inner = []
        definitions = []

        for module_name, module in sorted(compiled.modules.items()):
            self.module_name = module_name

            for type_name, compiled_type in sorted(module.items()):
                self.type_name = type_name
                self.reset()

                type_declaration = self.generate_type_declaration(compiled_type)

                if not type_declaration:
                    continue

                type_declarations.extend(type_declaration)

                declaration = self.generate_declaration()
                declarations.append(declaration)

                definition_inner = self.generate_definition_inner(compiled_type)
                definitions_inner.append(definition_inner)

                definition = self.generate_definition()
                definitions.append(definition)

        type_declarations = '\n'.join(type_declarations)
        declarations = '\n'.join(declarations)
        definitions = '\n'.join(definitions_inner + definitions)
        helpers = '\n'.join(self.generate_helpers(definitions))

        return type_declarations, declarations, helpers, definitions


def generate(compiled, namespace):
    return _Generator(namespace).generate(compiled)
