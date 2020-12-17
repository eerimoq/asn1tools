#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "nala.h"

#include "files/c_source/oer.h"
#include "files/c_source/c_source-minus.h"

#define membersof(a) (sizeof(a) / (sizeof((a)[0])))

static bool fequal(double v1, double v2)
{
    return (fabs(v1 - v2) < 0.000001);
}

TEST(oer_c_source_a)
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
    ASSERT_EQ(oer_c_source_a_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
                     "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
                     "\x00\x00\x00\x04\xff\x05\x05\x05\x05\x05\x05\x05\x05"
                     "\x05\x05\x05",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_a_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, -1);
    ASSERT_EQ(decoded.b, -2);
    ASSERT_EQ(decoded.c, -3);
    ASSERT_EQ(decoded.d, -4);
    ASSERT_EQ(decoded.e, 1);
    ASSERT_EQ(decoded.f, 2);
    ASSERT_EQ(decoded.g, 3);
    ASSERT_EQ(decoded.h, 4);
    ASSERT_TRUE(decoded.i);
    ASSERT_MEMORY_EQ(&decoded.j.buf[0],
                     "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                     sizeof(decoded.j.buf));
}

TEST(oer_c_source_a_decode_spare_data)
{
    uint8_t encoded[43] =
        "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
        "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
        "\x00\x00\x00\x04\xff\x05\x05\x05\x05\x05\x05\x05\x05"
        "\x05\x05\x05\x00";
    struct oer_c_source_a_t decoded;

    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_a_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), 42);

    ASSERT_EQ(decoded.a, -1);
    ASSERT_EQ(decoded.b, -2);
    ASSERT_EQ(decoded.c, -3);
    ASSERT_EQ(decoded.d, -4);
    ASSERT_EQ(decoded.e, 1);
    ASSERT_EQ(decoded.f, 2);
    ASSERT_EQ(decoded.g, 3);
    ASSERT_EQ(decoded.h, 4);
    ASSERT_TRUE(decoded.i);
    ASSERT_MEMORY_EQ(&decoded.j.buf[0],
                     "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                     sizeof(decoded.j.buf));
}

TEST(oer_c_source_a_encode_error_no_mem)
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

    ASSERT_EQ(oer_c_source_a_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), -ENOMEM);
}

TEST(oer_c_source_a_decode_error_out_of_data)
{
    uint8_t encoded[41] =
        "\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff"
        "\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00"
        "\x00\x00\x00\x04\xff\x05\x05\x05\x05\x05\x05\x05\x05"
        "\x05\x05";
    struct oer_c_source_a_t decoded;

    ASSERT_EQ(oer_c_source_a_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), -EOUTOFDATA);
}

TEST(oer_c_source_b_choice_a)
{
    uint8_t encoded[2];
    struct oer_c_source_b_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_b_choice_a_e;
    decoded.value.a = -10;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_b_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x80\xf6", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_b_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.choice, oer_c_source_b_choice_a_e);
    ASSERT_EQ(decoded.value.a, -10);
}

TEST(oer_c_source_b_choice_b)
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
    ASSERT_EQ(oer_c_source_b_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x81\xff\xff\xfe\xff\xff\xff\xfd\xff\xff\xff\xff\xff"
                     "\xff\xff\xfc\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00"
                     "\x00\x00\x00\x00\x04\xff\x05\x05\x05\x05\x05\x05\x05"
                     "\x05\x05\x05\x05",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_b_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.choice, oer_c_source_b_choice_b_e);
    ASSERT_EQ(decoded.value.b.a, -1);
    ASSERT_EQ(decoded.value.b.b, -2);
    ASSERT_EQ(decoded.value.b.c, -3);
    ASSERT_EQ(decoded.value.b.d, -4);
    ASSERT_EQ(decoded.value.b.e, 1);
    ASSERT_EQ(decoded.value.b.f, 2);
    ASSERT_EQ(decoded.value.b.g, 3);
    ASSERT_EQ(decoded.value.b.h, 4);
    ASSERT_TRUE(decoded.value.b.i);
    ASSERT_MEMORY_EQ(&decoded.value.b.j.buf[0],
                     "\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05\x05",
                     sizeof(decoded.value.b.j.buf));
}

