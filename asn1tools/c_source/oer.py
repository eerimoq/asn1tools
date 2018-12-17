"""Basic Octet Encoding Rules (OER) codec generator.

"""

from .utils import camel_to_snake_case
from ..codecs import oer
from ..errors import Error


STRUCT_FMT = '''\
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

DEFINITION_FMT = '''\
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_encode(
    uint8_t *dst_p,
    size_t size,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p)
{{
    return (0);
}}

ssize_t {namespace}_{module_name_snake}_{type_name_snake}_decode(
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p,
    const uint8_t *src_p,
    size_t size)
{{
    return (0);
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

static size_t encoder_alloc(struct encoder_t *self_p,
                            size_t size)
{
    ssize_t pos;

    if (self_p->pos + (ssize_t)size <= self_p->size) {
        pos = self_p->pos;
        self_p->pos += size;
    } else {
        pos = -ENOMEM;
        self_p->pos = -ENOMEM;
        self_p->size = -ENOMEM;
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

static size_t decoder_free(struct decoder_t *self_p,
                           size_t size)
{
    ssize_t pos;

    if (self_p->pos + (ssize_t)size <= self_p->size) {
        pos = self_p->pos;
        self_p->pos += size;
    } else {
        pos = -EOUTOFDATA;
        self_p->pos = -EOUTOFDATA;
        self_p->size = -EOUTOFDATA;
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

static uint64_t decoder_read_double(struct decoder_t *self_p)
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


def _format_type_name(length, is_signed):
    type_name = 'int{}_t'.format(length)

    if not is_signed:
        type_name = 'u' + type_name

    return type_name


def type_length(length):
    if length <= 8:
        return 8
    elif length <= 16:
        return 16
    elif length <= 32:
        return 32
    else:
        return 64


def _format_integer(compiled_type):
    if compiled_type.fmt is None:
        raise Error('INTEGER not fixed size.')

    type_name = _format_type_name(8 * compiled_type.length,
                                  compiled_type.fmt[1].islower())

    return '    {} value;'.format(type_name)


def _format_sequence(compiled_type):
    members = []

    for member in compiled_type.root_members:
        members.append('    bool {};'.format(member.name))

    return members


def _generate_struct(namespace, compiled_type, module_name, type_name):
    module_name_snake = camel_to_snake_case(module_name)
    type_name_snake = camel_to_snake_case(type_name)
    members = []

    if isinstance(compiled_type, oer.Integer):
        members.append(_format_integer(compiled_type))
    elif isinstance(compiled_type, oer.Sequence):
        members.extend(_format_sequence(compiled_type))

    return STRUCT_FMT.format(namespace=namespace,
                             module_name_snake=module_name_snake,
                             type_name_snake=type_name_snake,
                             members='\n'.join(members))


def _generate_declaration(namespace, module_name, type_name):
    module_name_snake = camel_to_snake_case(module_name)
    type_name_snake = camel_to_snake_case(type_name)

    return DECLARATION_FMT.format(namespace=namespace,
                                  module_name=module_name,
                                  type_name=type_name,
                                  module_name_snake=module_name_snake,
                                  type_name_snake=type_name_snake)


def _generate_definition(namespace, module_name, type_name):
    module_name_snake = camel_to_snake_case(module_name)
    type_name_snake = camel_to_snake_case(type_name)

    return DEFINITION_FMT.format(namespace=namespace,
                                 module_name_snake=module_name_snake,
                                 type_name_snake=type_name_snake)


def generate(compiled, namespace):
    structs = []
    declarations = []
    definitions = []

    for module_name, module in sorted(compiled.modules.items()):
        for type_name, compiled_type in sorted(module.items()):
            struct = _generate_struct(namespace,
                                      compiled_type.type,
                                      module_name,
                                      type_name)
            structs.append(struct)

            declaration = _generate_declaration(namespace,
                                                module_name,
                                                type_name)
            declarations.append(declaration)

            definition = _generate_definition(namespace,
                                              module_name,
                                              type_name)
            definitions.append(definition)

    structs = '\n'.join(structs)
    declarations = '\n'.join(declarations)
    definitions = '\n'.join(definitions)

    return structs, declarations, HELPERS, definitions
