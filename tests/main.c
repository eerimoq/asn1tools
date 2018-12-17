#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <math.h>

#include "files/c_source/c_source/oer.h"

static bool fequal(double v1, double v2)
{
    return (fabs(v1 - v2) < 0.000001);
}

static void test_oer_c_source_a(void)
{
    uint8_t encoded[55];
    struct oer_c_source_a_t decoded;

    /* Encode. */
    decoded.a = -1;
    decoded.b = -2;
    decoded.c = -3;
    decoded.d = -4;
    decoded.e = 1;
    decoded.f = 2;
    decoded.g = 3;
    decoded.h = 4;
    decoded.i = 1.0f;
    decoded.j = 1.0;
    decoded.k = true;
    memset(&decoded.l[0], 5, sizeof(decoded.l));

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_a_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
                  "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
                  "\x00\x00\x00\x04\x3f\x80\x00\x00\x3f\xf0\x00\x00\x00"
                  "\x00\x00\x00\xff\x0b\x05\x05\x05\x05\x05\x05\x05\x05"
                  "\x05\x05\x05",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_a_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.a == -1);
    assert(decoded.b == -2);
    assert(decoded.c == -3);
    assert(decoded.d == -4);
    assert(decoded.e == 1);
    assert(decoded.f == 2);
    assert(decoded.g == 3);
    assert(decoded.h == 4);
    assert(fequal(decoded.i, 1.0f));
    assert(fequal(decoded.j, 1.0));
    assert(decoded.k);
    assert(memcmp(&decoded.l[0],
                  "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                  sizeof(decoded.l)) == 0);
}

static void test_oer_c_source_a_decode_spare_data(void)
{
    uint8_t encoded[56] =
        "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
        "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
        "\x00\x00\x00\x04\x3f\x80\x00\x00\x3f\xf0\x00\x00\x00"
        "\x00\x00\x00\xff\x0b\x05\x05\x05\x05\x05\x05\x05\x05"
        "\x05\x05\x05\x00";
    struct oer_c_source_a_t decoded;

    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_a_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == 55);

    assert(decoded.a == -1);
    assert(decoded.b == -2);
    assert(decoded.c == -3);
    assert(decoded.d == -4);
    assert(decoded.e == 1);
    assert(decoded.f == 2);
    assert(decoded.g == 3);
    assert(decoded.h == 4);
    assert(fequal(decoded.i, 1.0f));
    assert(fequal(decoded.j, 1.0));
    assert(decoded.k);
    assert(memcmp(&decoded.l[0],
                  "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                  sizeof(decoded.l)) == 0);
}

static void test_oer_c_source_a_encode_error_no_mem(void)
{
    uint8_t encoded[54];
    struct oer_c_source_a_t decoded;

    decoded.a = -1;
    decoded.b = -2;
    decoded.c = -3;
    decoded.d = -4;
    decoded.e = 1;
    decoded.f = 2;
    decoded.g = 3;
    decoded.h = 4;
    decoded.i = 1.0f;
    decoded.j = 1.0;
    decoded.k = true;
    memset(&decoded.l[0], 5, sizeof(decoded.l));

    assert(oer_c_source_a_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == -ENOMEM);
}

static void test_oer_c_source_a_decode_error_out_of_data(void)
{
    uint8_t encoded[54] =
        "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
        "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
        "\x00\x00\x00\x04\x3f\x80\x00\x00\x3f\xf0\x00\x00\x00"
        "\x00\x00\x00\xff\x0b\x05\x05\x05\x05\x05\x05\x05\x05"
        "\x05\x05";
    struct oer_c_source_a_t decoded;

    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_a_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == -EOUTOFDATA);
}

int main(void)
{
    test_oer_c_source_a();
    test_oer_c_source_a_decode_spare_data();
    test_oer_c_source_a_encode_error_no_mem();
    test_oer_c_source_a_decode_error_out_of_data();

    return (0);
}