TEST(oer_c_source_b_decode_error_bad_choice)
{
    /* 0x80 (a), 0x81 (b) and 0x82 (c) are valid tags in the encoded
       data. */
    uint8_t encoded[2] = "\x83\x00";
    struct oer_c_source_b_t decoded;

    ASSERT_EQ(oer_c_source_b_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), -EBADCHOICE);
}

TEST(oer_c_source_c_empty)
{
    uint8_t encoded[2];
    struct oer_c_source_c_t decoded;

    /* Encode. */
    decoded.length = 0;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_c_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x01\x00", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_c_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 0);
}

TEST(oer_c_source_c_2_elements)
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
    ASSERT_EQ(oer_c_source_c_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x01\x02\x80\xf5\x80\x0d", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_c_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 2);
    ASSERT_EQ(decoded.elements[0].choice, oer_c_source_b_choice_a_e);
    ASSERT_EQ(decoded.elements[0].value.a, -11);
    ASSERT_EQ(decoded.elements[1].choice, oer_c_source_b_choice_a_e);
    ASSERT_EQ(decoded.elements[1].value.a, 13);
}

TEST(oer_c_source_c_decode_error_bad_length)
{
    uint8_t encoded[8] = "\x01\x03\x80\xf5\x80\x0d\x80\x0e";
    struct oer_c_source_c_t decoded;

    ASSERT_EQ(oer_c_source_c_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), -EBADLENGTH);
}

TEST(oer_c_source_d_all_present)
{
    uint8_t encoded[21];
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
    decoded.elements[0].m.s = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_d_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x01\x01\x80\x00\x01\x03\x00\x02\x54\x55\xf0\x00\x02\x80\x03\x03"
                     "\x03\x03\x03\xff\xff",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_d_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 1);
    ASSERT_EQ(decoded.elements[0].a.b.choice, oer_c_source_d_a_b_choice_c_e);
    ASSERT_EQ(decoded.elements[0].a.b.value.c, 0);
    ASSERT_EQ(decoded.elements[0].a.e.length, 3);
    ASSERT_EQ(decoded.elements[0].g.h, oer_c_source_d_g_h_j_e);
    ASSERT_EQ(decoded.elements[0].g.l.length, 2);
    ASSERT_EQ(decoded.elements[0].g.l.buf[0], 0x54);
    ASSERT_EQ(decoded.elements[0].g.l.buf[1], 0x55);
    ASSERT_TRUE(decoded.elements[0].m.is_n_present);
    ASSERT_EQ(decoded.elements[0].m.n, false);
    ASSERT_EQ(decoded.elements[0].m.o, 2);
    ASSERT_TRUE(decoded.elements[0].m.is_p_present);
    ASSERT_MEMORY_EQ(&decoded.elements[0].m.p.q.buf[0],
                     "\x03\x03\x03\x03\x03",
                     sizeof(decoded.elements[0].m.p.q.buf));
    ASSERT_TRUE(decoded.elements[0].m.p.is_r_present);
    ASSERT_EQ(decoded.elements[0].m.p.r, true);
    ASSERT_EQ(decoded.elements[0].m.s, true);
}

TEST(oer_c_source_d_some_missing)
{
    uint8_t encoded[19];
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
    decoded.elements[0].m.s = false;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_d_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));

    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x01\x01\x81\x00\x01\x03\x80\x82\x02\x00\x01\x54\x20\x00\x03"
                     "\x03\x03\x03\x03",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_d_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 1);
    ASSERT_EQ(decoded.elements[0].a.b.choice, oer_c_source_d_a_b_choice_d_e);
    ASSERT_EQ(decoded.elements[0].a.b.value.d, false);
    ASSERT_EQ(decoded.elements[0].a.e.length, 3);
    ASSERT_EQ(decoded.elements[0].g.h, oer_c_source_d_g_h_k_e);
    ASSERT_EQ(decoded.elements[0].g.l.length, 1);
    ASSERT_EQ(decoded.elements[0].g.l.buf[0], 0x54);
    ASSERT_FALSE(decoded.elements[0].m.is_n_present);
    ASSERT_EQ(decoded.elements[0].m.o, 3);
    ASSERT_TRUE(decoded.elements[0].m.is_p_present);
    ASSERT_MEMORY_EQ(&decoded.elements[0].m.p.q.buf[0],
                     "\x03\x03\x03\x03\x03",
                     sizeof(decoded.elements[0].m.p.q.buf));
    ASSERT_FALSE(decoded.elements[0].m.p.is_r_present);
    ASSERT_EQ(decoded.elements[0].m.s, false);
}

