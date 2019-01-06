#include <stdint.h>
#include <stddef.h>

#include "uper.h"

static void test_uper_c_source_a(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_a_t decoded;

    res = uper_c_source_a_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_a_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_b(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_b_t decoded;

    res = uper_c_source_b_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_b_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_c(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_c_t decoded;

    res = uper_c_source_c_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_c_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_d(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_d_t decoded;

    res = uper_c_source_d_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_d_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_e(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_e_t decoded;

    res = uper_c_source_e_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_e_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_f(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_f_t decoded;

    res = uper_c_source_f_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_f_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_g(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_g_t decoded;

    res = uper_c_source_g_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_g_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_h(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_h_t decoded;

    res = uper_c_source_h_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_h_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_i(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_i_t decoded;

    res = uper_c_source_i_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_i_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_j(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_j_t decoded;

    res = uper_c_source_j_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_j_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_k(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_k_t decoded;

    res = uper_c_source_k_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_k_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_l(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_l_t decoded;

    res = uper_c_source_l_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_l_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_m(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_m_t decoded;

    res = uper_c_source_m_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_m_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_n(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_n_t decoded;

    res = uper_c_source_n_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_n_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_o(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_o_t decoded;

    res = uper_c_source_o_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_o_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_p(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_p_t decoded;

    res = uper_c_source_p_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_p_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_q(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_q_t decoded;

    res = uper_c_source_q_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_q_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_r(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_r_t decoded;

    res = uper_c_source_r_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_r_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_s(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_s_t decoded;

    res = uper_c_source_s_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_s_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_t(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_t_t decoded;

    res = uper_c_source_t_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_t_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_u(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_u_t decoded;

    res = uper_c_source_u_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_u_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_v(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_v_t decoded;

    res = uper_c_source_v_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_v_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_w(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_w_t decoded;

    res = uper_c_source_w_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_w_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_x(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_x_t decoded;

    res = uper_c_source_x_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_x_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_y(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_y_t decoded;

    res = uper_c_source_y_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_y_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_z(const uint8_t *encoded_p,
                                 size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_z_t decoded;

    res = uper_c_source_z_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_z_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_ab(const uint8_t *encoded_p,
                                  size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_ab_t decoded;

    res = uper_c_source_ab_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_ab_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

static void test_uper_c_source_ac(const uint8_t *encoded_p,
                                  size_t size)
{
    ssize_t res;
    uint8_t encoded[size];
    struct uper_c_source_ac_t decoded;

    res = uper_c_source_ac_decode(&decoded, encoded_p, size);

    if (res >= 0) {
        uper_c_source_ac_encode(&encoded[0], sizeof(encoded), &decoded);
    }
}

int LLVMFuzzerTestOneInput(const uint8_t *data_p, size_t size)
{
    test_uper_c_source_a(data_p, size);
    test_uper_c_source_b(data_p, size);
    test_uper_c_source_c(data_p, size);
    test_uper_c_source_d(data_p, size);
    test_uper_c_source_e(data_p, size);
    test_uper_c_source_f(data_p, size);
    test_uper_c_source_g(data_p, size);
    test_uper_c_source_h(data_p, size);
    test_uper_c_source_i(data_p, size);
    test_uper_c_source_j(data_p, size);
    test_uper_c_source_k(data_p, size);
    test_uper_c_source_l(data_p, size);
    test_uper_c_source_m(data_p, size);
    test_uper_c_source_n(data_p, size);
    test_uper_c_source_o(data_p, size);
    test_uper_c_source_p(data_p, size);
    test_uper_c_source_q(data_p, size);
    test_uper_c_source_r(data_p, size);
    test_uper_c_source_s(data_p, size);
    test_uper_c_source_t(data_p, size);
    test_uper_c_source_u(data_p, size);
    test_uper_c_source_v(data_p, size);
    test_uper_c_source_w(data_p, size);
    test_uper_c_source_x(data_p, size);
    test_uper_c_source_y(data_p, size);
    test_uper_c_source_z(data_p, size);
    test_uper_c_source_ab(data_p, size);
    test_uper_c_source_ac(data_p, size);

    return (0);
}
