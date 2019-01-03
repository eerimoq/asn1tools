#include <assert.h>
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

#include "uper.h"

int main(int argc, const char *argv[])
{
    int i;
    int res;
    uint8_t encoded[40];
    struct uper_my_protocol_pdu_t decoded;

    decoded.a = 12345678;
    decoded.b.choice = uper_my_protocol_pdu_b_choice_a_e;
    decoded.b.value.a.length = 2;

    /* First element. */
    decoded.b.value.a.elements[0].choice = uper_my_protocol_b_choice_a_e;
    decoded.b.value.a.elements[0].value.a.is_a_present = true;
    decoded.b.value.a.elements[0].value.a.a.a.length = 0;
    decoded.b.value.a.elements[0].value.a.a.is_b_present = false;
    decoded.b.value.a.elements[0].value.a.a.c = 0;
    decoded.b.value.a.elements[0].value.a.b = 4294967295;
    decoded.b.value.a.elements[0].value.a.c.choice = uper_my_protocol_c_c_choice_a_e;
    decoded.b.value.a.elements[0].value.a.c.value.a.elements[0].length = 3;
    memcpy(&decoded.b.value.a.elements[0].value.a.c.value.a.elements[0].buf[0],
           "\x00\x01\x02",
           3);
    decoded.b.value.a.elements[0].value.a.c.value.a.elements[1].length = 4;
    memcpy(&decoded.b.value.a.elements[0].value.a.c.value.a.elements[1].buf[0],
           "\x00\x01\x02\x03",
           4);
    decoded.b.value.a.elements[0].value.a.c.value.a.elements[2].length = 5;
    memcpy(&decoded.b.value.a.elements[0].value.a.c.value.a.elements[2].buf[0],
           "\x00\x01\x02\x03\x04",
           5);
    decoded.b.value.a.elements[0].value.a.d.a = true;

    /* Second element. */
    decoded.b.value.a.elements[1].choice = uper_my_protocol_b_choice_b_e;
    decoded.b.value.a.elements[1].value.b.length = 16;
    memcpy(&decoded.b.value.a.elements[1].value.b.buf[0],
           "\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a",
           16);

    for (i = 0; i < atoi(argv[1]); i++) {
        /* Encode the PDU. */
        res = uper_my_protocol_pdu_encode(&encoded[0],
                                          sizeof(encoded),
                                          &decoded);
        assert(res == sizeof(encoded));
        assert(memcmp(&encoded[0],
                      "\x80\xbc\x61\x4e\x02\x0f\xff\xff\xff\xf1\x00\x00\x81\x18"
                      "\x00\x08\x10\x1a\x00\x00\x81\x01\x82\x7e\xb4\xb4\xb4\xb4"
                      "\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4",
                      sizeof(encoded)) == 0);

        /* Decode the PDU. */
        memset(&decoded, 0, sizeof(decoded));
        res = uper_my_protocol_pdu_decode(&decoded,
                                          &encoded[0],
                                          sizeof(encoded));
        assert(res == sizeof(encoded));

        /* Just a sanity check that decoding was performed. */
        assert(decoded.a == 12345678);
    }

    return (0);
}