TEST(oer_c_source_e)
{
    uint8_t encoded[3];
    struct oer_c_source_e_t decoded;

    /* Encode. */
    decoded.a.choice = oer_c_source_e_a_choice_b_e;
    decoded.a.value.b.choice = oer_c_source_e_a_b_choice_c_e;
    decoded.a.value.b.value.c = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_e_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x80\x80\xff", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_e_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a.choice, oer_c_source_e_a_choice_b_e);
    ASSERT_EQ(decoded.a.value.b.choice, oer_c_source_e_a_b_choice_c_e);
    ASSERT_EQ(decoded.a.value.b.value.c, true);
}

TEST(oer_c_source_f)
{
    uint8_t encoded[8];
    struct oer_c_source_f_t decoded;

    /* Encode. */
    decoded.length = 2;
    decoded.elements[0].elements[0] = false;
    decoded.elements[1].elements[0] = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_f_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x01\x02\x01\x01\x00\x01\x01\xff",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_f_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 2);
    ASSERT_EQ(decoded.elements[0].elements[0], false);
    ASSERT_EQ(decoded.elements[1].elements[0], true);
}

TEST(oer_c_source_g)
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
    ASSERT_EQ(oer_c_source_g_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x80\x80\xff\xff", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_g_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_TRUE(decoded.is_a_present);
    ASSERT_EQ(decoded.a, true);
    ASSERT_FALSE(decoded.is_b_present);
    ASSERT_FALSE(decoded.is_c_present);
    ASSERT_FALSE(decoded.is_d_present);
    ASSERT_FALSE(decoded.is_e_present);
    ASSERT_FALSE(decoded.is_f_present);
    ASSERT_FALSE(decoded.is_g_present);
    ASSERT_FALSE(decoded.is_h_present);
    ASSERT_TRUE(decoded.is_i_present);
    ASSERT_EQ(decoded.i, true);
}

TEST(oer_c_source_h)
{
    uint8_t encoded[1];
    struct oer_c_source_h_t decoded;

    /* Encode. */
    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_h_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_h_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), 0);
}

TEST(oer_c_source_i)
{
    uint8_t encoded[24];
    struct oer_c_source_i_t decoded;
    uint8_t data[24] =
        "\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03"
        "\x04\x01\x02\x03\x04\x01\x02\x03\x04";

    /* Encode. */
    memcpy(&decoded.buf[0], &data[0], sizeof(data));

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_i_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], &data[0], sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_i_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_MEMORY_EQ(&decoded.buf[0], &data[0], sizeof(data));
}

TEST(oer_c_source_j)
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
    ASSERT_EQ(oer_c_source_j_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x16\x01\x02\x03\x04\x01\x02\x03\x04\x01\x02\x03\x04\x01"
                     "\x02\x03\x04\x01\x02\x03\x04\x01\x02",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_j_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, sizeof(data));
    ASSERT_MEMORY_EQ(&decoded.buf[0], &data[0], sizeof(data));
}

TEST(oer_c_source_k)
{
    uint8_t encoded[1];
    struct oer_c_source_k_t decoded;

    /* Encode. */
    decoded.value = oer_c_source_k_a_e;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_k_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x00", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_k_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.value, oer_c_source_k_a_e);
}

TEST(oer_c_source_l)
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
        ASSERT_EQ(oer_c_source_l_encode(&encoded[0],
                                        sizeof(encoded),
                                        &decoded), datas[i].encoded_length);
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         datas[i].encoded_length);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(oer_c_source_l_decode(&decoded,
                                        &encoded[0],
                                        sizeof(encoded)), datas[i].encoded_length);

        ASSERT_EQ(decoded.length, datas[i].data_length);
        ASSERT_MEMORY_EQ(&decoded.buf[0], &data[0], datas[i].data_length);
    }
}

