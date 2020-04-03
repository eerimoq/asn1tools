#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <math.h>

#include "files/c_source/oer.h"
#include "files/c_source/c_source-minus.h"

#define membersof(a) (sizeof(a) / (sizeof((a)[0])))

static bool fequal(double v1, double v2)
{
    return (fabs(v1 - v2) < 0.000001);
}

static void test_oer_c_source_a(void)
{
    uint8_t encoded[42];
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
    decoded.i = true;
    memset(&decoded.j.buf[0], 5, sizeof(decoded.j.buf));

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_a_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
                  "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
                  "\x00\x00\x00\x04\xff\x05\x05\x05\x05\x05\x05\x05\x05"
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
    assert(decoded.i);
    assert(memcmp(&decoded.j.buf[0],
                  "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                  sizeof(decoded.j.buf)) == 0);
}

static void test_oer_c_source_a_decode_spare_data(void)
{
    uint8_t encoded[43] =
        "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
        "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
        "\x00\x00\x00\x04\xff\x05\x05\x05\x05\x05\x05\x05\x05"
        "\x05\x05\x05\x00";
    struct oer_c_source_a_t decoded;

    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_a_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == 42);

    assert(decoded.a == -1);
    assert(decoded.b == -2);
    assert(decoded.c == -3);
    assert(decoded.d == -4);
    assert(decoded.e == 1);
    assert(decoded.f == 2);
    assert(decoded.g == 3);
    assert(decoded.h == 4);
    assert(decoded.i);
    assert(memcmp(&decoded.j.buf[0],
                  "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                  sizeof(decoded.j.buf)) == 0);
}

static void test_oer_c_source_a_encode_error_no_mem(void)
{
    uint8_t encoded[41];
    struct oer_c_source_a_t decoded;

    decoded.a = -1;
    decoded.b = -2;
    decoded.c = -3;
    decoded.d = -4;
    decoded.e = 1;
    decoded.f = 2;
    decoded.g = 3;
    decoded.h = 4;
    decoded.i = true;
    memset(&decoded.j.buf[0], 5, sizeof(decoded.j.buf));

    assert(oer_c_source_a_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == -ENOMEM);
}

static void test_oer_c_source_a_decode_error_out_of_data(void)
{
    uint8_t encoded[41] =
        "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
        "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
        "\x00\x00\x00\x04\xff\x05\x05\x05\x05\x05\x05\x05\x05"
        "\x05\x05";
    struct oer_c_source_a_t decoded;

    assert(oer_c_source_a_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == -EOUTOFDATA);
}

static void test_oer_c_source_b_choice_a(void)
{
    uint8_t encoded[2];
    struct oer_c_source_b_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_b_choice_a_e;
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

    assert(decoded.choice == oer_c_source_b_choice_a_e);
    assert(decoded.value.a == -10);
}

static void test_oer_c_source_b_choice_b(void)
{
    uint8_t encoded[43];
    struct oer_c_source_b_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_b_choice_b_e;
    decoded.value.b.a = -1;
    decoded.value.b.b = -2;
    decoded.value.b.c = -3;
    decoded.value.b.d = -4;
    decoded.value.b.e = 1;
    decoded.value.b.f = 2;
    decoded.value.b.g = 3;
    decoded.value.b.h = 4;
    decoded.value.b.i = true;
    memset(&decoded.value.b.j.buf[0], 5, sizeof(decoded.value.b.j.buf));

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_b_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x81\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff"
                  "\xff\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00"
                  "\x00\x00\x00\x00\x04\xff\x05\x05\x05\x05\x05\x05\x05"
                  "\x05\x05\x05\x05",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_b_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == oer_c_source_b_choice_b_e);
    assert(decoded.value.b.a == -1);
    assert(decoded.value.b.b == -2);
    assert(decoded.value.b.c == -3);
    assert(decoded.value.b.d == -4);
    assert(decoded.value.b.e == 1);
    assert(decoded.value.b.f == 2);
    assert(decoded.value.b.g == 3);
    assert(decoded.value.b.h == 4);
    assert(decoded.value.b.i);
    assert(memcmp(&decoded.value.b.j.buf[0],
                  "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                  sizeof(decoded.value.b.j.buf)) == 0);
}

static void test_oer_c_source_b_decode_error_bad_choice(void)
{
    /* 0x80 (a), 0x81 (b) and 0x82 (c) are valid tags in the encoded
       data. */
    uint8_t encoded[2] = "\x83\x00";
    struct oer_c_source_b_t decoded;

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
    decoded.elements[0].choice = oer_c_source_b_choice_a_e;
    decoded.elements[0].value.a = -11;
    decoded.elements[1].choice = oer_c_source_b_choice_a_e;
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
    assert(decoded.elements[0].choice == oer_c_source_b_choice_a_e);
    assert(decoded.elements[0].value.a == -11);
    assert(decoded.elements[1].choice == oer_c_source_b_choice_a_e);
    assert(decoded.elements[1].value.a == 13);
}

static void test_oer_c_source_c_decode_error_bad_length(void)
{
    uint8_t encoded[8] = "\x01\x03\x80\xf5\x80\x0d\x80\x0e";
    struct oer_c_source_c_t decoded;

    assert(oer_c_source_c_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == -EBADLENGTH);
}

static void test_oer_c_source_d_all_present(void)
{
    uint8_t encoded[20];
    struct oer_c_source_d_t decoded;

    /* Encode. */
    decoded.length = 1;
    decoded.elements[0].a.b.choice = oer_c_source_d_a_b_choice_c_e;
    decoded.elements[0].a.b.value.c = 0;
    decoded.elements[0].a.e.length = 3;
    decoded.elements[0].g.h = oer_c_source_d_g_h_j_e;
    decoded.elements[0].g.l.length = 2;
    decoded.elements[0].g.l.buf[0] = 0x54;
    decoded.elements[0].g.l.buf[1] = 0x55;
    decoded.elements[0].m.is_n_present = true;
    decoded.elements[0].m.n = false;
    decoded.elements[0].m.o = 2;
    decoded.elements[0].m.is_p_present = true;
    memset(&decoded.elements[0].m.p.q.buf[0],
           3,
           sizeof(decoded.elements[0].m.p.q.buf));
    decoded.elements[0].m.p.is_r_present = true;
    decoded.elements[0].m.p.r = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_d_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x01\x01\x80\x00\x01\x03\x01\x02\x54\x55\xe0\x00\x02\x80"
                  "\x03\x03\x03\x03\x03\xff",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_d_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 1);
    assert(decoded.elements[0].a.b.choice == oer_c_source_d_a_b_choice_c_e);
    assert(decoded.elements[0].a.b.value.c == 0);
    assert(decoded.elements[0].a.e.length == 3);
    assert(decoded.elements[0].g.h == oer_c_source_d_g_h_j_e);
    assert(decoded.elements[0].g.l.length == 2);
    assert(decoded.elements[0].g.l.buf[0] == 0x54);
    assert(decoded.elements[0].g.l.buf[1] == 0x55);
    assert(decoded.elements[0].m.is_n_present);
    assert(decoded.elements[0].m.n == false);
    assert(decoded.elements[0].m.o == 2);
    assert(decoded.elements[0].m.is_p_present);
    assert(memcmp(&decoded.elements[0].m.p.q.buf[0],
                  "\x03\x03\x03\x03\x03",
                  sizeof(decoded.elements[0].m.p.q.buf)) == 0);
    assert(decoded.elements[0].m.p.is_r_present);
    assert(decoded.elements[0].m.p.r == true);
}

static void test_oer_c_source_d_some_missing(void)
{
    uint8_t encoded[16];
    struct oer_c_source_d_t decoded;

    /* Encode. */
    decoded.length = 1;
    decoded.elements[0].a.b.choice = oer_c_source_d_a_b_choice_d_e;
    decoded.elements[0].a.b.value.d = false;
    decoded.elements[0].a.e.length = 3;
    decoded.elements[0].g.h = oer_c_source_d_g_h_k_e;
    decoded.elements[0].g.l.length = 1;
    decoded.elements[0].g.l.buf[0] = 0x54;
    decoded.elements[0].m.is_n_present = false;
    /* Default value 3. */
    decoded.elements[0].m.o = 3;
    decoded.elements[0].m.is_p_present = true;
    memset(&decoded.elements[0].m.p.q.buf[0],
           3,
           sizeof(decoded.elements[0].m.p.q.buf));
    decoded.elements[0].m.p.is_r_present = false;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_d_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x01\x01\x81\x00\x01\x03\x02\x01\x54\x20\x00\x03\x03\x03"
                  "\x03\x03",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_d_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 1);
    assert(decoded.elements[0].a.b.choice == oer_c_source_d_a_b_choice_d_e);
    assert(decoded.elements[0].a.b.value.d == false);
    assert(decoded.elements[0].a.e.length == 3);
    assert(decoded.elements[0].g.h == oer_c_source_d_g_h_k_e);
    assert(decoded.elements[0].g.l.length == 1);
    assert(decoded.elements[0].g.l.buf[0] == 0x54);
    assert(!decoded.elements[0].m.is_n_present);
    assert(decoded.elements[0].m.o == 3);
    assert(decoded.elements[0].m.is_p_present);
    assert(memcmp(&decoded.elements[0].m.p.q.buf[0],
                  "\x03\x03\x03\x03\x03",
                  sizeof(decoded.elements[0].m.p.q.buf)) == 0);
    assert(!decoded.elements[0].m.p.is_r_present);
}

static void test_oer_c_source_e(void)
{
    uint8_t encoded[3];
    struct oer_c_source_e_t decoded;

    /* Encode. */
    decoded.a.choice = oer_c_source_e_a_choice_b_e;
    decoded.a.value.b.choice = oer_c_source_e_a_b_choice_c_e;
    decoded.a.value.b.value.c = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_e_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x80\x80\xff",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_e_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.a.choice == oer_c_source_e_a_choice_b_e);
    assert(decoded.a.value.b.choice == oer_c_source_e_a_b_choice_c_e);
    assert(decoded.a.value.b.value.c == true);
}

static void test_oer_c_source_f(void)
{
    uint8_t encoded[8];
    struct oer_c_source_f_t decoded;

    /* Encode. */
    decoded.length = 2;
    decoded.elements[0].elements[0] = false;
    decoded.elements[1].elements[0] = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_f_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x01\x02\x01\x01\x00\x01\x01\xff",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_f_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 2);
    assert(decoded.elements[0].elements[0] == false);
    assert(decoded.elements[1].elements[0] == true);
}

static void test_oer_c_source_g(void)
{
    uint8_t encoded[4];
    struct oer_c_source_g_t decoded;

    /* Encode. */
    decoded.is_a_present = true;
    decoded.a = true;
    decoded.is_b_present = false;
    decoded.is_c_present = false;
    decoded.is_d_present = false;
    decoded.is_e_present = false;
    decoded.is_f_present = false;
    decoded.is_g_present = false;
    decoded.is_h_present = false;
    decoded.is_i_present = true;
    decoded.i = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_g_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x80\x80\xff\xff",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_g_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.is_a_present);
    assert(decoded.a == true);
    assert(!decoded.is_b_present);
    assert(!decoded.is_c_present);
    assert(!decoded.is_d_present);
    assert(!decoded.is_e_present);
    assert(!decoded.is_f_present);
    assert(!decoded.is_g_present);
    assert(!decoded.is_h_present);
    assert(decoded.is_i_present);
    assert(decoded.i == true);
}

static void test_oer_c_source_h(void)
{
    uint8_t encoded[1];
    struct oer_c_source_h_t decoded;

    /* Encode. */
    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_h_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_h_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == 0);
}

static void test_oer_c_source_i(void)
{
    uint8_t encoded[24];
    struct oer_c_source_i_t decoded;
    uint8_t data[24] =
        "\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03"
        "\x04\x01\x02\x03\x04\x01\x02\x03\x04";

    /* Encode. */
    memcpy(&decoded.buf[0], &data[0], sizeof(data));

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_i_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  &data[0],
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_i_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(memcmp(&decoded.buf[0], &data[0], sizeof(data)) == 0);
}

static void test_oer_c_source_j(void)
{
    uint8_t encoded[23];
    struct oer_c_source_j_t decoded;
    uint8_t data[22] =
        "\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03"
        "\x04\x01\x02\x03\x04\x01\x02";

    /* Encode. */
    decoded.length = sizeof(data);
    memcpy(&decoded.buf[0], &data[0], sizeof(data));

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_j_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x16\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01"
                  "\x02\x03\x04\x01\x02\x03\x04\x01\x02",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_j_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == sizeof(data));
    assert(memcmp(&decoded.buf[0], &data[0], sizeof(data)) == 0);
}

