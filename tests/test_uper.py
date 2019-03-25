#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools
import sys
from copy import deepcopy
import string
from asn1tools.codecs import restricted_utc_time_to_datetime as ut2dt
from asn1tools.codecs import restricted_generalized_time_to_datetime as gt2dt
import datetime

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')
sys.path.append('tests/files/oma')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from lpp_14_3_0 import EXPECTED as LPP_14_3_0
from x691_a4 import EXPECTED as X691_A4
from ulp import EXPECTED as OMA_ULP


class Asn1ToolsUPerTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_boolean(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "END",
            'uper')

        datas = [
            ('A',                     True, b'\x80'),
            ('A',                    False, b'\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_integer(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "B ::= INTEGER (5..99) "
            "C ::= INTEGER (-10..10) "
            "D ::= INTEGER (5..99, ...) "
            "E ::= INTEGER (1000..1000) "
            "F ::= SEQUENCE { "
            "  a INTEGER (4..4), "
            "  b INTEGER (40..40), "
            "  c INTEGER (400..400) "
            "} "
            "G ::= B (6..7) "
            "H ::= SEQUENCE { "
            "  a G (7..7) "
            "} "
            "I ::= INTEGER (5..99, ..., 101..105) "
            "J ::= SEQUENCE { "
            "    a BOOLEAN, "
            "    b INTEGER (-10000..704000000000000001), "
            "    c BOOLEAN "
            "} "
            "END",
            'uper')

        datas = [
            ('A',                       32768, b'\x03\x00\x80\x00'),
            ('A',                       32767, b'\x02\x7f\xff'),
            ('A',                         256, b'\x02\x01\x00'),
            ('A',                         255, b'\x02\x00\xff'),
            ('A',                         128, b'\x02\x00\x80'),
            ('A',                         127, b'\x01\x7f'),
            ('A',                           1, b'\x01\x01'),
            ('A',                           0, b'\x01\x00'),
            ('A',                          -1, b'\x01\xff'),
            ('A',                        -128, b'\x01\x80'),
            ('A',                        -129, b'\x02\xff\x7f'),
            ('A',                        -256, b'\x02\xff\x00'),
            ('A',                      -32768, b'\x02\x80\x00'),
            ('A',                      -32769, b'\x03\xff\x7f\xff'),
            ('B',                           5, b'\x00'),
            ('B',                           6, b'\x02'),
            ('B',                          99, b'\xbc'),
            ('C',                         -10, b'\x00'),
            ('C',                          -1, b'\x48'),
            ('C',                           0, b'\x50'),
            ('C',                           1, b'\x58'),
            ('C',                          10, b'\xa0'),
            ('D',                          99, b'\x5e'),
            ('E',                        1000, b''),
            ('F', {'a': 4, 'b': 40, 'c': 400}, b''),
            ('G',                           7, b'\x80'),
            ('H',                    {'a': 7}, b''),
            ('I',                         103, b'\x80\xb3\x80'),
            ('J',
             {'a': True, 'b': 0, 'c': True},
             b'\x80\x00\x00\x00\x00\x01\x38\x84')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_real(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= REAL "
            "B ::= SEQUENCE { "
            "    a REAL, "
            "    ... "
            "}"
            "END",
            'uper')

        datas = [
            ('A',                     0.0, b'\x00'),
            ('A',                    -0.0, b'\x00'),
            ('A',            float('inf'), b'\x01\x40'),
            ('A',           float('-inf'), b'\x01\x41'),
            ('A',                     1.0, b'\x03\x80\x00\x01'),
            ('A',
             1.1,
             b'\x09\x80\xcd\x08\xcc\xcc\xcc\xcc\xcc\xcd'),
            ('A',
             1234.5678,
             b'\x09\x80\xd6\x13\x4a\x45\x6d\x5c\xfa\xad'),
            ('A',                       8, b'\x03\x80\x03\x01'),
            ('A',                   0.625, b'\x03\x80\xfd\x05'),
            ('A',
             10000000000000000146306952306748730309700429878646550592786107871697963642511482159104,
             b'\x0a\x81\x00\xe9\x02\x92\xe3\x2a\xc6\x85\x59'),
            ('A',
             0.00000000000000000000000000000000000000000000000000000000000000000000000000000000000001,
             b'\x0a\x81\xfe\xae\x13\xe4\x97\x06\x5c\xd6\x1f'),
            ('B', {'a': 1.0}, b'\x01\xc0\x00\x00\x80'),
            ('B',
             {'a': 1000000000},
             b'\x02\xc0\x04\x8e\xe6\xb2\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_bit_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BIT STRING "
            "B ::= BIT STRING (SIZE (9)) "
            "C ::= BIT STRING (SIZE (5..7)) "
            "D ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b BIT STRING "
            "} "
            "E ::= BIT STRING { "
            "  a (0), "
            "  b (1), "
            "  c (2) "
            "} "
            "F ::= SEQUENCE { "
            "  a BIT STRING, "
            "  b BOOLEAN "
            "} "
            "G ::= BIT STRING { "
            "  a (0), "
            "  b (1), "
            "  c (2) "
            "} (SIZE (2..3))"
            "H ::= BIT STRING { "
            "  a (3) "
            "} "
            "I ::= BIT STRING { "
            "  a (0), "
            "  b (1), "
            "  c (2) "
            "} (SIZE (8..9))"
            "J ::= SEQUENCE { "
            "  a E DEFAULT { b } "
            "} "
            "K ::= SEQUENCE { "
            "  a E DEFAULT {b, c}, "
            "  b E DEFAULT '011'B, "
            "  c E DEFAULT '60'H "
            "} "
            "L ::= SEQUENCE { "
            "  a E DEFAULT { } "
            "} "
            "M ::= SEQUENCE { "
            "  a BIT STRING { a(7) } DEFAULT { a } "
            "} "
            "N ::= SEQUENCE { "
            "  a BIT STRING { a(8) } DEFAULT { a } "
            "} "
            "O ::= SEQUENCE { "
            "  a SEQUENCE { "
            "    a E DEFAULT { a } "
            "  } "
            "} "
            "P ::= SEQUENCE { "
            "  a A DEFAULT '00'B, "
            "  b E DEFAULT '00'B "
            "} "
            "Q ::= SEQUENCE SIZE (0..2) OF BIT STRING (SIZE(1..255)) "
            "R ::= SEQUENCE SIZE (0..2) OF BIT STRING (SIZE(1..256)) "
            "S ::= SEQUENCE SIZE (0..2) OF BIT STRING (SIZE(2..256)) "
            "T ::= SEQUENCE SIZE (0..2) OF BIT STRING (SIZE(2..257)) "
            "U ::= BIT STRING (SIZE (1..160, ...)) "
            "V ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b BIT STRING (SIZE (1..160, ...)) "
            "} "
            "END",
            'uper')

        datas = [
            ('A',              (b'', 0), b'\x00'),
            ('A',          (b'\x00', 1), b'\x01\x00'),
            ('A',          (b'\x40', 4), b'\x04\x40'),
            ('A',      (b'\x00\x00', 9), b'\x09\x00\x00'),
            ('A',
             (299 * b'\x55' + b'\x54', 2399),
             b'\x89\x5f' + 299 * b'\x55' + b'\x54'),
            ('B',      (b'\x12\x80', 9), b'\x12\x80'),
            ('C',          (b'\x34', 6), b'\x4d'),
            ('D',
             {'a': True, 'b': (b'\x40', 4)},
             b'\x82\x20'),
            ('E',          (b'\x80', 1), b'\x01\x80'),
            ('E',          (b'\xe0', 3), b'\x03\xe0'),
            ('E',          (b'\x01', 8), b'\x08\x01'),
            ('F',
             {'a': (b'\x80', 2), 'b': True},
             b'\x02\xa0'),
            ('F',
             {'a': (b'', 0), 'b': True},
             b'\x00\x80'),
            ('G',          (b'\x80', 2), b'\x40'),
            ('G',          (b'\x40', 2), b'\x20'),
            ('G',          (b'\x20', 3), b'\x90'),
            ('G',          (b'\x00', 2), b'\x00'),
            ('J',       {'a': (b'', 0)}, b'\x80\x00'),
            ('J',   {'a': (b'\x20', 3)}, b'\x81\x90'),
            ('J',   {'a': (b'\x40', 2)}, b'\x00'),
            ('K',
             {'a': (b'\x40', 2), 'b': (b'\x40', 2), 'c': (b'\x40', 2)},
             b'\xe0\x48\x12\x04\x80'),
            ('K',
             {'a': (b'\x60', 3), 'b': (b'\x60', 3), 'c': (b'\x60', 3)},
             b'\x00'),
            ('L',   {'a': (b'', 0)}, b'\x00'),
            ('M',   {'a': (b'\x01', 8)}, b'\x00'),
            ('N',   {'a': (b'\x00\x80', 9)}, b'\x00'),
            ('O',   {'a': {'a': (b'\x80', 1)}}, b'\x00'),
            ('O',   {'a': {'a': (b'\x40', 2)}}, b'\x81\x20'),
            ('P',
             {'a': (b'\x00', 2), 'b': (b'\x00', 2)},
             b'\x00'),
            ('Q',                   [(b'\x40', 2)], b'\x40\x50'),
            ('R',                   [(b'\x40', 2)], b'\x40\x50'),
            ('S',                   [(b'\x40', 2)], b'\x40\x10'),
            ('T',                   [(b'\x40', 2)], b'\x40\x10'),
            ('U',                     (b'\x80', 1), b'\x00\x40'),
            ('V',   {'a': True, 'b': (b'\xe0', 3)}, b'\x80\xb8')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Trailing zero bits should be stripped when encoding named
        # bit list. Default value is not encoded, but part of
        # decoded. Also ignore dangling bits.
        datas = [
            ('E',          (b'\x80', 2), b'\x01\x80', (b'\x80', 1)),
            ('E',          (b'\x40', 3), b'\x02\x40', (b'\x40', 2)),
            ('E',          (b'\x00', 3), b'\x00',     (b'', 0)),
            ('E',          (b'\x00', 8), b'\x00',     (b'', 0)),
            ('G',          (b'\x40', 3), b'\x20',     (b'\x40', 2)),
            ('H',          (b'\x00', 1), b'\x00',     (b'', 0)),
            ('I',      (b'\x00\x00', 9), b'\x00\x00', (b'\x00', 8)),
            ('J',                    {}, b'\x00',     {'a': (b'\x40', 2)}),
            ('J',   {'a': (b'\x40', 3)}, b'\x00',     {'a': (b'\x40', 2)}),
            ('J',   {'a': (b'\x60', 2)}, b'\x00',     {'a': (b'\x40', 2)}),
            ('K',
             {},
             b'\x00',
             {'a': (b'\x60', 3), 'b': (b'\x60', 3), 'c': (b'\x60', 3)}),
            ('A',      (b'\x7f\xff', 1), b'\x01\x00', (b'\x00', 1)),
            ('P',
             {'a': (b'\x00', 3), 'b': (b'\x00', 3)},
             b'\x80\xc0',
             {'a': (b'\x00', 3), 'b': (b'\x00', 2)})
        ]

        for type_name, decoded_1, encoded, decoded_2 in datas:
            self.assertEqual(foo.encode(type_name, decoded_1), encoded)
            self.assertEqual(foo.decode(type_name, encoded), decoded_2)

    def test_octet_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OCTET STRING "
            "B ::= OCTET STRING (SIZE (2)) "
            "C ::= OCTET STRING (SIZE (3)) "
            "D ::= OCTET STRING (SIZE (3..7)) "
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b OCTET STRING "
            "} "
            "F ::= OCTET STRING (SIZE (1..MAX)) "
            "G ::= OCTET STRING (SIZE (65535)) "
            "H ::= OCTET STRING (SIZE (65536)) "
            "I ::= OCTET STRING (SIZE (MIN..5)) "
            "J ::= OCTET STRING (SIZE (MIN..MAX)) "
            "K ::= OCTET STRING (SIZE (1..2, ...)) "
            "M ::= SEQUENCE SIZE (0..2) OF OCTET STRING (SIZE(1..256)) "
            "N ::= SEQUENCE SIZE (0..2) OF OCTET STRING (SIZE(1..257)) "
            "END",
            'uper')

        datas = [
            ('A',                   b'\x00', b'\x01\x00'),
            ('A',             500 * b'\x00', b'\x81\xf4' + 500 * b'\x00'),
            ('B',               b'\xab\xcd', b'\xab\xcd'),
            ('C',           b'\xab\xcd\xef', b'\xab\xcd\xef'),
            ('D',       b'\x89\xab\xcd\xef', b'\x31\x35\x79\xbd\xe0'),
            ('E', {'a': True, 'b': b'\x00'}, b'\x80\x80\x00'),
            ('F',                   b'\x12', b'\x01\x12'),
            ('G',     32767 * b'\x01\x02' + b'\x01', 32767 * b'\x01\x02' + b'\x01'),
            ('H',
             32768 * b'\x01\x02',
             b'\xc4' + 32768 * b'\x01\x02'
             + b'\x00'),
            ('I',                       b'', b'\x00'),
            ('J',                       b'', b'\x00'),
            ('K',               b'\x12\x34', b'\x44\x8d\x00'),
            ('K',           b'\x12\x34\x56', b'\x81\x89\x1a\x2b\x00'),
            ('M',             [b'\x12\x34'], b'\x40\x44\x8d\x00'),
            ('M',     [b'\x12\x34\x56\x78'], b'\x40\xc4\x8d\x15\x9e\x00'),
            ('N',             [b'\x12\x34'], b'\x40\x22\x46\x80'),
            ('N',     [b'\x12\x34\x56\x78'], b'\x40\x62\x46\x8a\xcf\x00'),
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_object_identifier(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OBJECT IDENTIFIER "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b OBJECT IDENTIFIER "
            "} "
            "END",
            'uper')

        datas = [
            ('A',                   '1.2', b'\x01\x2a'),
            ('A',              '1.2.3321', b'\x03\x2a\x99\x79'),
            ('B', {'a': True, 'b': '1.2'}, b'\x80\x95\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_external(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= EXTERNAL "
            "END",
            'uper')

        datas = [
            ('A',    {'encoding': ('octet-aligned', b'\x12')}, b'\x08\x08\x90')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_enumerated(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= ENUMERATED { one(1) } "
            "B ::= ENUMERATED { zero(0), one(1), ... } "
            "C ::= ENUMERATED { one(1), four(4), two(2), ..., six(6), nine(9) } "
            "D ::= ENUMERATED { a, ..., "
            "aa, ab, ac, ad, ae, af, ag, ah, ai, aj, ak, al, am, an, ao, ap, "
            "aq, ar, as, at, au, av, aw, ax, ay, az, ba, bb, bc, bd, be, bf, "
            "bg, bh, bi, bj, bk, bl, bm, bn, bo, bp, bq, br, bs, bt, bu, bv, "
            "bw, bx, by, bz, ca, cb, cc, cd, ce, cf, cg, ch, ci, cj, ck, cl, "
            "cm, cn, co, cp, cq, cr, cs, ct, cu, cv, cw, cx, cy, cz, da, db, "
            "dc, dd, de, df, dg, dh, di, dj, dk, dl, dm, dn, do, dp, dq, dr, "
            "ds, dt, du, dv, dw, dx, dy, dz, ea, eb, ec, ed, ee, ef, eg, eh, "
            "ei, ej, ek, el, em, en, eo, ep, eq, er, es, et, eu, ev, ew, ex, "
            "ey, ez, fa, fb, fc, fd, fe, ff, fg, fh, fi, fj, fk, fl, fm, fn, "
            "fo, fp, fq, fr, fs, ft, fu, fv, fw, fx, fy, fz, ga, gb, gc, gd, "
            "ge, gf, gg, gh, gi, gj, gk, gl, gm, gn, go, gp, gq, gr, gs, gt, "
            "gu, gv, gw, gx, gy, gz, ha, hb, hc, hd, he, hf, hg, hh, hi, hj, "
            "hk, hl, hm, hn, ho, hp, hq, hr, hs, ht, hu, hv, hw, hx, hy, hz, "
            "ia, ib, ic, id, ie, if, ig, ih, ii, ij, ik, il, im, in, io, ip, "
            "iq, ir, is, it, iu, iv, iw, ix, iy, iz, ja, jb, jc, jd, je, jf, "
            "jg, jh, ji, jj, jk, jl, jm, jn, jo, jp, jq, jr, js, jt, ju, jv, "
            "jw, jx, jy, jz } "
            "E ::= SEQUENCE {"
            "  a ENUMERATED { zero(0), one(1) } DEFAULT one"
            "}"
            "END",
            'uper')

        datas = [
            ('A',         'one', b''),
            ('B',        'zero', b'\x00'),
            ('B',         'one', b'\x40'),
            ('C',         'one', b'\x00'),
            ('C',         'two', b'\x20'),
            ('C',        'four', b'\x40'),
            ('C',         'six', b'\x80'),
            ('C',        'nine', b'\x81'),
            ('D',          'aa', b'\x80'),
            ('D',          'cl', b'\xbf'),
            ('D',          'cm', b'\xc0\x50\x00'),
            ('D',          'jv', b'\xc0\x7f\xc0'),
            ('D',          'jw', b'\xc0\x80\x40\x00'),
            ('D',          'jz', b'\xc0\x80\x40\xc0'),
            ('E', {'a': 'zero'}, b'\x80'),
            ('E',  {'a': 'one'}, b'\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Default value is not encoded, but part of decoded.
        datas = [
            ('E', {}, b'\x00', {'a': 'one'})
        ]

        for type_name, decoded_1, encoded_1, decoded_2 in datas:
            self.assertEqual(foo.encode(type_name, decoded_1), encoded_1)
            self.assertEqual(foo.decode(type_name, encoded_1), decoded_2)

    def test_sequence(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE {} "
            "B ::= SEQUENCE { "
            "  a INTEGER DEFAULT 0 "
            "} "
            "C ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ... "
            "} "
            "D ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]] "
            "} "
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  ... "
            "} "
            "F ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  ..., "
            "  c BOOLEAN "
            "} "
            "G ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  [[ "
            "  c BOOLEAN "
            "  ]], "
            "  ..., "
            "  d BOOLEAN "
            "} "
            "H ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  ... "
            "} "
            "I ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN "
            "} "
            "J ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN OPTIONAL "
            "} "
            "K ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN, "
            "  c BOOLEAN "
            "} "
            "L ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN, "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "M ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b SEQUENCE { "
            "    a INTEGER"
            "  } OPTIONAL, "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "N ::= SEQUENCE { "
            "  a BOOLEAN DEFAULT TRUE "
            "} "
            "O ::= SEQUENCE { "
            "  ..., "
            "  a BOOLEAN DEFAULT TRUE "
            "} "
            "P ::= SEQUENCE { "
            "  ..., "
            "  [[ "
            "  a BOOLEAN, "
            "  b BOOLEAN DEFAULT TRUE "
            "  ]] "
            "} "
            "Q ::= SEQUENCE { "
            "  a C, "
            "  b INTEGER "
            "} "
            "R ::= SEQUENCE { "
            "  a D, "
            "  b INTEGER "
            "} "
            "S ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b SEQUENCE { "
            "    a BOOLEAN, "
            "    b BOOLEAN OPTIONAL, "
            "    ... "
            "  } "
            "} "
            "T ::= SEQUENCE { "
            "  a SEQUENCE OF T OPTIONAL "
            "} "
            "U ::= SEQUENCE { "
            "  ..., "
            "  a SEQUENCE { "
            "    a INTEGER "
            "  } "
            "} "
            "V ::= SEQUENCE { "
            "  ..., "
            "  a BOOLEAN OPTIONAL, "
            "  b BOOLEAN OPTIONAL, "
            "  c BOOLEAN OPTIONAL "
            "} "
            "W ::= SEQUENCE { "
            "  ..., "
            "  a1 BOOLEAN, "
            "  a2 BOOLEAN, "
            "  a3 BOOLEAN, "
            "  a4 BOOLEAN, "
            "  a5 BOOLEAN, "
            "  a6 BOOLEAN, "
            "  a7 BOOLEAN, "
            "  a8 BOOLEAN, "
            "  a9 BOOLEAN, "
            "  a10 BOOLEAN, "
            "  a11 BOOLEAN, "
            "  a12 BOOLEAN, "
            "  a13 BOOLEAN, "
            "  a14 BOOLEAN, "
            "  a15 BOOLEAN, "
            "  a16 BOOLEAN, "
            "  a17 BOOLEAN, "
            "  a18 BOOLEAN, "
            "  a19 BOOLEAN, "
            "  a20 BOOLEAN, "
            "  a21 BOOLEAN, "
            "  a22 BOOLEAN, "
            "  a23 BOOLEAN, "
            "  a24 BOOLEAN, "
            "  a25 BOOLEAN, "
            "  a26 BOOLEAN, "
            "  a27 BOOLEAN, "
            "  a28 BOOLEAN, "
            "  a29 BOOLEAN, "
            "  a30 BOOLEAN, "
            "  a31 BOOLEAN, "
            "  a32 BOOLEAN, "
            "  a33 BOOLEAN, "
            "  a34 BOOLEAN, "
            "  a35 BOOLEAN, "
            "  a36 BOOLEAN, "
            "  a37 BOOLEAN, "
            "  a38 BOOLEAN, "
            "  a39 BOOLEAN, "
            "  a40 BOOLEAN, "
            "  a41 BOOLEAN, "
            "  a42 BOOLEAN, "
            "  a43 BOOLEAN, "
            "  a44 BOOLEAN, "
            "  a45 BOOLEAN, "
            "  a46 BOOLEAN, "
            "  a47 BOOLEAN, "
            "  a48 BOOLEAN, "
            "  a49 BOOLEAN, "
            "  a50 BOOLEAN, "
            "  a51 BOOLEAN, "
            "  a52 BOOLEAN, "
            "  a53 BOOLEAN, "
            "  a54 BOOLEAN, "
            "  a55 BOOLEAN, "
            "  a56 BOOLEAN, "
            "  a57 BOOLEAN, "
            "  a58 BOOLEAN, "
            "  a59 BOOLEAN, "
            "  a60 BOOLEAN, "
            "  a61 BOOLEAN, "
            "  a62 BOOLEAN, "
            "  a63 BOOLEAN, "
            "  a64 BOOLEAN, "
            "  a65 BOOLEAN "
            "} "
            "END",
            'uper')

        datas = [
            ('A',                                {}, b''),
            ('O',                                {}, b'\x00'),
            ('B',                          {'a': 0}, b'\x00'),
            ('B',                          {'a': 1}, b'\x80\x80\x80'),
            ('C',                       {'a': True}, b'\x40'),
            ('D',                       {'a': True}, b'\x40'),
            ('E',                       {'a': True}, b'\x40'),
            ('H',                       {'a': True}, b'\x40'),
            ('I',                       {'a': True}, b'\x40'),
            ('J',                       {'a': True}, b'\x40'),
            ('K',                       {'a': True}, b'\x40'),
            ('L',                       {'a': True}, b'\x40'),
            ('M',                       {'a': True}, b'\x40'),
            ('N',                       {'a': True}, b'\x00'),
            ('N',                      {'a': False}, b'\x80'),
            ('P',                                {}, b'\x00'),
            ('O',                       {'a': True}, b'\x80\x80\xc0\x00'),
            ('O',                      {'a': False}, b'\x80\x80\x80\x00'),
            ('P',            {'a': True, 'b': True}, b'\x80\x80\xa0\x00'),
            ('P',           {'a': True, 'b': False}, b'\x80\x80\xe0\x00'),
            ('D',            {'a': True, 'b': True}, b'\xc0\x40\x60\x00'),
            ('E',            {'a': True, 'b': True}, b'\xc0\x40\x60\x00'),
            ('F',            {'a': True, 'c': True}, b'\x60'),
            ('G',            {'a': True, 'd': True}, b'\x60'),
            ('I',            {'a': True, 'b': True}, b'\xc0\x40\x60\x00'),
            ('J',            {'a': True, 'b': True}, b'\xc0\x40\x60\x00'),
            ('K',            {'a': True, 'b': True}, b'\xc0\xc0\x30\x00'),
            ('F', {'a': True, 'b': True, 'c': True}, b'\xe0\x20\x30\x00'),
            ('K', {'a': True, 'b': True, 'c': True}, b'\xc0\xe0\x30\x00\x30\x00'),
            ('L', {'a': True, 'b': True, 'c': True}, b'\xc0\x40\x70\x00'),
            ('G', {'a': True, 'b': True, 'd': True}, b'\xe0\x60\x18\x00'),
            ('G',
             {'a': True, 'b': True, 'c': True, 'd': True},
             b'\xe0\x70\x18\x00\x18\x00'),
            ('M',
             {'a': True, 'b': {'a': 5}, 'c': True},
             b'\xc0\x40\xe0\x20\xb0\x00'),
            ('Q',      {'a': {'a': True}, 'b': 100}, b'\x40\x59\x00'),
            ('R',
             {'a': {'a': True, 'b': True}, 'b': 100},
             b'\xc0\x40\x60\x00\x59\x00'),
            ('S',
             {'a': True, 'b': {'a': True, 'b': True}},
             b'\xc0\x40\x5c\x00'),
            ('T',                       {'a': [{}]}, b'\x80\x80'),
            ('T',                {'a': [{'a': []}]}, b'\x80\xc0\x00'),
            ('V',                      {'a': False}, b'\x82\x80\x20\x00'),
            ('V',                      {'b': False}, b'\x82\x40\x20\x00'),
            ('V',                      {'c': False}, b'\x82\x20\x20\x00'),
            ('W',
             {'a1': True},
             b'\xd0\x60\x00\x00\x00\x00\x00\x00\x00\x00\x30\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Non-symmetrical encoding and decoding because default values
        # are not encoded, but part of the decoded (given that the
        # root and addition is present).
        self.assertEqual(foo.encode('N', {}), b'\x00')
        self.assertEqual(foo.decode('N', b'\x00'), {'a': True})
        self.assertEqual(foo.encode('P', {'a': True}), b'\x80\x80\xa0\x00')
        self.assertEqual(foo.decode('P', b'\x80\x80\xa0\x00'),
                         {'a': True, 'b': True})

        # Decode D as C. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('C', b'\xc0\x40\x60\x00'), {'a': True})

        # Decode R as Q. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('Q', b'\xc0\x40\x60\x00\x59\x00'),
                         {'a': {'a': True}, 'b': 100})

        # Decode error of present addition member (out of data).
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('U', b'\x80\x81\x81\x02\xee')

        self.assertEqual(str(cm.exception),
                         'a: a: out of data at bit offset 25 (3.1 bytes)')

    def test_sequence_of(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE OF INTEGER "
            "B ::= SEQUENCE SIZE (2) OF INTEGER "
            "C ::= SEQUENCE SIZE (1..5) OF INTEGER "
            "D ::= SEQUENCE SIZE (1..2, ...) OF INTEGER "
            "E ::= SEQUENCE SIZE (1..2, ..., 6..7) OF INTEGER "
            "F ::= SEQUENCE SIZE (1..10000) OF OCTET STRING "
            "END",
            'uper')

        datas = [
            ('A',                [], b'\x00'),
            ('A',               [1], b'\x01\x01\x01'),
            ('A',            [1, 2], b'\x02\x01\x01\x01\x02'),
            ('A',     1000 * [1, 2], b'\x87\xd0' + 1000 * b'\x01\x01\x01\x02'),
            ('A',       16384 * [1], b'\xc1' + 16384 * b'\x01\x01' + b'\x00'),
            ('B',            [1, 2], b'\x01\x01\x01\x02'),
            ('B', [4663, 222322233], b'\x02\x12\x37\x04\x0d\x40\x5e\x39'),
            ('C',               [1], b'\x00\x20\x20'),
            ('C',            [1, 2], b'\x20\x20\x20\x20\x40'),
            ('D',            [2, 1], b'\x40\x40\x80\x40\x40'),
            ('E',
             6 * [1],
             b'\x83\x00\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80'),
            ('F',   300 * [b'\x56'], b'\x04\xac' + 300 * b'\x05\x58')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_choice(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= CHOICE { "
            "  a BOOLEAN "
            "} "
            "B ::= CHOICE { "
            "  a BOOLEAN, "
            "  ... "
            "} "
            "C ::= CHOICE { "
            "  a BOOLEAN, "
            "  b INTEGER, "
            "  ..., "
            "  [[ "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "D ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  ... "
            "} "
            "E ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN "
            "  ]], "
            "  [[ "
            "  c BOOLEAN "
            "  ]], "
            "  ... "
            "} "
            "F ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  ... "
            "} "
            "G ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN "
            "} "
            "H ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  b BOOLEAN, "
            "  c BOOLEAN "
            "} "
            "I ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b BOOLEAN, "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "J ::= CHOICE { "
            "  a BOOLEAN, "
            "  ..., "
            "  [[ "
            "  b CHOICE { "
            "    a INTEGER"
            "  }, "
            "  c BOOLEAN "
            "  ]] "
            "} "
            "K ::= CHOICE { "
            "  a BOOLEAN, "
            "  b BOOLEAN, "
            "  c BOOLEAN, "
            "  ..., "
            "  d BOOLEAN, "
            "  e BOOLEAN, "
            "  f BOOLEAN, "
            "  g BOOLEAN, "
            "  h BOOLEAN "
            "} "
            "L ::= CHOICE { "
            "  a BOOLEAN, "
            "  b BOOLEAN, "
            "  c BOOLEAN, "
            "  ..., "
            "  d BOOLEAN, "
            "  e BOOLEAN, "
            "  f BOOLEAN, "
            "  g BOOLEAN, "
            "  h BOOLEAN, "
            "  i BOOLEAN "
            "} "
            "END",
            'uper')

        datas = [
            ('A',            ('a', True), b'\x80'),
            ('B',            ('a', True), b'\x40'),
            ('C',            ('a', True), b'\x20'),
            ('C',               ('b', 1), b'\x40\x40\x40'),
            ('C',            ('c', True), b'\x80\x01\x80'),
            ('D',            ('a', True), b'\x40'),
            ('D',            ('b', True), b'\x80\x01\x80'),
            ('E',            ('a', True), b'\x40'),
            ('E',            ('b', True), b'\x80\x01\x80'),
            ('E',            ('c', True), b'\x81\x01\x80'),
            ('F',            ('a', True), b'\x40'),
            ('G',            ('a', True), b'\x40'),
            ('G',            ('b', True), b'\x80\x01\x80'),
            ('H',            ('a', True), b'\x40'),
            ('H',            ('b', True), b'\x80\x01\x80'),
            ('H',            ('c', True), b'\x81\x01\x80'),
            ('I',            ('a', True), b'\x40'),
            ('I',            ('b', True), b'\x80\x01\x80'),
            ('I',            ('c', True), b'\x81\x01\x80'),
            ('J',            ('a', True), b'\x40'),
            ('J',        ('b', ('a', 1)), b'\x80\x02\x01\x01'),
            ('J',            ('c', True), b'\x81\x01\x80'),
            ('L',            ('i', True), b'\x85\x01\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Bad additions index.
        decoded = foo.decode('K', b'\x85\x01\x80')
        self.assertEqual(decoded, (None, None))

        # Bad addition value.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('K', ('i', True))

        self.assertEqual(
            str(cm.exception),
            "Expected choice 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h', but "
            "got 'i'.")

    def test_utf8_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE { "
            "    a BOOLEAN, "
            "    b UTF8String, "
            "    c UTF8String OPTIONAL"
            "} "
            "B ::= UTF8String (SIZE (10)) "
            "C ::= UTF8String (SIZE (0..1)) "
            "D ::= UTF8String (SIZE (2..3) ^ (FROM (\"a\"..\"g\"))) "
            "E ::= UTF8String "
            "END",
            'uper')

        datas = [
            ('A', {'a': True, 'b': u''}, b'\x40\x00'),
            ('A',
             {'a': True, 'b': u'1', 'c': u'foo'},
             b'\xc0\x4c\x40\xd9\x9b\xdb\xc0'),
            ('A',
             {'a': True, 'b': 300 * u'1'},
             b'\x60\x4b\x0c' + 299 * b'\x4c' + b'\x40'),
            ('B',
             u'1234567890',
             b'\x0a\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30'),
            ('C',                   u'', b'\x00'),
            ('C',                  u'P', b'\x01\x50'),
            ('D',                u'agg', b'\x03\x61\x67\x67'),
            ('E',                u'bar', b'\x03\x62\x61\x72'),
            ('E',           u'a\u1010c', b'\x05\x61\xe1\x80\x90\x63'),
            ('E',
             15000 * u'123',
             b'\xc2' + 10922 * b'123' + b'12\xaf\xc83' + 4077 * b'123')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x70\x00\x00\x00')

        self.assertEqual(str(cm.exception),
                         'b: Bad length determinant fragmentation value 0xc0.')

    def test_numeric_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NumericString "
            "B ::= NumericString (SIZE (5)) "
            "C ::= NumericString (SIZE (19..133)) "
            "D ::= NumericString (FROM (\"0\"..\"5\")) "
            "E ::= NumericString (FROM (\"0\"..\"2\", ..., \"4\"..\"5\")) "
            "F ::= NumericString (SIZE (1..4, ..., 6..7)) "
            "G ::= NumericString (SIZE (0..MAX)) "
            "H ::= NumericString (SIZE (2..MAX)) "
            "END",
            'uper')

        datas = [
            ('A',        ' 0123456789', b'\x0b\x01\x23\x45\x67\x89\xa0'),
            ('B',              '1 9 5', b'\x20\xa0\x60'),
            ('C',
             '0123456789 9876543210',
             b'\x04\x24\x68\xac\xf1\x34\x15\x30\xec\xa8\x64\x20'),
            ('D',                  '5', b'\x01\xa0'),
            #('E',                  '2', b'\x01\x30'),
            #('E',                  '5', b'\x01\x60')
            ('F',                   '0', b'\x02'),
            ('G',                    '', b'\x00'),
            ('H',                 '345', b'\x03\x45\x60')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Bad character 'a' should raise an exception.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', 'a', check_constraints=False)

        self.assertEqual(
            str(cm.exception),
            "Expected a character in ' 0123456789', but got 'a' (0x61)'.")

        # Bad value 11 should raise an exception.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x01\xb0')

        self.assertEqual(
            str(cm.exception),
            "Expected a value in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "
            "but got 11.")

        # Decode size extension is not yet supported.
        with self.assertRaises(NotImplementedError) as cm:
            foo.decode('F', b'\x83\x08\x88\x88\x80')

        self.assertEqual(
            str(cm.exception),
            "String size extension is not yet implemented.")

    def test_printable_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= PrintableString "
            "B ::= PrintableString (SIZE (16)) "
            "C ::= PrintableString (SIZE (0..31)) "
            "D ::= SEQUENCE { "
            "    a BOOLEAN, "
            "    b PrintableString (SIZE (36)), "
            "    c BOOLEAN "
            "} "
            "E ::= SEQUENCE { "
            "    a BOOLEAN, "
            "    b PrintableString (SIZE (0..22)), "
            "    c BOOLEAN "
            "} "
            "F ::= SEQUENCE { "
            "    a BOOLEAN, "
            "    b PrintableString, "
            "    c BOOLEAN "
            "} "
            "END",
            'uper')

        datas = [
            ('A',
             (string.ascii_uppercase
              + string.ascii_lowercase
              + string.digits
              + " '()+,-./:=?"),
             b'\x4a\x83\x0a\x1c\x48\xb1\xa3\xc8\x93\x2a\x5c\xc9\xb3\xa7\xd0\xa3'
             b'\x4a\x9d\x4a\xb5\xab\xd8\xb3\x6b\x0e\x2c\x79\x32\xe6\xcf\xa3\x4e'
             b'\xad\x7b\x36\xee\xdf\xc3\x8f\x2e\x7d\x3a\xf6\xef\xe3\xcf\xa6\x0c'
             b'\x59\x33\x68\xd5\xb3\x77\x0e\x50\x27\x50\xa5\x5a\xc5\xab\x97\xba'
             b'\x7a\xfc'),
            ('B',
             '0123456789abcdef',
             b'\x60\xc5\x93\x36\x8d\x5b\x37\x70\xe7\x0e\x2c\x79\x32\xe6'),
            ('C',                 '', b'\x00'),
            ('C',                '2', b'\x0b\x20'),
            ('D',
             {'a': True, 'b': 12 * '123', 'c': True},
             b'\xb1\x64\xcd\x8b\x26\x6c\x59\x33\x62\xc9\x9b\x16\x4c\xd8\xb2\x66'
             b'\xc5\x93\x36\x2c\x99\xb1\x64\xcd\x8b\x26\x6c\x59\x33\x62\xc9\x9c'),
            ('E',
             {'a': True, 'b': '', 'c': True},
             b'\x82'),
            ('F',
             {'a': True, 'b': '123', 'c': True},
             b'\x81\xb1\x64\xce')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Bad character '[' should raise an exception.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', '[', check_constraints=False)

        self.assertEqual(
            str(cm.exception),
            "Expected a character in ' '()+,-./0123456789:=?ABCDEFGHIJKLMNO"
            "PQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', but got '[' (0x5b)'.")

    def test_ia5_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= IA5String "
            "B ::= IA5String (SIZE (1..256)) "
            "C ::= IA5String (SIZE (2)) "
            "D ::= IA5String (SIZE (19..133)) "
            "END",
            'uper')

        datas = [
            ('A', 'bar', b'\x03\xc5\x87\x90'),
            ('A',
             17 * 'HejHoppHappHippAbcde',
             b'\x81\x54\x91\x97\x54\x8d\xfc\x38\x48\xc3\xc3\x84\x8d\x3c\x38'
             b'\x41\xc5\x8f\x26\x59\x19\x75\x48\xdf\xc3\x84\x8c\x3c\x38\x48'
             b'\xd3\xc3\x84\x1c\x58\xf2\x65\x91\x97\x54\x8d\xfc\x38\x48\xc3'
             b'\xc3\x84\x8d\x3c\x38\x41\xc5\x8f\x26\x59\x19\x75\x48\xdf\xc3'
             b'\x84\x8c\x3c\x38\x48\xd3\xc3\x84\x1c\x58\xf2\x65\x91\x97\x54'
             b'\x8d\xfc\x38\x48\xc3\xc3\x84\x8d\x3c\x38\x41\xc5\x8f\x26\x59'
             b'\x19\x75\x48\xdf\xc3\x84\x8c\x3c\x38\x48\xd3\xc3\x84\x1c\x58'
             b'\xf2\x65\x91\x97\x54\x8d\xfc\x38\x48\xc3\xc3\x84\x8d\x3c\x38'
             b'\x41\xc5\x8f\x26\x59\x19\x75\x48\xdf\xc3\x84\x8c\x3c\x38\x48'
             b'\xd3\xc3\x84\x1c\x58\xf2\x65\x91\x97\x54\x8d\xfc\x38\x48\xc3'
             b'\xc3\x84\x8d\x3c\x38\x41\xc5\x8f\x26\x59\x19\x75\x48\xdf\xc3'
             b'\x84\x8c\x3c\x38\x48\xd3\xc3\x84\x1c\x58\xf2\x65\x91\x97\x54'
             b'\x8d\xfc\x38\x48\xc3\xc3\x84\x8d\x3c\x38\x41\xc5\x8f\x26\x59'
             b'\x19\x75\x48\xdf\xc3\x84\x8c\x3c\x38\x48\xd3\xc3\x84\x1c\x58'
             b'\xf2\x65\x91\x97\x54\x8d\xfc\x38\x48\xc3\xc3\x84\x8d\x3c\x38'
             b'\x41\xc5\x8f\x26\x59\x19\x75\x48\xdf\xc3\x84\x8c\x3c\x38\x48'
             b'\xd3\xc3\x84\x1c\x58\xf2\x65\x91\x97\x54\x8d\xfc\x38\x48\xc3'
             b'\xc3\x84\x8d\x3c\x38\x41\xc5\x8f\x26\x59\x19\x75\x48\xdf\xc3'
             b'\x84\x8c\x3c\x38\x48\xd3\xc3\x84\x1c\x58\xf2\x65\x91\x97\x54'
             b'\x8d\xfc\x38\x48\xc3\xc3\x84\x8d\x3c\x38\x41\xc5\x8f\x26\x50'),
            ('B', 'Hej', b'\x02\x91\x97\x50'),
            ('C',  'He', b'\x91\x94'),
            ('D',
             'HejHoppHappHippAbcde',
             b'\x03\x23\x2e\xa9\x1b\xf8\x70\x91\x87\x87\x09\x1a\x78\x70\x83\x8b'
             b'\x1e\x4c\xa0'),
            ('A',
             1638 * '1234567890' + '123',
             b'\xbf\xff'
             + 409 * (b'\x62\xc9\x9b\x46\xad\x9b\xb8\x72\xc1\x8b'
                      b'\x26\x6d\x1a\xb6\x6e\xe1\xcb\x06\x2c\x99'
                      b'\xb4\x6a\xd9\xbb\x87\x2c\x18\xb2\x66\xd1'
                      b'\xab\x66\xee\x1c\xb0')
             + b'\x62\xc9\x9b\x46\xad\x9b\xb8\x72\xc1\x8b\x26\x6d\x1a\xb6\x6e\xe1'
             + b'\xcb\x06\x2c\x99\x80'),
            ('A',
             1638 * '1234567890' + '1234',
             b'\xc1'
             + 409 * (b'\x62\xc9\x9b\x46\xad\x9b\xb8\x72\xc1\x8b'
                      b'\x26\x6d\x1a\xb6\x6e\xe1\xcb\x06\x2c\x99'
                      b'\xb4\x6a\xd9\xbb\x87\x2c\x18\xb2\x66\xd1'
                      b'\xab\x66\xee\x1c\xb0')
             + b'\x62\xc9\x9b\x46\xad\x9b\xb8\x72\xc1\x8b\x26\x6d\x1a\xb6\x6e\xe1'
             + b'\xcb\x06\x2c\x99\xb4'
             + b'\x00'),
            ('A',
             1638 * '1234567890' + '12345',
             b'\xc1'
             + 409 * (b'\x62\xc9\x9b\x46\xad\x9b\xb8\x72\xc1\x8b'
                      b'\x26\x6d\x1a\xb6\x6e\xe1\xcb\x06\x2c\x99'
                      b'\xb4\x6a\xd9\xbb\x87\x2c\x18\xb2\x66\xd1'
                      b'\xab\x66\xee\x1c\xb0')
             + b'\x62\xc9\x9b\x46\xad\x9b\xb8\x72\xc1\x8b\x26\x6d\x1a\xb6\x6e\xe1'
             + b'\xcb\x06\x2c\x99\xb4'
             + b'\x01'
             + b'\x6a')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_visible_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= VisibleString (SIZE (19..133)) "
            "B ::= VisibleString (SIZE (5)) "
            "C ::= VisibleString (SIZE (19..1000)) "
            "D ::= VisibleString (FROM (\"a\"..\"z\")) (SIZE (1..255)) "
            "END",
            'uper')

        datas = [
            ('A',
             'HejHoppHappHippAbcde',
             b'\x03\x23\x2e\xa9\x1b\xf8\x70\x91\x87\x87\x09\x1a\x78\x70\x83\x8b'
             b'\x1e\x4c\xa0'),
            ('B', 'Hejaa', b'\x91\x97\x56\x1c\x20'),
            ('C',
             17 * 'HejHoppHappHippAbcde',
             b'\x50\x64\x65\xd5\x23\x7f\x0e\x12\x30\xf0\xe1\x23\x4f\x0e\x10\x71'
             b'\x63\xc9\x96\x46\x5d\x52\x37\xf0\xe1\x23\x0f\x0e\x12\x34\xf0\xe1'
             b'\x07\x16\x3c\x99\x64\x65\xd5\x23\x7f\x0e\x12\x30\xf0\xe1\x23\x4f'
             b'\x0e\x10\x71\x63\xc9\x96\x46\x5d\x52\x37\xf0\xe1\x23\x0f\x0e\x12'
             b'\x34\xf0\xe1\x07\x16\x3c\x99\x64\x65\xd5\x23\x7f\x0e\x12\x30\xf0'
             b'\xe1\x23\x4f\x0e\x10\x71\x63\xc9\x96\x46\x5d\x52\x37\xf0\xe1\x23'
             b'\x0f\x0e\x12\x34\xf0\xe1\x07\x16\x3c\x99\x64\x65\xd5\x23\x7f\x0e'
             b'\x12\x30\xf0\xe1\x23\x4f\x0e\x10\x71\x63\xc9\x96\x46\x5d\x52\x37'
             b'\xf0\xe1\x23\x0f\x0e\x12\x34\xf0\xe1\x07\x16\x3c\x99\x64\x65\xd5'
             b'\x23\x7f\x0e\x12\x30\xf0\xe1\x23\x4f\x0e\x10\x71\x63\xc9\x96\x46'
             b'\x5d\x52\x37\xf0\xe1\x23\x0f\x0e\x12\x34\xf0\xe1\x07\x16\x3c\x99'
             b'\x64\x65\xd5\x23\x7f\x0e\x12\x30\xf0\xe1\x23\x4f\x0e\x10\x71\x63'
             b'\xc9\x96\x46\x5d\x52\x37\xf0\xe1\x23\x0f\x0e\x12\x34\xf0\xe1\x07'
             b'\x16\x3c\x99\x64\x65\xd5\x23\x7f\x0e\x12\x30\xf0\xe1\x23\x4f\x0e'
             b'\x10\x71\x63\xc9\x96\x46\x5d\x52\x37\xf0\xe1\x23\x0f\x0e\x12\x34'
             b'\xf0\xe1\x07\x16\x3c\x99\x64\x65\xd5\x23\x7f\x0e\x12\x30\xf0\xe1'
             b'\x23\x4f\x0e\x10\x71\x63\xc9\x96\x46\x5d\x52\x37\xf0\xe1\x23\x0f'
             b'\x0e\x12\x34\xf0\xe1\x07\x16\x3c\x99\x64\x65\xd5\x23\x7f\x0e\x12'
             b'\x30\xf0\xe1\x23\x4f\x0e\x10\x71\x63\xc9\x94'),
            ('D', 'hej', b'\x02\x39\x12')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Bad character 0x19 should raise an exception.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', '\x19', check_constraints=False)

        self.assertEqual(
            str(cm.exception),
            "Expected a character in ' !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEF"
            "GHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~', but got"
            " '.' (0x19)'.")

    def test_general_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GeneralString "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b GeneralString "
            "} "
            "END",
            'uper')

        datas = [
            ('A',                      '', b'\x00'),
            ('A',                     '2', b'\x01\x32'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\xa5\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_bmp_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BMPString "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b BMPString "
            "} "
            "END",
            'uper')

        datas = [
            ('A',                      '', b'\x00'),
            ('A',                   '123', b'\x03\x00\x31\x00\x32\x00\x33'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\x80\x25\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_graphic_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GraphicString "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b GraphicString "
            "} "
            "END",
            'uper')

        datas = [
            ('A',                      '', b'\x00'),
            ('A',                     '2', b'\x01\x32'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\xa5\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_teletex_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= TeletexString "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b TeletexString "
            "} "
            "END",
            'uper')

        datas = [
            ('A',                  u'123', b'\x03\x31\x32\x33'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\xa5\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_universal_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UniversalString "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b UniversalString "
            "} "
            "END",
            'uper')

        datas = [
            ('A',
             u'åäö',
             b'\x03\x00\x00\x00\xe5\x00\x00\x00\xe4\x00\x00\x00\xf6'),
            ('A',
             u'1𐈃Q',
             b'\x03\x00\x00\x00\x31\x00\x01\x02\x03\x00\x00\x00\x51'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\x80\x00\x00\x25\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_utc_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTCTime "
            "END",
            'uper')

        datas = [
            ('A',
             ut2dt('010203040506Z'),
             b'\x0d\x60\xc5\x83\x26\x0c\xd8\x34\x60\xd5\x83\x6b\x40')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_generalized_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GeneralizedTime "
            "END",
            'uper')

        datas = [
            ('A',
             gt2dt('20001231235959.999Z'),
             b'\x13\x64\xc1\x83\x06\x2c\x99\xb1\x64\xcd\xab\x96\xae\x57\x39\x72'
             b'\xe6\xd0')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_date(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= DATE "
            "END",
            'uper')

        datas = [
            ('A', datetime.date(1748, 12, 31), b'\xc0\x81\xb5\x2f\xc0'),
            ('A',   datetime.date(1749, 1, 1), b'\x80\x00\x00'),
            ('A', datetime.date(2004, 12, 31), b'\xbf\xef\xc0'),
            ('A',   datetime.date(2005, 1, 1), b'\x00\x00'),
            ('A', datetime.date(2020, 12, 31), b'\x3e\xfc'),
            ('A',   datetime.date(2021, 1, 1), b'\x40\x00\x00'),
            ('A', datetime.date(2276, 12, 31), b'\x7f\xef\xc0'),
            ('A',   datetime.date(2277, 1, 1), b'\xc0\x82\x39\x40\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_time_of_day(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= TIME-OF-DAY "
            "END",
            'uper')

        datas = [
            ('A',    datetime.time(0, 0, 0), b'\x00\x00\x00'),
            ('A', datetime.time(23, 59, 59), b'\xbf\x7d\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_date_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= DATE-TIME "
            "END",
            'uper')

        datas = [
            ('A',
             datetime.datetime(1748, 12, 31, 23, 59, 59),
             b'\xc0\x81\xb5\x2f\xd7\xef\xb0'),
            ('A',
             datetime.datetime(1749, 1, 1, 0, 1, 2),
             b'\x80\x00\x00\x04\x20'),
            ('A',
             datetime.datetime(2004, 12, 31, 23, 59, 58),
             b'\xbf\xef\xd7\xef\xa0'),
            ('A',
             datetime.datetime(2005, 1, 1, 1, 2, 3),
             b'\x00\x00\x10\x83'),
            ('A',
             datetime.datetime(2020, 12, 31, 23, 59, 57),
             b'\x3e\xfd\x7e\xf9'),
            ('A',
             datetime.datetime(2021, 1, 1, 2, 3, 4),
             b'\x40\x00\x02\x0c\x40'),
            ('A',
             datetime.datetime(2276, 12, 31, 23, 59, 56),
             b'\x7f\xef\xd7\xef\x80'),
            ('A',
             datetime.datetime(2277, 1, 1, 4, 5, 6),
             b'\xc0\x82\x39\x40\x04\x14\x60')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_foo(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'uper')

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Question.
        encoded = foo.encode('Question', {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded, b'\x01\x01\x09\x93\xcd\x03\x15\x6c\x5e\xb3\x7e')
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Answer.
        encoded = foo.encode('Answer', {'id': 1, 'answer': False})
        self.assertEqual(encoded, b'\x01\x01\x00')
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

        # Encode a question with missing field 'id'.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            encoded = foo.encode('Question', {'question': 'Is 1+1=3?'})

        self.assertEqual(
            str(cm.exception),
            "Sequence member 'id' not found in {'question': 'Is 1+1=3?'}.")

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'uper')

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode_length(b'')

        self.assertEqual(str(cm.exception),
                         "Decode length is not supported for this codec.")

    def test_versions(self):
        foo = asn1tools.compile_files('tests/files/versions.asn', 'uper')

        # Encode as V1, decode as V1, V2 and V3
        decoded_v1 = {
            'userName': 'myUserName',
            'password': 'myPassword',
            'accountNumber': 54224445
        }

        encoded_v1 = foo.encode('V1', decoded_v1)

        self.assertEqual(foo.decode('V1', encoded_v1), decoded_v1)
        self.assertEqual(foo.decode('V2', encoded_v1), decoded_v1)
        self.assertEqual(foo.decode('V3', encoded_v1), decoded_v1)

        # Encode as V2, decode as V1, V2 and V3
        decoded_v2 = {
            'userName': 'myUserName',
            'password': 'myPassword',
            'accountNumber': 54224445,
            'minutesLastLoggedIn': 5
        }

        encoded_v2 = foo.encode('V2', decoded_v2)

        self.assertEqual(foo.decode('V1', encoded_v2), decoded_v1)
        self.assertEqual(foo.decode('V2', encoded_v2), decoded_v2)
        self.assertEqual(foo.decode('V3', encoded_v2), decoded_v2)

        # Encode as V3, decode as V1, V2 and V3
        decoded_v3 = {
            'userName': 'myUserName',
            'password': 'myPassword',
            'accountNumber': 54224445,
            'minutesLastLoggedIn': 5,
            'certificate': None,
            'thumb': None
        }

        encoded_v3 = foo.encode('V3', decoded_v3)

        self.assertEqual(foo.decode('V1', encoded_v3), decoded_v1)
        self.assertEqual(foo.decode('V2', encoded_v3), decoded_v2)
        self.assertEqual(foo.decode('V3', encoded_v3), decoded_v3)

    def test_x691_a1(self):
        a1 = asn1tools.compile_files('tests/files/x691_a1.asn', 'uper')

        decoded = {
            'name': {
                'givenName': 'John',
                'initial': 'P',
                'familyName': 'Smith'
            },
            'title': 'Director',
            'number': 51,
            'dateOfHire': '19710917',
            'nameOfSpouse': {
                'givenName': 'Mary',
                'initial': 'T',
                'familyName': 'Smith'
            },
            'children': [
                {
                    'name': {
                        'givenName': 'Ralph',
                        'initial': 'T',
                        'familyName': 'Smith'
                    },
                    'dateOfBirth': '19571111'
                },
                {
                    'name': {
                        'givenName': 'Susan',
                        'initial': 'B',
                        'familyName': 'Jones'
                    },
                    'dateOfBirth': '19590717'
                }
            ]
        }

        encoded = (
            b'\x82\x4a\xdf\xa3\x70\x0d\x00\x5a\x7b\x74\xf4\xd0\x02\x66\x11\x13'
            b'\x4f\x2c\xb8\xfa\x6f\xe4\x10\xc5\xcb\x76\x2c\x1c\xb1\x6e\x09\x37'
            b'\x0f\x2f\x20\x35\x01\x69\xed\xd3\xd3\x40\x10\x2d\x2c\x3b\x38\x68'
            b'\x01\xa8\x0b\x4f\x6e\x9e\x9a\x02\x18\xb9\x6a\xdd\x8b\x16\x2c\x41'
            b'\x69\xf5\xe7\x87\x70\x0c\x20\x59\x5b\xf7\x65\xe6\x10\xc5\xcb\x57'
            b'\x2c\x1b\xb1\x6e'
        )

        self.assert_encode_decode(a1, 'PersonnelRecord', decoded, encoded)

    def test_x691_a2(self):
        a2 = asn1tools.compile_files('tests/files/x691_a2.asn', 'uper')

        decoded = {
            'name': {
                'givenName': 'John',
                'initial': 'P',
                'familyName': 'Smith'
            },
            'title': 'Director',
            'number': 51,
            'dateOfHire': '19710917',
            'nameOfSpouse': {
                'givenName': 'Mary',
                'initial': 'T',
                'familyName': 'Smith'
            },
            'children': [
                {
                    'name': {
                        'givenName': 'Ralph',
                        'initial': 'T',
                        'familyName': 'Smith'
                    },
                    'dateOfBirth': '19571111'
                },
                {
                    'name': {
                        'givenName': 'Susan',
                        'initial': 'B',
                        'familyName': 'Jones'
                    },
                    'dateOfBirth': '19590717'
                }
            ]
        }

        encoded = (
            b'\x86\x5d\x51\xd2\x88\x8a\x51\x25\xf1\x80\x99\x84\x44\xd3\xcb\x2e'
            b'\x3e\x9b\xf9\x0c\xb8\x84\x8b\x86\x73\x96\xe8\xa8\x8a\x51\x25\xf1'
            b'\x81\x08\x9b\x93\xd7\x1a\xa2\x29\x44\x97\xc6\x32\xae\x22\x22\x22'
            b'\x98\x5c\xe5\x21\x88\x5d\x54\xc1\x70\xca\xc8\x38\xb8'
        )

        self.assert_encode_decode(a2, 'PersonnelRecord', decoded, encoded)

    def test_x691_a3(self):
        a3 = asn1tools.compile_files('tests/files/x691_a3.asn', 'uper')

        decoded = {
            'name': {
                'givenName': 'John',
                'initial': 'P',
                'familyName': 'Smith'
            },
            'title': 'Director',
            'number': 51,
            'dateOfHire': '19710917',
            'nameOfSpouse': {
                'givenName': 'Mary',
                'initial': 'T',
                'familyName': 'Smith'
            },
            'children': [
                {
                    'name': {
                        'givenName': 'Ralph',
                        'initial': 'T',
                        'familyName': 'Smith'
                    },
                    'dateOfBirth': '19571111'
                },
                {
                    'name': {
                        'givenName': 'Susan',
                        'initial': 'B',
                        'familyName': 'Jones'
                    },
                    'dateOfBirth': '19590717',
                    'sex': 'female'
                }
            ]
        }

        encoded = (
            b'\x40\xcb\xaa\x3a\x51\x08\xa5\x12\x5f\x18\x03\x30\x88\x9a\x79\x65'
            b'\xc7\xd3\x7f\x20\xcb\x88\x48\xb8\x19\xce\x5b\xa2\xa1\x14\xa2\x4b'
            b'\xe3\x01\x13\x72\x7a\xe3\x54\x22\x94\x49\x7c\x61\x95\x71\x11\x18'
            b'\x22\x98\x5c\xe5\x21\x84\x2e\xaa\x60\xb8\x32\xb2\x0e\x2e\x02\x02'
            b'\x80'
        )

        self.assert_encode_decode(a3, 'PersonnelRecord', decoded, encoded)

    def test_x691_a4(self):
        a4 = asn1tools.compile_dict(deepcopy(X691_A4), 'uper')

        decoded = {
            'a': 253,
            'b': True,
            'c': ('e', True),
            'g': '123',
            'h': True
        }

        encoded = (
            b'\x9e\x00\x06\x00\x04\x0a\x46\x90'
        )

        self.assert_encode_decode(a4, 'Ax', decoded, encoded)

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'uper')

        # Message 1.
        decoded = {
            'message': (
                'c1',
                (
                    'paging',
                    {
                        'systemInfoModification': 'true',
                        'nonCriticalExtension': {
                        }
                    }
                )
            )
        }

        encoded = b'\x28'

        self.assert_encode_decode(rrc, 'PCCH-Message', decoded, encoded)

        # Message 2.
        decoded = {
            'message': (
                'c1',
                ('paging', {})
            )
        }

        encoded = b'\x00'

        self.assert_encode_decode(rrc, 'PCCH-Message', decoded, encoded)

        # Message 3.
        decoded = {
            'message': {
                'dl-Bandwidth': 'n6',
                'phich-Config': {
                    'phich-Duration': 'normal',
                    'phich-Resource': 'half'
                },
                'systemFrameNumber': (b'\x12', 8),
                'spare': (b'\x34\x40', 10)
            }
        }

        encoded = b'\x04\x48\xd1'

        self.assert_encode_decode(rrc, 'BCCH-BCH-Message', decoded, encoded)

        # Message #4.
        decoded = {
            'message': (
                'c1',
                (
                    'systemInformation',
                    {
                        'criticalExtensions': (
                            'systemInformation-r8',
                            {
                                'sib-TypeAndInfo': [
                                    (
                                        'sib2',
                                        {
                                            'ac-BarringInfo': {
                                                'ac-BarringForEmergency': True,
                                                'ac-BarringForMO-Data': {
                                                    'ac-BarringFactor': 'p95',
                                                    'ac-BarringTime': 's128',
                                                    'ac-BarringForSpecialAC': (b'\xf0', 5)
                                                }
                                            },
                                            'radioResourceConfigCommon': {
                                                'rach-ConfigCommon': {
                                                    'preambleInfo': {
                                                        'numberOfRA-Preambles': 'n24',
                                                        'preamblesGroupAConfig': {
                                                            'sizeOfRA-PreamblesGroupA': 'n28',
                                                            'messageSizeGroupA': 'b144',
                                                            'messagePowerOffsetGroupB': 'minusinfinity'
                                                        }
                                                    },
                                                    'powerRampingParameters': {
                                                        'powerRampingStep': 'dB0',
                                                        'preambleInitialReceivedTargetPower': 'dBm-102'
                                                    },
                                                    'ra-SupervisionInfo': {
                                                        'preambleTransMax': 'n8',
                                                        'ra-ResponseWindowSize': 'sf6',
                                                        'mac-ContentionResolutionTimer': 'sf48'
                                                    },
                                                    'maxHARQ-Msg3Tx': 8
                                                },
                                                'bcch-Config': {
                                                    'modificationPeriodCoeff': 'n2'
                                                },
                                                'pcch-Config': {
                                                    'defaultPagingCycle': 'rf256',
                                                    'nB': 'twoT'
                                                },
                                                'prach-Config': {
                                                    'rootSequenceIndex': 836,
                                                    'prach-ConfigInfo': {
                                                        'prach-ConfigIndex': 33,
                                                        'highSpeedFlag': False,
                                                        'zeroCorrelationZoneConfig': 10,
                                                        'prach-FreqOffset': 64
                                                    }
                                                },
                                                'pdsch-ConfigCommon': {
                                                    'referenceSignalPower': -60,
                                                    'p-b': 2
                                                },
                                                'pusch-ConfigCommon': {
                                                    'pusch-ConfigBasic': {
                                                        'n-SB': 1,
                                                        'hoppingMode': 'interSubFrame',
                                                        'pusch-HoppingOffset': 10,
                                                        'enable64QAM': False
                                                    },
                                                    'ul-ReferenceSignalsPUSCH': {
                                                        'groupHoppingEnabled': True,
                                                        'groupAssignmentPUSCH': 22,
                                                        'sequenceHoppingEnabled': False,
                                                        'cyclicShift': 5
                                                    }
                                                },
                                                'pucch-ConfigCommon': {
                                                    'deltaPUCCH-Shift': 'ds1',
                                                    'nRB-CQI': 98,
                                                    'nCS-AN': 4,
                                                    'n1PUCCH-AN': 2047
                                                },
                                                'soundingRS-UL-ConfigCommon': (
                                                    'setup',
                                                    {
                                                        'srs-BandwidthConfig': 'bw0',
                                                        'srs-SubframeConfig': 'sc4',
                                                        'ackNackSRS-SimultaneousTransmission': True
                                                    }),
                                                'uplinkPowerControlCommon': {
                                                    'p0-NominalPUSCH': -126,
                                                    'alpha': 'al0',
                                                    'p0-NominalPUCCH': -127,
                                                    'deltaFList-PUCCH': {
                                                        'deltaF-PUCCH-Format1': 'deltaF-2',
                                                        'deltaF-PUCCH-Format1b': 'deltaF1',
                                                        'deltaF-PUCCH-Format2': 'deltaF0',
                                                        'deltaF-PUCCH-Format2a': 'deltaF-2',
                                                        'deltaF-PUCCH-Format2b': 'deltaF0'
                                                    },
                                                    'deltaPreambleMsg3': -1
                                                },
                                                'ul-CyclicPrefixLength': 'len1'
                                            },
                                            'ue-TimersAndConstants': {
                                                't300': 'ms100',
                                                't301': 'ms200',
                                                't310': 'ms50',
                                                'n310': 'n2',
                                                't311': 'ms30000',
                                                'n311': 'n2'
                                            },
                                            'freqInfo': {
                                                'additionalSpectrumEmission': 3
                                            },
                                            'timeAlignmentTimerCommon': 'sf500'
                                        }
                                    ),
                                    (
                                        'sib3',
                                        {
                                            'cellReselectionInfoCommon': {
                                                'q-Hyst': 'dB0',
                                                'speedStateReselectionPars': {
                                                    'mobilityStateParameters': {
                                                        't-Evaluation': 's180',
                                                        't-HystNormal': 's180',
                                                        'n-CellChangeMedium': 1,
                                                        'n-CellChangeHigh': 16
                                                    },
                                                    'q-HystSF': {
                                                        'sf-Medium': 'dB-6',
                                                        'sf-High': 'dB-4'
                                                    }
                                                }
                                            },
                                            'cellReselectionServingFreqInfo': {
                                                'threshServingLow': 7,
                                                'cellReselectionPriority': 3
                                            },
                                            'intraFreqCellReselectionInfo': {
                                                'q-RxLevMin': -33,
                                                's-IntraSearch': 0,
                                                'presenceAntennaPort1': False,
                                                'neighCellConfig': (b'\x80', 2),
                                                't-ReselectionEUTRA': 4
                                            }
                                        }
                                    ),
                                    (
                                        'sib4',
                                        {
                                        }
                                    ),
                                    (
                                        'sib5',
                                        {
                                            'interFreqCarrierFreqList': [
                                                {
                                                    'dl-CarrierFreq': 1,
                                                    'q-RxLevMin': -45,
                                                    't-ReselectionEUTRA': 0,
                                                    'threshX-High': 31,
                                                    'threshX-Low': 29,
                                                    'allowedMeasBandwidth': 'mbw6',
                                                    'presenceAntennaPort1': True,
                                                    'neighCellConfig': (b'\x00', 2),
                                                    'q-OffsetFreq': 'dB0'
                                                }
                                            ]
                                        }
                                    ),
                                    (
                                        'sib6',
                                        {
                                            't-ReselectionUTRA': 3
                                        }
                                    ),
                                    (
                                        'sib7',
                                        {
                                            't-ReselectionGERAN': 3
                                        }
                                    ),
                                    (
                                        'sib8',
                                        {
                                            'parameters1XRTT': {
                                                'longCodeState1XRTT': (b'\x01#Eg\x89\x00', 42)
                                            }
                                        }
                                    ),
                                    (
                                        'sib9',
                                        {
                                            'hnb-Name': b'4'
                                        }
                                    ),
                                    (
                                        'sib10',
                                        {
                                            'messageIdentifier': (b'#4', 16),
                                            'serialNumber': (b'\x124', 16),
                                            'warningType': b'2\x12'
                                        }
                                    ),
                                    (
                                        'sib11',
                                        {
                                            'messageIdentifier': (b'g\x88', 16),
                                            'serialNumber': (b'T5', 16),
                                            'warningMessageSegmentType': 'notLastSegment',
                                            'warningMessageSegmentNumber': 19,
                                            'warningMessageSegment': b'\x12'
                                        }
                                    )
                                ]
                            }
                        )
                    }
                )
            )
        }

        encoded = (
            b'\x04\x81\x3f\xbe\x2a\x64\x12\xb2\xf3\x3a\x24\x2a\x80\x02\x02\x9b'
            b'\x29\x8a\x7f\xf8\x24\x00\x00\x11\x00\x24\xe2\x08\x05\x06\xc3\xc4'
            b'\x76\x92\x81\x41\x00\xc0\x00\x00\x0b\x23\xfd\x10\x80\xca\x19\x82'
            b'\x80\x48\xd1\x59\xe2\x43\xa0\x1a\x20\x23\x34\x12\x34\x32\x12\x48'
            b'\xcf\x10\xa8\x6a\x4c\x04\x48'
        )

        self.assert_encode_decode(rrc, 'BCCH-DL-SCH-Message', decoded, encoded)

        # Message 5.
        decoded = {
            'message': (
                'c1',
                (
                    'counterCheck', {
                        'rrc-TransactionIdentifier': 0,
                        'criticalExtensions': (
                            'criticalExtensionsFuture',
                            {
                            }
                        )
                    }
                )
            )
        }

        encoded = b'\x41'

        self.assert_encode_decode(rrc, 'DL-DCCH-Message', decoded, encoded)

        # Message 6.
        decoded = {
            'message': (
                'c1',
                (
                    'counterCheck',
                    {
                        'rrc-TransactionIdentifier': 0,
                        'criticalExtensions': (
                            'c1',
                            (
                                'counterCheck-r8',
                                {
                                    'drb-CountMSB-InfoList': [
                                        {
                                            'drb-Identity': 32,
                                            'countMSB-Uplink': 33554431,
                                            'countMSB-Downlink': 33554431
                                        }
                                    ],
                                    'nonCriticalExtension': {
                                    }
                                }
                            )
                        )
                    }
                )
            )
        }

        encoded = b'\x40\x21\xff\xff\xff\xff\xff\xff\xfc'

        self.assert_encode_decode(rrc, 'DL-DCCH-Message', decoded, encoded)

        # Message 7.
        decoded = {
            'message': (
                'c1',
                (
                    'counterCheckResponse',
                    {
                        'rrc-TransactionIdentifier': 0,
                        'criticalExtensions': (
                            'counterCheckResponse-r8',
                            {
                                'drb-CountInfoList': [
                                ],
                                'nonCriticalExtension': {
                                }
                            }
                        )
                    }
                )
            )
        }

        encoded = b'\x50\x80'

        self.assert_encode_decode(rrc, 'UL-DCCH-Message', decoded, encoded)

    def test_lpp_14_3_0(self):
        lpp = asn1tools.compile_dict(deepcopy(LPP_14_3_0), 'uper')

        # Message 1.
        decoded = {
            'transactionID': {
                'initiator': 'targetDevice',
                'transactionNumber': 254
            },
            'endTransaction': True,
            'lpp-MessageBody': (
                'c1',
                (
                    'provideAssistanceData',
                    {
                        'criticalExtensions': (
                            'c1',
                            (
                                'spare1',
                                None
                            )
                        )
                    }
                )
            )
        }

        encoded = b'\x93\xfd\x1b'

        self.assert_encode_decode(lpp, 'LPP-Message', decoded, encoded)

        # Message 2.
        decoded = {
            'transactionID': {
                'initiator': 'targetDevice',
                'transactionNumber': 254
            },
            'endTransaction': True,
            'lpp-MessageBody': (
                'c1',
                (
                    'requestCapabilities',
                    {
                        'criticalExtensions': (
                            'c1',
                            (
                                'requestCapabilities-r9',
                                {
                                    'bt-RequestCapabilities-r13':{
                                    }
                                }
                            )
                        )
                    }
                )
            )
        }

        encoded = b'\x93\xfd\x00\x80\x04\x04\x40'

        self.assert_encode_decode(lpp, 'LPP-Message', decoded, encoded)

        # Message 3.
        decoded = {
            'transactionID': {
                'initiator': 'targetDevice',
                'transactionNumber': 255
            },
            'endTransaction': False,
            'lpp-MessageBody': (
                'c1',
                (
                    'requestCapabilities',
                    {
                        'criticalExtensions': (
                            'c1',
                            (
                                'requestCapabilities-r9',
                                {
                                    'epdu-RequestCapabilities': [
                                        {
                                            'ePDU-Identifier': {
                                                'ePDU-ID': 256
                                            },
                                            'ePDU-Body': b''
                                        }
                                    ],
                                    'tbs-RequestCapabilities-r13': {
                                    },
                                    'bt-RequestCapabilities-r13':{
                                    }
                                }
                            )
                        )
                    }
                )
            )
        }

        encoded = b'\x93\xfe\x00\x84\x0f\xf0\x00\x10\x15\x00'

        self.assert_encode_decode(lpp, 'LPP-Message', decoded, encoded)

        # Message 4.
        decoded = {
            'transactionID': {
                'initiator': 'targetDevice',
                'transactionNumber': 0
            },
            'endTransaction': False,
            'lpp-MessageBody': (
                'c1',
                (
                    'provideLocationInformation',
                    {
                        'criticalExtensions': (
                            'c1',
                            (
                                'provideLocationInformation-r9',
                                {
                                    'ecid-ProvideLocationInformation': {
                                        'ecid-SignalMeasurementInformation': {
                                            'measuredResultsList': [
                                                {
                                                    'physCellId': 1,
                                                    'arfcnEUTRA': 40000,
                                                    'systemFrameNumber': (
                                                        b'\x55\x80', 10),
                                                    'arfcnEUTRA-v9a0': 70000,
                                                    'nrsrp-Result-r14': 9
                                                }
                                            ]
                                        }
                                    }
                                }
                            )
                        )
                    }
                )
            )
        }

        encoded = (
            b'\x92\x00\x28\x09\x00\xa0\x03\x38\x80\xab\x01\xc0\xe0\x8b\x80\x00'
            b'\xa0\x48\x00'
        )

        self.assert_encode_decode(lpp, 'LPP-Message', decoded, encoded)

    def test_etsi_cam_pdu_descriptions_1_3_2(self):
        files = [
            'tests/files/etsi/cam_pdu_descriptions_1_3_2.asn',
            'tests/files/etsi/its_container_1_2_1.asn'
        ]
        cam = asn1tools.compile_files(files, 'uper')

        # Message 1.
        decoded = {
            'header': {
                'protocolVersion': 1,
                'messageID': 1,
                'stationID': 4294967295
            },
            'cam': {
                'generationDeltaTime': 65535,
                'camParameters': {
                    'basicContainer': {
                        'stationType': 2,
                        'referencePosition': {
                            'latitude': -900000000,
                            'longitude': 1800000001,
                            'positionConfidenceEllipse': {
                                'semiMajorConfidence': 333,
                                'semiMinorConfidence': 324,
                                'semiMajorOrientation': 3601
                            },
                            'altitude': {
                                'altitudeValue': -100000,
                                'altitudeConfidence': 'alt-000-50'
                            }
                        }
                    },
                    'highFrequencyContainer': (
                        'basicVehicleContainerHighFrequency',
                        {
                            'heading': {
                                'headingValue': 22,
                                'headingConfidence': 36
                            },
                            'speed': {
                                'speedValue': 16383,
                                'speedConfidence': 100
                            },
                            'driveDirection': 'backward',
                            'vehicleLength': {
                                'vehicleLengthValue': 1000,
                                'vehicleLengthConfidenceIndication': 'unavailable'
                            },
                            'vehicleWidth': 1,
                            'longitudinalAcceleration': {
                                'longitudinalAccelerationValue': -140,
                                'longitudinalAccelerationConfidence': 1
                            },
                            'curvature': {
                                'curvatureValue': 0,
                                'curvatureConfidence': 'outOfRange'
                            },
                            'curvatureCalculationMode': 'yawRateNotUsed',
                            'yawRate': {
                                'yawRateValue': 0,
                                'yawRateConfidence': 'degSec-100-00'
                            }
                        }
                    )
                }
            }
        }

        encoded = (
            b'\x01\x01\xff\xff\xff\xff\xff\xff\x00\x20\x00\x00\x00\x1a\xd2\x74'
            b'\x80\x22\x9a\x28\x9c\x22\x00\x00\x0a\x00\x01\x64\x7f\xff\xe3\x7e'
            b'\x78\x00\x50\x0b\xa9\x86\x2f\xff\xcc'
        )

        self.assert_encode_decode(cam, 'CAM', decoded, encoded)

        # Message 2.
        decoded = {
            'header': {
                'protocolVersion': 2,
                'messageID': 3,
                'stationID': 294967295
            },
            'cam': {
                'generationDeltaTime': 65534,
                'camParameters': {
                    'basicContainer': {
                        'stationType': 2,
                        'referencePosition': {
                            'latitude': -900000000,
                            'longitude': 1800000001,
                            'positionConfidenceEllipse': {
                                'semiMajorConfidence': 333,
                                'semiMinorConfidence': 324,
                                'semiMajorOrientation': 3601
                            },
                            'altitude': {
                                'altitudeValue': -100000,
                                'altitudeConfidence': 'alt-000-50'
                            }
                        }
                    },
                    'highFrequencyContainer': (
                        'basicVehicleContainerHighFrequency',
                        {
                            'heading': {
                                'headingValue': 22,
                                'headingConfidence': 36
                            },
                            'speed': {
                                'speedValue': 16383,
                                'speedConfidence': 100
                            },
                            'driveDirection': 'backward',
                            'vehicleLength': {
                                'vehicleLengthValue': 1000,
                                'vehicleLengthConfidenceIndication': 'unavailable'
                            },
                            'vehicleWidth': 1,
                            'longitudinalAcceleration': {
                                'longitudinalAccelerationValue': -140,
                                'longitudinalAccelerationConfidence': 1
                            },
                            'curvature': {
                                'curvatureValue': 0,
                                'curvatureConfidence': 'outOfRange'
                            },
                            'curvatureCalculationMode': 'yawRateNotUsed',
                            'yawRate': {
                                'yawRateValue': 0,
                                'yawRateConfidence': 'degSec-100-00'
                            },
                            'cenDsrcTollingZone': {
                                'protectedZoneLatitude': 888,
                                'protectedZoneLongitude': 92323,
                                'cenDsrcTollingZoneID': 0
                            }
                        }
                    )
                }
            }
        }

        encoded = (
            b'\x02\x03\x11\x94\xd7\xff\xff\xfe\x00\x20\x00\x00\x00\x1a\xd2\x74'
            b'\x80\x22\x9a\x28\x9c\x22\x00\x00\x0a\x01\x01\x64\x7f\xff\xe3\x7e'
            b'\x78\x00\x50\x0b\xa9\x86\x2f\xff\xcd\x6b\x49\xd8\xf0\xd6\x96\x75'
            b'\x46\x00\x00\x00\x00'
        )

        self.assert_encode_decode(cam, 'CAM', decoded, encoded)

        # Message 3.
        decoded = {
            'header': {
                'protocolVersion': 2,
                'messageID': 4,
                'stationID': 24967295
            },
            'cam': {
                'generationDeltaTime': 65534,
                'camParameters': {
                    'basicContainer': {
                        'stationType': 2,
                        'referencePosition': {
                            'latitude': -900000000,
                            'longitude': 1800000001,
                            'positionConfidenceEllipse': {
                                'semiMajorConfidence': 333,
                                'semiMinorConfidence': 324,
                                'semiMajorOrientation': 3601
                            },
                            'altitude': {
                                'altitudeValue': -100000,
                                'altitudeConfidence': 'alt-000-50'
                            }
                        }
                    },
                    'highFrequencyContainer': (
                        'rsuContainerHighFrequency',
                        {
                            'protectedCommunicationZonesRSU': [
                                {
                                    'protectedZoneType': 'cenDsrcTolling',
                                    'protectedZoneLatitude': 332,
                                    'protectedZoneLongitude': 123,
                                    'protectedZoneRadius': 255
                                }
                            ]
                        }
                    )
                }
            }
        }

        encoded = (
            b'\x02\x04\x01\x7c\xf8\x7f\xff\xfe\x00\x20\x00\x00\x00\x1a\xd2\x74'
            b'\x80\x22\x9a\x28\x9c\x22\x00\x00\x0a\xa0\x8d\x69\x3a\x93\x1a\xd2'
            b'\x74\x9e\xdf\xc0'
        )

        self.assert_encode_decode(cam, 'CAM', decoded, encoded)

    def test_etsi_its_container_1_2_1(self):
        its = asn1tools.compile_files('tests/files/etsi/its_container_1_2_1.asn',
                                      'uper')

        # Message 1.
        decoded = [
            [],
            [],
            [
                {
                    'pathPosition': {
                        'deltaLatitude': 44,
                        'deltaLongitude': -1,
                        'deltaAltitude': 0
                    },
                    'pathDeltaTime': 1
                }
            ]
        ]

        encoded = (
            b'\x40\x00\x0e\x00\x2b\x7f\xff\x98\xce\x00\x00\x00'
        )

        self.assert_encode_decode(its, 'Traces', decoded, encoded)

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'uper')

        self.assertEqual(repr(all_types.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(all_types.types['Integer']), 'Integer(Integer)')
        self.assertEqual(repr(all_types.types['Real']), 'Real(Real)')
        self.assertEqual(repr(all_types.types['Bitstring']), 'BitString(Bitstring)')
        self.assertEqual(repr(all_types.types['Octetstring']),
                         'OctetString(Octetstring)')
        self.assertEqual(repr(all_types.types['Null']), 'Null(Null)')
        self.assertEqual(repr(all_types.types['Objectidentifier']),
                         'ObjectIdentifier(Objectidentifier)')
        self.assertEqual(repr(all_types.types['Enumerated']),
                         'Enumerated(Enumerated)')
        self.assertEqual(repr(all_types.types['Utf8string']),
                         'UTF8String(Utf8string)')
        self.assertEqual(repr(all_types.types['Sequence']), 'Sequence(Sequence, [])')
        self.assertEqual(repr(all_types.types['Set']), 'Set(Set, [])')
        self.assertEqual(repr(all_types.types['Sequence2']),
                         'Sequence(Sequence2, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Set2']), 'Set(Set2, [Integer(a)])')
        self.assertEqual(repr(all_types.types['Numericstring']),
                         'NumericString(Numericstring)')
        self.assertEqual(repr(all_types.types['Printablestring']),
                         'PrintableString(Printablestring)')
        self.assertEqual(repr(all_types.types['Ia5string']), 'IA5String(Ia5string)')
        self.assertEqual(repr(all_types.types['Universalstring']),
                         'UniversalString(Universalstring)')
        self.assertEqual(repr(all_types.types['Visiblestring']),
                         'VisibleString(Visiblestring)')
        self.assertEqual(repr(all_types.types['Generalstring']),
                         'GeneralString(Generalstring)')
        self.assertEqual(repr(all_types.types['Bmpstring']),
                         'BMPString(Bmpstring)')
        self.assertEqual(repr(all_types.types['Teletexstring']),
                         'TeletexString(Teletexstring)')
        self.assertEqual(repr(all_types.types['Graphicstring']),
                         'GraphicString(Graphicstring)')
        self.assertEqual(repr(all_types.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(all_types.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(all_types.types['SetOf']), 'SetOf(SetOf, Integer())')
        self.assertEqual(repr(all_types.types['Any']), 'Any(Any)')
        self.assertEqual(repr(all_types.types['Sequence12']),
                         'Sequence(Sequence12, [SequenceOf(a, Recursive(Sequence12))])')

    def test_all_types_automatic_tags(self):
        all_types = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn', 'uper')

        datas = [
            ('Sequence3',
             {'a': 1, 'c': 2,'d': True},
             b'\x00\x80\x80\x81\x40')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_containing(self):
        """CONTAINING is currently not automatically encoded/decoded. Should
        it? Sometimes the contained data is pre-encoded, prior to this
        encoding.

        """

        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b OCTET STRING (CONTAINING A)"
            "} "
            "END",
            'uper')

        datas = [
            ('B', {'a': False, 'b': b'\x80'}, b'\x00\xc0\x00')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_error_out_of_data(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "B ::= SEQUENCE { "
            "  a SEQUENCE { "
            "    b BOOLEAN, "
            "    c INTEGER "
            "  } "
            "} "
            "END",
            'uper')

        datas = [
            ('A', b'',         'out of data at bit offset 0 (0.0 bytes)'),
            ('B', b'\x00',     'a: c: out of data at bit offset 1 (0.1 bytes)'),
            ('B', b'\x80\x80', 'a: c: out of data at bit offset 9 (1.1 bytes)')
        ]

        for type_name, encoded, message in datas:
            with self.assertRaises(asn1tools.codecs.per.OutOfDataError) as cm:
                foo.decode(type_name, encoded)

            self.assertEqual(str(cm.exception), message)

    def test_oma_ulp(self):
        ulp = asn1tools.compile_dict(deepcopy(OMA_ULP), 'uper')

        decoded = {
            'length': 162,
            'version': {'maj': 2, 'min': 0, 'servind': 0},
            'sessionID': {
                'setSessionID': {
                    'sessionId': 8838,
                    'setId': ('imsi', b'\x64\x00\x00\x00\x00\x00\x20\xf2')
                },
                'slpSessionID': {
                    'sessionID': b'\x00\x00\x40\x00',
                    'slpId': ('iPAddress', ('ipv4Address', b'\x7f\x00\x00\x01'))
                }
            },
            'message': (
                'msSUPLPOSINIT', {
                    'sETCapabilities': {
                        'posTechnology': {
                            'agpsSETassisted': True,
                            'agpsSETBased': True,
                            'autonomousGPS': False,
                            'aFLT': False,
                            'eCID': True,
                            'eOTD': False,
                            'oTDOA': True,
                            'ver2-PosTechnology-extension': {
                                'gANSSPositionMethods': [
                                    {
                                        'ganssId': 4,
                                        'gANSSPositioningMethodTypes': {
                                            'setAssisted': True,
                                            'setBased': True,
                                            'autonomous': True
                                        },
                                        'gANSSSignals': (b'\x80', 1)
                                    }
                                ]
                            }
                        },
                        'prefMethod': 'noPreference',
                        'posProtocol': {
                            'tia801': False,
                            'rrlp': False,
                            'rrc': False,
                            'ver2-PosProtocol-extension': {
                                'lpp': True,
                                'posProtocolVersionLPP': {
                                    'majorVersionField': 12,
                                    'technicalVersionField': 4,
                                    'editorialVersionField': 0
                                }
                            }
                        }
                    },
                    'locationId': {
                        'cellInfo': (
                            'ver2-CellInfo-extension', (
                                'lteCell',
                                {
                                    'cellGlobalIdEUTRA': {
                                        'plmn-Identity': {
                                            'mcc': [3, 1, 0],
                                            'mnc': [3, 1, 0]
                                        },
                                        'cellIdentity': (b'\x34\xa3\x20\x20', 28)
                                    },
                                    'physCellId': 304,
                                    'trackingAreaCode': (b'\x13\x8e', 16),
                                    'rsrpResult': 59,
                                    'rsrqResult': 24,
                                    'tA': 1,
                                    'measResultListEUTRA': [
                                        {
                                            'physCellId': 275,
                                            'measResult': {
                                                'rsrpResult': 45,
                                                'rsrqResult': 14
                                            }
                                        },
                                        {
                                            'physCellId': 200,
                                            'measResult': {
                                                'rsrpResult': 39,
                                                'rsrqResult': 8
                                            }
                                        }
                                    ]
                                }
                            )
                        ),
                        'status': 'current'
                    },
                    'sUPLPOS': {
                        'posPayLoad': (
                            'ver2-PosPayLoad-extension',
                            {
                                'lPPPayload': [
                                    b'\x92\x2b\x08\x31\xe2\x00\x5d\x00\x82\x17'
                                    b'\x40\x27\x04\x88\x22\x1b\x80\x00\x2d\xe4'
                                    b'\x00\x00\x41\x88\x3c\x09\x24\x30\x44\x18'
                                    b'\xb3\x18\x66\x8f\xc0\x03\x24\x01\x01',
                                    b'\x92\x2c\x10\x62\x62\x13\x10\x34\xa3\x20'
                                    b'\x26\xa4\x01\x40\x84\x00\x00\x00\x00\x01'
                                    b'\x41\x20\x02\x00\x00\x00\x00'
                                ]
                            }
                        )
                    },
                    'ver': (b'\x52\x88\xec\xab\xa9\x37\x5c\x4e', 64)
                }
            )
        }

        encoded = (
            b'\x00\xa2\x02\x00\x00\xc8\xa1\x8d\x90\x00\x00\x00\x00\x00\x83'
            b'\xc8\x00\x01\x00\x00\x3f\x80\x00\x00\x98\xdc\xa0\x20\x68\x08'
            b'\xe2\x14\x00\x82\x06\x0c\x04\x00\x20\x05\x49\xe9\x88\x4c\x40'
            b'\xd2\x8c\x80\xa6\x02\x71\xce\xd8\x00\x25\x13\x6b\x4e\x32\x1a'
            b'\x72\x09\x00\x8e\x90\x02\x69\x22\xb0\x83\x1e\x20\x05\xd0\x08'
            b'\x21\x74\x02\x70\x48\x82\x21\xb8\x00\x02\xde\x40\x00\x04\x18'
            b'\x83\xc0\x92\x43\x04\x41\x8b\x31\x86\x68\xfc\x00\x32\x40\x10'
            b'\x10\x01\xa9\x22\xc1\x06\x26\x21\x31\x03\x4a\x32\x02\x6a\x40'
            b'\x14\x08\x40\x00\x00\x00\x00\x14\x12\x00\x20\x00\x00\x00\x00'
            b'\xa5\x11\xd9\x57\x52\x6e\xb8\x9c'
        )

        self.assert_encode_decode(ulp, 'ULP-PDU', decoded, encoded)


if __name__ == '__main__':
    unittest.main()