TEST(oer_c_source_l_decode_error_bad_length)
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
        ASSERT_EQ(oer_c_source_l_decode(&decoded,
                                        &datas[i].encoded[0],
                                        datas[i].length), datas[i].res);
    }
}

TEST(oer_c_source_o)
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
    ASSERT_EQ(oer_c_source_o_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
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
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_o_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 260);

    for (i = 0; i < 260; i++) {
        ASSERT_EQ(decoded.elements[i], true);
    }
}

TEST(oer_c_source_q_c256)
{
    uint8_t encoded[4];
    struct oer_c_source_q_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_q_choice_c256_e;
    decoded.value.c256 = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_q_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\xbf\x81\x7f\xff", 4);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_q_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.choice, oer_c_source_q_choice_c256_e);
    ASSERT_EQ(decoded.value.c256, true);
}

TEST(oer_c_source_q_c257)
{
    uint8_t encoded[4];
    struct oer_c_source_q_t decoded;

    /* Encode. */
    decoded.choice = oer_c_source_q_choice_c257_e;
    decoded.value.c257 = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_q_encode(&encoded[0],
                                    sizeof(encoded),
                                    &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\xbf\x82\x00\xff", 4);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_q_decode(&decoded,
                                    &encoded[0],
                                    sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.choice, oer_c_source_q_choice_c257_e);
    ASSERT_EQ(decoded.value.c257, true);
}

