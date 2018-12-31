#include <assert.h>
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

#include "my_protocol.h"

int main()
{
    bool ok;
    int res;
    uint8_t encoded[40];
    PDU decoded;
    BitStream bit_stream ;

    decoded.a = 12345678;
    decoded.b.kind = PDU_b_a_PRESENT;
    decoded.b.u.a.nCount = 2;

    /* First element. */
    decoded.b.u.a.arr[0].kind = B_a_PRESENT;
    decoded.b.u.a.arr[0].u.a.exist.a = 1;
    decoded.b.u.a.arr[0].u.a.a.a.nCount = 0;
    decoded.b.u.a.arr[0].u.a.a.exist.b = 0;
    decoded.b.u.a.arr[0].u.a.a.c = 0;
    decoded.b.u.a.arr[0].u.a.b = 4294967295;
    decoded.b.u.a.arr[0].u.a.c.kind = C_c_a_PRESENT;
    decoded.b.u.a.arr[0].u.a.c.u.a.arr[0].nCount = 3;
    memcpy(&decoded.b.u.a.arr[0].u.a.c.u.a.arr[0].arr[0],
           "\x00\x01\x02",
           3);
    decoded.b.u.a.arr[0].u.a.c.u.a.arr[1].nCount = 4;
    memcpy(&decoded.b.u.a.arr[0].u.a.c.u.a.arr[1].arr[0],
           "\x00\x01\x02\x03",
           4);
    decoded.b.u.a.arr[0].u.a.c.u.a.arr[2].nCount = 5;
    memcpy(&decoded.b.u.a.arr[0].u.a.c.u.a.arr[2].arr[0],
           "\x00\x01\x02\x03\x04",
           5);
    decoded.b.u.a.arr[0].u.a.d.a = true;

    /* Second element. */
    decoded.b.u.a.arr[1].kind = B_b_PRESENT;
    decoded.b.u.a.arr[1].u.b.nCount = 16;
    memcpy(&decoded.b.u.a.arr[1].u.b.arr[0],
           "\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a\x5a",
           16);

    /* Encode the PDU. */
    BitStream_Init(&bit_stream,
                   &encoded[0],
                   sizeof(encoded));

    ok = PDU_Encode(&decoded, &bit_stream, &res, false);
    assert(ok);

    BitStream_GetLength(&bit_stream);
    assert(BitStream_GetLength(&bit_stream) == sizeof(encoded));

    assert(memcmp(&encoded[0],
                  "\x80\xbc\x61\x4e\x02\x0f\xff\xff\xff\xf1\x00\x00\x81\x18"
                  "\x00\x08\x10\x1a\x00\x00\x81\x01\x82\x7e\xb4\xb4\xb4\xb4"
                  "\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4\xb4",
                  sizeof(encoded)) == 0);

    /* Decode the PDU. */
    memset(&decoded, 0, sizeof(decoded));

    BitStream_AttachBuffer(&bit_stream,
                           &encoded[0],
                           sizeof(encoded));

    ok = PDU_Decode(&decoded, &bit_stream, &res);
    assert(ok);

    /* Just a sanity check that decoding was performed. */
    assert(decoded.a == 12345678);

    return (0);
}
