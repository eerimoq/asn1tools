#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "nala.h"

#include "uper.h"
#include "boolean_uper.h"
#include "octet_string_uper.h"

#define membersof(a) (sizeof(a) / (sizeof((a)[0])))

TEST(uper_c_source_a)
{
    uint8_t encoded[42];
    struct uper_c_source_a_t decoded;

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
    ASSERT_EQ(uper_c_source_a_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x7f\x7f\xfe\x7f\xff\xff\xfd\x7f\xff\xff\xff\xff\xff\xff\xfc"
                     "\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04"
                     "\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82\x80",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_a_decode(&decoded,
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

TEST(uper_c_source_a_encode_error_no_mem)
{
    uint8_t encoded[41];
    struct uper_c_source_a_t decoded;

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

    ASSERT_EQ(uper_c_source_a_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), -ENOMEM);
}

TEST(uper_c_source_a_decode_error_out_of_data)
{
    uint8_t encoded[41] =
        "\x7f\x7f\xfe\x7f\xff\xff\xfd\x7f\xff\xff\xff\xff\xff\xff\xfc"
        "\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04"
        "\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82";
    struct uper_c_source_a_t decoded;

    ASSERT_EQ(uper_c_source_a_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), -EOUTOFDATA);
}

TEST(uper_c_source_b_choice_a)
{
    uint8_t encoded[2];
    struct uper_c_source_b_t decoded;

    /* Encode. */
    decoded.choice = uper_c_source_b_choice_a_e;
    decoded.value.a = -10;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_b_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x1d\x80",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_b_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.choice, uper_c_source_b_choice_a_e);
    ASSERT_EQ(decoded.value.a, -10);
}

TEST(uper_c_source_b_choice_b)
{
    uint8_t encoded[42];
    struct uper_c_source_b_t decoded;

    /* Encode. */
    decoded.choice = uper_c_source_b_choice_b_e;
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
    ASSERT_EQ(uper_c_source_b_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x5f\xdf\xff\x9f\xff\xff\xff\x5f\xff\xff\xff\xff\xff\xff\xff"
                     "\x00\x40\x00\x80\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x01"
                     "\x20\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_b_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.choice, uper_c_source_b_choice_b_e);
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

TEST(uper_c_source_b_decode_error_bad_choice)
{
    uint8_t encoded[2] = "\xdd\x80";
    struct uper_c_source_b_t decoded;

    ASSERT_EQ(uper_c_source_b_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), -EBADCHOICE);
}

TEST(uper_c_source_c_empty)
{
    uint8_t encoded[1];
    struct uper_c_source_c_t decoded;

    /* Encode. */
    decoded.length = 0;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_c_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x00",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_c_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 0);
}

TEST(uper_c_source_c_2_elements)
{
    uint8_t encoded[3];
    struct uper_c_source_c_t decoded;

    /* Encode. */
    decoded.length = 2;
    decoded.elements[0].choice = uper_c_source_b_choice_a_e;
    decoded.elements[0].value.a = -11;
    decoded.elements[1].choice = uper_c_source_b_choice_a_e;
    decoded.elements[1].value.a = 13;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_c_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x87\x52\x34",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_c_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 2);
    ASSERT_EQ(decoded.elements[0].choice, uper_c_source_b_choice_a_e);
    ASSERT_EQ(decoded.elements[0].value.a, -11);
    ASSERT_EQ(decoded.elements[1].choice, uper_c_source_b_choice_a_e);
    ASSERT_EQ(decoded.elements[1].value.a, 13);
}

TEST(uper_c_source_c_decode_error_bad_length)
{
    uint8_t encoded[4] = "\xc7\x52\x34\x00";
    struct uper_c_source_c_t decoded;

    ASSERT_EQ(uper_c_source_c_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), -EBADLENGTH);
}

TEST(uper_c_source_d_all_present)
{
    uint8_t encoded[10];
    struct uper_c_source_d_t decoded;

    /* Encode. */
    decoded.length = 1;
    decoded.elements[0].a.b.choice = uper_c_source_d_a_b_choice_c_e;
    decoded.elements[0].a.b.value.c = 0;
    decoded.elements[0].a.e.length = 3;
    decoded.elements[0].g.h = uper_c_source_d_g_h_j_e;
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

    ASSERT_EQ(uper_c_source_d_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x00\xaa\x2a\xfa\x40\xc0\xc0\xc0\xc0\xf0",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_d_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 1);
    ASSERT_EQ(decoded.elements[0].a.b.choice, uper_c_source_d_a_b_choice_c_e);
    ASSERT_EQ(decoded.elements[0].a.b.value.c, 0);
    ASSERT_EQ(decoded.elements[0].a.e.length, 3);
    ASSERT_EQ(decoded.elements[0].g.h, uper_c_source_d_g_h_j_e);
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

TEST(uper_c_source_d_some_missing)
{
    uint8_t encoded[8];
    struct uper_c_source_d_t decoded;

    /* Encode. */
    decoded.length = 1;
    decoded.elements[0].a.b.choice = uper_c_source_d_a_b_choice_d_e;
    decoded.elements[0].a.b.value.d = false;
    decoded.elements[0].a.e.length = 3;
    decoded.elements[0].g.h = uper_c_source_d_g_h_k_e;
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
    ASSERT_EQ(uper_c_source_d_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x09\x8a\x84\x03\x03\x03\x03\x03",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_d_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 1);
    ASSERT_EQ(decoded.elements[0].a.b.choice, uper_c_source_d_a_b_choice_d_e);
    ASSERT_EQ(decoded.elements[0].a.b.value.d, false);
    ASSERT_EQ(decoded.elements[0].a.e.length, 3);
    ASSERT_EQ(decoded.elements[0].g.h, uper_c_source_d_g_h_k_e);
    ASSERT_EQ(decoded.elements[0].g.l.length, 1);
    ASSERT_EQ(decoded.elements[0].g.l.buf[0], 0x54);
    ASSERT_FALSE(decoded.elements[0].m.is_n_present);
    ASSERT_EQ(decoded.elements[0].m.o, 3);
    ASSERT_TRUE(decoded.elements[0].m.is_p_present);
    ASSERT_MEMORY_EQ(&decoded.elements[0].m.p.q.buf[0],
                     "\x03\x03\x03\x03\x03",
                     sizeof(decoded.elements[0].m.p.q.buf));
    ASSERT_FALSE(decoded.elements[0].m.p.is_r_present);
    ASSERT_EQ(decoded.elements[0].m.p.r, false);
}

TEST(uper_c_source_d_decode_error_bad_enum)
{
    uint8_t encoded[10] = "\x01\xd5\x15\x7a\x40\xc0\xc0\xc0\xc0\xe0";
    struct uper_c_source_d_t decoded;

    ASSERT_EQ(uper_c_source_d_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), -EBADENUM);
}

TEST(uper_c_source_e)
{
    uint8_t encoded[1];
    struct uper_c_source_e_t decoded;

    /* Encode. */
    decoded.a.choice = uper_c_source_e_a_choice_b_e;
    decoded.a.value.b.choice = uper_c_source_e_a_b_choice_c_e;
    decoded.a.value.b.value.c = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_e_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x80",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_e_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a.choice, uper_c_source_e_a_choice_b_e);
    ASSERT_EQ(decoded.a.value.b.choice, uper_c_source_e_a_b_choice_c_e);
    ASSERT_EQ(decoded.a.value.b.value.c, true);
}

TEST(uper_c_source_f)
{
    uint8_t encoded[1];
    struct uper_c_source_f_t decoded;

    /* Encode. */
    decoded.length = 2;
    decoded.elements[0].elements[0] = false;
    decoded.elements[1].elements[0] = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_f_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\xa0",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_f_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.length, 2);
    ASSERT_EQ(decoded.elements[0].elements[0], false);
    ASSERT_EQ(decoded.elements[1].elements[0], true);
}

TEST(uper_c_source_g)
{
    uint8_t encoded[2];
    struct uper_c_source_g_t decoded;

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
    ASSERT_EQ(uper_c_source_g_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x80\xe0",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_g_decode(&decoded,
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

TEST(uper_c_source_h)
{
    uint8_t encoded[1];
    struct uper_c_source_h_t decoded;

    /* Encode. */
    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_h_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_h_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), 0);
}

TEST(uper_c_source_q_c256)
{
    uint8_t encoded[2];
    struct uper_c_source_q_t decoded;

    /* Encode. */
    decoded.choice = uper_c_source_q_choice_c256_e;
    decoded.value.c256 = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_q_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x7f\xc0", 2);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_q_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.choice, uper_c_source_q_choice_c256_e);
    ASSERT_EQ(decoded.value.c256, true);
}

TEST(uper_c_source_q_c257)
{
    uint8_t encoded[2];
    struct uper_c_source_q_t decoded;

    /* Encode. */
    decoded.choice = uper_c_source_q_choice_c257_e;
    decoded.value.c257 = true;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_q_encode(&encoded[0],
                                     sizeof(encoded),
                                     &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0], "\x80\x40", 2);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_q_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.choice, uper_c_source_q_choice_c257_e);
    ASSERT_EQ(decoded.value.c257, true);
}

TEST(uper_c_source_r)
{
    struct data_t {
        int8_t decoded;
        uint8_t encoded[1];
    } datas[] = {
        {
            .decoded = -1,
            .encoded = "\x00"
        },
        {
            .decoded = 0,
            .encoded = "\x80"
        }
    };
    uint8_t encoded[1];
    struct uper_c_source_r_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_r_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_r_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_s)
{
    struct data_t {
        int8_t decoded;
        uint8_t encoded[1];
    } datas[] = {
        {
            .decoded = -2,
            .encoded = "\x00"
        },
        {
            .decoded = 1,
            .encoded = "\xc0"
        }
    };
    uint8_t encoded[1];
    struct uper_c_source_s_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_s_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_s_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_t)
{
    struct data_t {
        int8_t decoded;
        uint8_t encoded[1];
    } datas[] = {
        {
            .decoded = -1,
            .encoded = "\x00"
        },
        {
            .decoded = 2,
            .encoded = "\xc0"
        }
    };
    uint8_t encoded[1];
    struct uper_c_source_t_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_t_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_t_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_u)
{
    struct data_t {
        int8_t decoded;
        uint8_t encoded[1];
    } datas[] = {
        {
            .decoded = -64,
            .encoded = "\x00"
        }
    };
    uint8_t encoded[1];
    struct uper_c_source_u_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_u_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_u_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_v)
{
    struct data_t {
        int8_t decoded;
        uint8_t encoded[1];
    } datas[] = {
        {
            .decoded = -128,
            .encoded = "\x00"
        }
    };
    uint8_t encoded[1];
    struct uper_c_source_v_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_v_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_v_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_w)
{
    struct data_t {
        int16_t decoded;
        uint8_t encoded[2];
    } datas[] = {
        {
            .decoded = -1,
            .encoded = "\x00\x00"
        },
        {
            .decoded = 510,
            .encoded = "\xff\x80"
        }
    };
    uint8_t encoded[2];
    struct uper_c_source_w_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_w_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_w_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_x)
{
    struct data_t {
        int16_t decoded;
        uint8_t encoded[2];
    } datas[] = {
        {
            .decoded = -2,
            .encoded = "\x00\x00"
        },
        {
            .decoded = 510,
            .encoded = "\x80\x00"
        }
    };
    uint8_t encoded[2];
    struct uper_c_source_x_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_x_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_x_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_y)
{
    struct data_t {
        uint16_t decoded;
        uint8_t encoded[2];
    } datas[] = {
        {
            .decoded = 10000,
            .encoded = "\x00\x00"
        },
        {
            .decoded = 10512,
            .encoded = "\x80\x00"
        }
    };
    uint8_t encoded[2];
    struct uper_c_source_y_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_y_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_y_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_z_decode_error_out_of_data)
{
    uint8_t encoded[1];
    struct uper_c_source_z_t decoded;

    ASSERT_EQ(uper_c_source_z_decode(&decoded,
                                     &encoded[0],
                                     0), -EOUTOFDATA);
}

TEST(uper_c_source_ab)
{
    uint8_t encoded[2];
    struct uper_c_source_ab_t decoded;

    /* Encode. */
    decoded.a = 0;
    decoded.b = 10300;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_ab_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\xa5\x80",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_ab_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, 0);
    ASSERT_EQ(decoded.b, 10300);
}

TEST(uper_c_source_ae)
{
    uint8_t encoded[1];
    struct uper_c_source_ae_t decoded;

    /* Encode. */
    decoded.is_a_present = true;
    decoded.a = false;
    decoded.b = true;
    decoded.c = false;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_ae_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x40",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_ae_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, false);
    ASSERT_EQ(decoded.b, true);
    ASSERT_EQ(decoded.c, false);
}

TEST(uper_c_source_af)
{
    uint8_t encoded[24];
    uint8_t encoded2[24] = "\xc4\x7f\xc1\x30\x10\x11\x10\x00\x44\x80\x44\xc0"
        "\x45\x00\x45\x40\x45\x80\x45\xc0\x46\x00\x46\x40";
    struct uper_c_source_af_t decoded;

    /* Encode. */
    decoded.a = true;
    decoded.b.c = true;
    decoded.b.d = 17;
    decoded.b.is_d_addition_present = true;
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
    ASSERT_TRUE(uper_c_source_af_encode(&encoded[0],
                                        sizeof(encoded),
                                        &decoded) < 0);

    // Decode.
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_TRUE(uper_c_source_af_decode(&decoded,
                                        &encoded2[0],
                                        sizeof(encoded2)) < 0);
}

TEST(uper_c_source_al)
{
    struct data_t {
        int16_t decoded;
        uint8_t encoded[2];
    } datas[] = {
        {
            .decoded = -129,
            .encoded = "\x00\x00"
        },
        {
            .decoded = 127,
            .encoded = "\x80\x00"
        }
    };
    uint8_t encoded[2];
    struct uper_c_source_al_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_al_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_al_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_am)
{
    struct data_t {
        int16_t decoded;
        uint8_t encoded[1];
    } datas[] = {
        {
            .decoded = -2,
            .encoded = "\x00"
        },
        {
            .decoded = 128,
            .encoded = "\x82"
        }
    };
    uint8_t encoded[1];
    struct uper_c_source_am_t decoded;
    unsigned int i;

    for (i = 0; i < membersof(datas); i++) {
        /* Encode. */
        decoded.value = datas[i].decoded;

        memset(&encoded[0], 0, sizeof(encoded));
        ASSERT_EQ(uper_c_source_am_encode(&encoded[0],
                                         sizeof(encoded),
                                         &decoded), sizeof(encoded));
        ASSERT_MEMORY_EQ(&encoded[0],
                         &datas[i].encoded[0],
                         sizeof(encoded));

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        ASSERT_EQ(uper_c_source_am_decode(&decoded,
                                         &encoded[0],
                                         sizeof(encoded)), sizeof(encoded));

        ASSERT_EQ(decoded.value, datas[i].decoded);
    }
}

TEST(uper_c_source_ao)
{
    uint8_t encoded[17];
    struct uper_c_source_ao_t decoded;

    /* Encode. */
    decoded.a = UPER_C_SOURCE_AO_A_C;
    decoded.b = UPER_C_SOURCE_AO_B_A;
    decoded.c = 0x5;
    decoded.d = UPER_C_SOURCE_AO_D_B;
    decoded.e = UPER_C_SOURCE_AO_E_C;

    memset(&encoded[0], 0, sizeof(encoded));
    ASSERT_EQ(uper_c_source_ao_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded), sizeof(encoded));
    ASSERT_MEMORY_EQ(&encoded[0],
                     "\x01\x80\x00\x00\x52\x00\x00\x00\x00\x00\x00\x00\x00"
                     "\x00\x00\x00\x10",
                     sizeof(encoded));

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_ao_decode(&decoded,
                                     &encoded[0],
                                     sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.a, UPER_C_SOURCE_AO_A_C);
    ASSERT_EQ(decoded.b, UPER_C_SOURCE_AO_B_A);
    ASSERT_EQ(decoded.c, 0x5);
    ASSERT_EQ(decoded.d, UPER_C_SOURCE_AO_D_B);
    ASSERT_EQ(decoded.e, UPER_C_SOURCE_AO_E_C);
}

TEST(uper_c_source_ap)
{
    uint8_t encoded[2] = "\x88\x20";
    struct uper_c_source_ap_t decoded;

    decoded.b.a = 16;
    decoded.c.value = uper_c_ref_referenced_enum_b_e;
    decoded.d = 1;

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    ASSERT_EQ(uper_c_source_ap_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)), sizeof(encoded));

    ASSERT_EQ(decoded.b.a, 16);
    ASSERT_EQ(decoded.c.value, uper_c_ref_referenced_enum_b_e);
}