TEST(oer_c_source_x)
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
        ASSERT_EQ(oer_c_source_x_encode(&encoded[0],
                                        sizeof(encoded),
                                        &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0], &datas[i].encoded[0], sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(oer_c_source_x_decode(&decoded,
                                        &encoded[0],
                                        sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(oer_c_source_y)
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
        ASSERT_EQ(oer_c_source_y_encode(&encoded[0],
                                        sizeof(encoded),
                                        &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0], &datas[i].encoded[0], sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(oer_c_source_y_decode(&decoded,
                                        &encoded[0],
                                        sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(oer_c_source_ab)
{
    uint8_t encoded[3];
    struct oer_c_source_ab_t decoded;

    /* Encode. */
    decoded.a = 0;
    decoded.b = 10300;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_ab_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x00\x28\x3c", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_ab_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, 0);
    ASSERT_EQ(decoded.b, 10300);
}

TEST(oer_c_source_ae)
{
    uint8_t encoded[3];
    struct oer_c_source_ae_t decoded;

    /* Encode. */
    decoded.is_a_present = true;
    decoded.a = false;
    decoded.b = true;
    decoded.c = false;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_ae_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x40\x00\x00", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_ae_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, false);
    ASSERT_EQ(decoded.b, true);
    ASSERT_EQ(decoded.c, false);
}

TEST(oer_c_source_af)
{
    uint8_t encoded[32];
    struct oer_c_source_af_t decoded;

    /* Encode. */
    decoded.a = true;
    decoded.b.c = true;
    decoded.is_b_addition_present = true;
    decoded.b.d = 17;
    decoded.b.is_d_addition_present = true;
    decoded.b.e = oer_c_source_ah_e_g_e;
    decoded.b.is_e_addition_present = true;
    decoded.e = 18;
    decoded.is_e_addition_present = true;
    decoded.f = 19;
    decoded.is_f_addition_present = true;
    decoded.g = 20;
    decoded.is_g_addition_present = true;
    decoded.h = 21;
    decoded.is_h_addition_present = true;
    decoded.i = 22;
    decoded.is_i_addition_present = true;
    decoded.j = 23;
    decoded.is_j_addition_present = true;
    decoded.k = 24;
    decoded.is_k_addition_present = true;
    decoded.l = 25;
    decoded.is_l_addition_present = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_af_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x80\xff\x03\x07\xff\x80\x09\x80\xff\x02\x06\xc0\x01\x11"
                     "\x01\x01\x01\x12\x01\x13\x01\x14\x01\x15\x01\x16\x01\x17"
                     "\x01\x18\x01\x19",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_af_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, true);
    ASSERT_TRUE(decoded.is_b_addition_present);
    ASSERT_EQ(decoded.b.c, true);
    ASSERT_TRUE(decoded.b.is_d_addition_present);
    ASSERT_EQ(decoded.b.d, 17);
    ASSERT_TRUE(decoded.b.is_e_addition_present);
    ASSERT_EQ(decoded.b.e, oer_c_source_ah_e_g_e);
    ASSERT_TRUE(decoded.is_e_addition_present);
    ASSERT_EQ(decoded.e, 18);
    ASSERT_TRUE(decoded.is_f_addition_present);
    ASSERT_EQ(decoded.f, 19);
    ASSERT_TRUE(decoded.is_g_addition_present);
    ASSERT_EQ(decoded.g, 20);
    ASSERT_TRUE(decoded.is_h_addition_present);
    ASSERT_EQ(decoded.h, 21);
    ASSERT_TRUE(decoded.is_i_addition_present);
    ASSERT_EQ(decoded.i, 22);
    ASSERT_TRUE(decoded.is_j_addition_present);
    ASSERT_EQ(decoded.j, 23);
    ASSERT_TRUE(decoded.is_k_addition_present);
    ASSERT_EQ(decoded.k, 24);
    ASSERT_TRUE(decoded.is_l_addition_present);
    ASSERT_EQ(decoded.l, 25);
}

TEST(oer_c_source_af_past)
{
    uint8_t encoded[12] = "\x80\xff\x02\x05\xe0\x02\x00\xff\x01\x12\x01\x13";
    struct oer_c_source_af_t decoded;

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_af_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, true);
    ASSERT_TRUE(decoded.is_b_addition_present);
    ASSERT_EQ(decoded.b.c, true);
    ASSERT_FALSE(decoded.b.is_d_addition_present);
    ASSERT_TRUE(decoded.is_e_addition_present);
    ASSERT_EQ(decoded.e, 18);
    ASSERT_TRUE(decoded.is_f_addition_present);
    ASSERT_EQ(decoded.f, 19);
    ASSERT_FALSE(decoded.is_g_addition_present);
    ASSERT_FALSE(decoded.is_h_addition_present);
    ASSERT_FALSE(decoded.is_i_addition_present);
    ASSERT_FALSE(decoded.is_j_addition_present);
    ASSERT_FALSE(decoded.is_k_addition_present);
    ASSERT_FALSE(decoded.is_l_addition_present);
}

TEST(oer_c_source_af_future)
{
    uint8_t encoded[37] = "\x80\xff\x04\x02\xff\xc0\x00\x0b\x80\xff\x02\x03"
        "\xe0\x01\x11\x01\x01\x01\xab\x01\x12\x01\x13\x01\x14\x01\x15\x01\x16\x01"
        "\x17\x01\x18\x01\x19\x01\x1a";
    struct oer_c_source_af_t decoded;

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_af_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, true);
    ASSERT_TRUE(decoded.is_b_addition_present);
    ASSERT_EQ(decoded.b.c, true);
    ASSERT_TRUE(decoded.b.is_d_addition_present);
    ASSERT_EQ(decoded.b.d, 17);
    ASSERT_TRUE(decoded.is_e_addition_present);
    ASSERT_EQ(decoded.e, 18);
    ASSERT_TRUE(decoded.is_f_addition_present);
    ASSERT_EQ(decoded.f, 19);
    ASSERT_TRUE(decoded.is_g_addition_present);
    ASSERT_EQ(decoded.g, 20);
    ASSERT_TRUE(decoded.is_h_addition_present);
    ASSERT_EQ(decoded.h, 21);
    ASSERT_TRUE(decoded.is_i_addition_present);
    ASSERT_EQ(decoded.i, 22);
    ASSERT_TRUE(decoded.is_j_addition_present);
    ASSERT_EQ(decoded.j, 23);
    ASSERT_TRUE(decoded.is_k_addition_present);
    ASSERT_EQ(decoded.k, 24);
    ASSERT_TRUE(decoded.is_l_addition_present);
    ASSERT_EQ(decoded.l, 25);
}

TEST(oer_c_source_ag)
{
    uint8_t encoded[36];
    struct oer_c_source_ag_t decoded;

    /* Encode. */
    decoded.a = true;
    decoded.b.length = 2;
    memcpy(&decoded.b.buf[0], "\x84\x55", 2);
    decoded.is_b_addition_present = true;
    decoded.c.length = 4;
    decoded.c.elements[0] = true;
    decoded.c.elements[1] = false;
    decoded.c.elements[2] = true;
    decoded.c.elements[3] = false;
    decoded.is_c_addition_present = true;
    decoded.d = oer_c_source_ag_d_f_e;
    decoded.is_d_addition_present = true;
    decoded.is_h_addition_present = true;
    decoded.i = 1.0f;
    decoded.is_i_addition_present = true;
    decoded.j.choice = oer_c_source_ag_j_choice_k_e;
    decoded.j.value.k = 60693;
    decoded.is_j_addition_present = true;
    memcpy(&decoded.m.buf[0], "\xf0\xf1\xf2\xf3\xf4", 5);
    decoded.is_m_addition_present = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_ag_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));

    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x80\xff\x02\x01\xfe\x03\x02\x84\x55\x06\x01\x04\xff\x00"
                     "\xff\x00\x03\x82\x01\x00\x00\x04\x3f\x80\x00\x00\x03\x80"
                     "\xed\x15\x05\xf0\xf1\xf2\xf3\xf4",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_ag_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, true);
    ASSERT_TRUE(decoded.is_b_addition_present);
    ASSERT_EQ(decoded.b.length, 2);
    ASSERT_MEMORY_EQ(&decoded.b.buf[0], "\x84\x55", 2);
    ASSERT_TRUE(decoded.is_c_addition_present);
    ASSERT_EQ(decoded.c.length, 4);
    ASSERT_TRUE(decoded.c.elements[0]);
    ASSERT_FALSE(decoded.c.elements[1]);
    ASSERT_TRUE(decoded.c.elements[2]);
    ASSERT_FALSE(decoded.c.elements[3]);
    ASSERT_TRUE(decoded.is_d_addition_present);
    ASSERT_EQ(decoded.d, oer_c_source_ag_d_f_e);
    ASSERT_TRUE(decoded.is_h_addition_present);
    ASSERT_TRUE(decoded.is_i_addition_present);
    ASSERT_TRUE(decoded.i >= 1.0f);
    ASSERT_TRUE(decoded.i <= 1.0f);
    ASSERT_TRUE(decoded.is_j_addition_present);
    ASSERT_EQ(decoded.j.choice, oer_c_source_ag_j_choice_k_e);
    ASSERT_EQ(decoded.j.value.k, 60693);
    ASSERT_TRUE(decoded.is_m_addition_present);
    ASSERT_MEMORY_EQ(&decoded.m.buf[0], "\xf0\xf1\xf2\xf3\xf4", 5);
}

