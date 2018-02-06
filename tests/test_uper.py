import unittest
from .utils import Asn1ToolsBaseTest
import asn1tools
import sys
from copy import deepcopy

sys.path.append('tests/files')
sys.path.append('tests/files/3gpp')

from rrc_8_6_0 import EXPECTED as RRC_8_6_0
from lpp_14_3_0 import EXPECTED as LPP_14_3_0
from x691_a2 import EXPECTED as X691_A2
from x691_a4 import EXPECTED as X691_A4


class Asn1ToolsUPerTest(Asn1ToolsBaseTest):

    maxDiff = None

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
                         ': Decode length not supported for this codec.')

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
        a2 = asn1tools.compile_dict(deepcopy(X691_A2), 'uper')

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
        with self.assertRaises(asn1tools.ParseError) as cm:
            a3 = asn1tools.compile_files('tests/files/x691_a3.asn', 'uper')

        self.assertEqual(
            str(cm.exception),
            "Invalid ASN.1 syntax at line 10, column 22: 'SEQUENCE >!<"
            "(SIZE(2, ...)) OF ChildInformation OPTIONAL,': Expected \"{\".")

        return

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
            'c': {
                'e': True
            },
            'g': '123',
            'h': True
        }

        encoded = (
            b'\x9e\x00\x06\x00\x04\x0a\x46\x90'
        )

        with self.assertRaises(asn1tools.EncodeError):
            self.assert_encode_decode(a4, 'Ax', decoded, encoded)

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_dict(deepcopy(RRC_8_6_0), 'uper')

        # Message 1.
        decoded = {
            'message': {
                'c1' : {
                    'paging': {
                        'systemInfoModification': 'true',
                        'nonCriticalExtension': {
                        }
                    }
                }
            }
        }

        encoded = b'\x28'

        self.assert_encode_decode(rrc, 'PCCH-Message', decoded, encoded)

        # Message 2.
        decoded = {
            'message': {
                'c1' : {
                    'paging': {
                    }
                }
            }
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

        # Message 4.
        decoded = {
            'message': {
                'c1': {
                    'systemInformation': {
                        'criticalExtensions': {
                            'systemInformation-r8': {
                                'sib-TypeAndInfo': [
                                    {
                                        'sib2': {
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
                                                'soundingRS-UL-ConfigCommon': {
                                                    'setup': {
                                                        'srs-BandwidthConfig': 'bw0',
                                                        'srs-SubframeConfig': 'sc4',
                                                        'ackNackSRS-SimultaneousTransmission': True
                                                    }
                                                },
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
                                    },
                                    {
                                        'sib3': {
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
                                    },
                                    {
                                        'sib4': {
                                        }
                                    },
                                    {
                                        'sib5': {
                                            'interFreqCarrierFreqList': [
                                                {
                                                    'dl-CarrierFreq': 1,
                                                    'q-RxLevMin': -45,
                                                    't-ReselectionEUTRA': 0,
                                                    'threshX-High': 31,
                                                    'threshX-Low': 29 ,
                                                    'allowedMeasBandwidth': 'mbw6',
                                                    'presenceAntennaPort1': True,
                                                    'q-OffsetFreq': 'dB0',
                                                    'neighCellConfig': (b'\x00', 2)
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        'sib6': {
                                            't-ReselectionUTRA': 3
                                        }
                                    },
                                    {
                                        'sib7': {
                                            't-ReselectionGERAN': 3
                                        }
                                    },
                                    {
                                        'sib8': {
                                            'parameters1XRTT': {
                                                'longCodeState1XRTT': (b'\x01\x23\x45\x67\x89\x00', 42)
                                            }
                                        }
                                    },
                                    {
                                        'sib9': {
                                            'hnb-Name': b'\x34'
                                        }
                                    },
                                    {
                                        'sib10': {
                                            'messageIdentifier': (b'\x23\x34', 16),
                                            'serialNumber': (b'\x12\x34', 16),
                                            'warningType': b'\x32\x12'
                                        }
                                    },
                                    {
                                        'sib11': {
                                            'messageIdentifier': (b'\x67\x88', 16),
                                            'serialNumber': (b'\x54\x35', 16),
                                            'warningMessageSegmentType': 'notLastSegment',
                                            'warningMessageSegmentNumber': 19,
                                            'warningMessageSegment': b'\x12'
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
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
            'message': {
                'c1': {
                    'counterCheck': {
                        'rrc-TransactionIdentifier': 0,
                        'criticalExtensions': {
                            'criticalExtensionsFuture': {}
                        }
                    }
                }
            }
        }

        encoded = b'\x41'

        self.assert_encode_decode(rrc, 'DL-DCCH-Message', decoded, encoded)

        # Message 6.
        decoded = {
            'message': {
                'c1': {
                    'counterCheck': {
                        'rrc-TransactionIdentifier': 0,
                        'criticalExtensions': {
                            'c1': {
                                'counterCheck-r8': {
                                    'drb-CountMSB-InfoList': [
                                        {
                                            'drb-Identity': 32,
                                            'countMSB-Uplink': 33554431,
                                            'countMSB-Downlink': 33554431
                                        }
                                    ],
                                    'nonCriticalExtension': {}
                                }
                            }
                        }
                    }
                }
            }
        }

        encoded = b'\x40\x21\xff\xff\xff\xff\xff\xff\xfc'

        self.assert_encode_decode(rrc, 'DL-DCCH-Message', decoded, encoded)

        # Message 7.
        decoded = {
            'message': {
                'c1': {
                    'counterCheckResponse': {
                        'rrc-TransactionIdentifier': 0,
                        'criticalExtensions': {
                            'counterCheckResponse-r8': {
                                'drb-CountInfoList': [
                                ],
                                'nonCriticalExtension': {}
                            }
                        }
                    }
                }
            }
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
            'lpp-MessageBody': {
                'c1': {
                    'provideAssistanceData': {
                        'criticalExtensions': {
                            'c1': {
                                'spare1': None
                            }
                        }
                    }
                }
            }
        }

        encoded = b'\x93\xfd\x1b'

        self.assert_encode_decode(lpp, 'LPP-Message', decoded, encoded)

    def test_encode_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'uper')

        self.assertEqual(all_types.encode('Boolean', True), b'\x80')
        self.assertEqual(all_types.encode('Boolean', False), b'\x00')
        self.assertEqual(all_types.encode('Integer', 32768), b'\x03\x00\x80\x00')
        self.assertEqual(all_types.encode('Integer', 32767), b'\x02\x7f\xff')
        self.assertEqual(all_types.encode('Integer', 256), b'\x02\x01\x00')
        self.assertEqual(all_types.encode('Integer', 255), b'\x02\x00\xff')
        self.assertEqual(all_types.encode('Integer', 128), b'\x02\x00\x80')
        self.assertEqual(all_types.encode('Integer', 127), b'\x01\x7f')
        self.assertEqual(all_types.encode('Integer', 1), b'\x01\x01')
        self.assertEqual(all_types.encode('Integer', 0), b'\x01\x00')
        self.assertEqual(all_types.encode('Integer', -1), b'\x01\xff')
        self.assertEqual(all_types.encode('Integer', -128), b'\x01\x80')
        self.assertEqual(all_types.encode('Integer', -129), b'\x02\xff\x7f')
        self.assertEqual(all_types.encode('Integer', -256), b'\x02\xff\x00')
        self.assertEqual(all_types.encode('Integer', -32768), b'\x02\x80\x00')
        self.assertEqual(all_types.encode('Integer', -32769), b'\x03\xff\x7f\xff')
        self.assertEqual(all_types.encode('Bitstring', (b'\x40', 4)),
                         b'\x04\x40')
        self.assertEqual(all_types.encode('Bitstring2', (b'\x12\x80', 9)),
                         b'\x12\x80')
        self.assertEqual(all_types.encode('Bitstring3', (b'\x34', 6)),
                         b'\x4d')
        self.assertEqual(all_types.encode('Octetstring', b'\x00'),
                         b'\x01\x00')
        self.assertEqual(all_types.encode('Octetstring2', b'\xab\xcd'),
                         b'\xab\xcd')
        self.assertEqual(all_types.encode('Octetstring3', b'\xab\xcd\xef'),
                         b'\xab\xcd\xef')
        self.assertEqual(all_types.encode('Octetstring4', b'\x89\xab\xcd\xef'),
                         b'\x31\x35\x79\xbd\xe0')
        self.assertEqual(all_types.encode('Enumerated', 'one'), b'\x00')
        self.assertEqual(all_types.encode('Enumerated2', 'two'), b'\x40')
        self.assertEqual(all_types.encode('Sequence', {}), b'')
        self.assertEqual(all_types.encode('Sequence2', {}), b'\x00')
        self.assertEqual(all_types.encode('Sequence2', {'a': 0}), b'\x00')
        self.assertEqual(all_types.encode('Sequence2', {'a': 1}), b'\x80\x80\x80')
        self.assertEqual(all_types.encode('Sequence3', {'a': True}), b'\x40')
        self.assertEqual(all_types.encode('Sequence4', {'a': True}), b'\x40')

        with self.assertRaises(AssertionError):
            self.assertEqual(all_types.encode('Sequence4', {'a': 1, 'b': True}),
                             b'\xc0\x40\x60\x00')

        self.assertEqual(all_types.encode('Sequence5', {'a': True}), b'\x40')

        with self.assertRaises(AssertionError):
            self.assertEqual(all_types.encode('Sequence5', {'a': True, 'b': True}),
                             b'\xc0\x40\x60\x00')

        with self.assertRaises(AssertionError):
            self.assertEqual(all_types.encode('Sequence6', {'a': True, 'c': True}),
                             b'\x60')

        with self.assertRaises(AssertionError):
            self.assertEqual(all_types.encode('Sequence6',
                                              {'a': True, 'b': True, 'c': True}),
                             b'\xe0\x20\x30\x00')

        with self.assertRaises(AssertionError):
            self.assertEqual(all_types.encode('Sequence7', {'a': True, 'd': True}),
                             b'\x60')

        with self.assertRaises(AssertionError):
            self.assertEqual(all_types.encode('Sequence7',
                                              {'a': True, 'b': True, 'd': True}),
                             b'\xe0\x60\x18\x00')

        with self.assertRaises(AssertionError):
            self.assertEqual(
                all_types.encode('Sequence7',
                                 {'a': True, 'b': True, 'c': True, 'd': True}),
                b'\xe0\x70\x18\x00\x18\x00')

        with self.assertRaises(NotImplementedError):
            all_types.encode('Sequence12', {'a': [{'a': []}]})

        self.assertEqual(all_types.encode('Ia5string', 'bar'), b'\x03\xc5\x87\x90')

    def test_decode_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'uper')

        self.assertEqual(all_types.decode('Boolean', b'\x80'), True)
        self.assertEqual(all_types.decode('Boolean', b'\x00'), False)
        self.assertEqual(all_types.decode('Integer', b'\x03\x00\x80\x00'), 32768)
        self.assertEqual(all_types.decode('Integer', b'\x02\x7f\xff'), 32767)
        self.assertEqual(all_types.decode('Integer', b'\x02\x01\x00'), 256)
        self.assertEqual(all_types.decode('Integer', b'\x02\x00\xff'), 255)
        self.assertEqual(all_types.decode('Integer', b'\x02\x00\x80'), 128)
        self.assertEqual(all_types.decode('Integer', b'\x01\x7f'), 127)
        self.assertEqual(all_types.decode('Integer', b'\x01\x01'), 1)
        self.assertEqual(all_types.decode('Integer', b'\x01\x00'), 0)
        self.assertEqual(all_types.decode('Integer', b'\x01\xff'), -1)
        self.assertEqual(all_types.decode('Integer', b'\x01\x80'), -128)
        self.assertEqual(all_types.decode('Integer', b'\x02\xff\x7f'), -129)
        self.assertEqual(all_types.decode('Integer', b'\x02\xff\x00'), -256)
        self.assertEqual(all_types.decode('Integer', b'\x02\x80\x00'), -32768)
        self.assertEqual(all_types.decode('Integer', b'\x03\xff\x7f\xff'), -32769)
        self.assertEqual(all_types.decode('Bitstring', b'\x04\x40'),
                         (b'\x40', 4))
        self.assertEqual(all_types.decode('Bitstring2', b'\x12\x80'),
                         (b'\x12\x80', 9))
        self.assertEqual(all_types.decode('Bitstring3', b'\x4d'),
                         (b'\x34', 6))
        self.assertEqual(all_types.decode('Octetstring', b'\x01\x00'),
                         b'\x00')
        self.assertEqual(all_types.decode('Octetstring2', b'\xab\xcd'),
                         b'\xab\xcd')
        self.assertEqual(all_types.decode('Octetstring3', b'\xab\xcd\xef'),
                         b'\xab\xcd\xef')
        self.assertEqual(all_types.decode('Octetstring4', b'\x31\x35\x79\xbd\xe0'),
                         b'\x89\xab\xcd\xef')
        self.assertEqual(all_types.decode('Enumerated', b'\x00'), 'one')
        self.assertEqual(all_types.decode('Enumerated2', b'\x40'), 'two')
        self.assertEqual(all_types.decode('Sequence', b''), {})
        self.assertEqual(all_types.decode('Sequence2', b'\x00'), {'a': 0})
        self.assertEqual(all_types.decode('Sequence2', b'\x80\x80\x80'), {'a': 1})

        with self.assertRaises(NotImplementedError):
            all_types.decode('Sequence12', b'\x80\x80')

        self.assertEqual(all_types.decode('Ia5string', b'\x03\xc5\x87\x90'), 'bar')

    def test_repr_all_types(self):
        all_types = asn1tools.compile_files('tests/files/all_types.asn',
                                            'uper')

        self.assertEqual(repr(all_types.types['Boolean']), 'Boolean(Boolean)')
        self.assertEqual(repr(all_types.types['Integer']), 'Integer(Integer)')
        self.assertEqual(repr(all_types.types['Bitstring']), 'BitString(Bitstring)')
        self.assertEqual(repr(all_types.types['Octetstring']), 'OctetString(Octetstring)')
        self.assertEqual(repr(all_types.types['Null']), 'Null(Null)')
        self.assertEqual(repr(all_types.types['Objectidentifier']),
                         'ObjectIdentifier(Objectidentifier)')
        self.assertEqual(repr(all_types.types['Enumerated']), 'Enumerated(Enumerated)')
        self.assertEqual(repr(all_types.types['Utf8string']), 'UTF8String(Utf8string)')
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
        self.assertEqual(repr(all_types.types['Bmpstring']),
                         'BMPString(Bmpstring)')
        self.assertEqual(repr(all_types.types['Teletexstring']),
                         'TeletexString(Teletexstring)')
        self.assertEqual(repr(all_types.types['Utctime']), 'UTCTime(Utctime)')
        self.assertEqual(repr(all_types.types['SequenceOf']),
                         'SequenceOf(SequenceOf, Integer())')
        self.assertEqual(repr(all_types.types['SetOf']), 'SetOf(SetOf, Integer())')

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


if __name__ == '__main__':
    unittest.main()
