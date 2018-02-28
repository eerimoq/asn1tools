#!/usr/bin/env python

"""A performance example comparing the UPER encoding and decoding
performance of two ASN.1 Python packages.

Example execution:

$ ./packages.py
Starting encoding and decoding of a message 3000 times. This may take a few seconds.

Encoding the message 3000 times took:

PACKAGE      SECONDS
asn1tools    0.674007
pycrate      2.880219

Decoding the message 3000 times took:

PACKAGE      SECONDS
asn1tools    0.598906
pycrate      2.295481
$

"""

from __future__ import print_function

import os
import timeit
import asn1tools

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
RRC_8_6_0_ASN_PATH = os.path.join(SCRIPT_DIR,
                                  '..',
                                  '..',
                                  '..',
                                  'tests',
                                  'files',
                                  '3gpp',
                                  'rrc_8_6_0.asn')

DECODED_MESSAGE_ASN1TOOLS = {
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

DECODED_MESSAGE_PYCRATE = {
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
                                            'ac-BarringForSpecialAC': (30, 5)
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
                                            }
                                            ,
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
                                            }
                                        ),
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
                                        'neighCellConfig': (2,
                                                            2),
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
                                            'neighCellConfig': (0, 2),
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
                                        'longCodeState1XRTT': (19546873380, 42)
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
                                    'messageIdentifier': (9012, 16),
                                    'serialNumber': (4660, 16),
                                    'warningType': b'2\x12'
                                }
                            ),
                            (
                                'sib11',
                                {
                                    'messageIdentifier': (26504, 16),
                                    'serialNumber': (21557, 16),
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

ENCODED_MESSAGE = (
    b'\x04\x81\x3f\xbe\x2a\x64\x12\xb2\xf3\x3a\x24\x2a\x80\x02\x02\x9b'
    b'\x29\x8a\x7f\xf8\x24\x00\x00\x11\x00\x24\xe2\x08\x05\x06\xc3\xc4'
    b'\x76\x92\x81\x41\x00\xc0\x00\x00\x0b\x23\xfd\x10\x80\xca\x19\x82'
    b'\x80\x48\xd1\x59\xe2\x43\xa0\x1a\x20\x23\x34\x12\x34\x32\x12\x48'
    b'\xcf\x10\xa8\x6a\x4c\x04\x48'
)

ITERATIONS = 3000


def asn1tools_encode_decode():
    rrc = asn1tools.compile_files(RRC_8_6_0_ASN_PATH, 'uper')

    def encode():
        rrc.encode('BCCH-DL-SCH-Message', DECODED_MESSAGE_ASN1TOOLS)

    def decode():
        rrc.decode('BCCH-DL-SCH-Message', ENCODED_MESSAGE)

    encode_time = timeit.timeit(encode, number=ITERATIONS)
    decode_time = timeit.timeit(decode, number=ITERATIONS)

    return encode_time, decode_time


def pycrate_encode_decode():
    try:
        import rrc_8_6_0_pycrate

        rrc = rrc_8_6_0_pycrate.EUTRA_RRC_Definitions.BCCH_DL_SCH_Message

        def encode():
            rrc.set_val(DECODED_MESSAGE_PYCRATE)
            rrc.to_uper()

        def decode():
            rrc.from_uper(ENCODED_MESSAGE)
            rrc()

        encode_time = timeit.timeit(encode, number=ITERATIONS)
        decode_time = timeit.timeit(decode, number=ITERATIONS)
    except ImportError:
        encode_time = float('inf')
        decode_time = float('inf')
        print('Unable to import pycrate.')
    except Exception as e:
        encode_time = float('inf')
        decode_time = float('inf')
        print('pycrate error: {}'.format(str(e)))

    return encode_time, decode_time


print('Starting encoding and decoding of a message {} times. This may '
      'take a few seconds.'.format(ITERATIONS))

asn1tools_encode_time, asn1tools_decode_time = asn1tools_encode_decode()
pycrate_encode_time, pycrate_decode_time = pycrate_encode_decode()

# Encode comparsion output.
measurements = [
    ('asn1tools', asn1tools_encode_time),
    ('pycrate', pycrate_encode_time)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print('Encoding the message {} times took:'.format(ITERATIONS))
print()
print('PACKAGE      SECONDS')
for package, seconds in measurements:
    print('{:12s} {:f}'.format(package, seconds))

# Decode comparsion output.
measurements = [
    ('asn1tools', asn1tools_decode_time),
    ('pycrate', pycrate_decode_time)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print('Decoding the message {} times took:'.format(ITERATIONS))
print()
print('PACKAGE      SECONDS')
for package, seconds in measurements:
    print('{:12s} {:f}'.format(package, seconds))
