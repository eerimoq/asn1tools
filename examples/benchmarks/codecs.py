#!/usr/bin/env python

"""A performance example comparing the performance of all codecs.

"""

from __future__ import print_function

import os
import timeit
import asn1tools

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
RRC_8_6_0_ASN_PATH = os.path.join(SCRIPT_DIR, '..', '..', 'tests', 'files', 'rrc_8_6_0.asn')

DECODED_MESSAGE = {
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

ENCODED_MESSAGE_BER = (
    b'\x30\x82\x01\x96\xa0\x82\x01\x92\xa0\x82\x01\x8e\xa0\x82\x01\x8a'
    b'\xa0\x82\x01\x86\xa0\x82\x01\x82\xa0\x82\x01\x7e\xa0\x81\xdd\xa0'
    b'\x0f\x80\x01\x01\xa2\x0a\x80\x01\x0f\x81\x01\x05\x82\x02\x03\xf0'
    b'\xa1\x81\xad\xa0\x26\xa0\x0e\x80\x01\x05\xa1\x09\x80\x01\x06\x81'
    b'\x01\x01\x82\x01\x00\xa1\x06\x80\x01\x00\x81\x01\x09\xa2\x09\x80'
    b'\x01\x05\x81\x01\x04\x82\x01\x05\x83\x01\x08\xa1\x03\x80\x01\x00'
    b'\xa2\x06\x80\x01\x03\x81\x01\x01\xa3\x12\x80\x02\x03\x44\xa1\x0c'
    b'\x80\x01\x21\x81\x01\x00\x82\x01\x0a\x83\x01\x40\xa4\x06\x80\x01'
    b'\xc4\x81\x01\x02\xa5\x1c\xa0\x0c\x80\x01\x01\x81\x01\x00\x82\x01'
    b'\x0a\x83\x01\x00\xa1\x0c\x80\x01\x01\x81\x01\x16\x82\x01\x00\x83'
    b'\x01\x05\xa6\x0d\x80\x01\x00\x81\x01\x62\x82\x01\x04\x83\x02\x07'
    b'\xff\xa7\x0b\xa1\x09\x80\x01\x00\x81\x01\x04\x82\x01\x01\xa8\x1d'
    b'\x80\x01\x82\x81\x01\x00\x82\x01\x81\xa3\x0f\x80\x01\x00\x81\x01'
    b'\x00\x82\x01\x01\x83\x01\x00\x84\x01\x01\x84\x01\xff\x89\x01\x00'
    b'\xa2\x12\x80\x01\x00\x81\x01\x01\x82\x01\x01\x83\x01\x01\x84\x01'
    b'\x06\x85\x01\x01\xa3\x03\x82\x01\x03\x85\x01\x00\xa1\x37\xa0\x1b'
    b'\x80\x01\x00\xa1\x16\xa0\x0c\x80\x01\x03\x81\x01\x03\x82\x01\x01'
    b'\x83\x01\x10\xa1\x06\x80\x01\x00\x81\x01\x01\xa1\x06\x81\x01\x07'
    b'\x82\x01\x03\xa2\x10\x80\x01\xdf\x82\x01\x00\x84\x01\x00\x85\x02'
    b'\x06\x80\x86\x01\x04\xa2\x00\xa3\x20\xa0\x1e\x30\x1c\x80\x01\x01'
    b'\x81\x01\xd3\x83\x01\x00\x85\x01\x1f\x86\x01\x1d\x87\x01\x00\x88'
    b'\x01\x01\x8a\x02\x06\x00\x8b\x01\x0f\xa4\x03\x82\x01\x03\xa5\x03'
    b'\x80\x01\x03\xa6\x0b\xa3\x09\x81\x07\x06\x01\x23\x45\x67\x89\x00'
    b'\xa7\x03\x80\x01\x34\xa8\x0e\x80\x03\x00\x23\x34\x81\x03\x00\x12'
    b'\x34\x82\x02\x32\x12\xa9\x13\x80\x03\x00\x67\x88\x81\x03\x00\x54'
    b'\x35\x82\x01\x00\x83\x01\x13\x84\x01\x12'
)

ENCODED_MESSAGE_UPER = (
    b'\x04\x81\x3f\xbe\x2a\x64\x12\xb2\xf3\x3a\x24\x2a\x80\x02\x02\x9b'
    b'\x29\x8a\x7f\xf8\x24\x00\x00\x11\x00\x24\xe2\x08\x05\x06\xc3\xc4'
    b'\x76\x92\x81\x41\x00\xc0\x00\x00\x0b\x23\xfd\x10\x80\xca\x19\x82'
    b'\x80\x48\xd1\x59\xe2\x43\xa0\x1a\x20\x23\x34\x12\x34\x32\x12\x48'
    b'\xcf\x10\xa8\x6a\x4c\x04\x48'
)

ITERATIONS = 3000


def encode_decode_ber():
    rrc_8_6_0 = asn1tools.compile_files(RRC_8_6_0_ASN_PATH)

    def encode():
        rrc_8_6_0.encode('BCCH-DL-SCH-Message', DECODED_MESSAGE)

    def decode():
        rrc_8_6_0.decode('BCCH-DL-SCH-Message', ENCODED_MESSAGE_BER)

    encode_time = timeit.timeit(encode, number=ITERATIONS)
    decode_time = timeit.timeit(decode, number=ITERATIONS)

    return encode_time, decode_time


def encode_decode_uper():
    rrc_8_6_0 = asn1tools.compile_files(RRC_8_6_0_ASN_PATH, 'uper')

    def encode():
        rrc_8_6_0.encode('BCCH-DL-SCH-Message', DECODED_MESSAGE)

    def decode():
        rrc_8_6_0.decode('BCCH-DL-SCH-Message', ENCODED_MESSAGE_UPER)

    encode_time = timeit.timeit(encode, number=ITERATIONS)
    decode_time = timeit.timeit(decode, number=ITERATIONS)

    return encode_time, decode_time


print('Starting encoding and decoding of a message {} times. This may '
      'take a few seconds.'.format(ITERATIONS))

ber_encode_time, ber_decode_time = encode_decode_ber()
uper_encode_time, uper_decode_time = encode_decode_uper()

# Encode comparsion output.
measurements = [
    ('ber', ber_encode_time),
    ('uper', uper_encode_time)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print('Encoding the message {} times took:'.format(ITERATIONS))
print()
print('CODEC      SECONDS')
for package, seconds in measurements:
    print('{:10s} {:f}'.format(package, seconds))

# Decode comparsion output.
measurements = [
    ('ber', ber_decode_time),
    ('uper', uper_decode_time)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print('Decoding the message {} times took:'.format(ITERATIONS))
print()
print('CODEC      SECONDS')
for package, seconds in measurements:
    print('{:10s} {:f}'.format(package, seconds))