TEST(oer_c_source_an)
{
    struct data_t {
        int32_t decoded;
        uint8_t encoded[5];
        uint8_t encoded_length;
    } datas[] = {
        {
            .decoded = oer_c_source_an_a_e,
            .encoded = "\x84\xff\x00\x00\x00",
            .encoded_length = 5
        },
        {
            .decoded = oer_c_source_an_b_e,
            .encoded = "\x83\x80\x00\x00",
            .encoded_length = 4
        },
        {
            .decoded = oer_c_source_an_c_e,
            .encoded = "\x83\xff\x00\x00",
            .encoded_length = 4
        },
        {
            .decoded = oer_c_source_an_d_e,
            .encoded = "\x82\x80\x00",
            .encoded_length = 3
        },
        {
            .decoded = oer_c_source_an_e_e,
            .encoded = "\x81\x80",
            .encoded_length = 2
        },
        {
            .decoded = oer_c_source_an_f_e,
            .encoded = "\x00",
            .encoded_length = 1
        },
        {
            .decoded = oer_c_source_an_g_e,
            .encoded = "\x7f",
            .encoded_length = 1
        },
        {
            .decoded = oer_c_source_an_h_e,
            .encoded = "\x82\x00\x80",
            .encoded_length = 3
        },
        {
            .decoded = oer_c_source_an_i_e,
            .encoded = "\x82\x7f\xff",
            .encoded_length = 3
        },
        {
            .decoded = oer_c_source_an_j_e,
            .encoded = "\x83\x01\x00\x00",
            .encoded_length = 4
        },
        {
            .decoded = oer_c_source_an_k_e,
            .encoded = "\x84\x01\x00\x00\x00",
            .encoded_length = 5
        },
    };
    uint8_t encoded[5];
    struct oer_c_source_an_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(oer_c_source_an_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), datas[i].encoded_length);
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         datas[i].encoded_length);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(oer_c_source_an_decode(&decoded,
                                         &encoded[0],
                                         datas[i].encoded_length),
                                         datas[i].encoded_length);

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(oer_c_source_ao)
{
    uint8_t encoded[17];
    struct oer_c_source_ao_t decoded;

    /* Encode. */
    decoded.a = OER_C_SOURCE_AO_A_C;
    decoded.b = OER_C_SOURCE_AO_B_A;
    decoded.c = 0x50;
    decoded.d = OER_C_SOURCE_AO_D_B;
    decoded.e = OER_C_SOURCE_AO_E_C;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_c_source_ao_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x01\x80\x00\x00\x50\x20\x00\x00\x00\x00\x00\x00\x00\x00"
                     "\x00\x00\x01",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_ao_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, OER_C_SOURCE_AO_A_C);
    ASSERT_EQ(decoded.b, OER_C_SOURCE_AO_B_A);
    ASSERT_EQ(decoded.c, 0x50);
    ASSERT_EQ(decoded.d, OER_C_SOURCE_AO_D_B);
    ASSERT_EQ(decoded.e, OER_C_SOURCE_AO_E_C);
}