static void test_oer_c_source_k(void)
{
    uint8_t encoded[1];
    struct oer_c_source_k_t decoded;

    /* Encode. */
    decoded.value = oer_c_source_k_a_e;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_k_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x00",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_k_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.value == oer_c_source_k_a_e);
}

static void test_oer_c_source_l(void)
{
    struct data_t {
        uint16_t data_length;
        uint16_t encoded_length;
        uint8_t encoded[263];
    } datas[] = {
        {
            .data_length = 0,
            .encoded_length = 1,
            .encoded = "\x00"
        },
        {
            .data_length = 127,
            .encoded_length = 128,
            .encoded =
            "\x7f\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5"
        },
        {
            .data_length = 128,
            .encoded_length = 130,
            .encoded =
            "\x81\x80\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5"
        },
        {
            .data_length = 260,
            .encoded_length = 263,
            .encoded =
            "\x82\x01\x04\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
            "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        }
    };
    uint8_t encoded[263];
    struct oer_c_source_l_t decoded;
    uint8_t data[260] =
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5\xa5"
        "\xa5\xa5\xa5\xa5\xa5";
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.length = datas[i].data_length;
        memcpy(&decoded.buf[0], &data[0], decoded.length);

        memset(&encoded[0], 0, sizeof(encoded));
        assert(oer_c_source_l_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded) == datas[i].encoded_length);
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      datas[i].encoded_length) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(oer_c_source_l_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)) == datas[i].encoded_length);

        assert(decoded.length == datas[i].data_length);
        assert(memcmp(&decoded.buf[0],
                      &data[0],
                      datas[i].data_length) == 0);
    }
}

