import logging
import unittest

import asn1tools
from asn1tools.schema import Module, Sequence, Boolean, Integer
from asn1tools.codecs import ber


class Asn1ToolsTest(unittest.TestCase):

    maxDiff = None

    def test_str(self):
        module = Module(
            'Foo',
            [
                Sequence(
                    'Bar',
                    [
                        Integer('foo', optional=True),
                        Integer('bar', default=5),
                        Sequence(
                            'fie',
                            [
                                Integer('fum'),
                                Integer('foo'),
                            ])
                    ]),
                Sequence('Fie', [])
            ])

        self.assertEqual(
            str(module),
            """Foo DEFINITIONS ::= BEGIN
    Bar ::= SEQUENCE {
        foo INTEGER OPTIONAL,
        bar INTEGER DEFAULT 5,
        fie SEQUENCE {
            fum INTEGER,
            foo INTEGER
        }
    },
    Fie ::= SEQUENCE {
    }
END""")

    def test_integer(self):
        foo = Integer('foo')

        # BER encode and decode.
        encoded = ber.encode(1, foo)
        self.assertEqual(encoded, b'\x02\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, 1)

        encoded = ber.encode(-32768, foo)
        self.assertEqual(encoded, b'\x02\x02\x80\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, -32768)

        encoded = ber.encode(-32769, foo)
        self.assertEqual(encoded, b'\x02\x03\xff\x7f\xff')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, -32769)

    def test_boolean(self):
        foo = Boolean('foo')

        # BER encode and decode.
        encoded = ber.encode(True, foo)
        self.assertEqual(encoded, b'\x01\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, True)

        encoded = ber.encode(False, foo)
        self.assertEqual(encoded, b'\x01\x01\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, False)

        encoded = ber.encode(1000, foo)
        self.assertEqual(encoded, b'\x01\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, True)

        encoded = ber.encode(0, foo)
        self.assertEqual(encoded, b'\x01\x01\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, False)

    def test_sequence(self):
        foo = Sequence('foo', [Integer('bar', default=0),
                               Boolean('fie')])

        # BER encode and decode.
        encoded = ber.encode({'bar': 5, 'fie': True}, foo)
        self.assertEqual(encoded, b'\x30\x06\x02\x01\x05\x01\x01\x01')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, {'bar': 5, 'fie': True})

        encoded = ber.encode({'bar': -1, 'fie': False}, foo)
        self.assertEqual(encoded, b'\x30\x06\x02\x01\xff\x01\x01\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, {'bar': -1, 'fie': False})

        encoded = ber.encode({'fie': False}, foo)
        self.assertEqual(encoded, b'\x30\x03\x01\x01\x00')
        decoded = ber.decode(encoded, foo)
        self.assertEqual(decoded, {'bar': 0, 'fie': False})

    def test_compile_file(self):
        foo = asn1tools.compile_file('tests/files/foo.asn')

        # Get a list of all types.
        self.assertEqual(foo.get_type_names(), {'Foo': ['Question', 'Answer']})

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded, b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3?')

        # Decode the encoded question.
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Get an non-existing type.
        with self.assertRaises(LookupError) as cm:
            foo.get_type('Bar')

        self.assertEqual(str(cm.exception), "Type 'Bar' not found.")

        # Get the answer type from the schema.
        answer = foo.get_type('Answer')

        # Encode an answer.
        encoded = answer.encode({'id': 1, 'answer': False})
        self.assertEqual(encoded, b'0\x06\x02\x01\x01\x01\x01\x00')

        # Decode the encoded answer.
        decoded = answer.decode(encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

    def test_rrc_8_6_0(self):
        rrc = asn1tools.compile_file('tests/files/rrc_8.6.0.asn')
        #print(rrc)
        self.assertEqual(
            rrc.get_type_names(),
            {
                'EUTRA-InterNodeDefinitions': [
                    'HandoverCommand',
                    'HandoverCommand-r8-IEs',
                    'HandoverPreparationInformation',
                    'HandoverPreparationInformation-r8-IEs',
                    'UERadioAccessCapabilityInformation',
                    'UERadioAccessCapabilityInformation-r8-IEs',
                    'AS-Config',
                    'AS-Context',
                    'ReestablishmentInfo',
                    'AdditionalReestabInfoList',
                    'AdditionalReestabInfo',
                    'Key-eNodeB-Star',
                    'RRM-Config'
                ],
                'EUTRA-RRC-Definitions': [
                    'BCCH-BCH-Message',
                    'BCCH-BCH-MessageType',
                    'BCCH-DL-SCH-Message',
                    'BCCH-DL-SCH-MessageType',
                    'PCCH-Message',
                    'PCCH-MessageType',
                    'DL-CCCH-Message',
                    'DL-CCCH-MessageType',
                    'DL-DCCH-Message',
                    'DL-DCCH-MessageType',
                    'UL-CCCH-Message',
                    'UL-CCCH-MessageType',
                    'UL-DCCH-Message',
                    'UL-DCCH-MessageType',
                    'CounterCheck',
                    'CounterCheck-r8-IEs',
                    'DRB-CountMSB-InfoList',
                    'DRB-CountMSB-Info',
                    'CounterCheckResponse',
                    'CounterCheckResponse-r8-IEs',
                    'DRB-CountInfoList',
                    'DRB-CountInfo',
                    'CSFBParametersRequestCDMA2000',
                    'CSFBParametersRequestCDMA2000-r8-IEs',
                    'CSFBParametersResponseCDMA2000',
                    'CSFBParametersResponseCDMA2000-r8-IEs',
                    'DLInformationTransfer',
                    'DLInformationTransfer-r8-IEs',
                    'HandoverFromEUTRAPreparationRequest',
                    'HandoverFromEUTRAPreparationRequest-r8-IEs',
                    'MasterInformationBlock',
                    'MeasurementReport',
                    'MeasurementReport-r8-IEs',
                    'MobilityFromEUTRACommand',
                    'MobilityFromEUTRACommand-r8-IEs',
                    'Handover',
                    'CellChangeOrder',
                    'SI-OrPSI-GERAN',
                    'SystemInfoListGERAN',
                    'Paging',
                    'PagingRecordList',
                    'PagingRecord',
                    'PagingUE-Identity',
                    'IMSI',
                    'IMSI-Digit',
                    'RRCConnectionReconfiguration',
                    'RRCConnectionReconfiguration-r8-IEs',
                    'SecurityConfigHO',
                    'RRCConnectionReconfigurationComplete',
                    'RRCConnectionReconfigurationComplete-r8-IEs',
                    'RRCConnectionReestablishment',
                    'RRCConnectionReestablishment-r8-IEs',
                    'RRCConnectionReestablishmentComplete',
                    'RRCConnectionReestablishmentComplete-r8-IEs',
                    'RRCConnectionReestablishmentReject',
                    'RRCConnectionReestablishmentReject-r8-IEs',
                    'RRCConnectionReestablishmentRequest',
                    'RRCConnectionReestablishmentRequest-r8-IEs',
                    'ReestabUE-Identity',
                    'ReestablishmentCause',
                    'RRCConnectionReject',
                    'RRCConnectionReject-r8-IEs',
                    'RRCConnectionRelease',
                    'RRCConnectionRelease-r8-IEs',
                    'ReleaseCause',
                    'RedirectedCarrierInfo',
                    'IdleModeMobilityControlInfo',
                    'FreqPriorityListEUTRA',
                    'FreqPriorityEUTRA',
                    'FreqsPriorityListGERAN',
                    'FreqsPriorityGERAN',
                    'FreqPriorityListUTRA-FDD',
                    'FreqPriorityUTRA-FDD',
                    'FreqPriorityListUTRA-TDD',
                    'FreqPriorityUTRA-TDD',
                    'BandClassPriorityListHRPD',
                    'BandClassPriorityHRPD',
                    'BandClassPriorityList1XRTT',
                    'BandClassPriority1XRTT',
                    'RRCConnectionRequest',
                    'RRCConnectionRequest-r8-IEs',
                    'InitialUE-Identity',
                    'EstablishmentCause',
                    'RRCConnectionSetup',
                    'RRCConnectionSetup-r8-IEs',
                    'RRCConnectionSetupComplete',
                    'RRCConnectionSetupComplete-r8-IEs',
                    'RegisteredMME',
                    'SecurityModeCommand',
                    'SecurityModeCommand-r8-IEs',
                    'SecurityConfigSMC',
                    'SecurityModeComplete',
                    'SecurityModeComplete-r8-IEs',
                    'SecurityModeFailure',
                    'SecurityModeFailure-r8-IEs',
                    'SystemInformation',
                    'SystemInformation-r8-IEs',
                    'SystemInformationBlockType1',
                    'PLMN-IdentityList',
                    'PLMN-IdentityInfo',
                    'SchedulingInfoList',
                    'SchedulingInfo',
                    'SIB-MappingInfo',
                    'SIB-Type',
                    'UECapabilityEnquiry',
                    'UECapabilityEnquiry-r8-IEs',
                    'UE-CapabilityRequest',
                    'UECapabilityInformation',
                    'UECapabilityInformation-r8-IEs',
                    'ULHandoverPreparationTransfer',
                    'ULHandoverPreparationTransfer-r8-IEs',
                    'ULInformationTransfer',
                    'ULInformationTransfer-r8-IEs',
                    'SystemInformationBlockType2',
                    'AC-BarringConfig',
                    'MBSFN-SubframeConfigList',
                    'MBSFN-SubframeConfig',
                    'SystemInformationBlockType3',
                    'SystemInformationBlockType4',
                    'IntraFreqNeighCellList',
                    'IntraFreqNeighCellInfo',
                    'IntraFreqBlackCellList',
                    'SystemInformationBlockType5',
                    'InterFreqCarrierFreqList',
                    'InterFreqCarrierFreqInfo',
                    'InterFreqNeighCellList',
                    'InterFreqNeighCellInfo',
                    'InterFreqBlackCellList',
                    'SystemInformationBlockType6',
                    'CarrierFreqListUTRA-FDD',
                    'CarrierFreqUTRA-FDD',
                    'CarrierFreqListUTRA-TDD',
                    'CarrierFreqUTRA-TDD',
                    'SystemInformationBlockType7',
                    'CarrierFreqsInfoListGERAN',
                    'CarrierFreqsInfoGERAN',
                    'SystemInformationBlockType8',
                    'CellReselectionParametersCDMA2000',
                    'NeighCellListCDMA2000',
                    'NeighCellCDMA2000',
                    'NeighCellsPerBandclassListCDMA2000',
                    'NeighCellsPerBandclassCDMA2000',
                    'PhysCellIdListCDMA2000',
                    'BandClassListCDMA2000',
                    'BandClassInfoCDMA2000',
                    'SystemInformationBlockType9',
                    'SystemInformationBlockType10',
                    'SystemInformationBlockType11',
                    'AntennaInfoCommon',
                    'AntennaInfoDedicated',
                    'CQI-ReportConfig',
                    'CQI-ReportPeriodic',
                    'DRB-Identity',
                    'LogicalChannelConfig',
                    'MAC-MainConfig',
                    'DRX-Config',
                    'PDCP-Config',
                    'PDSCH-ConfigCommon',
                    'PDSCH-ConfigDedicated',
                    'PHICH-Config',
                    'PhysicalConfigDedicated',
                    'P-Max',
                    'PRACH-ConfigSIB',
                    'PRACH-Config',
                    'PRACH-ConfigInfo',
                    'PresenceAntennaPort1',
                    'PUCCH-ConfigCommon',
                    'PUCCH-ConfigDedicated',
                    'PUSCH-ConfigCommon',
                    'PUSCH-ConfigDedicated',
                    'UL-ReferenceSignalsPUSCH',
                    'RACH-ConfigCommon',
                    'RACH-ConfigDedicated',
                    'RadioResourceConfigCommonSIB',
                    'RadioResourceConfigCommon',
                    'BCCH-Config',
                    'PCCH-Config',
                    'UL-CyclicPrefixLength',
                    'RadioResourceConfigDedicated',
                    'SRB-ToAddModList',
                    'SRB-ToAddMod',
                    'DRB-ToAddModList',
                    'DRB-ToAddMod',
                    'DRB-ToReleaseList',
                    'RLC-Config',
                    'UL-AM-RLC',
                    'DL-AM-RLC',
                    'UL-UM-RLC',
                    'DL-UM-RLC',
                    'SN-FieldLength',
                    'T-PollRetransmit',
                    'PollPDU',
                    'PollByte',
                    'T-Reordering',
                    'T-StatusProhibit',
                    'SchedulingRequestConfig',
                    'SoundingRS-UL-ConfigCommon',
                    'SoundingRS-UL-ConfigDedicated',
                    'SPS-Config',
                    'SPS-ConfigDL',
                    'SPS-ConfigUL',
                    'N1-PUCCH-AN-PersistentList',
                    'TDD-Config',
                    'TimeAlignmentTimer',
                    'TPC-PDCCH-Config',
                    'TPC-Index',
                    'UplinkPowerControlCommon',
                    'UplinkPowerControlDedicated',
                    'DeltaFList-PUCCH',
                    'NextHopChainingCount',
                    'SecurityAlgorithmConfig',
                    'ShortMAC-I',
                    'AdditionalSpectrumEmission',
                    'ARFCN-ValueCDMA2000',
                    'ARFCN-ValueEUTRA',
                    'ARFCN-ValueGERAN',
                    'ARFCN-ValueUTRA',
                    'BandclassCDMA2000',
                    'BandIndicatorGERAN',
                    'CarrierFreqCDMA2000',
                    'CarrierFreqGERAN',
                    'CarrierFreqsGERAN',
                    'ExplicitListOfARFCNs',
                    'CDMA2000-Type',
                    'CellIdentity',
                    'CellIndexList',
                    'CellIndex',
                    'CellReselectionPriority',
                    'CSFB-RegistrationParam1XRTT',
                    'CellGlobalIdEUTRA',
                    'CellGlobalIdUTRA',
                    'CellGlobalIdGERAN',
                    'CellGlobalIdCDMA2000',
                    'MobilityControlInfo',
                    'CarrierBandwidthEUTRA',
                    'CarrierFreqEUTRA',
                    'MobilityParametersCDMA2000',
                    'MobilityStateParameters',
                    'PhysCellId',
                    'PhysCellIdRange',
                    'PhysCellIdCDMA2000',
                    'PhysCellIdGERAN',
                    'PhysCellIdUTRA-FDD',
                    'PhysCellIdUTRA-TDD',
                    'PLMN-Identity',
                    'MCC',
                    'MNC',
                    'MCC-MNC-Digit',
                    'PreRegistrationInfoHRPD',
                    'SecondaryPreRegistrationZoneIdListHRPD',
                    'PreRegistrationZoneIdHRPD',
                    'Q-RxLevMin',
                    'Q-OffsetRange',
                    'Q-OffsetRangeInterRAT',
                    'ReselectionThreshold',
                    'SpeedStateScaleFactors',
                    'SystemTimeInfoCDMA2000',
                    'TrackingAreaCode',
                    'T-Reselection',
                    'AllowedMeasBandwidth',
                    'Hysteresis',
                    'MeasConfig',
                    'MeasIdToRemoveList',
                    'MeasObjectToRemoveList',
                    'ReportConfigToRemoveList',
                    'MeasGapConfig',
                    'MeasId',
                    'MeasIdToAddModList',
                    'MeasIdToAddMod',
                    'MeasObjectCDMA2000',
                    'CellsToAddModListCDMA2000',
                    'CellsToAddModCDMA2000',
                    'MeasObjectEUTRA',
                    'CellsToAddModList',
                    'CellsToAddMod',
                    'BlackCellsToAddModList',
                    'BlackCellsToAddMod',
                    'MeasObjectGERAN',
                    'MeasObjectId',
                    'MeasObjectToAddModList',
                    'MeasObjectToAddMod',
                    'MeasObjectUTRA',
                    'CellsToAddModListUTRA-FDD',
                    'CellsToAddModUTRA-FDD',
                    'CellsToAddModListUTRA-TDD',
                    'CellsToAddModUTRA-TDD',
                    'MeasResults',
                    'MeasResultListEUTRA',
                    'MeasResultEUTRA',
                    'MeasResultListUTRA',
                    'MeasResultUTRA',
                    'MeasResultListGERAN',
                    'MeasResultGERAN',
                    'MeasResultsCDMA2000',
                    'MeasResultListCDMA2000',
                    'MeasResultCDMA2000',
                    'PLMN-IdentityList2',
                    'QuantityConfig',
                    'QuantityConfigEUTRA',
                    'QuantityConfigUTRA',
                    'QuantityConfigGERAN',
                    'QuantityConfigCDMA2000',
                    'ReportConfigEUTRA',
                    'ThresholdEUTRA',
                    'ReportConfigId',
                    'ReportConfigInterRAT',
                    'ThresholdUTRA',
                    'ThresholdGERAN',
                    'ThresholdCDMA2000',
                    'ReportConfigToAddModList',
                    'ReportConfigToAddMod',
                    'ReportInterval',
                    'RSRP-Range',
                    'RSRQ-Range',
                    'TimeToTrigger',
                    'C-RNTI',
                    'DedicatedInfoCDMA2000',
                    'DedicatedInfoNAS',
                    'FilterCoefficient',
                    'MMEC',
                    'NeighCellConfig',
                    'RAND-CDMA2000',
                    'RAT-Type',
                    'RRC-TransactionIdentifier',
                    'S-TMSI',
                    'UE-CapabilityRAT-ContainerList',
                    'UE-CapabilityRAT-Container',
                    'UE-EUTRA-Capability',
                    'AccessStratumRelease',
                    'PDCP-Parameters',
                    'PhyLayerParameters',
                    'RF-Parameters',
                    'SupportedBandListEUTRA',
                    'SupportedBandEUTRA',
                    'MeasParameters',
                    'BandListEUTRA',
                    'BandInfoEUTRA',
                    'InterFreqBandList',
                    'InterFreqBandInfo',
                    'InterRAT-BandList',
                    'InterRAT-BandInfo',
                    'IRAT-ParametersUTRA-FDD',
                    'SupportedBandListUTRA-FDD',
                    'SupportedBandUTRA-FDD',
                    'IRAT-ParametersUTRA-TDD128',
                    'SupportedBandListUTRA-TDD128',
                    'SupportedBandUTRA-TDD128',
                    'IRAT-ParametersUTRA-TDD384',
                    'SupportedBandListUTRA-TDD384',
                    'SupportedBandUTRA-TDD384',
                    'IRAT-ParametersUTRA-TDD768',
                    'SupportedBandListUTRA-TDD768',
                    'SupportedBandUTRA-TDD768',
                    'IRAT-ParametersGERAN',
                    'SupportedBandListGERAN',
                    'SupportedBandGERAN',
                    'IRAT-ParametersCDMA2000-HRPD',
                    'SupportedBandListHRPD',
                    'IRAT-ParametersCDMA2000-1XRTT',
                    'SupportedBandList1XRTT',
                    'UE-TimersAndConstants'
                ],
                'EUTRA-UE-Variables': [
                    'VarMeasConfig',
                    'VarMeasReportList',
                    'VarMeasReport',
                    'CellsTriggeredList',
                    'VarShortMAC-Input'
                ]
            })

        # Encode various messages.
        encoded = rrc.encode('PCCH-Message',
                             {
                                 'message': {
                                     'c1' : {
                                         'paging': {
                                             'systemInfoModification': 'true',
                                             'nonCriticalExtension': {
                                             }
                                         }
                                     }
                                 }
                             })
        self.assertEqual(encoded,
                         b'0\x0b\xa0\t\xa0\x07\xa0\x05\x81\x01\x00\xa3\x00')

        encoded = rrc.encode('PCCH-Message',
                             {
                                 'message': {
                                     'c1' : {
                                         'paging': {
                                         }
                                     }
                                 }
                             })
        self.assertEqual(encoded,
                         b'0\x06\xa0\x04\xa0\x02\xa0\x00')

        encoded = rrc.encode('BCCH-BCH-Message',
                             {
                                 'message': {
                                     'dl-Bandwidth': 'n6',
                                     'phich-Config': {
                                         'phich-Duration': 'normal',
                                         'phich-Resource': 'half'
                                     },
                                     'systemFrameNumber': b'\x12',
                                     'spare': b'\x34\x56'
                                 }
                             })
        self.assertEqual(encoded,
                         b'0\x16\xa0\x14\x80\x01\x00\xa1' \
                         b'\x06\x80\x01\x00\x81\x01\x01\x82' \
                         b'\x02\x00\x12\x83\x03\x064V')


# This file is not '__main__' when executed via 'python setup.py
# test'.
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    unittest.main()
