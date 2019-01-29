use rust_source::Error;
use rust_source::{RustSourceA, RustSourceAJ};
use rust_source::RustSourceB;
use rust_source::{RustSourceD, RustSourceDElemAB, RustSourceDElemGH};
use rust_source::{RustSourceE, RustSourceEA, RustSourceEAB};

#[test]
fn test_uper_c_source_a() {
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

    assert_eq!(a.encode(&mut encoded).unwrap(), encoded.len());
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

    assert_eq!(a.decode(&encoded).unwrap(), encoded.len());
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

#[test]
fn test_uper_c_source_a_encode_error_no_mem() {
    let mut encoded = [0; 41];
    let mut a: RustSourceA = Default::default();

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

    assert_eq!(a.encode(&mut encoded), Err(Error::OutOfMemory));
}

#[test]
fn test_uper_c_source_a_decode_error_out_of_data() {
    let encoded = [
        0x7f, 0x7f, 0xfe, 0x7f, 0xff, 0xff, 0xfd, 0x7f, 0xff, 0xff,
        0xff, 0xff, 0xff, 0xff, 0xfc, 0x01, 0x00, 0x02, 0x00, 0x00,
        0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04,
        0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82, 0x82,
        0x82
    ];
    let mut a: RustSourceA = Default::default();

    assert_eq!(a.decode(&encoded), Err(Error::OutOfData));
}

#[test]
fn test_uper_c_source_b_choice_a() {
    let mut encoded = [0; 2];
    let mut b;

    // Encode.
    b = RustSourceB::A(-10);

    assert_eq!(b.encode(&mut encoded).unwrap(), encoded.len());
    assert_eq!(encoded[..],
               [
                   0x1d, 0x80
               ][..]);

    // Decode.
    b = Default::default();

    assert_eq!(b.decode(&encoded).unwrap(), encoded.len());
    assert_eq!(b, RustSourceB::A(-10));
}

#[test]
fn test_uper_c_source_b_choice_b() {
    let mut encoded = [0; 42];
    let mut b;
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
    b = RustSourceB::B(a);

    assert_eq!(b.encode(&mut encoded).unwrap(), encoded.len());
    assert_eq!(encoded[..],
               [
                   0x5f, 0xdf, 0xff, 0x9f, 0xff, 0xff, 0xff, 0x5f, 0xff, 0xff,
                   0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x40, 0x00, 0x80, 0x00,
                   0x00, 0x00, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
                   0x20, 0xa0, 0xa0, 0xa0, 0xa0, 0xa0, 0xa0, 0xa0, 0xa0, 0xa0,
                   0xa0, 0xa0
               ][..]);

    // Decode.
    b = Default::default();

    assert_eq!(b.decode(&encoded).unwrap(), encoded.len());

    match b {
        RustSourceB::B(value) => {
            assert_eq!(value, a);
        },
        _ => panic!("")
    }
}

#[test]
fn test_uper_c_source_b_decode_error_bad_choice() {
    let encoded = [0xdd, 0x80];
    let mut b: RustSourceB = Default::default();

    assert_eq!(b.decode(&encoded), Err(Error::BadChoice));
}

#[test]
fn test_uper_c_source_d_all_present() {
    let mut encoded = [0; 10];
    let mut d: RustSourceD = Default::default();

    // Encode.
    d.length = 1;
    d.elements[0].a.b = RustSourceDElemAB::C(0);
    d.elements[0].a.e.length = 3;
    d.elements[0].g.h = RustSourceDElemGH::J;
    d.elements[0].g.l.length = 2;
    d.elements[0].g.l.buf = [0x54, 0x55];
    d.elements[0].m.is_n_present = true;
    d.elements[0].m.n = false;
    d.elements[0].m.o = 2;
    d.elements[0].m.is_p_present = true;
    d.elements[0].m.p.q.buf = [3, 3, 3, 3, 3];
    d.elements[0].m.p.is_r_present = true;
    d.elements[0].m.p.r = true;

    assert_eq!(d.encode(&mut encoded).unwrap(), encoded.len());
    assert_eq!(encoded[..],
               [
                   0x00, 0xd5, 0x15, 0x7a, 0x40, 0xc0, 0xc0, 0xc0, 0xc0, 0xe0
               ][..]);

    // Decode.
    d = Default::default();

    assert_eq!(d.decode(&encoded).unwrap(), encoded.len());

    assert_eq!(d.length, 1);
    assert_eq!(d.elements[0].a.b, RustSourceDElemAB::C(0));
    assert_eq!(d.elements[0].a.e.length, 3);
    assert_eq!(d.elements[0].g.h, RustSourceDElemGH::J);
    assert_eq!(d.elements[0].g.l.length, 2);
    assert_eq!(d.elements[0].g.l.buf, [0x54, 0x55]);
    assert_eq!(d.elements[0].m.is_n_present, true);
    assert_eq!(d.elements[0].m.n, false);
    assert_eq!(d.elements[0].m.o, 2);
    assert_eq!(d.elements[0].m.is_p_present, true);
    assert_eq!(d.elements[0].m.p.q.buf, [3, 3, 3, 3, 3]);
    assert_eq!(d.elements[0].m.p.is_r_present, true);
    assert_eq!(d.elements[0].m.p.r, true);
}

#[test]
fn test_uper_c_source_d_some_missing() {
    let mut encoded = [0; 8];
    let mut d: RustSourceD = Default::default();

    // Encode.
    d.length = 1;
    d.elements[0].a.b = RustSourceDElemAB::D(false);
    d.elements[0].a.e.length = 3;
    d.elements[0].g.h = RustSourceDElemGH::K;
    d.elements[0].g.l.length = 1;
    d.elements[0].g.l.buf[0] = 0x54;
    d.elements[0].m.is_n_present = false;
    // Default value 3.
    d.elements[0].m.o = 3;
    d.elements[0].m.is_p_present = true;
    d.elements[0].m.p.q.buf = [3, 3, 3, 3, 3];
    d.elements[0].m.p.is_r_present = false;

    assert_eq!(d.encode(&mut encoded).unwrap(), encoded.len());
    assert_eq!(encoded[..],
               [
                   0x09, 0x15, 0x08, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c
               ][..]);

    // Decode.
    d = Default::default();

    assert_eq!(d.decode(&encoded).unwrap(), encoded.len());

    assert_eq!(d.length, 1);
    assert_eq!(d.elements[0].a.b, RustSourceDElemAB::D(false));
    assert_eq!(d.elements[0].a.e.length, 3);
    assert_eq!(d.elements[0].g.h, RustSourceDElemGH::K);
    assert_eq!(d.elements[0].g.l.length, 1);
    assert_eq!(d.elements[0].g.l.buf[0], 0x54);
    assert_eq!(d.elements[0].m.is_n_present, false);
    assert_eq!(d.elements[0].m.o, 3);
    assert_eq!(d.elements[0].m.is_p_present, true);
    assert_eq!(d.elements[0].m.p.q.buf, [3, 3, 3, 3, 3]);
    assert_eq!(d.elements[0].m.p.is_r_present, false);
}

#[test]
fn test_uper_c_source_d_decode_error_bad_enum() {
    let encoded = [
        0x01, 0xd5, 0x15, 0x7a, 0x40, 0xc0, 0xc0, 0xc0, 0xc0, 0xe0
    ];
    let mut d: RustSourceD = Default::default();

    assert_eq!(d.decode(&encoded), Err(Error::BadEnum));
}

#[test]
fn test_uper_c_source_e() {
    let mut encoded = [0; 1];
    let mut e: RustSourceE = Default::default();

    // Encode.
    e.a = RustSourceEA::B(RustSourceEAB::C(true));

    assert_eq!(e.encode(&mut encoded).unwrap(), encoded.len());
    assert_eq!(encoded[..],
               [
                   0x80
               ][..]);

    // Decode.
    e = Default::default();

    assert_eq!(e.decode(&encoded).unwrap(), encoded.len());

    let RustSourceEA::B(RustSourceEAB::C(value)) = e.a;

    assert_eq!(value, true);
}
