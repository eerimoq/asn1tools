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

static void test_oer_c_source_b_choice_a(void)
{
    uint8_t encoded[2];
    struct oer_c_source_b_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_b_choice_a_t;
    decoded.value.a = -10;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_b_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x80\xf6",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_b_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == oer_c_source_b_choice_a_t);
    assert(decoded.value.a == -10);
}

static void test_oer_c_source_b_choice_b(void)
{
    uint8_t encoded[56];
    struct oer_c_source_b_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_b_choice_b_t;
    decoded.value.b.a = -1;
    decoded.value.b.b = -2;
    decoded.value.b.c = -3;
    decoded.value.b.d = -4;
    decoded.value.b.e = 1;
    decoded.value.b.f = 2;
    decoded.value.b.g = 3;
    decoded.value.b.h = 4;
    decoded.value.b.i = 1.0f;
    decoded.value.b.j = 1.0;
    decoded.value.b.k = true;
    memset(&decoded.value.b.l[0], 5, sizeof(decoded.value.b.l));

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_b_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x81\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff"
                  "\xff\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00"
                  "\x00\x00\x00\x00\x04\x3f\x80\x00\x00\x3f\xf0\x00\x00"
                  "\x00\x00\x00\x00\xff\x0b\x05\x05\x05\x05\x05\x05\x05"
                  "\x05\x05\x05\x05",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_b_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == oer_c_source_b_choice_b_t);
    assert(decoded.value.b.a == -1);
    assert(decoded.value.b.b == -2);
    assert(decoded.value.b.c == -3);
    assert(decoded.value.b.d == -4);
    assert(decoded.value.b.e == 1);
    assert(decoded.value.b.f == 2);
    assert(decoded.value.b.g == 3);
    assert(decoded.value.b.h == 4);
    assert(fequal(decoded.value.b.i, 1.0f));
    assert(fequal(decoded.value.b.j, 1.0));
    assert(decoded.value.b.k);
    assert(memcmp(&decoded.value.b.l[0],
                  "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                  sizeof(decoded.value.b.l)) == 0);
}

static void test_oer_c_source_b_decode_error_bad_choice(void)
{
    /* 0x80 (a) and 0x81 (b) are valid tags in the encoded data. */
    uint8_t encoded[2] = "\x82\x00";
    struct oer_c_source_b_t decoded;

    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_b_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == -EBADCHOICE);
}

static void test_oer_c_source_c_empty(void)
{
    uint8_t encoded[2];
    struct oer_c_source_c_t decoded;

    /* Encode. */
    decoded.length = 0;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_c_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x01\x00",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_c_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 0);
}

static void test_oer_c_source_c_2_elements(void)
{
    uint8_t encoded[6];
    struct oer_c_source_c_t decoded;

    /* Encode. */
    decoded.length = 2;
    decoded.elements[0].choice = oer_c_source_b_choice_a_t;
    decoded.elements[0].value.a = -11;
    decoded.elements[1].choice = oer_c_source_b_choice_a_t;
    decoded.elements[1].value.a = 13;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_c_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x01\x02\x80\xf5\x80\x0d",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_c_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 2);
    assert(decoded.elements[0].choice == oer_c_source_b_choice_a_t);
    assert(decoded.elements[0].value.a == -11);
    assert(decoded.elements[1].choice == oer_c_source_b_choice_a_t);
    assert(decoded.elements[1].value.a == 13);
}

int main(void)
{
    test_oer_c_source_a();
    test_oer_c_source_a_decode_spare_data();
    test_oer_c_source_a_encode_error_no_mem();
    test_oer_c_source_a_decode_error_out_of_data();

    test_oer_c_source_b_choice_a();
    test_oer_c_source_b_choice_b();
    test_oer_c_source_b_decode_error_bad_choice();

    test_oer_c_source_c_empty();
    test_oer_c_source_c_2_elements();

    return (0);
}