static void test_oer_c_source_l_decode_error_bad_length(void)
{
    struct data_t {
        int res;
        uint16_t length;
        uint8_t encoded[16];
    } datas[] = {
        {
            .res = -EBADLENGTH,
            .length = 3,
            .encoded = "\x82\x01\xff"
        },
        {
            .res = -EBADLENGTH,
            .length = 4,
            .encoded = "\x83\x01\xff\x00"
        },
        {
            .res = -EBADLENGTH,
            .length = 5,
            .encoded = "\x84\x01\x00\x01\x00"
        },
        {
            .res = -EOUTOFDATA,
            .length = 1,
            .encoded = "\x83"
        },
        {
            .res = -EBADLENGTH,
            .length = 2,
            .encoded = "\xff\x00"
        }
    };
    struct oer_c_source_l_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        memset(&decoded, 0, sizeof(decoded));
        assert(oer_c_source_l_decode(&decoded,
                                     &datas[i].encoded[0],
                                     datas[i].length) == datas[i].res);
    }
}

static void test_oer_c_source_o(void)
{
    int i;
    uint8_t encoded[263];
    struct oer_c_source_o_t decoded;

    /* Encode. */
    decoded.length = 260;

    for (i = 0; i < 260; i++) {
        decoded.elements[i] = true;
    }

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_o_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x02\x01\x04\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
                  "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_o_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 260);

    for (i = 0; i < 260; i++) {
        assert(decoded.elements[i] == true);
    }
}

