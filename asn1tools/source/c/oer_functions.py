"""Functions required by the OER C code generator

"""

from .utils import ENCODER_ABORT
from .utils import DECODER_ABORT

ENUMERATED_VALUE_LENGTH = '''
static uint8_t enumerated_value_length(int32_t value)
{
    uint8_t length;

    if ((value >=0) && (value < 128)) {
        length = 0;
    } else if ((value >= -128) && (value < 128)) {
        length = 1;
    } else if ((value >= -32768) && (value < 32768)) {
        length = 2;
    } else if ((value >= -8388608) && (value < 8388608)) {
        length = 3;
    } else {
        length = 4;
    }

    return length;
}\
'''

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

ENCODER_APPEND_LONG_UINT = '''
static void encoder_append_long_uint(struct encoder_t *self_p,
                                     uint64_t value,
                                     uint8_t number_of_bytes)
{
    const uint8_t *value_p = (const uint8_t*)&value;
    uint8_t buf[8];
    for(uint32_t byte = 0; byte < number_of_bytes; byte++) {
        buf[number_of_bytes - byte - 1] = *value_p++;
    }
    encoder_append_bytes(self_p, buf, number_of_bytes);
}\
'''

ENCODER_APPEND_INT = '''
static void encoder_append_int(struct encoder_t *self_p,
                               int32_t value,
                               uint8_t number_of_bytes)
{
    switch (number_of_bytes) {

    case 1:
        encoder_append_int8(self_p, (int8_t)value);
        break;

    case 2:
        encoder_append_int16(self_p, (int16_t)value);
        break;

    case 3:
        encoder_append_uint8(self_p, (uint8_t)((uint32_t)value >> 16));
        encoder_append_int16(self_p, (int16_t)value);
        break;

    default:
        encoder_append_int32(self_p, value);
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
        value = ((uint32_t)decoder_read_uint8(self_p) << 16u);
        value |= decoder_read_uint16(self_p);
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

DECODER_READ_LONG_UINT = '''
static uint64_t decoder_read_long_uint(struct decoder_t *self_p,
                                       uint8_t number_of_bytes)
{
    uint64_t value = 0;

    for(uint8_t byte = 0; byte < number_of_bytes; byte++) {
        value = decoder_read_uint8(self_p) | (value << 8);
    }

    return (value);
}\
'''

DECODER_READ_INT = '''
static int32_t decoder_read_int(struct decoder_t *self_p,
                                uint8_t number_of_bytes)
{
    int32_t value;
    uint32_t tmp;

    switch (number_of_bytes) {

    case 1:
        value = decoder_read_int8(self_p);
        break;

    case 2:
        value = decoder_read_int16(self_p);
        break;

    case 3:
        tmp = ((uint32_t)decoder_read_uint8(self_p) << 16u);
        tmp |= decoder_read_uint16(self_p);
        if((tmp & 0x800000u) == 0x800000u) {
            tmp += 0xff000000u;
        }
        value = (int32_t)tmp;
        break;

    case 4:
        value = decoder_read_int32(self_p);
        break;

    default:
        value = 2147483647;
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

functions = [
    ('decoder_read_tag(', DECODER_READ_TAG),
    ('decoder_read_length_determinant(', DECODER_READ_LENGTH_DETERMINANT),
    ('decoder_read_bool(', DECODER_READ_BOOL),
    ('decoder_read_double(', DECODER_READ_DOUBLE),
    ('decoder_read_float(', DECODER_READ_FLOAT),
    ('decoder_read_int(', DECODER_READ_INT),
    ('decoder_read_uint(', DECODER_READ_UINT),
    ('decoder_read_long_uint(', DECODER_READ_LONG_UINT),
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
    ('encoder_append_int(', ENCODER_APPEND_INT),
    ('encoder_append_uint(', ENCODER_APPEND_UINT),
    ('encoder_append_long_uint(', ENCODER_APPEND_LONG_UINT),
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
    ('length_determinant_length(', LENGTH_DETERMINANT_LENGTH),
    ('enumerated_value_length(', ENUMERATED_VALUE_LENGTH)
]
