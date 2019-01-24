#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <math.h>

#include "uper.h"
#include "boolean_uper.h"
#include "octet_string_uper.h"

#define membersof(a) (sizeof(a) / (sizeof((a)[0])))

static void test_uper_c_source_a(void)
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
    assert(uper_c_source_a_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x7f\x7f\xfe\x7f\xff\xff\xfd\x7f\xff\xff\xff\xff\xff\xff\xfc"
                  "\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04"
                  "\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82\x80",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_a_decode(&decoded,
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

static void test_uper_c_source_a_encode_error_no_mem(void)
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

    assert(uper_c_source_a_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == -ENOMEM);
}

static void test_uper_c_source_a_decode_error_out_of_data(void)
{
    uint8_t encoded[41] =
        "\x7f\x7f\xfe\x7f\xff\xff\xfd\x7f\xff\xff\xff\xff\xff\xff\xfc"
        "\x01\x00\x02\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x04"
        "\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82\x82";
    struct uper_c_source_a_t decoded;

    assert(uper_c_source_a_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == -EOUTOFDATA);
}

static void test_uper_c_source_b_choice_a(void)
{
    uint8_t encoded[2];
    struct uper_c_source_b_t decoded;

    /* Encode. */
    decoded.choice = uper_c_source_b_choice_a_e;
    decoded.value.a = -10;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_b_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x1d\x80",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_b_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == uper_c_source_b_choice_a_e);
    assert(decoded.value.a == -10);
}

static void test_uper_c_source_b_choice_b(void)
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
    assert(uper_c_source_b_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x5f\xdf\xff\x9f\xff\xff\xff\x5f\xff\xff\xff\xff\xff\xff\xff"
                  "\x00\x40\x00\x80\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x01"
                  "\x20\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_b_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == uper_c_source_b_choice_b_e);
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

static void test_uper_c_source_b_decode_error_bad_choice(void)
{
    uint8_t encoded[2] = "\xdd\x80";
    struct uper_c_source_b_t decoded;

    assert(uper_c_source_b_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == -EBADCHOICE);
}

static void test_uper_c_source_c_empty(void)
{
    uint8_t encoded[1];
    struct uper_c_source_c_t decoded;

    /* Encode. */
    decoded.length = 0;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_c_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x00",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_c_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 0);
}

static void test_uper_c_source_c_2_elements(void)
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
    assert(uper_c_source_c_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x87\x52\x34",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_c_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 2);
    assert(decoded.elements[0].choice == uper_c_source_b_choice_a_e);
    assert(decoded.elements[0].value.a == -11);
    assert(decoded.elements[1].choice == uper_c_source_b_choice_a_e);
    assert(decoded.elements[1].value.a == 13);
}

static void test_uper_c_source_c_decode_error_bad_length(void)
{
    uint8_t encoded[4] = "\xc7\x52\x34\x00";
    struct uper_c_source_c_t decoded;

    assert(uper_c_source_c_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == -EBADLENGTH);
}

static void test_uper_c_source_d_all_present(void)
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

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_d_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x00\xd5\x15\x7a\x40\xc0\xc0\xc0\xc0\xe0",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_d_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 1);
    assert(decoded.elements[0].a.b.choice == uper_c_source_d_a_b_choice_c_e);
    assert(decoded.elements[0].a.b.value.c == 0);
    assert(decoded.elements[0].a.e.length == 3);
    assert(decoded.elements[0].g.h == uper_c_source_d_g_h_j_e);
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

static void test_uper_c_source_d_some_missing(void)
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

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_d_encode(&encoded[0],
                                 sizeof(encoded),
                                 &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x09\x15\x08\x0c\x0c\x0c\x0c\x0c",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_d_decode(&decoded,
                                 &encoded[0],
                                 sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 1);
    assert(decoded.elements[0].a.b.choice == uper_c_source_d_a_b_choice_d_e);
    assert(decoded.elements[0].a.b.value.d == false);
    assert(decoded.elements[0].a.e.length == 3);
    assert(decoded.elements[0].g.h == uper_c_source_d_g_h_k_e);
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

static void test_uper_c_source_d_decode_error_bad_enum(void)
{
    uint8_t encoded[10] = "\x01\xd5\x15\x7a\x40\xc0\xc0\xc0\xc0\xe0";
    struct uper_c_source_d_t decoded;

    assert(uper_c_source_d_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == -EBADENUM);
}

static void test_uper_c_source_e(void)
{
    uint8_t encoded[1];
    struct uper_c_source_e_t decoded;

    /* Encode. */
    decoded.a.choice = uper_c_source_e_a_choice_b_e;
    decoded.a.value.b.choice = uper_c_source_e_a_b_choice_c_e;
    decoded.a.value.b.value.c = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_e_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x80",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_e_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.a.choice == uper_c_source_e_a_choice_b_e);
    assert(decoded.a.value.b.choice == uper_c_source_e_a_b_choice_c_e);
    assert(decoded.a.value.b.value.c == true);
}

static void test_uper_c_source_f(void)
{
    uint8_t encoded[1];
    struct uper_c_source_f_t decoded;

    /* Encode. */
    decoded.length = 2;
    decoded.elements[0].elements[0] = false;
    decoded.elements[1].elements[0] = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_f_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\xa0",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_f_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.length == 2);
    assert(decoded.elements[0].elements[0] == false);
    assert(decoded.elements[1].elements[0] == true);
}

static void test_uper_c_source_g(void)
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
    assert(uper_c_source_g_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\x80\xe0",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_g_decode(&decoded,
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

static void test_uper_c_source_h(void)
{
    uint8_t encoded[1];
    struct uper_c_source_h_t decoded;

    /* Encode. */
    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_h_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_h_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == 0);
}

static void test_uper_c_source_q_c256(void)
{
    uint8_t encoded[2];
    struct uper_c_source_q_t decoded;

    /* Encode. */
    decoded.choice = uper_c_source_q_choice_c256_e;
    decoded.value.c256 = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_q_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0], "\x7f\xc0", 2) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_q_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == uper_c_source_q_choice_c256_e);
    assert(decoded.value.c256 == true);
}

