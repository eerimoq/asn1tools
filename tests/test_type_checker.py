#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import unittest
import datetime
import asn1tools.codecs.type_checker
from copy import deepcopy

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from information_object import EXPECTED as INFORMATION_OBJECT


class Asn1ToolsEncodeTypeCheckerTest(unittest.TestCase):

    maxDiff = None

    def assert_good_bad(self,
                        type_spec,
                        expected_type_string,
                        good_datas,
                        bad_datas,
                        bad_datas_strings=None):
        foo = asn1tools.parse_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= " + type_spec + " "
            "END")

        foo = asn1tools.codecs.type_checker.compile_dict(foo)

        for data in good_datas:
            foo['Foo']['A'].encode(data)

        if bad_datas_strings is None:
            bad_datas_strings = [str(data) for data in bad_datas]

        for data, bad_datas_string in zip(bad_datas, bad_datas_strings):
            with self.assertRaises(asn1tools.EncodeError) as cm:
                foo['Foo']['A'].encode(data)

            self.assertEqual(str(cm.exception),
                             '{}, but got {}.'.format(expected_type_string,
                                                      bad_datas_string))

    def test_boolean(self):
        self.assert_good_bad('BOOLEAN',
                             'Expected data of type bool',
                             good_datas=[True, False],
                             bad_datas=[1, 'foo'])

    def test_integer(self):
        self.assert_good_bad('INTEGER',
                             'Expected data of type int or str',
                             good_datas=[1, -1],
                             bad_datas=[[], None])

    def test_real(self):
        self.assert_good_bad('REAL',
                             'Expected data of type float or int',
                             good_datas=[1, -1.0],
                             bad_datas=['1.0', None])

    def test_null(self):
        self.assert_good_bad('NULL',
                             'Expected None',
                             good_datas=[None],
                             bad_datas=['1.0', 1])

    def test_bit_string(self):
        self.assert_good_bad('BIT STRING',
                             'Expected data of type tuple(bytes, int)',
                             good_datas=[(b'', 0)],
                             bad_datas=[1, '101', (1, 0, 1), None])

        self.assert_good_bad('BIT STRING',
                             'Expected at least 1 bit(s) data',
                             good_datas=[],
                             bad_datas=[(b'', 1)],
                             bad_datas_strings=['0'])

    def test_bytes(self):
        self.assert_good_bad('OCTET STRING',
                             'Expected data of type bytes or bytearray',
                             good_datas=[b'7', bytearray()],
                             bad_datas=[1, {}, None])

    def test_object_identifier(self):
        self.assert_good_bad('OBJECT IDENTIFIER',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_enumerated(self):
        self.assert_good_bad('ENUMERATED { a(0) }',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_sequence(self):
        self.assert_good_bad('SEQUENCE { a NULL }',
                             'Expected data of type dict',
                             good_datas=[{}],
                             bad_datas=[(1, ), 1, b'101', None])

        self.assert_good_bad('SEQUENCE { a A OPTIONAL }',
                             'a: a: Expected data of type dict',
                             good_datas=[{'a': {'a': {}}}],
                             bad_datas=[{'a': {'a': []}}],
                             bad_datas_strings=['[]'])

    def test_sequence_of(self):
        self.assert_good_bad('SEQUENCE OF NULL',
                             'Expected data of type list',
                             good_datas=[[None, None]],
                             bad_datas=[{}, None])

    def test_set(self):
        self.assert_good_bad('SET { a NULL }',
                             'Expected data of type dict',
                             good_datas=[{}],
                             bad_datas=[(1, ), 1, b'101', None])

    def test_set_of(self):
        self.assert_good_bad('SET OF NULL',
                             'Expected data of type list',
                             good_datas=[[None, None]],
                             bad_datas=[{}, None])

    def test_choice(self):
        self.assert_good_bad('CHOICE { a NULL }',
                             'Expected data of type tuple(str, object)',
                             good_datas=[('a', None)],
                             bad_datas=[(1, None), {'a': 1}, None])

        self.assert_good_bad('CHOICE { a CHOICE { b CHOICE { c NULL } } }',
                             'a: b: Expected data of type tuple(str, object)',
                             good_datas=[('a', ('b', ('c', None)))],
                             bad_datas=[('a', ('b', {}))],
                             bad_datas_strings=['{}'])

    def test_utf8_string(self):
        self.assert_good_bad('UTF8String',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_numeric_string(self):
        self.assert_good_bad('NumericString',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_printable_string(self):
        self.assert_good_bad('PrintableString',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_ia5_string(self):
        self.assert_good_bad('IA5String',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_visible_string(self):
        self.assert_good_bad('VisibleString',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_general_string(self):
        self.assert_good_bad('GeneralString',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_bmp_string(self):
        self.assert_good_bad('BMPString',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_graphic_string(self):
        self.assert_good_bad('GraphicString',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_teletex_string(self):
        self.assert_good_bad('TeletexString',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_universal_string(self):
        self.assert_good_bad('UniversalString',
                             'Expected data of type str',
                             good_datas=['5', u'6'],
                             bad_datas=[1, {}, None])

    def test_utc_time(self):
        self.assert_good_bad('UTCTime',
                             'Expected data of type datetime.datetime',
                             good_datas=[datetime.datetime(1, 2, 3)],
                             bad_datas=[1.4, None])

    def test_generalized_time(self):
        self.assert_good_bad('GeneralizedTime',
                             'Expected data of type datetime.datetime',
                             good_datas=[datetime.datetime(1, 2, 3)],
                             bad_datas=[1.4, None])

    def test_rrc_8_6_0(self):
        rrc = asn1tools.codecs.type_checker.compile_dict(deepcopy(RRC_8_6_0))

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

        rrc['EUTRA-RRC-Definitions']['BCCH-DL-SCH-Message'].encode(decoded)

    def test_information_object(self):
        information_object = asn1tools.codecs.type_checker.compile_dict(
            deepcopy(INFORMATION_OBJECT))

        # Message 1 - without constraints.
        decoded = {
            'id': 0,
            'value': b'\x05',
            'comment': 'item 0',
            'extra': 2
        }

        information_object['InformationObject']['ItemWithoutConstraints'].encode(
            decoded)

        # Message 1 - with constraints.
        decoded = {
            'id': 0,
            'value': True,
            'comment': 'item 0',
            'extra': 2
        }

        information_object['InformationObject']['ItemWithConstraints'].encode(
            decoded)

        # Message 1 failure - with constraints.
        decoded = {
            'id': 0,
            'value': b'\x05',
            'comment': 'item 0',
            'extra': 2
        }

        # No checks of open types performed yet.
        with self.assertRaises(AssertionError):
            with self.assertRaises(asn1tools.EncodeError) as cm:
                information_object['InformationObject']['ItemWithConstraints'].encode(
                    decoded)

            self.assertEqual(str(cm.exception),
                             "Expected data of type bool, but got b'\x05'.")

        # Message 2.
        decoded = {
            'id': 1,
            'value': {
                'myValue': 7,
                'myType': 0
            },
            'comment': 'item 1',
            'extra': 5
        }

        information_object['InformationObject']['ItemWithConstraints'].encode(
            decoded)

        # Message 3 - error class.
        decoded = {
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

        information_object['InformationObject']['ErrorReturn'].encode(
            decoded)


if __name__ == '__main__':
    unittest.main()
