#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import unittest
import asn1tools
import sys
import math
from copy import deepcopy
from asn1tools.codecs import utc_time_to_datetime as ut2dt
from asn1tools.codecs import generalized_time_to_datetime as gt2dt

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0


def loadb(encoded):
    return json.loads(encoded.decode('utf-8'))


class Asn1ToolsJerTest(unittest.TestCase):

    maxDiff = None

    def assert_encode_decode_string(self, foo, type_name, decoded, encoded):
        self.assertEqual(loadb(foo.encode(type_name, decoded)),
                         loadb(encoded))
        self.assertEqual(foo.decode(type_name, encoded), decoded)

    def test_real(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= REAL "
            "END",
            'jer')

        datas = [
            ('A',                 1.0, b'1.0'),
            ('A',                -2.0, b'-2.0'),
            ('A',        float('inf'), b'"INF"'),
            ('A',       float('-inf'), b'"-INF"')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

        self.assertEqual(foo.encode('A', float('nan')), b'"NaN"')
        self.assertTrue(math.isnan(foo.decode('A', b'"NaN"')))

        self.assertEqual(foo.decode('A', b'"0"'), 0.0)
        self.assertEqual(foo.decode('A', b'"-0"'), 0.0)

    def test_bit_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= BIT STRING "
            "B ::= BIT STRING (SIZE (6)) "
            "END",
            'jer')

        datas = [
            ('A',       (b'\x40', 4), b'{"value": "40", "length": 4}'),
            ('A',       (b'\xab', 8), b'{"value": "AB", "length": 8}'),
            ('B',       (b'\xac', 6), b'"AC"')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_octet_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= OCTET STRING "
            "END",
            'jer')

        datas = [
            ('A', b'\x01\x23\x45\x67\x89\xab\xcd\xef', b'"0123456789ABCDEF"')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_object_identifier(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= OBJECT IDENTIFIER "
            "END",
            'jer')

        datas = [
            ('A', '1.2.3', b'"1.2.3"')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_external(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= EXTERNAL "
            "END",
            'jer')

        datas = [
            ('A',
             {'encoding': ('octet-aligned', b'\x12')},
             b'{"encoding": {"octet-aligned": "12"}}')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_enumerated(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= ENUMERATED { "
            "  a(1), "
            "  b(3) "
            "} "
            "END",
            'jer')

        datas = [
            ('A',           'a', b'"a"'),
            ('A',           'b', b'"b"')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

        # Encode error.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', 'c')

        self.assertEqual(str(cm.exception),
                         "Enumeration value 'c' not found in ['a', 'b'].")

        # Decode error.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'"c"')

        self.assertEqual(str(cm.exception),
                         "Enumeration value 'c' not found in ['a', 'b'].")

    def test_sequence(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= SEQUENCE { "
            "  a SEQUENCE OF A OPTIONAL "
            "} "
            "B ::= SEQUENCE { "
            "  a INTEGER DEFAULT 5 "
            "} "
            "C ::= SEQUENCE { "
            "  a INTEGER, "
            "  b INTEGER "
            "} "
            "END",
            'jer')

        datas = [
            ('A',                    {}, b'{}'),
            ('A',           {'a': [{}]}, b'{"a": [{}]}'),
            ('A',    {'a': [{'a': []}]}, b'{"a": [{"a": []}]}')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

        # Non-symmetrical encoding and decoding because default values
        # are not encoded, but part of the decoded (given that the
        # root and addition is present).
        self.assertEqual(foo.encode('B', {}), b'{}')
        self.assertEqual(foo.decode('B', b'{}'), {'a': 5})

        # Missing member.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            encoded = foo.encode('C', {'a': 1})

        self.assertEqual(
            str(cm.exception),
            "Sequence member 'b' not found in {'a': 1}.")

    def test_sequence_of(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= SEQUENCE OF INTEGER "
            "END",
            'jer')

        datas = [
            ('A',     [], b'[]'),
            ('A', [1, 3], b'[1, 3]')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_set_of(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= SET OF INTEGER "
            "END",
            'jer')

        datas = [
            ('A',     [], b'[]'),
            ('A', [1, 3], b'[1, 3]')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_choice(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= CHOICE { "
            "  a BOOLEAN, "
            "  b INTEGER "
            "} "
            "END",
            'jer')

        datas = [
            ('A',           ('a', True), b'{"a": true}'),
            ('A',              ('b', 3), b'{"b": 3}')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

        # Encode error.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            foo.encode('A', ('c', None))

        self.assertEqual(str(cm.exception),
                         "Expected choice 'a' or 'b', but got 'c'.")

        # Decode error.
        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode('A', b'{"c": null}')

        self.assertEqual(str(cm.exception),
                         "Expected choice 'a' or 'b', but got 'c'.")

    def test_utf8_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTF8String "
            "END",
            'jer')

        datas = [
            ('A',         u'', b'""'),
            ('A',      u'bar', b'"bar"'),
            ('A', u'a\u1010c', b'"a\xe1\x80\x90c"'),
            ('A',    u'f → ∝', b'"f \xe2\x86\x92 \xe2\x88\x9d"')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_universal_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UniversalString "
            "END",
            'jer')

        datas = [
            ('A',     u'bar', b'"bar"'),
            ('A',     u'åäö', b'\x22\xc3\xa5\xc3\xa4\xc3\xb6\x22')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_utc_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= UTCTime "
            "END",
            'jer')

        datas = [
            ('A', ut2dt('121001230001Z'), b'"121001230001Z"')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_generalized_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= GeneralizedTime "
            "END",
            'jer')

        datas = [
            ('A', gt2dt('20001231235959.999'), b'"20001231235959.999"')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

    def test_any(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS ::= "
            "BEGIN "
            "A ::= ANY "
            "END",
            'jer')

        with self.assertRaises(NotImplementedError) as cm:
            foo.encode('A', b'')

        self.assertEqual(str(cm.exception), 'ANY is not yet implemented.')

        with self.assertRaises(NotImplementedError) as cm:
            foo.decode('A', b'""')

        self.assertEqual(str(cm.exception), 'ANY is not yet implemented.')

    def test_foo(self):
        foo = asn1tools.compile_files(['tests/files/foo.asn'], 'jer')

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Question.
        decoded_message = {'id': 1, 'question': 'Is 1+1=3?'}
        encoded_message = b'{"id":1,"question":"Is 1+1=3?"}'

        encoded = foo.encode('Question', decoded_message)
        self.assertEqual(loadb(encoded), loadb(encoded_message))
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, decoded_message)

        # Answer.
        decoded_message = {'id': 1, 'answer': False}
        encoded_message = b'{"id":1,"answer":false}'

        encoded = foo.encode('Answer', decoded_message)
        self.assertEqual(loadb(encoded), loadb(encoded_message))
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, decoded_message)

    def test_decode_length(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'jer')

        with self.assertRaises(asn1tools.DecodeError) as cm:
            foo.decode_length(b'')

        self.assertEqual(str(cm.exception),
                         'Decode length is not supported for this codec.')

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'jer')

        # Message 1.
        decoded_message = {
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

        encoded_message = (
            b'{"message":{"c1":{"paging":{"systemInfoModification":"true","'
            b'nonCriticalExtension":{}}}}}'
        )

        encoded = rrc.encode('PCCH-Message', decoded_message)
        self.assertEqual(loadb(encoded), loadb(encoded_message))
        decoded = rrc.decode('PCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 2.
        decoded_message = {
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

        encoded_message = (
            b'{"message":{"dl-Bandwidth":"n6","phich-Config":{"phich-Duration'
            b'":"normal","phich-Resource":"half"},"spare":"3440","'
            b'systemFrameNumber":"12"}}'
        )

        encoded = rrc.encode('BCCH-BCH-Message', decoded_message)
        self.assertEqual(loadb(encoded), loadb(encoded_message))
        decoded = rrc.decode('BCCH-BCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 3.
        decoded_message = {
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
                                    ('sib7',
                                     {
                                         't-ReselectionGERAN': 3
                                     }
                                    ),
                                    ('sib8',
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
                                    ('sib10',
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

        encoded_message = (
            b'{"message":{"c1":{"systemInformation":{"criticalExtensions":{"sy'
            b'stemInformation-r8":{"sib-TypeAndInfo":[{"sib2":{"ac-BarringInfo'
            b'":{"ac-BarringForEmergency":true,"ac-BarringForMO-Data":{"ac-Bar'
            b'ringFactor":"p95","ac-BarringForSpecialAC":"F0","ac-BarringTime"'
            b':"s128"}},"freqInfo":{"additionalSpectrumEmission":3},"radioReso'
            b'urceConfigCommon":{"bcch-Config":{"modificationPeriodCoeff":"n2"'
            b'},"pcch-Config":{"defaultPagingCycle":"rf256","nB":"twoT"},"pdsc'
            b'h-ConfigCommon":{"p-b":2,"referenceSignalPower":-60},"prach-Conf'
            b'ig":{"prach-ConfigInfo":{"highSpeedFlag":false,"prach-ConfigInde'
            b'x":33,"prach-FreqOffset":64,"zeroCorrelationZoneConfig":10},"roo'
            b'tSequenceIndex":836},"pucch-ConfigCommon":{"deltaPUCCH-Shift":"d'
            b's1","n1PUCCH-AN":2047,"nCS-AN":4,"nRB-CQI":98},"pusch-ConfigComm'
            b'on":{"pusch-ConfigBasic":{"enable64QAM":false,"hoppingMode":"int'
            b'erSubFrame","n-SB":1,"pusch-HoppingOffset":10},"ul-ReferenceSign'
            b'alsPUSCH":{"cyclicShift":5,"groupAssignmentPUSCH":22,"groupHoppi'
            b'ngEnabled":true,"sequenceHoppingEnabled":false}},"rach-ConfigCom'
            b'mon":{"maxHARQ-Msg3Tx":8,"powerRampingParameters":{"powerRamping'
            b'Step":"dB0","preambleInitialReceivedTargetPower":"dBm-102"},"pre'
            b'ambleInfo":{"numberOfRA-Preambles":"n24","preamblesGroupAConfig"'
            b':{"messagePowerOffsetGroupB":"minusinfinity","messageSizeGroupA"'
            b':"b144","sizeOfRA-PreamblesGroupA":"n28"}},"ra-SupervisionInfo":'
            b'{"mac-ContentionResolutionTimer":"sf48","preambleTransMax":"n8",'
            b'"ra-ResponseWindowSize":"sf6"}},"soundingRS-UL-ConfigCommon":{"s'
            b'etup":{"ackNackSRS-SimultaneousTransmission":true,"srs-Bandwidth'
            b'Config":"bw0","srs-SubframeConfig":"sc4"}},"ul-CyclicPrefixLengt'
            b'h":"len1","uplinkPowerControlCommon":{"alpha":"al0","deltaFList-'
            b'PUCCH":{"deltaF-PUCCH-Format1":"deltaF-2","deltaF-PUCCH-Format1b'
            b'":"deltaF1","deltaF-PUCCH-Format2":"deltaF0","deltaF-PUCCH-Forma'
            b't2a":"deltaF-2","deltaF-PUCCH-Format2b":"deltaF0"},"deltaPreambl'
            b'eMsg3":-1,"p0-NominalPUCCH":-127,"p0-NominalPUSCH":-126}},"timeA'
            b'lignmentTimerCommon":"sf500","ue-TimersAndConstants":{"n310":"n2'
            b'","n311":"n2","t300":"ms100","t301":"ms200","t310":"ms50","t311"'
            b':"ms30000"}}},{"sib3":{"cellReselectionInfoCommon":{"q-Hyst":"dB'
            b'0","speedStateReselectionPars":{"mobilityStateParameters":{"n-Ce'
            b'llChangeHigh":16,"n-CellChangeMedium":1,"t-Evaluation":"s180","t'
            b'-HystNormal":"s180"},"q-HystSF":{"sf-High":"dB-4","sf-Medium":"d'
            b'B-6"}}},"cellReselectionServingFreqInfo":{"cellReselectionPriori'
            b'ty":3,"threshServingLow":7},"intraFreqCellReselectionInfo":{"nei'
            b'ghCellConfig":"80","presenceAntennaPort1":false,"q-RxLevMin":-33'
            b',"s-IntraSearch":0,"t-ReselectionEUTRA":4}}},{"sib4":{}},{"sib5"'
            b':{"interFreqCarrierFreqList":[{"allowedMeasBandwidth":"mbw6","dl'
            b'-CarrierFreq":1,"neighCellConfig":"00","presenceAntennaPort1":tr'
            b'ue,"q-OffsetFreq":"dB0","q-RxLevMin":-45,"t-ReselectionEUTRA":0,'
            b'"threshX-High":31,"threshX-Low":29}]}},{"sib6":{"t-ReselectionUT'
            b'RA":3}},{"sib7":{"t-ReselectionGERAN":3}},{"sib8":{"parameters1X'
            b'RTT":{"longCodeState1XRTT":"012345678900"}}},{"sib9":{"hnb-Name"'
            b':"34"}},{"sib10":{"messageIdentifier":"2334","serialNumber":"123'
            b'4","warningType":"3212"}},{"sib11":{"messageIdentifier":"6788","'
            b'serialNumber":"5435","warningMessageSegment":"12","warningMessag'
            b'eSegmentNumber":19,"warningMessageSegmentType":"notLastSegment"}'
            b'}]}}}}}}'
        )

        encoded = rrc.encode('BCCH-DL-SCH-Message', decoded_message)
        self.assertEqual(loadb(encoded), loadb(encoded_message))
        decoded = rrc.decode('BCCH-DL-SCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

    def test_all_types(self):
        foo = asn1tools.compile_files('tests/files/all_types.asn', 'jer')

        datas = [
            ('Boolean',             True, b'true'),
            ('Integer',              127, b'127'),
            ('Integer',                0, b'0'),
            ('Integer',             -128, b'-128'),
            ('Octetstring',      b'\x00', b'"00"'),
            ('Null',                None, b'null'),
            ('Utf8string',         'foo', b'"foo"'),
            ('Sequence',              {}, b'{}'),
            ('Sequence2',       {'a': 1}, b'{"a":1}'),
            ('Set',                   {}, b'{}'),
            ('Set2',            {'a': 2}, b'{"a":2}'),
            ('Numericstring',      '123', b'"123"'),
            ('Printablestring',    'foo', b'"foo"'),
            ('Ia5string',          'bar', b'"bar"'),
            ('Universalstring',    'bar', b'"bar"'),
            ('Visiblestring',      'bar', b'"bar"'),
            ('Generalstring',      'bar', b'"bar"'),
            ('Bmpstring',          'bar', b'"bar"'),
            ('Graphicstring',      'bar', b'"bar"'),
            ('Teletexstring',      'fum', b'"fum"')
        ]

        for type_name, decoded, encoded in datas:
            self.assertEqual(foo.encode(type_name, decoded), encoded)
            self.assertEqual(foo.decode(type_name, encoded), decoded)

        decoded_message = (b'\x80', 1)
        encoded_message = b'{"value":"80","length":1}'

        self.assertEqual(loadb(foo.encode('Bitstring', decoded_message)),
                         loadb(encoded_message))
        self.assertEqual(foo.decode('Bitstring', encoded_message),
                         decoded_message)

    def test_repr_all_types(self):
        foo = asn1tools.compile_files('tests/files/all_types.asn',
                                      'jer')

        self.assertEqual(repr(foo.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(foo.types['Integer']), 'Integer(Integer)')
        self.assertEqual(repr(foo.types['Real']), 'Real(Real)')
        self.assertEqual(repr(foo.types['Bitstring']), 'BitString(Bitstring)')
        self.assertEqual(repr(foo.types['Octetstring']), 'OctetString(Octetstring)')
        self.assertEqual(repr(foo.types['Null']), 'Null(Null)')
        self.assertEqual(repr(foo.types['Objectidentifier']),
                         'ObjectIdentifier(Objectidentifier)')
        self.assertEqual(repr(foo.types['Enumerated']), 'Enumerated(Enumerated)')
        self.assertEqual(repr(foo.types['Utf8string']), 'UTF8String(Utf8string)')
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
        self.assertEqual(repr(foo.types['Graphicstring']),
                         'GraphicString(Graphicstring)')
        self.assertEqual(repr(foo.types['Teletexstring']),
                         'TeletexString(Teletexstring)')
        self.assertEqual(repr(foo.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(foo.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(foo.types['SetOf']), 'SetOf(SetOf, Integer())')
        self.assertEqual(repr(foo.types['GeneralizedTime1']),
                         'GeneralizedTime(GeneralizedTime1)')
        self.assertEqual(repr(foo.types['Choice']),
                         'Choice(Choice, [Integer(a)])')
        self.assertEqual(repr(foo.types['Any']), 'Any(Any)')
        self.assertEqual(repr(foo.types['Sequence12']),
                         'Sequence(Sequence12, [SequenceOf(a, Recursive(Sequence12))])')

    def test_all_types_automatic_tags(self):
        foo = asn1tools.compile_files(
            'tests/files/all_types_automatic_tags.asn', 'jer')

        datas = [
            ('Sequence3', {'a': 1, 'c': 2,'d': True}, b'{"a":1,"c":2,"d":true}')
        ]

        for type_name, decoded, encoded in datas:
            self.assert_encode_decode_string(foo, type_name, decoded, encoded)

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
            'jer')

        datas = [
            ('A',
             {'a': {'b': True, 'c': 5}},
             [
                 b'{',
                 b'    "a": {',
                 b'        "c": 5,',
                 b'        "c": 5, ',
                 b'        "b": true,',
                 b'        "b": true, ',
                 b'        "c": 5',
                 b'        "b": true',
                 b'    }',
                 b'}'
             ])
        ]

        for type_name, decoded, encoded_lines in datas:
            encoded = foo.encode(type_name, decoded, indent=4)

            for line in encoded.splitlines():
                self.assertIn(line, encoded_lines)


if __name__ == '__main__':
    unittest.main()