static void test_uper_c_source_q_c257(void)
{
    uint8_t encoded[2];
    struct uper_c_source_q_t decoded;

    /* Encode. */
    decoded.choice = uper_c_source_q_choice_c257_e;
    decoded.value.c257 = true;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_q_encode(&encoded[0],
                                  sizeof(encoded),
                                  &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0], "\x80\x40", 2) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_q_decode(&decoded,
                                  &encoded[0],
                                  sizeof(encoded)) == sizeof(encoded));

    assert(decoded.choice == uper_c_source_q_choice_c257_e);
    assert(decoded.value.c257 == true);
}

static void test_uper_c_source_r(void)
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
        assert(uper_c_source_r_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(uper_c_source_r_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_uper_c_source_s(void)
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
        assert(uper_c_source_s_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(uper_c_source_s_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_uper_c_source_t(void)
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
        assert(uper_c_source_t_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(uper_c_source_t_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_uper_c_source_u(void)
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
        assert(uper_c_source_u_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(uper_c_source_u_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_uper_c_source_v(void)
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
        assert(uper_c_source_v_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(uper_c_source_v_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_uper_c_source_w(void)
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
        assert(uper_c_source_w_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(uper_c_source_w_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_uper_c_source_x(void)
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
        assert(uper_c_source_x_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(uper_c_source_x_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_uper_c_source_y(void)
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
        assert(uper_c_source_y_encode(&encoded[0],
                                      sizeof(encoded),
                                      &decoded) == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      &datas[i].encoded[0],
                      sizeof(encoded)) == 0);

        /* Decode. */
        memset(&decoded, 0, sizeof(decoded));
        assert(uper_c_source_y_decode(&decoded,
                                      &encoded[0],
                                      sizeof(encoded)) == sizeof(encoded));

        assert(decoded.value == datas[i].decoded);
    }
}

static void test_uper_c_source_z_decode_error_out_of_data(void)
{
    uint8_t encoded[1];
    struct uper_c_source_z_t decoded;

    assert(uper_c_source_z_decode(&decoded,
                                  &encoded[0],
                                  0) == -EOUTOFDATA);
}

static void test_uper_c_source_ab(void)
{
    uint8_t encoded[2];
    struct uper_c_source_ab_t decoded;

    /* Encode. */
    decoded.a = 0;
    decoded.b = 10300;

    memset(&encoded[0], 0, sizeof(encoded));
    assert(uper_c_source_ab_encode(&encoded[0],
                                   sizeof(encoded),
                                   &decoded) == sizeof(encoded));
    assert(memcmp(&encoded[0],
                  "\xa5\x80",
                  sizeof(encoded)) == 0);

    /* Decode. */
    memset(&decoded, 0, sizeof(decoded));
    assert(uper_c_source_ab_decode(&decoded,
                                   &encoded[0],
                                   sizeof(encoded)) == sizeof(encoded));

    assert(decoded.a == 0);
    assert(decoded.b == 10300);
}

int main(void)
{
    test_uper_c_source_a();
    test_uper_c_source_a_encode_error_no_mem();
    test_uper_c_source_a_decode_error_out_of_data();

    test_uper_c_source_b_choice_a();
    test_uper_c_source_b_choice_b();
    test_uper_c_source_b_decode_error_bad_choice();

    test_uper_c_source_c_empty();
    test_uper_c_source_c_2_elements();
    test_uper_c_source_c_decode_error_bad_length();

    test_uper_c_source_d_all_present();
    test_uper_c_source_d_some_missing();
    test_uper_c_source_d_decode_error_bad_enum();

    test_uper_c_source_e();
    test_uper_c_source_f();
    test_uper_c_source_g();
    test_uper_c_source_h();
    test_uper_c_source_q_c256();
    test_uper_c_source_q_c257();
    test_uper_c_source_r();
    test_uper_c_source_s();
    test_uper_c_source_t();
    test_uper_c_source_u();
    test_uper_c_source_v();
    test_uper_c_source_w();
    test_uper_c_source_x();
    test_uper_c_source_y();

    test_uper_c_source_z_decode_error_out_of_data();

    test_uper_c_source_ab();

    return (0);
}
