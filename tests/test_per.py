#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools
import sys
from copy import deepcopy

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from s1ap_14_4_0 import EXPECTED as S1AP_14_4_0
from x691_a4 import EXPECTED as X691_A4


class Asn1ToolsPerTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_boolean(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BOOLEAN "
            "B ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b BOOLEAN "
            "} "
            "END",
            'per')

        datas = [
            ('A',                     True, b'\x80'),
            ('A',                    False, b'\x00'),
            ('B', {'a': False, 'b': False}, b'\x00'),
            ('B',  {'a': True, 'b': False}, b'\x80'),
            ('B',  {'a': False, 'b': True}, b'\x40'),
            ('B',   {'a': True, 'b': True}, b'\xc0')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'')

        self.assertEqual(str(cm.exception),
                         'out of data at bit offset 0 (0.0 bytes)')

    def test_integer(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= INTEGER "
            "B ::= INTEGER (5..99) "
            "C ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b INTEGER, "
            "  c BOOLEAN, "
            "  d INTEGER (-10..400) "
            "} "
            "D ::= INTEGER (0..254) "
            "E ::= INTEGER (0..255) "
            "F ::= INTEGER (0..256) "
            "G ::= INTEGER (0..65535) "
            "H ::= INTEGER (0..65536) "
            "I ::= INTEGER (0..10000000000) "
            "J ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b INTEGER (0..254), "
            "  c INTEGER (0..255), "
            "  d BOOLEAN, "
            "  e INTEGER (0..256) "
            "} "
            "K ::= B (6..7) "
            "L ::= SEQUENCE { "
            "  a K (7..7) "
            "} "
            "M ::= INTEGER (5..99, ..., 101..105) "
            "N ::= INTEGER (0..65535) "
            "O ::= INTEGER (0..65536) "
            "P ::= INTEGER (0..2147483647) "
            "Q ::= INTEGER (0..4294967295) "
            "R ::= INTEGER (0..4294967296) "
            "END",
            'per')

        datas = [
            ('A',                    32768, b'\x03\x00\x80\x00'),
            ('A',                    32767, b'\x02\x7f\xff'),
            ('A',                      256, b'\x02\x01\x00'),
            ('A',                      255, b'\x02\x00\xff'),
            ('A',                      128, b'\x02\x00\x80'),
            ('A',                      127, b'\x01\x7f'),
            ('A',                        2, b'\x01\x02'),
            ('A',                        1, b'\x01\x01'),
            ('A',                        0, b'\x01\x00'),
            ('A',                       -1, b'\x01\xff'),
            ('A',                     -128, b'\x01\x80'),
            ('A',                     -129, b'\x02\xff\x7f'),
            ('A',                     -256, b'\x02\xff\x00'),
            ('A',                   -32768, b'\x02\x80\x00'),
            ('A',                   -32769, b'\x03\xff\x7f\xff'),
            ('B',                        5, b'\x00'),
            ('B',                        6, b'\x02'),
            ('B',                       99, b'\xbc'),
            ('C',
             {'a': True, 'b': 43554344223, 'c': False, 'd': -9},
             b'\x80\x05\x0a\x24\x0a\x8d\x1f\x00\x00\x01'),
            ('D',                      253, b'\xfd'),
            ('E',                      253, b'\xfd'),
            ('F',                      253, b'\x00\xfd'),
            ('G',                      253, b'\x00\xfd'),
            ('H',                      253, b'\x00\xfd'),
            ('H',                      256, b'\x40\x01\x00'),
            ('H',                    65536, b'\x80\x01\x00\x00'),
            ('I',                        0, b'\x00\x00'),
            ('I',                        1, b'\x00\x01'),
            ('I',              10000000000, b'\x80\x02\x54\x0b\xe4\x00'),
            ('J',
             {'a': False, 'b': 253, 'c': 253, 'd': False, 'e': 253},
             b'\x7e\x80\xfd\x00\x00\xfd'),
            ('K',                        7, b'\x80'),
            ('L',                 {'a': 7}, b''),
            ('M',                      103, b'\x80\x01\x67'),
            ('N',                        1, b'\x00\x01'),
            ('N',                      255, b'\x00\xff'),
            ('N',                      256, b'\x01\x00'),
            ('N',                    65535, b'\xff\xff'),
            ('O',                        1, b'\x00\x01'),
            ('O',                      255, b'\x00\xff'),
            ('O',                      256, b'\x40\x01\x00'),
            ('O',                    65535, b'\x40\xff\xff'),
            ('O',                    65536, b'\x80\x01\x00\x00'),
            ('P',                        1, b'\x00\x01'),
            ('P',                      255, b'\x00\xff'),
            ('P',                      256, b'\x40\x01\x00'),
            ('P',                    65535, b'\x40\xff\xff'),
            ('P',                    65536, b'\x80\x01\x00\x00'),
            ('P',                 16777215, b'\x80\xff\xff\xff'),
            ('P',                 16777216, b'\xc0\x01\x00\x00\x00'),
            ('P',                100000000, b'\xc0\x05\xf5\xe1\x00'),
            ('Q',               4294967295, b'\xc0\xff\xff\xff\xff'),
            ('R',               4294967296, b'\x80\x01\x00\x00\x00\x00')
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
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b BIT STRING (SIZE(1)), "
            "  c BIT STRING (SIZE(16)) "
            "} "
            "F ::= BIT STRING { "
            "  a (0), "
            "  b (1), "
            "  c (2) "
            "} "
            "G ::= SEQUENCE { "
            "  a BIT STRING, "
            "  b BOOLEAN "
            "} "
            "END",
            'per')

        datas = [
            ('A',          (b'\x40', 4), b'\x04\x40'),
            ('A',
             (299 * b'\x55' + b'\x54', 2399),
             b'\x89\x5f' + 299 * b'\x55' + b'\x54'),
            ('A',
             (2048 * b'\x55', 16384),
             b'\xc1' + 2048 * b'\x55' + b'\x00'),
            ('B',      (b'\x12\x80', 9), b'\x12\x80'),
            ('C',          (b'\x34', 6), b'\x40\x34'),
            ('D',
             {'a': True, 'b': (b'\x40', 4)},
             b'\x80\x04\x40'),
            ('E',
             {'a': True, 'b': (b'\x80', 1), 'c': (b'\x7f\x01', 16)},
             b'\xdf\xc0\x40'),
            ('F',          (b'\x80', 1), b'\x01\x80'),
            ('F',          (b'\xe0', 3), b'\x03\xe0'),
            ('F',          (b'\x01', 8), b'\x08\x01'),
            ('G',
             {'a': (b'\x80', 2), 'b': True},
             b'\x02\xa0'),
            ('G',
             {'a': (b'', 0), 'b': True},
             b'\x00\x80'),
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Trailing zero bits should be stripped when encoding named
        # bit list. Default value is not encoded, but part of
        # decoded. Also ignore dangling bits.
        datas = [
            ('F',          (b'\x80', 2), b'\x01\x80', (b'\x80', 1)),
            ('F',          (b'\x40', 3), b'\x02\x40', (b'\x40', 2)),
            ('F',          (b'\x00', 3), b'\x00',     (b'', 0)),
            ('F',          (b'\x00', 8), b'\x00',     (b'', 0))
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
            "F ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b OCTET STRING (SIZE(1)), "
            "  c OCTET STRING (SIZE(2)) "
            "} "
            "G ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b OCTET STRING (SIZE(3)) "
            "} "
            "H ::= OCTET STRING (SIZE (65535)) "
            "I ::= OCTET STRING (SIZE (65536)) "
            "J ::= OCTET STRING (SIZE (1..MAX)) "
            "K ::= OCTET STRING (SIZE (MIN..5)) "
            "END",
            'per')

        datas = [
            ('A',                           b'\x00', b'\x01\x00'),
            ('A',                     500 * b'\x00', b'\x81\xf4' + 500 * b'\x00'),
            ('B',                       b'\xab\xcd', b'\xab\xcd'),
            ('C',                   b'\xab\xcd\xef', b'\xab\xcd\xef'),
            ('D',               b'\x89\xab\xcd\xef', b'\x20\x89\xab\xcd\xef'),
            ('E',         {'a': True, 'b': b'\x00'}, b'\x80\x01\x00'),
            ('E', {'a': True, 'b': b'\x00\x01\x02'}, b'\x80\x03\x00\x01\x02'),
            ('F',
             {'a': True, 'b': b'\x12', 'c': b'\x34\x56'},
             b'\x89\x1a\x2b\x00'),
            ('G', {'a': True, 'b': b'\x00\x01\x02'}, b'\x80\x00\x01\x02'),
            ('H',     32767 * b'\x01\x02' + b'\x01', 32767 * b'\x01\x02' + b'\x01'),
            ('I',
             32768 * b'\x01\x02',
             b'\xc4' + 32768 * b'\x01\x02'
             + b'\x00'),
            ('A',
             4095 * b'\x00\x01\x02\x03' + b'\x00\x01\x02',
             b'\xbf\xff' + 4095 * b'\x00\x01\x02\x03' + b'\x00\x01\x02'),
            ('A',
             4095 * b'\x00\x01\x02\x03' + b'\x00\x01\x02\x03',
             b'\xc1' + 4095 * b'\x00\x01\x02\x03' + b'\x00\x01\x02\x03'
             + b'\x00'),
            ('A',
             4095 * b'\x00\x01\x02\x03' + b'\x00\x01\x02\x03\x00',
             b'\xc1' + 4095 * b'\x00\x01\x02\x03' + b'\x00\x01\x02\x03'
             + b'\x01' + b'\x00'),
            ('J',                           b'\x12', b'\x01\x12'),
            ('K',                               b'', b'\x00')
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
            'per')

        datas = [
            ('A',                   '1.2', b'\x01\x2a'),
            ('A',              '1.2.3321', b'\x03\x2a\x99\x79'),
            ('B', {'a': True, 'b': '1.2'}, b'\x80\x01\x2a')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_external(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= EXTERNAL "
            "END",
            'per')

        datas = [
            ('A',    {'encoding': ('octet-aligned', b'\x12')}, b'\x08\x01\x12')
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
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b B "
            "} "
            "F ::= SEQUENCE {"
            "  a ENUMERATED { zero(0), one(1) } DEFAULT one"
            "}"
            "END",
            'per')

        datas = [
            ('A',                    'one', b''),
            ('B',                   'zero', b'\x00'),
            ('B',                    'one', b'\x40'),
            ('C',                    'one', b'\x00'),
            ('C',                    'two', b'\x20'),
            ('C',                   'four', b'\x40'),
            ('C',                    'six', b'\x80'),
            ('C',                   'nine', b'\x81'),
            ('D',                     'aa', b'\x80'),
            ('D',                     'cl', b'\xbf'),
            ('D',                     'cm', b'\xc0\x50\x00'),
            ('D',                     'jv', b'\xc0\x7f\xc0'),
            ('D',                     'jw', b'\xc0\x80\x40\x00'),
            ('D',                     'jz', b'\xc0\x80\x40\xc0'),
            ('E', {'a': True, 'b': 'zero'}, b'\x80'),
            ('E',  {'a': True, 'b': 'one'}, b'\xa0'),
            ('F', {'a': 'zero'}, b'\x80'),
            ('F',  {'a': 'one'}, b'\x00')        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Default value is not encoded, but part of decoded.
        datas = [
            ('F', {}, b'\x00', {'a': 'one'})
        ]

        for type_name, decoded_1, encoded_1, decoded_2 in datas:
            self.assertEqual(foo.encode(type_name, decoded_1), encoded_1)
            self.assertEqual(foo.decode(type_name, encoded_1), decoded_2)

        # Bad root index.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('C', b'\x70')

        self.assertEqual(str(cm.exception),
                         "Expected enumeration index 0, 1 or 2, but got 3.")

        # Bad additions index.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('C', b'\x8f')

        self.assertEqual(str(cm.exception),
                         "Expected enumeration index 0 or 1, but got 15.")

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
            "  a OCTET STRING, "
            "  b INTEGER "
            "} "
            "END",
            'per')

        datas = [
            ('A',                                {}, b''),
            ('O',                                {}, b'\x00'),
            ('B',                          {'a': 0}, b'\x00'),
            ('B',                          {'a': 1}, b'\x80\x01\x01'),
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
            ('O',                       {'a': True}, b'\x80\x80\x01\x80'),
            ('O',                      {'a': False}, b'\x80\x80\x01\x00'),
            ('P',            {'a': True, 'b': True}, b'\x80\x80\x01\x40'),
            ('P',           {'a': True, 'b': False}, b'\x80\x80\x01\xc0'),
            ('D',            {'a': True, 'b': True}, b'\xc0\x40\x01\x80'),
            ('E',            {'a': True, 'b': True}, b'\xc0\x40\x01\x80'),
            ('F',            {'a': True, 'c': True}, b'\x60'),
            ('G',            {'a': True, 'd': True}, b'\x60'),
            ('I',            {'a': True, 'b': True}, b'\xc0\x40\x01\x80'),
            ('J',            {'a': True, 'b': True}, b'\xc0\x40\x01\x80'),
            ('K',            {'a': True, 'b': True}, b'\xc0\xc0\x01\x80'),
            ('F', {'a': True, 'b': True, 'c': True}, b'\xe0\x20\x01\x80'),
            ('K', {'a': True, 'b': True, 'c': True}, b'\xc0\xe0\x01\x80\x01\x80'),
            ('L', {'a': True, 'b': True, 'c': True}, b'\xc0\x40\x01\xc0'),
            ('G', {'a': True, 'b': True, 'd': True}, b'\xe0\x60\x01\x80'),
            ('G',
             {'a': True, 'b': True, 'c': True, 'd': True},
             b'\xe0\x70\x01\x80\x01\x80'),
            ('M',
             {'a': True, 'b': {'a': 5}, 'c': True},
             b'\xc0\x40\x04\x80\x01\x05\x80'),
            ('Q',      {'a': {'a': True}, 'b': 100}, b'\x40\x01\x64'),
            ('R',
             {'a': {'a': True, 'b': True}, 'b': 100},
             b'\xc0\x40\x01\x80\x01\x64'),
            ('S',
             {'a': True, 'b': {'a': True, 'b': True}},
             b'\xc0\x40\x01\x70'),
            ('T',                       {'a': [{}]}, b'\x80\x01\x00'),
            ('T',                {'a': [{'a': []}]}, b'\x80\x01\x80\x00'),
            ('V',
             {'a': 5000 * b'\x00', 'b': 1000},
             b'\x81\xc0\x93\x8a\x93\x88' + 5000 * b'\x00' + b'\x03\x02\x03\xe8')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Non-symmetrical encoding and decoding because default values
        # are not encoded, but part of the decoded (given that the
        # root and addition is present).
        self.assertEqual(foo.encode('N', {}), b'\x00')
        self.assertEqual(foo.decode('N', b'\x00'), {'a': True})
        self.assertEqual(foo.encode('P', {'a': True}), b'\x80\x80\x01\x40')
        self.assertEqual(foo.decode('P', b'\x80\x80\x01\x40'),
                         {'a': True, 'b': True})

        # Decode D as C. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('C', b'\xc0\x40\x01\x80'), {'a': True})

        # Decode R as Q. Extension addition "a.b" should be skipped.
        self.assertEqual(foo.decode('Q', b'\xc0\x40\x01\x80\x01\x64'),
                         {'a': {'a': True}, 'b': 100})

        # Decode error of present addition member (out of data).
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('U', b'\x80\x80\x03\x02\x05')

        self.assertEqual(str(cm.exception),
                         'a: a: out of data at bit offset 32 (4.0 bytes)')

        # Missing root member.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('K', {'b': True})

        self.assertEqual(str(cm.exception),
                         "Sequence member 'a' not found in {'b': True}.")

    def test_sequence_of(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE OF INTEGER "
            "B ::= SEQUENCE SIZE (2) OF INTEGER "
            "C ::= SEQUENCE SIZE (1..5) OF INTEGER "
            "D ::= SEQUENCE SIZE (1..2, ...) OF INTEGER "
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b SEQUENCE OF INTEGER "
            "} "
            "F ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b SEQUENCE SIZE(1) OF INTEGER "
            "} "
            "G ::= SEQUENCE SIZE (1..2, ..., 6..7) OF INTEGER "
            "H ::= SEQUENCE SIZE (1..MAX) OF INTEGER "
            "END",
            'per')

        datas = [
            ('A',                [], b'\x00'),
            ('A',               [1], b'\x01\x01\x01'),
            ('A',            [1, 2], b'\x02\x01\x01\x01\x02'),
            ('A',     1000 * [1, 2], b'\x87\xd0' + 1000 * b'\x01\x01\x01\x02'),
            ('A',       16384 * [1], b'\xc1' + 16384 * b'\x01\x01' + b'\x00'),
            ('A',
             65535 * [1],
             b'\xc3' + 49152 * b'\x01\x01' + b'\xbf\xff' + 16383 * b'\x01\x01'),
            ('A',
             100000 * [1],
             b'\xc4' + 65536 * b'\x01\x01'
             + b'\xc2' + 32768 * b'\x01\x01'
             + b'\x86\xa0' + 1696 * b'\x01\x01'),
            ('B',            [1, 2], b'\x01\x01\x01\x02'),
            ('B', [4663, 222322233], b'\x02\x12\x37\x04\x0d\x40\x5e\x39'),
            ('C',               [1], b'\x00\x01\x01'),
            ('C',            [1, 2], b'\x20\x01\x01\x01\x02'),
            ('D',            [2, 1], b'\x40\x01\x02\x01\x01'),
            ('E',  {'a': False, 'b': []}, b'\x00\x00'),
            ('E', {'a': False, 'b': [1]}, b'\x00\x01\x01\x01'),
            ('F', {'a': False, 'b': [1]}, b'\x00\x01\x01'),
            ('H',               [1], b'\x01\x01\x01')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Decode value in extension.
        with self.assertRaises(NotImplementedError) as cm:
            foo.decode(
                'G',
                b'\x80\x06\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01')

        self.assertEqual(str(cm.exception), 'Extension is not yet implemented.')

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
            "END",
            'per')

        datas = [
            ('A',            ('a', True), b'\x80'),
            ('B',            ('a', True), b'\x40'),
            ('C',            ('a', True), b'\x20'),
            ('C',               ('b', 1), b'\x40\x01\x01'),
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
            ('J',            ('c', True), b'\x81\x01\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Bad root index.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('K', b'\x70')

        self.assertEqual(str(cm.exception),
                         "Expected choice index 0, 1 or 2, but got 3.")

        # Bad additions index.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('K', b'\x8f')

        self.assertEqual(str(cm.exception),
                         "Expected choice index 0, 1, 2, 3 or 4, but got 15.")

        # Bad value.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('K', ('i', True))

        self.assertEqual(
            str(cm.exception),
            "Expected choice 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h', but "
            "got 'i'.")

        # Bad value.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', ('b', True))

        self.assertEqual(str(cm.exception), "Expected choice 'a', but got 'b'.")

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
            'per')

        datas = [
            ('A', {'a': True, 'b': u''}, b'\x40\x00'),
            ('A',
             {'a': True, 'b': u'1', 'c': u'foo'},
             b'\xc0\x01\x31\x03\x66\x6f\x6f'),
            ('A',
             {'a': True, 'b': 300 * u'1'},
             b'\x40\x81\x2c' + 300 * b'\x31'),
            ('B',
             u'1234567890',
             b'\x0a\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30'),
            ('C',                   u'', b'\x00'),
            ('C',                  u'P', b'\x01\x50'),
            ('D',                u'agg', b'\x03\x61\x67\x67'),
            ('E',                u'bar', b'\x03\x62\x61\x72'),
            ('E',           u'a\u1010c', b'\x05\x61\xe1\x80\x90\x63'),
            ('E',
             15000 * u'123' + u'\u1010',
             b'\xc2' + 10922 * b'123' + b'12\xaf\xcb3' + 4077 * b'123'
             + b'\xe1\x80\x90'),
            ('E',               u'1𐈃Q', b'\x06\x31\xf0\x90\x88\x83\x51')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x40\xc5\x00\x00\x00\x00')

        self.assertEqual(str(cm.exception),
                         'b: Bad length determinant fragmentation value 0xc5.')

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'\x40\xc1\x00\x00\x00\x00')

        self.assertEqual(str(cm.exception),
                         'b: out of data at bit offset 16 (2.0 bytes)')

    def test_numeric_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NumericString (FROM (\"0\"..\"2\", ..., \"4\"..\"5\")) "
            "B ::= NumericString (SIZE (1..4)) "
            "C ::= NumericString (SIZE (1..4, ...)) "
            "D ::= NumericString (SIZE (1..4, ..., 6..7)) "
            "E ::= NumericString (SIZE (0..MAX)) "
            "F ::= NumericString (SIZE (2..MAX)) "
            "END",
            'per')

        datas = [
            ('A',                  '2', b'\x01\x30'),
            ('B',               '1234', b'\xc0\x23\x45'),
            ('C',               '1234', b'\x60\x23\x45'),
            ('D',               '1234', b'\x60\x23\x45'),
            ('E',                   '', b'\x00'),
            ('F',                '345', b'\x03\x45\x60')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Encode size extension is not yet supported.
        with self.assertRaises(NotImplementedError) as cm:
            foo.encode('D', '123456')

        self.assertEqual(
            str(cm.exception),
            "String size extension is not yet implemented.")

        # Decode size extension is not yet supported.
        with self.assertRaises(NotImplementedError) as cm:
            foo.decode('D', b'\x80\x06\x23\x45\x67')

        self.assertEqual(
            str(cm.exception),
            "String size extension is not yet implemented.")

    def test_ia5_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= IA5String "
            "END",
            'per')

        datas = [
            ('A',
             1638 * '1234567890' + '123',
             b'\xbf\xff'
             + 1638 * b'\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30'
             + b'\x31\x32\x33'),
            ('A',
             1638 * '1234567890' + '1234',
             b'\xc1'
             + 1638 * b'\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30'
             + b'\x31\x32\x33\x34'
             + b'\x00'),
            ('A',
             1638 * '1234567890' + '12345',
             b'\xc1'
             + 1638 * b'\x31\x32\x33\x34\x35\x36\x37\x38\x39\x30'
             + b'\x31\x32\x33\x34'
             + b'\x01'
             + b'\x35')
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
            "D ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (1)) "
            "} "
            "E ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (2)) "
            "} "
            "F ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (3)) "
            "} "
            "G ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (0..1)) "
            "} "
            "H ::= SEQUENCE { "
            "  a BOOLEAN, "
            "  b VisibleString (SIZE (0..2)) "
            "} "
            "I ::= VisibleString (FROM (\"a\"..\"z\")) (SIZE (1..255)) "
            "J ::= VisibleString (FROM (\"a\")) "
            "K ::= VisibleString (FROM (\"a\"..\"a\")) "
            "END",
            'per')

        datas = [
            ('A',
             'HejHoppHappHippAbcde',
             b'\x02\x48\x65\x6a\x48\x6f\x70\x70\x48\x61\x70\x70\x48\x69\x70\x70'
             b'\x41\x62\x63\x64\x65'),
            ('B', 'Hejaa', b'\x48\x65\x6a\x61\x61'),
            ('C',
             17 * 'HejHoppHappHippAbcde',
             b'\x01\x41' + 17 * (b'\x48\x65\x6a\x48\x6f\x70\x70\x48\x61\x70'
                                 b'\x70\x48\x69\x70\x70\x41\x62\x63\x64\x65')),
            ('D',   {'a': True, 'b': '1'}, b'\x98\x80'),
            ('E',  {'a': True, 'b': '12'}, b'\x98\x99\x00'),
            ('F', {'a': True, 'b': '123'}, b'\x80\x31\x32\x33'),
            ('G',   {'a': True, 'b': '1'}, b'\xcc\x40'),
            ('H',   {'a': True, 'b': '1'}, b'\xa0\x31'),
            ('I',                   'hej', b'\x02\x68\x65\x6a'),
            ('J',                     'a', b'\x01'),
            ('K',                     'a', b'\x01')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Bad character 0x19 should raise an exception.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', '\x19')

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
            'per')

        datas = [
            ('A',                      '', b'\x00'),
            ('A',                     '2', b'\x01\x32'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\x01\x4b')
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
            'per')

        datas = [
            ('A',     '', b'\x00'),
            ('A',  '123', b'\x03\x00\x31\x00\x32\x00\x33'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\x01\x00\x4b')
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
            'per')

        datas = [
            ('A',                      '', b'\x00'),
            ('A',                     '2', b'\x01\x32'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\x01\x4b')
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
            'per')

        datas = [
            ('A',                  u'123', b'\x03\x31\x32\x33'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\x01\x4b')
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
            'per')

        datas = [
            ('A',
             u'åäö',
             b'\x03\x00\x00\x00\xe5\x00\x00\x00\xe4\x00\x00\x00\xf6'),
            ('A',
             u'1𐈃Q',
             b'\x03\x00\x00\x00\x31\x00\x01\x02\x03\x00\x00\x00\x51'),
            ('B', {'a': False, 'b': u'K'}, b'\x00\x01\x00\x00\x00\x4b')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_foo(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'per')

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded,
                         b'\x01\x01\x09\x49\x73\x20\x31\x2b\x31\x3d\x33\x3f')

        # Decode the encoded question.
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Encode an answer.
        encoded = foo.encode('Answer', {'id': 1, 'answer': False})
        self.assertEqual(encoded, b'\x01\x01\x00')

        # Decode the encoded answer.
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'per')

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode_length(b'')

        self.assertEqual(str(cm.exception),
                         'Decode length is not supported for this codec.')

    def test_versions(self):
        foo = asn1tools.compile_files('tests/files/versions.asn', 'per')

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
        a1 = asn1tools.compile_files('tests/files/x691_a1.asn', 'per')

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
            b'\x80\x04\x4a\x6f\x68\x6e\x01\x50\x05\x53\x6d\x69\x74\x68\x01\x33'
            b'\x08\x44\x69\x72\x65\x63\x74\x6f\x72\x08\x31\x39\x37\x31\x30\x39'
            b'\x31\x37\x04\x4d\x61\x72\x79\x01\x54\x05\x53\x6d\x69\x74\x68\x02'
            b'\x05\x52\x61\x6c\x70\x68\x01\x54\x05\x53\x6d\x69\x74\x68\x08\x31'
            b'\x39\x35\x37\x31\x31\x31\x31\x05\x53\x75\x73\x61\x6e\x01\x42\x05'
            b'\x4a\x6f\x6e\x65\x73\x08\x31\x39\x35\x39\x30\x37\x31\x37'
        )

        self.assert_encode_decode(a1, 'PersonnelRecord', decoded, encoded)

    def test_x691_a2(self):
        a2 = asn1tools.compile_files('tests/files/x691_a2.asn', 'per')

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
            b'\x86\x4a\x6f\x68\x6e\x50\x10\x53\x6d\x69\x74\x68\x01\x33\x08\x44'
            b'\x69\x72\x65\x63\x74\x6f\x72\x19\x71\x09\x17\x0c\x4d\x61\x72\x79'
            b'\x54\x10\x53\x6d\x69\x74\x68\x02\x10\x52\x61\x6c\x70\x68\x54\x10'
            b'\x53\x6d\x69\x74\x68\x19\x57\x11\x11\x10\x53\x75\x73\x61\x6e\x42'
            b'\x10\x4a\x6f\x6e\x65\x73\x19\x59\x07\x17'
        )

        self.assert_encode_decode(a2, 'PersonnelRecord', decoded, encoded)

    def test_x691_a3(self):
        a3 = asn1tools.compile_files('tests/files/x691_a3.asn', 'per')

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
            b'\x40\xc0\x4a\x6f\x68\x6e\x50\x08\x53\x6d\x69\x74\x68\x00\x00\x33'
            b'\x08\x44\x69\x72\x65\x63\x74\x6f\x72\x00\x19\x71\x09\x17\x03\x4d'
            b'\x61\x72\x79\x54\x08\x53\x6d\x69\x74\x68\x01\x00\x52\x61\x6c\x70'
            b'\x68\x54\x08\x53\x6d\x69\x74\x68\x00\x19\x57\x11\x11\x82\x00\x53'
            b'\x75\x73\x61\x6e\x42\x08\x4a\x6f\x6e\x65\x73\x00\x19\x59\x07\x17'
            b'\x01\x01\x40'
        )

        self.assert_encode_decode(a3, 'PersonnelRecord', decoded, encoded)

    def test_x691_a4(self):
        a4 = asn1tools.compile_dict(deepcopy(X691_A4), 'per')

        decoded = {
            'a': 253,
            'b': True,
            'c': ('e', True),
            'g': '123',
            'h': True
        }

        encoded = (
            b'\x9e\x00\x01\x80\x01\x02\x91\xa4'
        )

        self.assert_encode_decode(a4, 'Ax', decoded, encoded)

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'per')

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
                (
                    'paging', {
                    }
                )
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
                                                'longCodeState1XRTT': (b'\x01\x23\x45\x67\x89\x00', 42)
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
            b'\x04\x81\x3f\xbe\x2a\x64\x12\xb2\xf3\x20\x03\x44\x85\x50\x00\x40'
            b'\x53\x65\x31\x40\x07\xff\x82\x40\x00\x01\x10\x02\x4e\x20\x80\x50'
            b'\x6c\x3c\x47\x69\x28\x14\x10\x0c\x00\x00\x00\x01\x64\x7f\xa2\x10'
            b'\x19\x43\x30\x50\x01\x23\x45\x67\x89\x0e\x80\x34\x40\x46\x68\x24'
            b'\x68\x64\x24\x91\x9e\x21\x50\xd4\x98\x01\x12'
        )

        self.assert_encode_decode(rrc, 'BCCH-DL-SCH-Message', decoded, encoded)

    def test_all_types_automatic_tags(self):
        all_types = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn', 'per')

        datas = [
            ('Sequence3', {'a': 1, 'c': 2,'d': True}, b'\x00\x01\x01\x01\x02\x80')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(all_types, type_name, decoded, encoded)

    def test_bar(self):
        """A simple example.

        """

        bar = asn1tools.compile_files('tests/files/bar.asn', 'per')

        # Message 1.
        decoded = {
            'headerOnly': True,
            'lock': False,
            'acceptTypes': {
                'standardTypes': [(b'\x40', 2), (b'\x80', 1)]
            },
            'url': b'/ses/magic/moxen.html'
        }

        encoded = (
            b'\xd0\x02\x02\x40\x01\x80\x15\x2f\x73\x65\x73\x2f\x6d\x61\x67\x69'
            b'\x63\x2f\x6d\x6f\x78\x65\x6e\x2e\x68\x74\x6d\x6c'
        )

        self.assert_encode_decode(bar, 'GetRequest', decoded, encoded)

        # Message 2.
        decoded = {
            'headerOnly': False,
            'lock': False,
            'url': b'0'
        }

        encoded = b'\x00\x01\x30'

        self.assert_encode_decode(bar, 'GetRequest', decoded, encoded)

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'per')

        self.assertEqual(repr(all_types.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(all_types.types['Integer']), 'Integer(Integer)')
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
        self.assertEqual(repr(all_types.types['Choice']), "Choice(Choice, ['a'])")
        self.assertEqual(repr(all_types.types['Any']), 'Any(Any)')
        self.assertEqual(repr(all_types.types['Sequence12']),
                         'Sequence(Sequence12, [SequenceOf(a, Recursive(Sequence12))])')

    def test_s1ap_14_4_0(self):
        with self.assertRaises(asn1tools.CompileError) as cm:
            s1ap = asn1tools.compile_dict(deepcopy(S1AP_14_4_0), 'per')

        self.assertEqual(
            str(cm.exception),
            "Value 'lowerBound' not found in module 'S1AP-Containers'.")

        return

        # Message 1.
        decoded_message = (
            'successfulOutcome',
            {
                'procedureCode': 17,
                'criticality': 'reject',
                'value': {
                    'protocolIEs': [
                        {
                            'id': 105,
                            'criticality': 'reject',
                            'value': [
                                {
                                    'servedPLMNs': [
                                        b'\xab\xcd\xef',
                                        b'\x12\x34\x56'
                                    ],
                                    'servedGroupIDs': [
                                        b'\x22\x22'
                                    ],
                                    'servedMMECs': [
                                        b'\x11'
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        )

        encoded_message = (
            b'\x20\x11\x00\x15\x00\x00\x01\x00\x69\x00\x0e\x00\x40\xab\xcd\xef'
            b'\x12\x34\x56\x00\x00\x22\x22\x00\x11'
        )

        encoded = s1ap.encode('S1AP-PDU', decoded_message)
        self.assertEqual(encoded, encoded_message)

    def test_information_object(self):
        information_object = asn1tools.compile_files(
            'tests/files/information_object.asn', 'per')

        # Message 1 - without constraints.
        decoded_message = {
            'id': 0,
            'value': b'\x05',
            'comment': 'item 0',
            'extra': 2
        }

        encoded_message = (
            b'\x01\x00\x01\x05\x06\x69\x74\x65\x6d\x20\x30\x01\x02'
        )

        self.assert_encode_decode(information_object,
                                  'ItemWithoutConstraints',
                                  decoded_message,
                                  encoded_message)

        # Message 1 - with constraints.
        decoded_message = {
            'id': 0,
            'value': True,
            'comment': 'item 0',
            'extra': 2
        }

        encoded_message = (
            b'\x01\x00\x01\x80\x06\x69\x74\x65\x6d\x20\x30\x01\x02'
        )

        # ToDo: Constraints are not yet implemented.
        with self.assertRaises(TypeError) as cm:
            self.assert_encode_decode(information_object,
                                      'ItemWithConstraints',
                                      decoded_message,
                                      encoded_message)

        self.assertEqual(str(cm.exception), "object of type 'bool' has no len()")

        # Message 2.
        decoded_message = {
            'id': 1,
            'value': {
                'myValue': 7,
                'myType': 0
            },
            'comment': 'item 1',
            'extra': 5
        }

        encoded_message = (
            b'\x01\x01\x05\x02\x01\x07\x01\x00\x06\x69\x74\x65\x6d\x20\x31\x01'
            b'\x05'
        )

        # ToDo: Constraints are not yet implemented.
        with self.assertRaises(TypeError):
            self.assert_encode_decode(information_object,
                                      'ItemWithConstraints',
                                      decoded_message,
                                      encoded_message)

        # Message 3 - error class.
        decoded_message = {
            'errorCategory': 'A',
            'errors': [
                {
                    'errorCode': 1,
                    'errorInfo': 3
                },
                {
                    'errorCode': 2,
                    'errorInfo': True
                }
            ]
        }

        encoded_message = (
            b'\x41\x02\x01\x01\x02\x01\x03\x01\x02\x01\x80'
        )

        # ToDo: Constraints are not yet implemented.
        with self.assertRaises(TypeError):
            self.assert_encode_decode(information_object,
                                      'ErrorReturn',
                                      decoded_message,
                                      encoded_message)

        # Message 4 - C.
        decoded_message = {
            'a': 0
        }

        encoded_message = (
            b'\x00\x01\x00'
        )

        encoded = information_object.encode('C', decoded_message)
        self.assertEqual(encoded, encoded_message)

        # Message 5 - C.
        decoded_message = {
            'a': 0,
            'b': {
                'a': 0
            }
        }

        encoded_message = (
            b'\x80\x01\x00\x03\x00\x01\x00'
        )

        with self.assertRaises(TypeError):
            encoded = information_object.encode('C', decoded_message)
            self.assertEqual(encoded, encoded_message)

        # Message 6 - C.
        decoded_message = {
            'a': 0,
            'b': {
                'a': 0,
                'b': {
                    'a': 0,
                    'b': {
                        'a': 0
                    }
                }
            }
        }

        encoded_message = (
            b'\x80\x01\x00\x0b\x80\x01\x00\x07\x80\x01\x00\x03\x00\x01\x00'
        )

        with self.assertRaises(TypeError):
            encoded = information_object.encode('C', decoded_message)
            self.assertEqual(encoded, encoded_message)


if __name__ == '__main__':
    unittest.main()
