import unittest
import asn1tools


class Asn1ToolsUPerTest(unittest.TestCase):

    maxDiff = None

    def test_foo(self):
        foo = asn1tools.compile_files('tests/files/foo.asn', 'uper')

        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded,
                         b'\x01\x01\x09\x93\xcd\x03\x15\x6c\x5e\xb3\x7e')

        # Decode the encoded question.
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Encode an answer.
        encoded = foo.encode('Answer', {'id': 1, 'answer': False})
        self.assertEqual(encoded, b'\x01\x01\x00')

        # Decode the encoded answer.
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

        # Encode a question with missing field 'id'.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            encoded = foo.encode('Question', {'question': 'Is 1+1=3?'})

        self.assertEqual(
            str(cm.exception),
            "Sequence member 'id' not found in {'question': 'Is 1+1=3?'}.")

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_files('tests/files/rrc_8_6_0.asn', 'uper')

        # Message 1.
        decoded_message = {
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

        encoded_message = b'\x28'

        encoded = rrc.encode('PCCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('PCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 2.
        decoded_message = {
            'message': {
                'c1' : {
                    'paging': {
                    }
                }
            }
        }

        encoded_message = b'\x00'

        encoded = rrc.encode('PCCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('PCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 3.
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

        encoded_message = b'\x04\x48\xd1'

        encoded = rrc.encode('BCCH-BCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('BCCH-BCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 4.
        decoded_message = {
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

        encoded_message = (
            b'\x04\x81\x3f\xbe\x2a\x64\x12\xb2\xf3\x3a\x24\x2a\x80\x02\x02\x9b'
            b'\x29\x8a\x7f\xf8\x24\x00\x00\x11\x00\x24\xe2\x08\x05\x06\xc3\xc4'
            b'\x76\x92\x81\x41\x00\xc0\x00\x00\x0b\x23\xfd\x10\x80\xca\x19\x82'
            b'\x80\x48\xd1\x59\xe2\x43\xa0\x1a\x20\x23\x34\x12\x34\x32\x12\x48'
            b'\xcf\x10\xa8\x6a\x4c\x04\x48'
        )

        encoded = rrc.encode('BCCH-DL-SCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('BCCH-DL-SCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 5.
        decoded_message = {
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

        encoded_message = b'\x41'

        encoded = rrc.encode('DL-DCCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('DL-DCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 6.
        decoded_message = {
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

        encoded_message = b'\x40\x21\xff\xff\xff\xff\xff\xff\xfc'

        encoded = rrc.encode('DL-DCCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('DL-DCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

        # Message 7.
        decoded_message = {
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

        encoded_message = b'\x50\x80'

        encoded = rrc.encode('UL-DCCH-Message', decoded_message)
        self.assertEqual(encoded, encoded_message)
        decoded = rrc.decode('UL-DCCH-Message', encoded)
        self.assertEqual(decoded, decoded_message)

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
        self.assertEqual(all_types.encode('Sequence', {}), b'')
        self.assertEqual(all_types.encode('Sequence2', {}), b'\x00')
        self.assertEqual(all_types.encode('Sequence2', {'a': 0}), b'\x00')
        self.assertEqual(all_types.encode('Sequence2', {'a': 1}), b'\x80\x80\x80')
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
        self.assertEqual(all_types.decode('Sequence', b''), {})
        self.assertEqual(all_types.decode('Sequence2', b'\x00'), {'a': 0})
        self.assertEqual(all_types.decode('Sequence2', b'\x80\x80\x80'), {'a': 1})
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


if __name__ == '__main__':
    unittest.main()
