"""Basic Octet Encoding Rules (OER) codec generator.

"""

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

HELPERS = '''\
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

static void encoder_init(struct encoder_t *self_p,
                         uint8_t *buf_p,
                         size_t size)
{
    self_p->buf_p = buf_p;
    self_p->size = size;
    self_p->pos = 0;
}

static ssize_t encoder_get_result(struct encoder_t *self_p)
{
    return (self_p->pos);
}

static void encoder_abort(struct encoder_t *self_p,
                          ssize_t error)
{
    if (self_p->size >= 0) {
        self_p->size = -error;
        self_p->pos = -error;
    }
}

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
}

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
}

static void encoder_append_integer_8(struct encoder_t *self_p,
                                     uint8_t value)
{
    encoder_append_bytes(self_p, &value, sizeof(value));
}

static void encoder_append_integer_16(struct encoder_t *self_p,
                                      uint16_t value)
{
    uint8_t buf[2];

    buf[0] = (value >> 8);
    buf[1] = value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}

static void encoder_append_integer_32(struct encoder_t *self_p,
                                      uint32_t value)
{
    uint8_t buf[4];

    buf[0] = (value >> 24);
    buf[1] = (value >> 16);
    buf[2] = (value >> 8);
    buf[3] = value;

    encoder_append_bytes(self_p, &buf[0], sizeof(buf));
}

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
}

static void encoder_append_float(struct encoder_t *self_p,
                                 float value)
{
    uint32_t i32;

    memcpy(&i32, &value, sizeof(i32));

    encoder_append_integer_32(self_p, i32);
}

static void encoder_append_double(struct encoder_t *self_p,
                                  double value)
{
    uint64_t i64;

    memcpy(&i64, &value, sizeof(i64));

    encoder_append_integer_64(self_p, i64);
}

static void encoder_append_bool(struct encoder_t *self_p, bool value)
{
    encoder_append_integer_8(self_p, value ? 255 : 0);
}

static void decoder_init(struct decoder_t *self_p,
                         const uint8_t *buf_p,
                         size_t size)
{
    self_p->buf_p = buf_p;
    self_p->size = size;
    self_p->pos = 0;
}

static ssize_t decoder_get_result(struct decoder_t *self_p)
{
    return (self_p->pos);
}

static void decoder_abort(struct decoder_t *self_p,
                          ssize_t error)
{
    if (self_p->size >= 0) {
        self_p->size = -error;
        self_p->pos = -error;
    }
}

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
}

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

}

static uint8_t decoder_read_integer_8(struct decoder_t *self_p)
{
    uint8_t value;

    decoder_read_bytes(self_p, &value, sizeof(value));

    return (value);
}

static uint16_t decoder_read_integer_16(struct decoder_t *self_p)
{
    uint8_t buf[2];

    decoder_read_bytes(self_p, &buf[0], sizeof(buf));

    return ((buf[0] << 8) | buf[1]);
}

static uint32_t decoder_read_integer_32(struct decoder_t *self_p)
{
    uint8_t buf[4];

    decoder_read_bytes(self_p, &buf[0], sizeof(buf));

    return ((buf[0] << 24) | (buf[1] << 16) | (buf[2] << 8) | buf[3]);
}

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
}

static float decoder_read_float(struct decoder_t *self_p)
{
    float value;
    uint32_t i32;

    i32 = decoder_read_integer_32(self_p);

    memcpy(&value, &i32, sizeof(value));

    return (value);
}

static double decoder_read_double(struct decoder_t *self_p)
{
    double value;
    uint64_t i64;

    i64 = decoder_read_integer_64(self_p);

    memcpy(&value, &i64, sizeof(value));

    return (value);
}

static bool decoder_read_bool(struct decoder_t *self_p)
{
    uint8_t value;

    value = decoder_read_integer_8(self_p);

    return (value != 0);
}
'''


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


def is_user_type(type_):
    return type_.module_name is not None


def _indent_lines(lines):
    return [4 * ' ' + line for line in lines]


def _dedent_lines(lines):
    return [line[4:] for line in lines]


