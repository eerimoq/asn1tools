import unittest
from .utils import Asn1ToolsBaseTest
import sys
from copy import deepcopy

import asn1tools

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0


class Asn1ToolsAsn1Asn1Test(Asn1ToolsBaseTest):

    maxDiff = None

    def test_foo(self):
        foo = asn1tools.compile_files(['tests/files/foo.asn'], 'asn1')

        datas = [
            ('Question',
             {'id': 1, 'question': 'Is 1+1=3?'},
             b'question Question ::= { id 1, question "Is 1+1=3?" }')
        ]

        for name, decoded, encoded in datas:
            self.assertEqual(foo.encode(name, decoded), encoded)

    def test_foo_indent(self):
        foo = asn1tools.compile_files(['tests/files/foo.asn'], 'asn1')

        datas = [
            ('Question',
             {'id': 1, 'question': 'Is 1+1=3?'},
             b'question Question ::= {\n'
             b'  id 1,\n'
             b'  question "Is 1+1=3?"\n'
             b'}')
        ]

        for name, decoded, encoded in datas:
            actual = foo.encode(name, decoded, indent=2)
            self.assertEqual(actual, encoded)

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'asn1')

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

        encoded = (
            b"bcch-dl-sch-message BCCH-DL-SCH-Message ::= {\n"
            b"  message c1 : systemInformation : {\n"
            b"    criticalExtensions systemInformation-r8 : {\n"
            b"      sib-TypeAndInfo {\n"
            b"        sib2 : {\n"
            b"          ac-BarringInfo {\n"
            b"            ac-BarringForEmergency TRUE,\n"
            b"            ac-BarringForMO-Data {\n"
            b"              ac-BarringFactor p95,\n"
            b"              ac-BarringTime s128,\n"
            b"              ac-BarringForSpecialAC '11110'B\n"
            b"            }\n"
            b"          },\n"
            b"          radioResourceConfigCommon {\n"
            b"            rach-ConfigCommon {\n"
            b"              preambleInfo {\n"
            b"                numberOfRA-Preambles n24,\n"
            b"                preamblesGroupAConfig {\n"
            b"                  sizeOfRA-PreamblesGroupA n28,\n"
            b"                  messageSizeGroupA b144,\n"
            b"                  messagePowerOffsetGroupB minusinfinity\n"
            b"                }\n"
            b"              },\n"
            b"              powerRampingParameters {\n"
            b"                powerRampingStep dB0,\n"
            b"                preambleInitialReceivedTargetPower dBm-102\n"
            b"              },\n"
            b"              ra-SupervisionInfo {\n"
            b"                preambleTransMax n8,\n"
            b"                ra-ResponseWindowSize sf6,\n"
            b"                mac-ContentionResolutionTimer sf48\n"
            b"              },\n"
            b"              maxHARQ-Msg3Tx 8\n"
            b"            },\n"
            b"            bcch-Config {\n"
            b"              modificationPeriodCoeff n2\n"
            b"            },\n"
            b"            pcch-Config {\n"
            b"              defaultPagingCycle rf256,\n"
            b"              nB twoT\n"
            b"            },\n"
            b"            prach-Config {\n"
            b"              rootSequenceIndex 836,\n"
            b"              prach-ConfigInfo {\n"
            b"                prach-ConfigIndex 33,\n"
            b"                highSpeedFlag FALSE,\n"
            b"                zeroCorrelationZoneConfig 10,\n"
            b"                prach-FreqOffset 64\n"
            b"              }\n"
            b"            },\n"
            b"            pdsch-ConfigCommon {\n"
            b"              referenceSignalPower -60,\n"
            b"              p-b 2\n"
            b"            },\n"
            b"            pusch-ConfigCommon {\n"
            b"              pusch-ConfigBasic {\n"
            b"                n-SB 1,\n"
            b"                hoppingMode interSubFrame,\n"
            b"                pusch-HoppingOffset 10,\n"
            b"                enable64QAM FALSE\n"
            b"              },\n"
            b"              ul-ReferenceSignalsPUSCH {\n"
            b"                groupHoppingEnabled TRUE,\n"
            b"                groupAssignmentPUSCH 22,\n"
            b"                sequenceHoppingEnabled FALSE,\n"
            b"                cyclicShift 5\n"
            b"              }\n"
            b"            },\n"
            b"            pucch-ConfigCommon {\n"
            b"              deltaPUCCH-Shift ds1,\n"
            b"              nRB-CQI 98,\n"
            b"              nCS-AN 4,\n"
            b"              n1PUCCH-AN 2047\n"
            b"            },\n"
            b"            soundingRS-UL-ConfigCommon setup : {\n"
            b"              srs-BandwidthConfig bw0,\n"
            b"              srs-SubframeConfig sc4,\n"
            b"              ackNackSRS-SimultaneousTransmission TRUE\n"
            b"            },\n"
            b"            uplinkPowerControlCommon {\n"
            b"              p0-NominalPUSCH -126,\n"
            b"              alpha al0,\n"
            b"              p0-NominalPUCCH -127,\n"
            b"              deltaFList-PUCCH {\n"
            b"                deltaF-PUCCH-Format1 deltaF-2,\n"
            b"                deltaF-PUCCH-Format1b deltaF1,\n"
            b"                deltaF-PUCCH-Format2 deltaF0,\n"
            b"                deltaF-PUCCH-Format2a deltaF-2,\n"
            b"                deltaF-PUCCH-Format2b deltaF0\n"
            b"              },\n"
            b"              deltaPreambleMsg3 -1\n"
            b"            },\n"
            b"            ul-CyclicPrefixLength len1\n"
            b"          },\n"
            b"          ue-TimersAndConstants {\n"
            b"            t300 ms100,\n"
            b"            t301 ms200,\n"
            b"            t310 ms50,\n"
            b"            n310 n2,\n"
            b"            t311 ms30000,\n"
            b"            n311 n2\n"
            b"          },\n"
            b"          freqInfo {\n"
            b"            additionalSpectrumEmission 3\n"
            b"          },\n"
            b"          timeAlignmentTimerCommon sf500\n"
            b"        },\n"
            b"        sib3 : {\n"
            b"          cellReselectionInfoCommon {\n"
            b"            q-Hyst dB0,\n"
            b"            speedStateReselectionPars {\n"
            b"              mobilityStateParameters {\n"
            b"                t-Evaluation s180,\n"
            b"                t-HystNormal s180,\n"
            b"                n-CellChangeMedium 1,\n"
            b"                n-CellChangeHigh 16\n"
            b"              },\n"
            b"              q-HystSF {\n"
            b"                sf-Medium dB-6,\n"
            b"                sf-High dB-4\n"
            b"              }\n"
            b"            }\n"
            b"          },\n"
            b"          cellReselectionServingFreqInfo {\n"
            b"            threshServingLow 7,\n"
            b"            cellReselectionPriority 3\n"
            b"          },\n"
            b"          intraFreqCellReselectionInfo {\n"
            b"            q-RxLevMin -33,\n"
            b"            s-IntraSearch 0,\n"
            b"            presenceAntennaPort1 FALSE,\n"
            b"            neighCellConfig '10'B,\n"
            b"            t-ReselectionEUTRA 4\n"
            b"          }\n"
            b"        },\n"
            b"        sib4 : {\n"
            b"        },\n"
            b"        sib5 : {\n"
            b"          interFreqCarrierFreqList {\n"
            b"            {\n"
            b"              dl-CarrierFreq 1,\n"
            b"              q-RxLevMin -45,\n"
            b"              t-ReselectionEUTRA 0,\n"
            b"              threshX-High 31,\n"
            b"              threshX-Low 29,\n"
            b"              allowedMeasBandwidth mbw6,\n"
            b"              presenceAntennaPort1 TRUE,\n"
            b"              neighCellConfig '00'B,\n"
            b"              q-OffsetFreq dB0\n"
            b"            }\n"
            b"          }\n"
            b"        },\n"
            b"        sib6 : {\n"
            b"          t-ReselectionUTRA 3\n"
            b"        },\n"
            b"        sib7 : {\n"
            b"          t-ReselectionGERAN 3\n"
            b"        },\n"
            b"        sib8 : {\n"
            b"          parameters1XRTT {\n"
            b"            longCodeState1XRTT '000000010010001101000101011001111000100100'B\n"
            b"          }\n"
            b"        },\n"
            b"        sib9 : {\n"
            b"          hnb-Name '34'H\n"
            b"        },\n"
            b"        sib10 : {\n"
            b"          messageIdentifier '0010001100110100'B,\n"
            b"          serialNumber '0001001000110100'B,\n"
            b"          warningType '3212'H\n"
            b"        },\n"
            b"        sib11 : {\n"
            b"          messageIdentifier '0110011110001000'B,\n"
            b"          serialNumber '0101010000110101'B,\n"
            b"          warningMessageSegmentType notLastSegment,\n"
            b"          warningMessageSegmentNumber 19,\n"
            b"          warningMessageSegment '12'H\n"
            b"        }\n"
            b"      }\n"
            b"    }\n"
            b"  }\n"
            b"}"
        )

        self.assertEqual(rrc.encode('BCCH-DL-SCH-Message', decoded, indent=2),
                         encoded)

    def test_null(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= NULL "
            "END",
            'asn1')

        decoded = None
        encoded = b'a A ::= NULL'

        self.assertEqual(foo.encode('A', decoded), encoded)

    def test_utc_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UTCTime "
            "END",
            'asn1')

        decoded = '010203040506Z'
        encoded = b'a A ::= "010203040506Z"'

        self.assertEqual(foo.encode('A', decoded), encoded)

    def test_generalized_time(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= GeneralizedTime "
            "END",
            'asn1')

        decoded = '20001231235959.999Z'
        encoded = b'a A ::= "20001231235959.999Z"'

        self.assertEqual(foo.encode('A', decoded), encoded)

    def test_visible_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= VisibleString "
            "END",
            'asn1')

        decoded = 'foo'
        encoded = b'a A ::= "foo"'

        self.assertEqual(foo.encode('A', decoded), encoded)

    def test_universal_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= UniversalString "
            "END",
            'asn1')

        decoded = 'bar'
        encoded = b'a A ::= "bar"'

        self.assertEqual(foo.encode('A', decoded), encoded)

    def test_printable_string(self):
        foo = asn1tools.compile_string(
            "Foo DEFINITIONS AUTOMATIC TAGS ::= "
            "BEGIN "
            "A ::= PrintableString "
            "END",
            'asn1')

        decoded = 'foo'
        encoded = b'a A ::= "foo"'

        self.assertEqual(foo.encode('A', decoded), encoded)


if __name__ == '__main__':
    unittest.main()
