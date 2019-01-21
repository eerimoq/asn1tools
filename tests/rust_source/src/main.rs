mod rust_source;

use rust_source::rust_source::{a, d};

fn test_uper_c_source_a()
{
    let mut encoded = [0; 42];
    let mut a: a::A = Default::default();

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
               a::A {
                   a: -1,
                   b: -2,
                   c: -3,
                   d: -4,
                   e: 1,
                   f: 2,
                   g: 3,
                   h: 4,
                   i: true,
                   j: a::AJ {
                       buf: [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
                   }
               });
}

fn test_uper_c_source_d_all_present()
{
    let mut encoded = [0; 10];
    let mut d: d::D = Default::default();

    // Encode.
    d.length = 1;
    d.elements[0].a.b = d::DElemAB::C(0);
    d.elements[0].a.e.length = 3;
    d.elements[0].g.h = d::DElemGH::J;
    d.elements[0].g.l.length = 2;
    d.elements[0].g.l.buf = [0x54, 0x55];
    d.elements[0].m.n = Some(false);
    d.elements[0].m.o = 2;
    d.elements[0].m.p = Some(d::DElemMP {
        q: d::DElemMPQ {
            buf: [3, 3, 3, 3, 3]
        },
        r: Some(true)
    });

    assert_eq!(d.to_bytes(&mut encoded).unwrap(), encoded.len());
    assert_eq!(encoded[..],
               [
                   0x00, 0xd5, 0x15, 0x7a, 0x40, 0xc0, 0xc0, 0xc0, 0xc0, 0xe0
               ][..]);

    // Decode.
    d = Default::default();

    assert_eq!(d.from_bytes(&encoded).unwrap(), encoded.len());

    assert_eq!(d.length, 1);
    assert_eq!(d.elements[0].a.b, d::DElemAB::C(0));
    assert_eq!(d.elements[0].a.e.length, 3);
    assert_eq!(d.elements[0].g.h, d::DElemGH::J);
    assert_eq!(d.elements[0].g.l.length, 2);
    assert_eq!(d.elements[0].g.l.buf, [0x54, 0x55]);
    assert_eq!(d.elements[0].m.n, Some(false));
    assert_eq!(d.elements[0].m.o, 2);
    assert_eq!(d.elements[0].m.p, Some(d::DElemMP {
        q: d::DElemMPQ {
            buf: [3, 3, 3, 3, 3]
        },
        r: Some(true)
    }));
}

fn main() {
    test_uper_c_source_a();
    test_uper_c_source_d_all_present();
}
