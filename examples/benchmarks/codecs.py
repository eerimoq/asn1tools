#!/usr/bin/env python

"""A performance example comparing the performance of all codecs.

Example execution:

$ ./codecs.py
Starting encoding and decoding of a message 1000 times. This may take a few seconds.

Encoding the message 1000 times took:

CODEC      SECONDS
jer        0.163904
uper       0.283357
der        0.311143
per        0.317201
ber        0.341393
xer        0.892750

Decoding the message 1000 times took:

CODEC      SECONDS
jer        0.147299
uper       0.259876
per        0.287594
xer        0.412996
der        0.429471
ber        0.432863
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
                                  'tests',
                                  'files',
                                  '3gpp',
                                  'rrc_8_6_0.asn')

DECODED_MESSAGE = {
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

ENCODED_MESSAGE_DER = (
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

ENCODED_MESSAGE_PER = (
    b'\x04\x81\x3f\xbe\x2a\x64\x12\xb2\xf3\x20\x03\x44\x85\x50\x00\x40'
    b'\x53\x65\x31\x40\x07\xff\x82\x40\x00\x01\x10\x02\x4e\x20\x80\x50'
    b'\x6c\x3c\x47\x69\x28\x14\x10\x0c\x00\x00\x00\x01\x64\x7f\xa2\x10'
    b'\x19\x43\x30\x50\x01\x23\x45\x67\x89\x0e\x80\x34\x40\x46\x68\x24'
    b'\x68\x64\x24\x91\x9e\x21\x50\xd4\x98\x01\x12'
)

ENCODED_MESSAGE_JER = (
    b'{"message":{"c1":{"systemInformation":{"criticalExtensions":{"sy'
    b'stemInformation-r8":{"sib-TypeAndInfo":[{"sib2":{"ac-BarringInfo'
    b'":{"ac-BarringForEmergency":true,"ac-BarringForMO-Data":{"ac-Bar'
    b'ringFactor":"p95","ac-BarringForSpecialAC":"f0","ac-BarringTime"'
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

ENCODED_MESSAGE_XER = (
    b'<BCCH-DL-SCH-Message><message><c1><systemInformation><criticalEx'
    b'tensions><systemInformation-r8><sib-TypeAndInfo><sib2><ac-Barrin'
    b'gInfo><ac-BarringForEmergency><true /></ac-BarringForEmergency><'
    b'ac-BarringForMO-Data><ac-BarringFactor><p95 /></ac-BarringFactor'
    b'><ac-BarringTime><s128 /></ac-BarringTime><ac-BarringForSpecialA'
    b'C>11110</ac-BarringForSpecialAC></ac-BarringForMO-Data></ac-Barr'
    b'ingInfo><radioResourceConfigCommon><rach-ConfigCommon><preambleI'
    b'nfo><numberOfRA-Preambles><n24 /></numberOfRA-Preambles><preambl'
    b'esGroupAConfig><sizeOfRA-PreamblesGroupA><n28 /></sizeOfRA-Pream'
    b'blesGroupA><messageSizeGroupA><b144 /></messageSizeGroupA><messa'
    b'gePowerOffsetGroupB><minusinfinity /></messagePowerOffsetGroupB>'
    b'</preamblesGroupAConfig></preambleInfo><powerRampingParameters><'
    b'powerRampingStep><dB0 /></powerRampingStep><preambleInitialRecei'
    b'vedTargetPower><dBm-102 /></preambleInitialReceivedTargetPower><'
    b'/powerRampingParameters><ra-SupervisionInfo><preambleTransMax><n'
    b'8 /></preambleTransMax><ra-ResponseWindowSize><sf6 /></ra-Respon'
    b'seWindowSize><mac-ContentionResolutionTimer><sf48 /></mac-Conten'
    b'tionResolutionTimer></ra-SupervisionInfo><maxHARQ-Msg3Tx>8</maxH'
    b'ARQ-Msg3Tx></rach-ConfigCommon><bcch-Config><modificationPeriodC'
    b'oeff><n2 /></modificationPeriodCoeff></bcch-Config><pcch-Config>'
    b'<defaultPagingCycle><rf256 /></defaultPagingCycle><nB><twoT /></'
    b'nB></pcch-Config><prach-Config><rootSequenceIndex>836</rootSeque'
    b'nceIndex><prach-ConfigInfo><prach-ConfigIndex>33</prach-ConfigIn'
    b'dex><highSpeedFlag><false /></highSpeedFlag><zeroCorrelationZone'
    b'Config>10</zeroCorrelationZoneConfig><prach-FreqOffset>64</prach'
    b'-FreqOffset></prach-ConfigInfo></prach-Config><pdsch-ConfigCommo'
    b'n><referenceSignalPower>-60</referenceSignalPower><p-b>2</p-b></'
    b'pdsch-ConfigCommon><pusch-ConfigCommon><pusch-ConfigBasic><n-SB>'
    b'1</n-SB><hoppingMode><interSubFrame /></hoppingMode><pusch-Hoppi'
    b'ngOffset>10</pusch-HoppingOffset><enable64QAM><false /></enable6'
    b'4QAM></pusch-ConfigBasic><ul-ReferenceSignalsPUSCH><groupHopping'
    b'Enabled><true /></groupHoppingEnabled><groupAssignmentPUSCH>22</'
    b'groupAssignmentPUSCH><sequenceHoppingEnabled><false /></sequence'
    b'HoppingEnabled><cyclicShift>5</cyclicShift></ul-ReferenceSignals'
    b'PUSCH></pusch-ConfigCommon><pucch-ConfigCommon><deltaPUCCH-Shift'
    b'><ds1 /></deltaPUCCH-Shift><nRB-CQI>98</nRB-CQI><nCS-AN>4</nCS-A'
    b'N><n1PUCCH-AN>2047</n1PUCCH-AN></pucch-ConfigCommon><soundingRS-'
    b'UL-ConfigCommon><setup><srs-BandwidthConfig><bw0 /></srs-Bandwid'
    b'thConfig><srs-SubframeConfig><sc4 /></srs-SubframeConfig><ackNac'
    b'kSRS-SimultaneousTransmission><true /></ackNackSRS-SimultaneousT'
    b'ransmission></setup></soundingRS-UL-ConfigCommon><uplinkPowerCon'
    b'trolCommon><p0-NominalPUSCH>-126</p0-NominalPUSCH><alpha><al0 />'
    b'</alpha><p0-NominalPUCCH>-127</p0-NominalPUCCH><deltaFList-PUCCH'
    b'><deltaF-PUCCH-Format1><deltaF-2 /></deltaF-PUCCH-Format1><delta'
    b'F-PUCCH-Format1b><deltaF1 /></deltaF-PUCCH-Format1b><deltaF-PUCC'
    b'H-Format2><deltaF0 /></deltaF-PUCCH-Format2><deltaF-PUCCH-Format'
    b'2a><deltaF-2 /></deltaF-PUCCH-Format2a><deltaF-PUCCH-Format2b><d'
    b'eltaF0 /></deltaF-PUCCH-Format2b></deltaFList-PUCCH><deltaPreamb'
    b'leMsg3>-1</deltaPreambleMsg3></uplinkPowerControlCommon><ul-Cycl'
    b'icPrefixLength><len1 /></ul-CyclicPrefixLength></radioResourceCo'
    b'nfigCommon><ue-TimersAndConstants><t300><ms100 /></t300><t301><m'
    b's200 /></t301><t310><ms50 /></t310><n310><n2 /></n310><t311><ms3'
    b'0000 /></t311><n311><n2 /></n311></ue-TimersAndConstants><freqIn'
    b'fo><additionalSpectrumEmission>3</additionalSpectrumEmission></f'
    b'reqInfo><timeAlignmentTimerCommon><sf500 /></timeAlignmentTimerC'
    b'ommon></sib2><sib3><cellReselectionInfoCommon><q-Hyst><dB0 /></q'
    b'-Hyst><speedStateReselectionPars><mobilityStateParameters><t-Eva'
    b'luation><s180 /></t-Evaluation><t-HystNormal><s180 /></t-HystNor'
    b'mal><n-CellChangeMedium>1</n-CellChangeMedium><n-CellChangeHigh>'
    b'16</n-CellChangeHigh></mobilityStateParameters><q-HystSF><sf-Med'
    b'ium><dB-6 /></sf-Medium><sf-High><dB-4 /></sf-High></q-HystSF></'
    b'speedStateReselectionPars></cellReselectionInfoCommon><cellResel'
    b'ectionServingFreqInfo><threshServingLow>7</threshServingLow><cel'
    b'lReselectionPriority>3</cellReselectionPriority></cellReselectio'
    b'nServingFreqInfo><intraFreqCellReselectionInfo><q-RxLevMin>-33</'
    b'q-RxLevMin><s-IntraSearch>0</s-IntraSearch><presenceAntennaPort1'
    b'><false /></presenceAntennaPort1><neighCellConfig>10</neighCellC'
    b'onfig><t-ReselectionEUTRA>4</t-ReselectionEUTRA></intraFreqCellR'
    b'eselectionInfo></sib3><sib4 /><sib5><interFreqCarrierFreqList><I'
    b'nterFreqCarrierFreqInfo><dl-CarrierFreq>1</dl-CarrierFreq><q-RxL'
    b'evMin>-45</q-RxLevMin><t-ReselectionEUTRA>0</t-ReselectionEUTRA>'
    b'<threshX-High>31</threshX-High><threshX-Low>29</threshX-Low><all'
    b'owedMeasBandwidth><mbw6 /></allowedMeasBandwidth><presenceAntenn'
    b'aPort1><true /></presenceAntennaPort1><neighCellConfig>00</neigh'
    b'CellConfig><q-OffsetFreq><dB0 /></q-OffsetFreq></InterFreqCarrie'
    b'rFreqInfo></interFreqCarrierFreqList></sib5><sib6><t-Reselection'
    b'UTRA>3</t-ReselectionUTRA></sib6><sib7><t-ReselectionGERAN>3</t-'
    b'ReselectionGERAN></sib7><sib8><parameters1XRTT><longCodeState1XR'
    b'TT>000000010010001101000101011001111000100100</longCodeState1XRT'
    b'T></parameters1XRTT></sib8><sib9><hnb-Name>34</hnb-Name></sib9><'
    b'sib10><messageIdentifier>0010001100110100</messageIdentifier><se'
    b'rialNumber>0001001000110100</serialNumber><warningType>3212</war'
    b'ningType></sib10><sib11><messageIdentifier>0110011110001000</mes'
    b'sageIdentifier><serialNumber>0101010000110101</serialNumber><war'
    b'ningMessageSegmentType><notLastSegment /></warningMessageSegment'
    b'Type><warningMessageSegmentNumber>19</warningMessageSegmentNumbe'
    b'r><warningMessageSegment>12</warningMessageSegment></sib11></sib'
    b'-TypeAndInfo></systemInformation-r8></criticalExtensions></syste'
    b'mInformation></c1></message></BCCH-DL-SCH-Message>'
)

ITERATIONS = 1000


def encode_decode_ber():
    rrc_8_6_0 = asn1tools.compile_files(RRC_8_6_0_ASN_PATH)

    def encode():
        rrc_8_6_0.encode('BCCH-DL-SCH-Message', DECODED_MESSAGE)

    def decode():
        rrc_8_6_0.decode('BCCH-DL-SCH-Message', ENCODED_MESSAGE_BER)

    encode_time = timeit.timeit(encode, number=ITERATIONS)
    decode_time = timeit.timeit(decode, number=ITERATIONS)

    return encode_time, decode_time


def encode_decode_der():
    rrc_8_6_0 = asn1tools.compile_files(RRC_8_6_0_ASN_PATH)

    def encode():
        rrc_8_6_0.encode('BCCH-DL-SCH-Message', DECODED_MESSAGE)

    def decode():
        rrc_8_6_0.decode('BCCH-DL-SCH-Message', ENCODED_MESSAGE_DER)

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


def encode_decode_per():
    rrc_8_6_0 = asn1tools.compile_files(RRC_8_6_0_ASN_PATH, 'per')

    def encode():
        rrc_8_6_0.encode('BCCH-DL-SCH-Message', DECODED_MESSAGE)

    def decode():
        rrc_8_6_0.decode('BCCH-DL-SCH-Message', ENCODED_MESSAGE_PER)

    encode_time = timeit.timeit(encode, number=ITERATIONS)
    decode_time = timeit.timeit(decode, number=ITERATIONS)

    return encode_time, decode_time


def encode_decode_jer():
    rrc_8_6_0 = asn1tools.compile_files(RRC_8_6_0_ASN_PATH, 'jer')

    def encode():
        rrc_8_6_0.encode('BCCH-DL-SCH-Message', DECODED_MESSAGE)

    def decode():
        rrc_8_6_0.decode('BCCH-DL-SCH-Message', ENCODED_MESSAGE_JER)

    encode_time = timeit.timeit(encode, number=ITERATIONS)
    decode_time = timeit.timeit(decode, number=ITERATIONS)

    return encode_time, decode_time


def encode_decode_xer():
    rrc_8_6_0 = asn1tools.compile_files(RRC_8_6_0_ASN_PATH, 'xer')

    def encode():
        rrc_8_6_0.encode('BCCH-DL-SCH-Message', DECODED_MESSAGE)

    def decode():
        rrc_8_6_0.decode('BCCH-DL-SCH-Message', ENCODED_MESSAGE_XER)

    encode_time = timeit.timeit(encode, number=ITERATIONS)
    decode_time = timeit.timeit(decode, number=ITERATIONS)

    return encode_time, decode_time


print('Starting encoding and decoding of a message {} times. This may '
      'take a few seconds.'.format(ITERATIONS))

ber_encode_time, ber_decode_time = encode_decode_ber()
der_encode_time, der_decode_time = encode_decode_der()
uper_encode_time, uper_decode_time = encode_decode_uper()
per_encode_time, per_decode_time = encode_decode_per()
jer_encode_time, jer_decode_time = encode_decode_jer()
xer_encode_time, xer_decode_time = encode_decode_xer()

# Encode comparsion output.
measurements = [
    ('ber', ber_encode_time),
    ('der', der_encode_time),
    ('uper', uper_encode_time),
    ('per', per_encode_time),
    ('jer', jer_encode_time),
    ('xer', xer_encode_time)
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
    ('der', der_decode_time),
    ('uper', uper_decode_time),
    ('per', per_decode_time),
    ('jer', jer_decode_time),
    ('xer', xer_decode_time)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print('Decoding the message {} times took:'.format(ITERATIONS))
print()
print('CODEC      SECONDS')
for package, seconds in measurements:
    print('{:10s} {:f}'.format(package, seconds))