static void test_oer_c_source_q_c256(void)
{
    uint8_t encoded[4];
    struct oer_c_source_q_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_q_choice_c256_e;
    decoded.value.c256 = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_q_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0], "\xbf\x81\x7f\xff", 4) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_q_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == oer_c_source_q_choice_c256_e);
    assert(decoded.value.c256 == true);
}

static void test_oer_c_source_q_c257(void)
{
    uint8_t encoded[4];
    struct oer_c_source_q_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_q_choice_c257_e;
    decoded.value.c257 = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_q_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0], "\xbf\x82\x00\xff", 4) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_q_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == oer_c_source_q_choice_c257_e);
    assert(decoded.value.c257 == true);
}

static void test_oer_c_source_x(void)
{
    struct data_t {
        int16_t decoded;
        uint8_t encoded[2];
    } datas[] = {
        {
            .decoded = -2,
            .encoded = "\xff\xfe"
        },
        {
            .decoded = 510,
            .encoded = "\x01\xfe"
        }
    };
    uint8_t encoded[2];
    struct oer_c_source_x_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        assert(oer_c_source_x_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(oer_c_source_x_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_oer_c_source_y(void)
{
    struct data_t {
        uint16_t decoded;
        uint8_t encoded[2];
    } datas[] = {
        {
            .decoded = 10000,
            .encoded = "\x27\x10"
        },
        {
            .decoded = 10512,
            .encoded = "\x29\x10"
        }
    };
    uint8_t encoded[2];
    struct oer_c_source_y_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        assert(oer_c_source_y_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(oer_c_source_y_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_oer_c_source_ab(void)
{
    uint8_t encoded[3];
    struct oer_c_source_ab_t decoded;

    /* Encode. */
    decoded.a = 0;
    decoded.b = 10300;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_c_source_ab_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x00\x28\x3c",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_c_source_ab_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.a == 0);
    assert(decoded.b == 10300);
}

static void test_oer_programming_types_float(void)
{
    uint8_t encoded[4];
    struct oer_programming_types_float_t decoded;

    /* Encode. */
    decoded.value = 1.0f;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_programming_types_float_encode(&encoded[0],
                                              sizeof(encoded),
                                              &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x3f\x80\x00\x00",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_programming_types_float_decode(&decoded,
                                              &encoded[0],
                                              sizeof(encoded)) == sizeof(encoded));

    assert(fequal(decoded.value, 1.0f));
}

static void test_oer_programming_types_double(void)
{
    uint8_t encoded[8];
    struct oer_programming_types_double_t decoded;

    /* Encode. */
    decoded.value = 1.0;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(oer_programming_types_double_encode(&encoded[0],
                                               sizeof(encoded),
                                               &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x3f\xf0\x00\x00\x00\x00\x00\x00",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(oer_programming_types_double_decode(&decoded,
                                               &encoded[0],
                                               sizeof(encoded)) == sizeof(encoded));

    assert(fequal(decoded.value, 1.0));
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
    test_oer_c_source_c_decode_error_bad_length();

    test_oer_c_source_d_all_present();
    test_oer_c_source_d_some_missing();

    test_oer_c_source_e();
    test_oer_c_source_f();
    test_oer_c_source_g();
    test_oer_c_source_h();
    test_oer_c_source_i();
    test_oer_c_source_j();
    test_oer_c_source_k();
    test_oer_c_source_l();
    test_oer_c_source_l_decode_error_bad_length();
    test_oer_c_source_o();
    test_oer_c_source_q_c256();
    test_oer_c_source_q_c257();
    test_oer_c_source_x();
    test_oer_c_source_y();
    test_oer_c_source_ab();

    test_oer_programming_types_float();
    test_oer_programming_types_double();

    return (0);
}
