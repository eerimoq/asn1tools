"""Unaligned Packed Encoding Rules (UPER) C source code codec generator.

"""

from .utils import TYPE_DECLARATION_FMT
from .utils import DECLARATION_FMT
from .utils import DEFINITION_INNER_FMT
from .utils import DEFINITION_FMT
from .utils import canonical
from .utils import camel_to_snake_case
from .utils import join_lines
from .utils import format_type_name
from .utils import is_user_type
from .utils import indent_lines
from .utils import dedent_lines
from ..codecs import uper
from ..errors import Error


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
    self_p->size = (8 * size);
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
static ssize_t encoder_alloc(struct encoder_t *self_p,
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

ENCODER_APPEND_BITS = '''
static void encoder_append_bits(struct encoder_t *self_p,
                                const uint8_t *buf_p,
                                size_t number_of_bits)
{
    size_t i;

    for (i = 0; i < number_of_bits; i++) {
        encoder_append_bit(self_p, (buf_p[i / 8] >> (7 - (i % 8))) & 1);
    }
}\
'''

ENCODER_APPEND_BYTES = '''
static void encoder_append_bytes(struct encoder_t *self_p,
                                 const uint8_t *buf_p,
                                 size_t size)
{
    encoder_append_bits(self_p, buf_p, 8 * size);
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
    value += 9223372036854775808ul;
    encoder_append_uint64(self_p, (uint64_t)value);
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
    self_p->size = (8 * size);
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
static ssize_t decoder_free(struct decoder_t *self_p,
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

DECODER_READ_BITS = '''
static void decoder_read_bits(struct decoder_t *self_p,
                              uint8_t *buf_p,
                              size_t number_of_bits)
{
    size_t i;

    memset(buf_p, 0, number_of_bits / 8);

    for (i = 0; i < number_of_bits; i++) {
        buf_p[i / 8] |= (decoder_read_bit(self_p) << (7 - (i % 8)));
    }
}\
'''

DECODER_READ_BYTES = '''
static void decoder_read_bytes(struct decoder_t *self_p,
                               uint8_t *buf_p,
                               size_t size)
{
    decoder_read_bits(self_p, buf_p, 8 * size);
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

    return ((buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]);
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
    int64_t value;

    value = (int64_t)decoder_read_uint64(self_p);
    value -= 9223372036854775808ul;

    return (value);
}\
'''

DECODER_READ_BOOL = '''
static bool decoder_read_bool(struct decoder_t *self_p)
{
    return (decoder_read_bit(self_p));
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
        value |= decoder_read_bit(self_p);
    }

    return (value);
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


class _UserType(object):

    def __init__(self,
                 type_name,
                 module_name,
                 type_declaration,
                 declaration,
                 definition_inner,
                 definition,
                 used_user_types):
        self.type_name = type_name
        self.module_name = module_name
        self.type_declaration = type_declaration
        self.declaration = declaration
        self.definition_inner = definition_inner
        self.definition = definition
        self.used_user_types = used_user_types


def sort_user_types_by_used_user_types(user_types):
    reversed_sorted_user_types = []

    for user_type in user_types:
        user_type_name_tuple = (user_type.type_name, user_type.module_name)

        # Insert first in the reversed list if there are no types
        # using this type.
        insert_index = 0

        for i, reversed_sorted_user_type in enumerate(reversed_sorted_user_types, 1):
            if user_type_name_tuple in reversed_sorted_user_type.used_user_types:
                if i > insert_index:
                    insert_index = i

        reversed_sorted_user_types.insert(insert_index, user_type)

    return reversed(reversed_sorted_user_types)


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
        self.used_user_types = []

    def reset_type(self):
        self.helper_lines = []
        self.base_variables = set()
        self.used_suffixes_by_base_variables = {}
        self.encode_variable_lines = []
        self.decode_variable_lines = []
        self.used_user_types = []

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

        type_name = format_type_name(checker.minimum, checker.maximum)

        return [type_name]

    def format_real(self):
        return []

    def format_boolean(self):
        return ['bool']

    def format_octet_string(self, checker):
        if not checker.has_upper_bound():
            raise Error('OCTET STRING has no maximum length.')

        if checker.minimum == checker.maximum:
            lines = []
        elif checker.maximum < 256:
            lines = ['    uint8_t length;']
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

        return ['struct {'] + indent_lines(lines) + ['}']

    def format_sequence_of(self, type_, checker):
        if not checker.is_bound():
            raise Error('SEQUENCE OF has no maximum length.')

        lines = self.format_type(type_.element_type, checker.element_type)

        if lines:
            lines[-1] += ' elements[{}];'.format(checker.maximum)

        if checker.minimum == checker.maximum:
            length_lines = []
        elif checker.maximum < 256:
            length_lines = ['uint8_t length;']
        else:
            length_lines = ['uint32_t length;']

        return ['struct {'] + indent_lines(length_lines + lines) + ['}']

    def format_enumerated(self, type_):
        lines = ['enum {}_e'.format(self.location)]

        values = [
            '    {}_{}_e'.format(self.location, value)
            for value in sorted(type_.root_data_to_index)
        ]
        self.helper_lines += [
            'enum {}_e {{'.format(self.location)
        ] + join_lines(values, ',') + [
            '};',
            ''
        ]

        return lines

    def format_choice(self, type_, checker):
        lines = []
        choices = []

        for member in type_.root_index_to_member.values():
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
        ] + join_lines(choices, ',') + [
            '};',
            ''
        ]

        lines = [
            'enum {}_choice_e choice;'.format(self.location),
            'union {'
        ] + indent_lines(lines) + [
            '} value;'
        ]

        lines = ['struct {'] + indent_lines(lines) + ['}']

        return lines

    def format_user_type(self, type_name, module_name):
        module_name_snake = camel_to_snake_case(module_name)
        type_name_snake = camel_to_snake_case(type_name)

        self.used_user_types.append((type_name, module_name))

        return ['struct {}_{}_{}_t'.format(self.namespace,
                                           module_name_snake,
                                           type_name_snake)]

    def format_type(self, type_, checker):
        if isinstance(type_, uper.Integer):
            lines = self.format_integer(checker)
        elif isinstance(type_, uper.Boolean):
            lines = self.format_boolean()
        elif isinstance(type_, uper.Real):
            lines = self.format_real()
        elif isinstance(type_, uper.Null):
            lines = []
        elif isinstance(type_, uper.OctetString):
            lines = self.format_octet_string(checker)
        elif is_user_type(type_):
            lines = self.format_user_type(type_.type_name,
                                          type_.module_name)
        elif isinstance(type_, uper.Sequence):
            lines = self.format_sequence(type_, checker)
        elif isinstance(type_, uper.Choice):
            lines = self.format_choice(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            lines = self.format_sequence_of(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            lines = self.format_enumerated(type_)
        else:
            raise NotImplementedError(
                "Unsupported type '{}'.".format(type_.type_name))

        return lines

    def generate_type_declaration(self, compiled_type):
        type_ = compiled_type.type
        checker = compiled_type.constraints_checker.type
        lines = []

        try:
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
            elif isinstance(type_, uper.UTF8String):
                lines = self.format_utf8_string(checker)
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
                raise NotImplementedError(
                    "Unsupported type '{}'.".format(type_.type_name))
        except Error:
            return []

        if not lines:
            lines = ['uint8_t dummy;']

        lines = indent_lines(lines)

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
        type_name = format_type_name(checker.minimum, checker.maximum)
        suffix = type_name[:-2]

        return (
            [
                'encoder_append_{}(encoder_p, src_p->{});'.format(
                    suffix,
                    self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_{}(decoder_p);'.format(
                    self.location_inner(),
                    suffix)
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

        for member in type_.root_members:
            if member.optional:
                name = '{}is_{}_present'.format(self.location_inner('', '.'),
                                                member.name)
                encode_lines.append(
                    'encoder_append_bit(encoder_p, src_p->{} ? 1 : 0);'.format(
                        name))
                decode_lines.append(
                    'dst_p->{} = (decoder_read_bit(decoder_p) == 1);'.format(
                        name))

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
                ] + indent_lines(member_encode_lines) + [
                    '}',
                    ''
                ]
                member_decode_lines = [
                    '',
                    'if (dst_p->{}) {{'.format(is_present)
                ] + indent_lines(member_decode_lines) + [
                    '}',
                    ''
                ]

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
                '    src_p->{}length - {},'.format(location, checker.minimum),
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
                'dst_p->{}length += {};'.format(location, checker.minimum),
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
        unique_choice = self.add_unique_decode_variable('uint8_t {};', 'choice')
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

    def format_enumerated_inner(self):
        return (
            [
                'encoder_append_non_negative_binary_integer(encoder_p, '
                'src_p->{});'.format(self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_non_negative_binary_integer('
                'decoder_p);'.format(self.location_inner())
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
        unique_i = self.add_unique_variable(
            '{} {{}};'.format(format_type_name(0, checker.maximum)),
            'i')

        with self.c_members_backtrace_push('elements[{}]'.format(unique_i)):
            encode_lines, decode_lines = self.format_type_inner(
                type_.element_type,
                checker.element_type)

        if checker.minimum == checker.maximum:
            encode_lines = [
                'for ({ui} = 0; {ui} < {maximum}; {ui}++) {{'.format(
                    ui=unique_i,
                    maximum=checker.maximum),
            ] + indent_lines(encode_lines)
            decode_lines = [
                'for ({ui} = 0; {ui} < {maximum}; {ui}++) {{'.format(
                    ui=unique_i,
                    maximum=checker.maximum),
            ] + indent_lines(decode_lines)
        else:
            encode_lines = [
                'encoder_append_non_negative_binary_integer(',
                '    encoder_p,',
                '    src_p->{}length - {},'.format(self.location_inner('', '.'),
                                                   checker.minimum),
                '    {});'.format(type_.number_of_bits),
                '',
                'for ({ui} = 0; {ui} < src_p->{loc}length; {ui}++) {{'.format(
                    ui=unique_i,
                    loc=self.location_inner('', '.')),
            ] + indent_lines(encode_lines)
            decode_lines = [
                'dst_p->{}length = decoder_read_non_negative_binary_integer('.format(
                    self.location_inner('', '.')),
                '    decoder_p,',
                '    {});'.format(type_.number_of_bits),
                'dst_p->{}length += {};'.format(self.location_inner('', '.'),
                                                checker.minimum),
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
            ] + indent_lines(decode_lines)

        encode_lines += ['}', '']
        decode_lines += ['}', '']

        return encode_lines, decode_lines

    def format_type_inner(self, type_, checker):
        if isinstance(type_, uper.Integer):
            return self.format_integer_inner(checker)
        elif isinstance(type_, uper.Real):
            return self.format_real_inner()
        elif isinstance(type_, uper.Null):
            return [], []
        elif isinstance(type_, uper.Boolean):
            return self.format_boolean_inner()
        elif isinstance(type_, uper.OctetString):
            return self.format_octet_string_inner(type_, checker)
        elif is_user_type(type_):
            return self.format_user_type_inner(type_.type_name,
                                               type_.module_name)
        elif isinstance(type_, uper.Sequence):
            return self.format_sequence_inner(type_, checker)
        elif isinstance(type_, uper.Choice):
            return self.format_choice_inner(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            return self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            return self.format_enumerated_inner()
        else:
            raise NotImplementedError(type_)

    def generate_definition_inner(self, compiled_type):
        type_ = compiled_type.type
        checker = compiled_type.constraints_checker.type

        if isinstance(type_, uper.Integer):
            encode_lines, decode_lines = self.format_integer_inner(checker)
        elif isinstance(type_, uper.Boolean):
            encode_lines, decode_lines = self.format_boolean_inner()
        elif isinstance(type_, uper.Real):
            encode_lines, decode_lines = self.format_real_inner()
        elif isinstance(type_, uper.Sequence):
            encode_lines, decode_lines = self.format_sequence_inner(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            encode_lines, decode_lines = self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, uper.Choice):
            encode_lines, decode_lines = self.format_choice_inner(type_, checker)
        elif isinstance(type_, uper.OctetString):
            encode_lines, decode_lines = self.format_octet_string_inner(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            encode_lines, decode_lines = self.format_enumerated_inner()
        elif isinstance(type_, uper.Null):
            encode_lines, decode_lines = self.format_null_inner()
        else:
            encode_lines, decode_lines = [], []

        if self.encode_variable_lines:
            encode_lines = self.encode_variable_lines + [''] + encode_lines

        if self.decode_variable_lines:
            decode_lines = self.decode_variable_lines + [''] + decode_lines

        encode_lines = indent_lines(encode_lines) + ['']
        decode_lines = indent_lines(decode_lines) + ['']

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
            ('encoder_append_bit(', ENCODER_ALLOC),
            ('encoder_append_bit(', ENCODER_APPEND_BIT),
            ('encoder_append_bytes(', ENCODER_APPEND_BITS),
            ('encoder_append_bytes(', ENCODER_APPEND_BYTES),
            ('encoder_append_uint8(', ENCODER_APPEND_UINT8),
            ('encoder_append_uint16(', ENCODER_APPEND_UINT16),
            ('encoder_append_uint32(', ENCODER_APPEND_UINT32),
            ('encoder_append_uint64(', ENCODER_APPEND_UINT64),
            ('encoder_append_int8(', ENCODER_APPEND_INT8),
            ('encoder_append_int16(', ENCODER_APPEND_INT16),
            ('encoder_append_int32(', ENCODER_APPEND_INT32),
            ('encoder_append_int64(', ENCODER_APPEND_INT64),
            ('encoder_append_bool(', ENCODER_APPEND_BOOL),
            (
                'encoder_append_non_negative_binary_integer(',
                ENCODER_APPEND_NON_NEGATIVE_BINARY_INTEGER
            ),
            ('decoder_init(', DECODER_INIT),
            ('decoder_get_result(', DECODER_GET_RESULT),
            ('decoder_abort(', DECODER_ABORT),
            ('decoder_read_bit(', DECODER_FREE),
            ('decoder_read_bit(', DECODER_READ_BIT),
            ('decoder_read_bytes(', DECODER_READ_BITS),
            ('decoder_read_bytes(', DECODER_READ_BYTES),
            ('decoder_read_uint8(', DECODER_READ_UINT8),
            ('decoder_read_uint16(', DECODER_READ_UINT16),
            ('decoder_read_uint32(', DECODER_READ_UINT32),
            ('decoder_read_uint64(', DECODER_READ_UINT64),
            ('decoder_read_int8(', DECODER_READ_INT8),
            ('decoder_read_int16(', DECODER_READ_INT16),
            ('decoder_read_int32(', DECODER_READ_INT32),
            ('decoder_read_int64(', DECODER_READ_INT64),
            ('decoder_read_bool(', DECODER_READ_BOOL),
            (
                'decoder_read_non_negative_binary_integer(',
                DECODER_READ_NON_NEGATIVE_BINARY_INTEGER
            )
        ]

        for pattern, definition in functions:
            if pattern in definitions:
                helpers.append(definition)

        return helpers + ['']

    def generate(self, compiled):
        user_types = []

        for module_name, module in sorted(compiled.modules.items()):
            self.module_name = module_name

            for type_name, compiled_type in sorted(module.items()):
                self.type_name = type_name
                self.reset_type()

                type_declaration = self.generate_type_declaration(compiled_type)

                if not type_declaration:
                    continue

                declaration = self.generate_declaration()
                definition_inner = self.generate_definition_inner(compiled_type)
                definition = self.generate_definition()

                user_type = _UserType(type_name,
                                      module_name,
                                      type_declaration,
                                      declaration,
                                      definition_inner,
                                      definition,
                                      self.used_user_types)
                user_types.append(user_type)

        user_types = sort_user_types_by_used_user_types(user_types)

        type_declarations = []
        declarations = []
        definitions_inner = []
        definitions = []

        for user_type in user_types:
            type_declarations.extend(user_type.type_declaration)
            declarations.append(user_type.declaration)
            definitions_inner.append(user_type.definition_inner)
            definitions.append(user_type.definition)

        type_declarations = '\n'.join(type_declarations)
        declarations = '\n'.join(declarations)
        definitions = '\n'.join(definitions_inner + definitions)
        helpers = '\n'.join(self.generate_helpers(definitions))

        return type_declarations, declarations, helpers, definitions


def generate(compiled, namespace):
    return _Generator(namespace).generate(compiled)
