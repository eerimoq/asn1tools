#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <unistd.h>
#include <stdlib.h>

#include "PDU.h"

static void *alloc(size_t size)
{
    void *buf_p;

    buf_p = calloc(1, size);
    assert(buf_p != NULL);

    return (buf_p);
}

int main(int argc, const char *argv[])
{
    int i;
    int res;
    asn_enc_rval_t encrv;
    asn_dec_rval_t decrv;
    uint8_t encoded[40];
    PDU_t *decoded_p;
    B_t *b_p;
    D_t *d_p;

    decoded_p = alloc(sizeof(*decoded_p));
    decoded_p->a = 12345678;
    decoded_p->b.present = PDU__b_PR_a;

    /* First element. */
    b_p = alloc(sizeof(*b_p));
    b_p->present = B_PR_a;
    b_p->choice.a.a = alloc(sizeof(*b_p->choice.a.a));
    b_p->choice.a.a->c = 0;
    b_p->choice.a.b = 4294967295;
    b_p->choice.a.c.present = C__c_PR_a;

    d_p = alloc(sizeof(*d_p));
    res = OCTET_STRING_fromBuf(d_p, "\x00\x01\x02", 3);
    assert(res == 0);
    res = ASN_SEQUENCE_ADD(&b_p->choice.a.c.choice.a, d_p);
    assert(res == 0);

    d_p = alloc(sizeof(*d_p));
    res = OCTET_STRING_fromBuf(d_p, "\x00\x01\x02\x03", 4);
    assert(res == 0);
    res = ASN_SEQUENCE_ADD(&b_p->choice.a.c.choice.a, d_p);
    assert(res == 0);

    d_p = alloc(sizeof(*d_p));
    res = OCTET_STRING_fromBuf(d_p, "\x00\x01\x02\x03\x04", 5);
    assert(res == 0);
    res = ASN_SEQUENCE_ADD(&b_p->choice.a.c.choice.a, d_p);
    assert(res == 0);

    b_p->choice.a.d.a = 1;

    res = ASN_SEQUENCE_ADD(&decoded_p->b.choice.a, b_p);
    assert(res == 0);

    /* Second element. */
    b_p = alloc(sizeof(*b_p));
    b_p->present = B_PR_b;
    res = OCTET_STRING_fromBuf(
        &b_p->choice.b,
        "\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a",
        16);
    assert(res == 0);

    res = ASN_SEQUENCE_ADD(&decoded_p->b.choice.a, b_p);
    assert(res == 0);

    for (i = 0; i < atoi(argv[1]); i++) {
        /* Encode the PDU. */
        encrv = uper_encode_to_buffer(&asn_DEF_PDU,
                                      decoded_p,
                                      &encoded[0],
                                      sizeof(encoded));
        assert((encrv.encoded + 7) / 8 == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      "\x80\xbc\x61\x4e\x02\x0f\xff\xff\xff\xf1\x00\x00\x81\x18"
                      "\x00\x08\x10\x1a\x00\x00\x81\x01\x82\x7e\xb4\xb4\xb4\xb4"
                      "\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4",
                      sizeof(encoded)) == 0);

        ASN_STRUCT_FREE(asn_DEF_PDU, decoded_p);

        /* Decode the PDU. */
        decoded_p = NULL;
        decrv = uper_decode_complete(NULL,
                                     &asn_DEF_PDU,
                                     (void **)&decoded_p,
                                     &encoded[0],
                                     sizeof(encoded));
        assert(decrv.consumed == sizeof(encoded));

        /* Just a sanity check that decoding was performed. */
        assert(decoded_p->a == 12345678);
    }

    ASN_STRUCT_FREE(asn_DEF_PDU, decoded_p);

    return (0);
}