TEST(oer_c_source_ap)
{
    uint8_t encoded[3] = "\x80\x10\x01";
    struct oer_c_source_ap_t decoded;

    decoded.b.a = 16;
    decoded.c.value = oer_c_ref_referenced_enum_b_e;
    decoded.d = 1;

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_c_source_ap_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.b.a, 16);
    ASSERT_EQ(decoded.c.value, oer_c_ref_referenced_enum_b_e);
    ASSERT_EQ(decoded.d, 1);
}

TEST(oer_c_source_ag_erroneous_data)
{
    struct oer_c_source_ag_t decoded;

    // Wrong length determinant, valid unused bits
    uint8_t encoded[4] = "\x80\xff\xff\x00";
    ASSERT_EQ(oer_c_source_ag_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), -EOUTOFDATA);

    // Valid length determinant, invalid unused bits
    uint8_t encoded2[4] = "\x80\xff\x03\x0a";
    ASSERT_EQ(oer_c_source_ag_decode(&decoded,
                                     &encoded2[0],
                                     sizeof(encoded2)), -EBADLENGTH);

    // Invalid addition length of unknown future additions
    uint8_t encoded3[6] = "\x80\xff\x02\x00\x01\xff";
    ASSERT_EQ(oer_c_source_ag_decode(&decoded,
                                     &encoded3[0],
                                     sizeof(encoded3)), -EOUTOFDATA);
}

TEST(oer_programming_types_float)
{
    uint8_t encoded[4];
    struct oer_programming_types_float_t decoded;

    /* Encode. */
    decoded.value = 1.0f;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_programming_types_float_encode(&encoded[0],
                                                 sizeof(encoded),
                                                 &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x3f\x80\x00\x00", sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_programming_types_float_decode(&decoded,
                                                 &encoded[0],
                                                 sizeof(encoded)), sizeof(encoded));

    ASSERT_TRUE(fequal(decoded.value, 1.0f));
}

TEST(oer_programming_types_double)
{
    uint8_t encoded[8];
    struct oer_programming_types_double_t decoded;

    /* Encode. */
    decoded.value = 1.0;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(oer_programming_types_double_encode(&encoded[0],
                                                  sizeof(encoded),
                                                  &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x3f\xf0\x00\x00\x00\x00\x00\x00",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(oer_programming_types_double_decode(&decoded,
                                                  &encoded[0],
                                                  sizeof(encoded)), sizeof(encoded));

    ASSERT_TRUE(fequal(decoded.value, 1.0));
}