class _Generator(object):

    def __init__(self, namespace):
        self.namespace = namespace
        self.members_backtrace = []
        self.module_name = None
        self.type_name = None
        self.helper_lines = []

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

        if self.members_backtrace:
            location += '_{}'.format('_'.join(self.members_backtrace))

        return location

    def members_backtrace_push(self, member_name):
        self.members_backtrace.append(member_name)

    def members_backtrace_pop(self):
        self.members_backtrace.pop()

    def get_member_checker(self, checker, name):
        for member in checker.members:
            if member.name == name:
                return member

        raise Exception

    def format_integer(self, checker):
        if not checker.is_bound():
            raise Error('INTEGER not fixed size.')

        type_name = _format_type_name(checker.minimum, checker.maximum)

        return [type_name]

    def format_real(self):
        return ['float']

    def format_boolean(self):
        return ['bool']

    def format_octet_string(self, checker):
        if not checker.has_upper_bound():
            raise Error('OCTET STRING has no maximum length.')

        if checker.minimum == checker.maximum:
            lines = []
        else:
            lines = ['    uint8_t length;']

        return [
            'struct {'
            ] + lines + [
            '    uint8_t value[{}];'.format(checker.maximum),
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

            self.members_backtrace_push(member.name)

            try:
                member_lines = self.format_type(member, member_checker)
            finally:
                self.members_backtrace_pop()

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

        return [
            'struct {',
            '    uint8_t length;'
        ] + _indent_lines(lines) + [
            '}'
        ]

    def format_enumerated(self, type_):
        lines = ['enum {}_t'.format(self.location)]

        values = [
            '    {}_{}_t'.format(self.location, value)
            for value in type_.value_to_data.values()
        ]
        self.helper_lines += [
            'enum {}_t {{'.format(self.location)
        ] + [value + ',' for value in values[:-1]] + values[-1:] + [
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
            choice_lines = self.format_type(member, member_checker)

            if choice_lines:
                choice_lines[-1] += ' {};'.format(member.name)

            lines += choice_lines
            choices.append('    {}_choice_{}_t'.format(self.location,
                                                       member.name))

        self.helper_lines += [
            'enum {}_choice_t {{'.format(self.location)
        ] + [choice + ',' for choice in choices[:-1]] + choices[-1:] + [
            '};',
            ''
        ]

        lines = [
            'enum {}_choice_t choice;'.format(self.location),
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
        elif isinstance(type_, oer.Real):
            lines = self.format_real()
        elif isinstance(type_, oer.Null):
            lines = []
        elif isinstance(type_, oer.Boolean):
            lines = self.format_boolean()
        elif isinstance(type_, oer.OctetString):
            lines = self.format_octet_string(checker)
        elif is_user_type(type_):
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

    def generate_type_declaration(self, compiled_type):
        type_ = compiled_type.type
        checker = compiled_type.constraints_checker.type
        lines = []
        self.helper_lines = []

        try:
            if isinstance(type_, oer.Integer):
                lines = self.format_integer(checker)
                lines[0] += ' value;'
            elif isinstance(type_, oer.Boolean):
                lines = self.format_boolean()
                lines[0] += ' value;'
            elif isinstance(type_, oer.Sequence):
                lines = self.format_sequence(type_, checker)[1:-1]
                lines = _dedent_lines(lines)
            elif isinstance(type_, oer.Choice):
                lines = self.format_choice(type_, checker)
                lines = _dedent_lines(lines[1:-1])
            elif isinstance(type_, oer.SequenceOf):
                lines = self.format_sequence_of(type_, checker)[1:-1]
                lines = _dedent_lines(lines)
            elif isinstance(type_, oer.OctetString):
                lines = self.format_octet_string(checker)
            elif isinstance(type_, oer.Real):
                lines = []
            elif isinstance(type_, oer.UTF8String):
                lines = self.format_utf8_string(checker)
            else:
                raise NotImplementedError(type_)
        except Error:
            return []

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
                'encoder_append_integer_{}(encoder_p, src_p->value);'.format(length)
            ],
            [
                'dst_p->value = decoder_read_integer_{}(decoder_p);'.format(length)
            ]
        )

    def format_boolean_inner(self):
        return (
            ['encoder_append_bool(encoder_p, src_p->value);'],
            ['dst_p->value = decoder_read_bool(decoder_p);']
        )

    def format_real_inner(self):
        return (
            ['encoder_append_float(encoder_p, src_p->value);'],
            ['dst_p->value = decoder_read_float(decoder_p);']
        )

    def generate_definition_inner(self, compiled_type):
        type_ = compiled_type.type
        checker = compiled_type.constraints_checker.type
        encode_lines = []
        decode_lines = []

        if isinstance(type_, oer.Integer):
            encode_lines, decode_lines = self.format_integer_inner(checker)
        elif isinstance(type_, oer.Boolean):
            encode_lines, decode_lines = self.format_boolean_inner()
        elif isinstance(type_, oer.Real):
            encode_lines, decode_lines = self.format_real_inner()
        else:
            print(type_)

        encode_lines = _indent_lines(encode_lines)
        decode_lines = _indent_lines(decode_lines)

        encode_lines.append('')
        decode_lines.append('')

        return DEFINITION_INNER_FMT.format(namespace=self.namespace,
                                           module_name_snake=self.module_name_snake,
                                           type_name_snake=self.type_name_snake,
                                           encode_body='\n'.join(encode_lines),
                                           decode_body='\n'.join(decode_lines))

    def generate_definition(self):
        return DEFINITION_FMT.format(namespace=self.namespace,
                                     module_name_snake=self.module_name_snake,
                                     type_name_snake=self.type_name_snake)

    def generate(self, compiled):
        type_declarations = []
        declarations = []
        definitions_inner = []
        definitions = []

        for module_name, module in sorted(compiled.modules.items()):
            self.module_name = module_name

            for type_name, compiled_type in sorted(module.items()):
                self.type_name = type_name

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

        return type_declarations, declarations, HELPERS, definitions


def generate(compiled, namespace):
    return _Generator(namespace).generate(compiled)
