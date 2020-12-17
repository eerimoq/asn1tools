"""Functions required by the UPER C code generator

"""

from .utils import ENCODER_ABORT
from .utils import DECODER_ABORT

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
static ssize_t encoder_get_result(const struct encoder_t *self_p)
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

    self_p->buf_p[pos / 8] |= (uint8_t)(value << (7 - (pos % 8)));
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

    pos = encoder_alloc(self_p, 8u * size);

    if (pos < 0) {
        return;
    }

    byte_pos = ((size_t)pos / 8u);
    pos_in_byte = ((size_t)pos % 8u);

    if (pos_in_byte == 0u) {
        (void)memcpy(&self_p->buf_p[byte_pos], buf_p, size);
    } else {
        for (i = 0; i < size; i++) {
            self_p->buf_p[byte_pos + i] |= (buf_p[i] >> pos_in_byte);
            self_p->buf_p[byte_pos + i + 1] = (buf_p[i] << (8u - pos_in_byte));
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
    encoder_append_uint8(self_p, (uint8_t)value + 128);
}\
'''

ENCODER_APPEND_INT16 = '''
static void encoder_append_int16(struct encoder_t *self_p,
                                 int16_t value)
{
    encoder_append_uint16(self_p, (uint16_t)value + 32768);
}\
'''

ENCODER_APPEND_INT32 = '''
static void encoder_append_int32(struct encoder_t *self_p,
                                 int32_t value)
{
    encoder_append_uint32(self_p, (uint32_t)value + 2147483648);
}\
'''

ENCODER_APPEND_INT64 = '''
static void encoder_append_int64(struct encoder_t *self_p,
                                 int64_t value)
{
    uint64_t u64_value;

    u64_value = (uint64_t)value;
    u64_value += 9223372036854775808ull;

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
static ssize_t decoder_get_result(const struct decoder_t *self_p)
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

    pos = decoder_free(self_p, 8u * size);

    if (pos < 0) {
        return;
    }

    byte_pos = ((size_t)pos / 8u);
    pos_in_byte = ((size_t)pos % 8u);

    if (pos_in_byte == 0) {
        (void)memcpy(buf_p, &self_p->buf_p[byte_pos], size);
    } else {
        for (i = 0; i < size; i++) {
            buf_p[i] = (self_p->buf_p[byte_pos + i] << pos_in_byte);
            buf_p[i] |= (self_p->buf_p[byte_pos + i + 1] >> (8u - pos_in_byte));
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

    return (((uint16_t)buf[0] << 8) | (uint16_t)buf[1]);
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
    value -= 9223372036854775808ull;

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
