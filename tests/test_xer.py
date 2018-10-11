#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools
import sys
from copy import deepcopy
from asn1tools.codecs import utc_time_to_datetime as ut2dt
from asn1tools.codecs import generalized_time_to_datetime as gt2dt

sys.path.append('tests/files/3gpp')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0


class Asn1ToolsXerTest(Asn1ToolsBaseTest):

    maxDiff = None

    def test_real(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= REAL "
            "END",
            'xer')

        datas = [
            ('A', 1.0, b'<A>1.0E0</A>'),
            ('A', 10.0, b'<A>1.0E1</A>'),
            ('A', -1.0, b'<A>-1.0E0</A>'),
            ('A', -2, b'<A>-2.0E0</A>'),
            ('A', -9.99, b'<A>-9.99E0</A>'),
            ('A', -10.0, b'<A>-1.0E1</A>'),
            ('A', 0.31, b'<A>0.31E0</A>'),
            ('A', 2000.0, b'<A>2.0E3</A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_null(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NULL "
            "B ::= SEQUENCE OF NULL "
            "C ::= SEQUENCE { a NULL } "
            "END",
            'xer')

        datas = [
            ('A',         None, b'<A />'),
            ('B', [None, None], b'<B><NULL /><NULL /></B>'),
            ('C',  {'a': None}, b'<C><a /></C>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_bit_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BIT STRING "
            "END",
            'xer')

        datas = [
            ('A',         (b'', 0), b'<A />'),
            ('A', (b'\x00', 2), b'<A>00</A>'),
            ('A',     (b'\x40', 4), b'<A>0100</A>'),
            ('A', (b'\x40\x80', 9), b'<A>010000001</A>'),
            ('A',
             (b'\x11\x22\x33\x44\x55\x66\x76', 55),
             b'<A>0001000100100010001100110100010001010101011001100111011</A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_octet_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OCTET STRING "
            "END",
            'xer')

        datas = [
            ('A',         b'', b'<A />'),
            ('A', b'\x40\x80', b'<A>4080</A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_object_identifier(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OBJECT IDENTIFIER "
            "END",
            'xer')

        datas = [
            ('A',    '1.2.3', b'<A>1.2.3</A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'<A></A>')

        self.assertEqual(str(cm.exception),
                         "Expected an OBJECT IDENTIFIER, but got ''.")

    def test_external(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= EXTERNAL "
            "END",
            'xer')

        datas = [
            ('A',
             {'encoding': ('octet-aligned', b'\x12')},
             b'<A><encoding><octet-aligned>12</octet-aligned></encoding></A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_enumerated(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= ENUMERATED { r(5), t(10) } "
            "B ::= SEQUENCE OF ENUMERATED { a(0) } "
            "END",
            'xer')

        datas = [
            ('A',    'r', b'<A><r /></A>'),
            ('A',    't', b'<A><t /></A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

        # Encode error.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', 'foo')

        self.assertEqual(
            str(cm.exception),
            "Expected enumeration value 'r' or 't', but got 'foo'.")

        # Decode error.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'<A><bar /></A>')

        self.assertEqual(
            str(cm.exception),
            "Expected enumeration value 'r' or 't', but got 'bar'.")

        # Encode of error.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('B', ['foo'])

        self.assertEqual(
            str(cm.exception),
            "Expected enumeration value 'a', but got 'foo'.")

        # Decode of error.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('B', b'<B><bar /></B>')

        self.assertEqual(
            str(cm.exception),
            "Expected enumeration value 'a', but got 'bar'.")

    def test_sequence(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE { "
            "  a SEQUENCE OF A OPTIONAL "
            "} "
            "B ::= SEQUENCE { "
            "  a INTEGER DEFAULT 4 "
            "} "
            "END",
            'xer')

        datas = [
            ('A',                    {}, b'<A />'),
            ('A',           {'a': [{}]}, b'<A><a><A /></a></A>'),
            ('A',    {'a': [{'a': []}]}, b'<A><a><A><a /></A></a></A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

        # Non-symmetrical encoding and decoding.
        self.assertEqual(foo.encode('B', {}), b'<B />')
        self.assertEqual(foo.decode('B', b'<B />'), {'a': 4})

    def test_sequence_of(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE OF INTEGER "
            "B ::= SEQUENCE OF A "
            "C ::= SEQUENCE OF BOOLEAN "
            "D ::= SEQUENCE OF E "
            "E ::= BOOLEAN "
            "F ::= SEQUENCE OF CHOICE { a BOOLEAN, b INTEGER } "
            "G ::= SEQUENCE OF ENUMERATED { one } "
            "H ::= SEQUENCE OF SEQUENCE { a INTEGER } "
            "I ::= SEQUENCE OF BIT STRING "
            "J ::= SEQUENCE OF OCTET STRING "
            "K ::= SEQUENCE OF OBJECT IDENTIFIER "
            "L ::= SEQUENCE OF SEQUENCE OF NULL "
            "M ::= SEQUENCE OF SET OF NULL "
            "END",
            'xer')

        datas = [
            ('A',               [], b'<A />'),
            ('A',           [1, 4], b'<A><INTEGER>1</INTEGER><INTEGER>4</INTEGER></A>'),
            ('B',            [[5]], b'<B><A><INTEGER>5</INTEGER></A></B>'),
            ('C',    [True, False], b'<C><true /><false /></C>'),
            ('D',           [True], b'<D><true /></D>'),
            ('F',
             [('a', True), ('b', 1)],
             b'<F><a><true /></a><b>1</b></F>'),
            ('G',          ['one'], b'<G><one /></G>'),
            ('H',       [{'a': 1}], b'<H><SEQUENCE><a>1</a></SEQUENCE></H>'),
            ('I',   [(b'\x80', 1)], b'<I><BIT_STRING>1</BIT_STRING></I>'),
            ('J',        [b'\x12'], b'<J><OCTET_STRING>12</OCTET_STRING></J>'),
            ('K',
             ['1.2.30'],
             b'<K><OBJECT_IDENTIFIER>1.2.30</OBJECT_IDENTIFIER></K>'),
            ('L',
             [[None], []],
             b'<L><SEQUENCE_OF><NULL /></SEQUENCE_OF><SEQUENCE_OF /></L>'),
            ('M',
             [[None], []],
             b'<M><SET_OF><NULL /></SET_OF><SET_OF /></M>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_choice(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= CHOICE { "
            "  a BOOLEAN, "
            "  b INTEGER, "
            "  c CHOICE { "
            "    a INTEGER "
            "  } "
            "} "
            "B ::= SEQUENCE OF A "
            "END",
            'xer')

        datas = [
            ('A', ('a', True), b'<A><a><true /></a></A>'),
            ('A', ('b', 1), b'<A><b>1</b></A>'),
            ('A', ('c', ('a', 534)), b'<A><c><a>534</a></c></A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

        # Encode error.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', ('d', None))

        self.assertEqual(str(cm.exception),
                         "Expected choice 'a', 'b' or 'c', but got 'd'.")

        # Decode error.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'<A><d><true /></d></A>')

        self.assertEqual(str(cm.exception),
                         "Expected choice 'a', 'b' or 'c', but got 'd'.")

        # Encode of error.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('B', [('d', None)])

        self.assertEqual(str(cm.exception),
                         "Expected choice 'a', 'b' or 'c', but got 'd'.")

        # Decode of error.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('B', b'<A><d><true /></d></A>')

        self.assertEqual(str(cm.exception),
                         "Expected choice 'a', 'b' or 'c', but got 'd'.")

    def test_utf8_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTF8String "
            "END",
            'xer')

        datas = [
            ('A',         u'', b'<A />'),
            ('A',      u'bar', b'<A>bar</A>'),
            ('A', u'a\u1010c', b'<A>a&#4112;c</A>'),
            ('A',    u'f → ∝', b'<A>f &#8594; &#8733;</A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_universal_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UniversalString "
            "END",
            'xer')

        datas = [
            ('A',        u'bar', b'<A>bar</A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode(foo, type_name, decoded, encoded)

    def test_utc_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTCTime "
            "END",
            'xer')

        datas = [
            ('A', ut2dt('9205210000Z'), b'<A>9205210000Z</A>'),
            ('A', ut2dt('920622123421Z'), b'<A>920622123421Z</A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_generalized_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GeneralizedTime "
            "END",
            'xer')

        datas = [
            ('A', gt2dt('199205210000Z'), b'<A>199205210000Z</A>'),
            ('A', gt2dt('19920622123421Z'), b'<A>19920622123421Z</A>'),
            ('A', gt2dt('199207221321.3Z'), b'<A>199207221321.3Z</A>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_any(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= ANY "
            "END",
            'xer')

        with self.assertRaises(NotImplementedError) as cm:
            foo.encode('A', b'')

        self.assertEqual(str(cm.exception), 'ANY is not yet implemented.')

        with self.assertRaises(NotImplementedError) as cm:
            foo.decode('A', b'<A />')

        self.assertEqual(str(cm.exception), 'ANY is not yet implemented.')

    def test_foo(self):
        foo = asn1tools.compile_files(['tests/files/foo.asn'], 'xer')

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Question.
        decoded_message = {'id': 1, 'question': 'Is 1+1=3?'}
        encoded_message = (
            b'<Question><id>1</id><question>Is 1+1=3?</question></Question>'
        )

        encoded = foo.encode('Question', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, decoded_message)

        # Answer.
        decoded_message = {'id': 1, 'answer': False}
        encoded_message = (
            b'<Answer><id>1</id><answer><false /></answer></Answer>'
        )

        encoded = foo.encode('Answer', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, decoded_message)

        # Encode a question with missing field 'id'.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            encoded = foo.encode('Question', {'question': 'Is 1+1=3?'})

        self.assertEqual(
            str(cm.exception),
            "Sequence member 'id' not found in {'question': 'Is 1+1=3?'}.")

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'xer')

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode_length(b'')

        self.assertEqual(str(cm.exception),
                         'Decode length is not supported for this codec.')

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'xer')

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

        encoded = (
            b'<PCCH-Message><message><c1><paging><systemInfoModification><'
            b'true /></systemInfoModification><nonCriticalExtension /></pa'
            b'ging></c1></message></PCCH-Message>'
        )

        self.assert_encode_decode_string(rrc, 'PCCH-Message', decoded, encoded)

        # Message 2.
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

        encoded = (
            b'<BCCH-BCH-Message><message><dl-Bandwidth><n6 /></dl-Bandwidt'
            b'h><phich-Config><phich-Duration><normal /></phich-Duration><'
            b'phich-Resource><half /></phich-Resource></phich-Config><syst'
            b'emFrameNumber>00010010</systemFrameNumber><spare>0011010001<'
            b'/spare></message></BCCH-BCH-Message>'
        )

        self.assert_encode_decode_string(rrc, 'BCCH-BCH-Message', decoded, encoded)

        # Message 3.
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
            b'<BCCH-DL-SCH-Message><message><c1><systemInformation><critic'
            b'alExtensions><systemInformation-r8><sib-TypeAndInfo><sib2><a'
            b'c-BarringInfo><ac-BarringForEmergency><true /></ac-BarringFo'
            b'rEmergency><ac-BarringForMO-Data><ac-BarringFactor><p95 /></'
            b'ac-BarringFactor><ac-BarringTime><s128 /></ac-BarringTime><a'
            b'c-BarringForSpecialAC>11110</ac-BarringForSpecialAC></ac-Bar'
            b'ringForMO-Data></ac-BarringInfo><radioResourceConfigCommon><'
            b'rach-ConfigCommon><preambleInfo><numberOfRA-Preambles><n24 /'
            b'></numberOfRA-Preambles><preamblesGroupAConfig><sizeOfRA-Pre'
            b'amblesGroupA><n28 /></sizeOfRA-PreamblesGroupA><messageSizeG'
            b'roupA><b144 /></messageSizeGroupA><messagePowerOffsetGroupB>'
            b'<minusinfinity /></messagePowerOffsetGroupB></preamblesGroup'
            b'AConfig></preambleInfo><powerRampingParameters><powerRamping'
            b'Step><dB0 /></powerRampingStep><preambleInitialReceivedTarge'
            b'tPower><dBm-102 /></preambleInitialReceivedTargetPower></pow'
            b'erRampingParameters><ra-SupervisionInfo><preambleTransMax><n'
            b'8 /></preambleTransMax><ra-ResponseWindowSize><sf6 /></ra-Re'
            b'sponseWindowSize><mac-ContentionResolutionTimer><sf48 /></ma'
            b'c-ContentionResolutionTimer></ra-SupervisionInfo><maxHARQ-Ms'
            b'g3Tx>8</maxHARQ-Msg3Tx></rach-ConfigCommon><bcch-Config><mod'
            b'ificationPeriodCoeff><n2 /></modificationPeriodCoeff></bcch-'
            b'Config><pcch-Config><defaultPagingCycle><rf256 /></defaultPa'
            b'gingCycle><nB><twoT /></nB></pcch-Config><prach-Config><root'
            b'SequenceIndex>836</rootSequenceIndex><prach-ConfigInfo><prac'
            b'h-ConfigIndex>33</prach-ConfigIndex><highSpeedFlag><false />'
            b'</highSpeedFlag><zeroCorrelationZoneConfig>10</zeroCorrelati'
            b'onZoneConfig><prach-FreqOffset>64</prach-FreqOffset></prach-'
            b'ConfigInfo></prach-Config><pdsch-ConfigCommon><referenceSign'
            b'alPower>-60</referenceSignalPower><p-b>2</p-b></pdsch-Config'
            b'Common><pusch-ConfigCommon><pusch-ConfigBasic><n-SB>1</n-SB>'
            b'<hoppingMode><interSubFrame /></hoppingMode><pusch-HoppingOf'
            b'fset>10</pusch-HoppingOffset><enable64QAM><false /></enable6'
            b'4QAM></pusch-ConfigBasic><ul-ReferenceSignalsPUSCH><groupHop'
            b'pingEnabled><true /></groupHoppingEnabled><groupAssignmentPU'
            b'SCH>22</groupAssignmentPUSCH><sequenceHoppingEnabled><false '
            b'/></sequenceHoppingEnabled><cyclicShift>5</cyclicShift></ul-'
            b'ReferenceSignalsPUSCH></pusch-ConfigCommon><pucch-ConfigComm'
            b'on><deltaPUCCH-Shift><ds1 /></deltaPUCCH-Shift><nRB-CQI>98</'
            b'nRB-CQI><nCS-AN>4</nCS-AN><n1PUCCH-AN>2047</n1PUCCH-AN></puc'
            b'ch-ConfigCommon><soundingRS-UL-ConfigCommon><setup><srs-Band'
            b'widthConfig><bw0 /></srs-BandwidthConfig><srs-SubframeConfig'
            b'><sc4 /></srs-SubframeConfig><ackNackSRS-SimultaneousTransmi'
            b'ssion><true /></ackNackSRS-SimultaneousTransmission></setup>'
            b'</soundingRS-UL-ConfigCommon><uplinkPowerControlCommon><p0-N'
            b'ominalPUSCH>-126</p0-NominalPUSCH><alpha><al0 /></alpha><p0-'
            b'NominalPUCCH>-127</p0-NominalPUCCH><deltaFList-PUCCH><deltaF'
            b'-PUCCH-Format1><deltaF-2 /></deltaF-PUCCH-Format1><deltaF-PU'
            b'CCH-Format1b><deltaF1 /></deltaF-PUCCH-Format1b><deltaF-PUCC'
            b'H-Format2><deltaF0 /></deltaF-PUCCH-Format2><deltaF-PUCCH-Fo'
            b'rmat2a><deltaF-2 /></deltaF-PUCCH-Format2a><deltaF-PUCCH-For'
            b'mat2b><deltaF0 /></deltaF-PUCCH-Format2b></deltaFList-PUCCH>'
            b'<deltaPreambleMsg3>-1</deltaPreambleMsg3></uplinkPowerContro'
            b'lCommon><ul-CyclicPrefixLength><len1 /></ul-CyclicPrefixLeng'
            b'th></radioResourceConfigCommon><ue-TimersAndConstants><t300>'
            b'<ms100 /></t300><t301><ms200 /></t301><t310><ms50 /></t310><'
            b'n310><n2 /></n310><t311><ms30000 /></t311><n311><n2 /></n311'
            b'></ue-TimersAndConstants><freqInfo><additionalSpectrumEmissi'
            b'on>3</additionalSpectrumEmission></freqInfo><timeAlignmentTi'
            b'merCommon><sf500 /></timeAlignmentTimerCommon></sib2><sib3><'
            b'cellReselectionInfoCommon><q-Hyst><dB0 /></q-Hyst><speedStat'
            b'eReselectionPars><mobilityStateParameters><t-Evaluation><s18'
            b'0 /></t-Evaluation><t-HystNormal><s180 /></t-HystNormal><n-C'
            b'ellChangeMedium>1</n-CellChangeMedium><n-CellChangeHigh>16</'
            b'n-CellChangeHigh></mobilityStateParameters><q-HystSF><sf-Med'
            b'ium><dB-6 /></sf-Medium><sf-High><dB-4 /></sf-High></q-HystS'
            b'F></speedStateReselectionPars></cellReselectionInfoCommon><c'
            b'ellReselectionServingFreqInfo><threshServingLow>7</threshSer'
            b'vingLow><cellReselectionPriority>3</cellReselectionPriority>'
            b'</cellReselectionServingFreqInfo><intraFreqCellReselectionIn'
            b'fo><q-RxLevMin>-33</q-RxLevMin><s-IntraSearch>0</s-IntraSear'
            b'ch><presenceAntennaPort1><false /></presenceAntennaPort1><ne'
            b'ighCellConfig>10</neighCellConfig><t-ReselectionEUTRA>4</t-R'
            b'eselectionEUTRA></intraFreqCellReselectionInfo></sib3><sib4 '
            b'/><sib5><interFreqCarrierFreqList><InterFreqCarrierFreqInfo>'
            b'<dl-CarrierFreq>1</dl-CarrierFreq><q-RxLevMin>-45</q-RxLevMi'
            b'n><t-ReselectionEUTRA>0</t-ReselectionEUTRA><threshX-High>31'
            b'</threshX-High><threshX-Low>29</threshX-Low><allowedMeasBand'
            b'width><mbw6 /></allowedMeasBandwidth><presenceAntennaPort1><'
            b'true /></presenceAntennaPort1><neighCellConfig>00</neighCell'
            b'Config><q-OffsetFreq><dB0 /></q-OffsetFreq></InterFreqCarrie'
            b'rFreqInfo></interFreqCarrierFreqList></sib5><sib6><t-Reselec'
            b'tionUTRA>3</t-ReselectionUTRA></sib6><sib7><t-ReselectionGER'
            b'AN>3</t-ReselectionGERAN></sib7><sib8><parameters1XRTT><long'
            b'CodeState1XRTT>000000010010001101000101011001111000100100</l'
            b'ongCodeState1XRTT></parameters1XRTT></sib8><sib9><hnb-Name>3'
            b'4</hnb-Name></sib9><sib10><messageIdentifier>001000110011010'
            b'0</messageIdentifier><serialNumber>0001001000110100</serialN'
            b'umber><warningType>3212</warningType></sib10><sib11><message'
            b'Identifier>0110011110001000</messageIdentifier><serialNumber'
            b'>0101010000110101</serialNumber><warningMessageSegmentType><'
            b'notLastSegment /></warningMessageSegmentType><warningMessage'
            b'SegmentNumber>19</warningMessageSegmentNumber><warningMessag'
            b'eSegment>12</warningMessageSegment></sib11></sib-TypeAndInfo'
            b'></systemInformation-r8></criticalExtensions></systemInforma'
            b'tion></c1></message></BCCH-DL-SCH-Message>'
        )

        self.assert_encode_decode_string(rrc, 'BCCH-DL-SCH-Message', decoded, encoded)

    def test_all_types(self):
        foo = asn1tools.compile_files('tests/files/all_types.asn', 'xer')

        datas = [
            ('Boolean',        True, b'<Boolean><true /></Boolean>'),
            ('Integer',         127, b'<Integer>127</Integer>'),
            ('Integer',           0, b'<Integer>0</Integer>'),
            ('Integer',        -128, b'<Integer>-128</Integer>'),
            ('Sequence',         {}, b'<Sequence />'),
            ('Set',              {}, b'<Set />'),
            ('Sequence2',  {'a': 1}, b'<Sequence2><a>1</a></Sequence2>'),
            ('Set2',       {'a': 2}, b'<Set2><a>2</a></Set2>'),
            ('Ia5string',     'bar', b'<Ia5string>bar</Ia5string>'),
            ('SetOf',            [], b'<SetOf />')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_repr_all_types(self):
        foo = asn1tools.compile_files('tests/files/all_types.asn',
                                      'xer')

        self.assertEqual(repr(foo.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(foo.types['Integer']), 'Integer(Integer)')
        self.assertEqual(repr(foo.types['Real']), 'Real(Real)')
        self.assertEqual(repr(foo.types['Bitstring']), 'BitString(Bitstring)')
        self.assertEqual(repr(foo.types['Octetstring']),
                         'OctetString(Octetstring)')
        self.assertEqual(repr(foo.types['Null']), 'Null(Null)')
        self.assertEqual(repr(foo.types['Objectidentifier']),
                         'ObjectIdentifier(Objectidentifier)')
        self.assertEqual(repr(foo.types['Enumerated']),
                         'Enumerated(Enumerated)')
        self.assertEqual(repr(foo.types['Utf8string']),
                         'UTF8String(Utf8string)')
        self.assertEqual(repr(foo.types['Sequence']), 'Sequence(Sequence, [])')
        self.assertEqual(repr(foo.types['Set']), 'Set(Set, [])')
        self.assertEqual(repr(foo.types['Sequence2']),
                         'Sequence(Sequence2, [Integer(a)])')
        self.assertEqual(repr(foo.types['Set2']), 'Set(Set2, [Integer(a)])')
        self.assertEqual(repr(foo.types['Numericstring']),
                         'NumericString(Numericstring)')
        self.assertEqual(repr(foo.types['Printablestring']),
                         'PrintableString(Printablestring)')
        self.assertEqual(repr(foo.types['Ia5string']), 'IA5String(Ia5string)')
        self.assertEqual(repr(foo.types['Universalstring']),
                         'UniversalString(Universalstring)')
        self.assertEqual(repr(foo.types['Visiblestring']),
                         'VisibleString(Visiblestring)')
        self.assertEqual(repr(foo.types['Generalstring']),
                         'GeneralString(Generalstring)')
        self.assertEqual(repr(foo.types['Bmpstring']),
                         'BMPString(Bmpstring)')
        self.assertEqual(repr(foo.types['Teletexstring']),
                         'TeletexString(Teletexstring)')
        self.assertEqual(repr(foo.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(foo.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer(INTEGER))')
        self.assertEqual(repr(foo.types['SetOf']),
                         'SetOf(SetOf, Integer(INTEGER))')
        self.assertEqual(repr(foo.types['GeneralizedTime1']),
                         'GeneralizedTime(GeneralizedTime1)')
        self.assertEqual(repr(foo.types['Choice']),
                         'Choice(Choice, [Integer(a)])')
        self.assertEqual(repr(foo.types['Any']), 'Any(Any)')
        self.assertEqual(repr(foo.types['Sequence12']),
                         'Sequence(Sequence12, [SequenceOf(a, Recursive(Sequence12))])')

    def test_all_types_automatic_tags(self):
        foo = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn', 'xer')

        datas = [
            ('Sequence3',
             {'a': 1, 'c': 2,'d': True},
             b'<Sequence3><a>1</a><c>2</c><d><true /></d></Sequence3>')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_indent(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE { "
            "  a SEQUENCE { "
            "    b BOOLEAN, "
            "    c INTEGER "
            "  } "
            "} "
            "END",
            'xer')

        datas = [
            ('A',
             {'a': {'b': True, 'c': 5}},
             (b'<A>\n'
              b'    <a>\n'
              b'        <b>\n'
              b'            <true />\n'
              b'        </b>\n'
              b'        <c>5</c>\n'
              b'    </a>\n'
              b'</A>\n'))
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo,
                                             type_name,
                                             decoded,
                                             encoded,
                                             indent=4)

    def test_issue_34(self):
        """Test that a choice type with a recursive member can be compiled and
        used.

        """

        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN "
            "A ::= SEQUENCE { "
            "  a B "
            "} "
            "B ::= CHOICE { "
            "  b A, "
            "  c NULL "
            "} "
            "END ",
            'xer')

        decoded = {'a': ('b', {'a': ('c', None)})}
        encoded = b'<A><a><b><a><c /></a></b></a></A>'
        self.assert_encode_decode_string(foo,
                                         'A',
                                         decoded,
                                         encoded)


if __name__ == '__main__':
    unittest.main()
