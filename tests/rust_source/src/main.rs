mod rust_source;

use rust_source::{RustSourceA, RustSourceAJ};

fn test_uper_c_source_a()
{
    let mut encoded = [0; 42];
    let mut a: RustSourceA = Default::default();

    // Encode.
    a.a = -1;
    a.b = -2;
    a.c = -3;
    a.d = -4;
    a.e = 1;
    a.f = 2;
    a.g = 3;
    a.h = 4;
    a.i = true;
    a.j.buf = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5];

    assert_eq!(a.to_bytes(&mut encoded).unwrap(), encoded.len());
    assert_eq!(encoded[..],
               [
                   0x7f, 0x7f, 0xfe, 0x7f, 0xff, 0xff, 0xfd, 0x7f, 0xff, 0xff,
                   0xff, 0xff, 0xff, 0xff, 0xfc, 0x01, 0x00, 0x02, 0x00, 0x00,
                   0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04,
                   0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82,
                   0x82, 0x80
               ][..]);

    // Decode.
    a = Default::default();

    assert_eq!(a.from_bytes(&encoded).unwrap(), encoded.len());
    assert_eq!(a,
               RustSourceA {
                   a: -1,
                   b: -2,
                   c: -3,
                   d: -4,
                   e: 1,
                   f: 2,
                   g: 3,
                   h: 4,
                   i: true,
                   j: RustSourceAJ {
                       buf: [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
                   }
               });
}

fn main() {
    test_uper_c_source_a();
}
