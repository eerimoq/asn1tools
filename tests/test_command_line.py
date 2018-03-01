import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import asn1tools


class Asn1ToolsCommandLineTest(unittest.TestCase):

    maxDiff = None

    def test_command_line_help(self):
        argv = ['asn1tools', '--help']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit):
                    asn1tools._main()

        expected_output = [
            "usage: asn1tools [-h] [-d] [-v {0,1,2}] [--version] {decode} ...",
            "",
            "Various ASN.1 utilities.",
            "",
            "optional arguments:",
            "  -h, --help            show this help message and exit",
            "  -d, --debug",
            "  -v {0,1,2}, --verbose {0,1,2}",
            "                        Control the verbosity; ",
            "disable(0),",
            "warning(1)",
            "and",
            "debug(2).",
            "(default: 1).",
            "  --version             Print version information and exit.",
            "",
            "subcommands:",
            "  {decode}"
        ]

        print(stdout.getvalue())

        for line in expected_output:
            self.assertIn(line, stdout.getvalue())

    def test_command_line_decode_help(self):
        argv = ['asn1tools', 'decode', '--help']

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit):
                    asn1tools._main()

        expected_output = [
            "asn1tools decode [-h] [-c {ber,der,jer,per,uper,xer}]",
            "                        specification [specification ...] type hexstring",
            "",
            "Decode given hextring and print it to standard output.",
            "",
            "positional arguments:",
            "  specification         ASN.1 specification as one or more .asn files.",
            "  type                  Type to decode.",
            "  hexstring             Hexstring to decode, or - to ",
            "",
            "optional arguments:",
            "  -h, --help            show this help message and exit",
            "  -c {ber,der,jer,per,uper,xer}, --codec {ber,der,jer,per,uper,xer}",
            "                        Codec (default: ber)."
        ]

        print(stdout.getvalue())

        for line in expected_output:
            self.assertIn(line, stdout.getvalue())

    def test_command_line_decode_ber_foo_question(self):
        argv = [
            'asn1tools',
            'decode',
            'tests/files/foo.asn',
            'Question',
            '300e0201011609497320312b313d333f'
        ]

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        print(stdout.getvalue())

        self.assertIn('id: 1', stdout.getvalue())
        self.assertIn('question: Is 1+1=3?', stdout.getvalue())

    def test_command_line_decode_uper_foo_question(self):
        argv = [
            'asn1tools',
            'decode',
            '--codec', 'uper',
            'tests/files/foo.asn',
            'Question',
            '01010993cd03156c5eb37e'
        ]

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        print(stdout.getvalue())

        self.assertIn('id: 1', stdout.getvalue())
        self.assertIn('question: Is 1+1=3?', stdout.getvalue())

    def test_command_line_decode_ber_foo_question_stdin(self):
        argv = [
            'asn1tools',
            'decode',
            'tests/files/foo.asn',
            'Question',
            '-'
        ]
        input_data = '''
2018-02-24 11:22:09
300e0201011609497320312b313d333f
2018-02-24 11:24:15
300e0201011609497320312b313d333f

2018-02-24 11:24:16
ff0e0201011609497320312b313d333f
2018-02-24 13:24:16
300e0201011609497320312b313d333'''

        stdout = StringIO()

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', stdout):
                with patch('sys.argv', argv):
                    asn1tools._main()

        print(stdout.getvalue())

        self.assertEqual(stdout.getvalue().count('id: 1'), 2)
        self.assertEqual(stdout.getvalue().count('question: Is 1+1=3?'), 2)
        expected_output = [
            '2018-02-24 11:22:09',
            '2018-02-24 11:24:15',
            '2018-02-24 11:24:16',
            'ff0e0201011609497320312b313d333f',
            ": expected SEQUENCE with tag '30' at offset 0, but got 'ff'",
            '2018-02-24 13:24:16',
            "300e0201011609497320312b313d333"
        ]

        for line in expected_output:
            self.assertIn(line, stdout.getvalue())

    def test_command_line_decode_rfc1155_1157(self):
        argv = [
            'asn1tools',
            'decode',
            'tests/files/ietf/rfc1155.asn',
            'tests/files/ietf/rfc1157.asn',
            'Message',
            '30819f02010004067075626c6963a3819102013c020100020100308185302206'
            '122b06010401817d08330a0201070a86deb735040c3137322e33312e31392e37'
            '33301706122b06010401817d08330a0201050a86deb960020102302306122b06'
            '010401817d08330a0201070a86deb736040d3235352e3235352e3235352e3030'
            '2106122b06010401817d08330a0201070a86deb738040b3137322e33312e3139'
            '2e32'
        ]

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        expected_output = [
            "version: 0",
            "community: '7075626c6963'",
            "data:",
            "  set-request:",
            "    variable-bindings:",
            "      [0]:",
            "        name: 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130101",
            "        value:",
            "          simple:",
            "            string: '3137322e33312e31392e3733'",
            "      [1]:",
            "        name: 1.3.6.1.4.1.253.8.51.10.2.1.5.10.14130400",
            "        value:",
            "          simple:",
            "            number: 2",
            "      [2]:",
            "        name: 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130102",
            "        value:",
            "          simple:",
            "            string: '3235352e3235352e3235352e30'",
            "      [3]:",
            "        name: 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130104",
            "        value:",
            "          simple:",
            "            string: '3137322e33312e31392e32'",
            "    error-index: 0",
            "    error-status: 0",
            "    request-id: 60"
        ]

        print(stdout.getvalue())

        for line in expected_output:
            self.assertIn(line, stdout.getvalue())

    def test_command_line_decode_rrc_8_6_0_bcch_dl_sch_message(self):
        argv = [
            'asn1tools',
            'decode',
            'tests/files/3gpp/rrc_8_6_0.asn',
            'BCCH-DL-SCH-Message',
            '30820193a082018fa082018ba0820187a0820183a082017fa082017ba081'
            'dda00f8001ffa20a80010f810105820203f0a181ada026a00e800105a109'
            '800106810101820100a106800100810109a2098001058101048201058301'
            '08a103800100a206800103810101a31280020344a10c8001218101008201'
            '0a830140a4068001c4810102a51ca00c80010181010082010a830100a10c'
            '8001ff810116820100830105a60d800100810162820104830207ffa70ba1'
            '098001008101048201ffa81d800182810100820181a30f80010081010082'
            '01018301008401018401ff890100a2128001008101018201018301018401'
            '06850101a303820103850100a137a01b800100a116a00c80010381010382'
            '0101830110a106800100810101a106810107820103a2108001df82010084'
            '010085020680860104a200a31da01b30198001018101d383010085011f86'
            '011d8701008801ff8a020600a403820103a503800103a60ba30981070601'
            '2345678900a703800134a80e8003002334810300123482023212a9138003'
            '0067888103005435820100830113840112'
        ]

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        expected_output = [
            "message:",
            "  c1:",
            "    systemInformation:",
            "      criticalExtensions:",
            "        systemInformation-r8:",
            "          sib-TypeAndInfo:",
            "            [0]:",
            "              sib2:",
            "                ac-BarringInfo:",
            "                  ac-BarringForEmergency: True",
            "                  ac-BarringForMO-Data:",
            "                    ac-BarringFactor: p95",
            "                    ac-BarringTime: s128",
            "                    ac-BarringForSpecialAC: ('f0', 5)",
            "                radioResourceConfigCommon:",
            "                  rach-ConfigCommon:",
            "                    preambleInfo:",
            "                      numberOfRA-Preambles: n24",
            "                      preamblesGroupAConfig:",
            "                        sizeOfRA-PreamblesGroupA: n28",
            "                        messageSizeGroupA: b144",
            "                        messagePowerOffsetGroupB: minusinfinity",
            "                    powerRampingParameters:",
            "                      powerRampingStep: dB0",
            "                      preambleInitialReceivedTargetPower: dBm-102",
            "                    ra-SupervisionInfo:",
            "                      preambleTransMax: n8",
            "                      ra-ResponseWindowSize: sf6",
            "                      mac-ContentionResolutionTimer: sf48",
            "                    maxHARQ-Msg3Tx: 8",
            "                  bcch-Config:",
            "                    modificationPeriodCoeff: n2",
            "                  pcch-Config:",
            "                    defaultPagingCycle: rf256",
            "                    nB: twoT",
            "                  prach-Config:",
            "                    rootSequenceIndex: 836",
            "                    prach-ConfigInfo:",
            "                      prach-ConfigIndex: 33",
            "                      highSpeedFlag: False",
            "                      zeroCorrelationZoneConfig: 10",
            "                      prach-FreqOffset: 64",
            "                  pdsch-ConfigCommon:",
            "                    referenceSignalPower: -60",
            "                    p-b: 2",
            "                  pusch-ConfigCommon:",
            "                    pusch-ConfigBasic:",
            "                      n-SB: 1",
            "                      hoppingMode: interSubFrame",
            "                      pusch-HoppingOffset: 10",
            "                      enable64QAM: False",
            "                    ul-ReferenceSignalsPUSCH:",
            "                      groupHoppingEnabled: True",
            "                      groupAssignmentPUSCH: 22",
            "                      sequenceHoppingEnabled: False",
            "                      cyclicShift: 5",
            "                  pucch-ConfigCommon:",
            "                    deltaPUCCH-Shift: ds1",
            "                    nRB-CQI: 98",
            "                    nCS-AN: 4",
            "                    n1PUCCH-AN: 2047",
            "                  soundingRS-UL-ConfigCommon:",
            "                    setup:",
            "                      srs-BandwidthConfig: bw0",
            "                      srs-SubframeConfig: sc4",
            "                      ackNackSRS-SimultaneousTransmission: True",
            "                  uplinkPowerControlCommon:",
            "                    p0-NominalPUSCH: -126",
            "                    alpha: al0",
            "                    p0-NominalPUCCH: -127",
            "                    deltaFList-PUCCH:",
            "                      deltaF-PUCCH-Format1: deltaF-2",
            "                      deltaF-PUCCH-Format1b: deltaF1",
            "                      deltaF-PUCCH-Format2: deltaF0",
            "                      deltaF-PUCCH-Format2a: deltaF-2",
            "                      deltaF-PUCCH-Format2b: deltaF0",
            "                    deltaPreambleMsg3: -1",
            "                  ul-CyclicPrefixLength: len1",
            "                ue-TimersAndConstants:",
            "                  t300: ms100",
            "                  t301: ms200",
            "                  t310: ms50",
            "                  n310: n2",
            "                  t311: ms30000",
            "                  n311: n2",
            "                freqInfo:",
            "                  additionalSpectrumEmission: 3",
            "                timeAlignmentTimerCommon: sf500",
            "            [1]:",
            "              sib3:",
            "                cellReselectionInfoCommon:",
            "                  q-Hyst: dB0",
            "                  speedStateReselectionPars:",
            "                    mobilityStateParameters:",
            "                      t-Evaluation: s180",
            "                      t-HystNormal: s180",
            "                      n-CellChangeMedium: 1",
            "                      n-CellChangeHigh: 16",
            "                    q-HystSF:",
            "                      sf-Medium: dB-6",
            "                      sf-High: dB-4",
            "                cellReselectionServingFreqInfo:",
            "                  threshServingLow: 7",
            "                  cellReselectionPriority: 3",
            "                intraFreqCellReselectionInfo:",
            "                  q-RxLevMin: -33",
            "                  s-IntraSearch: 0",
            "                  presenceAntennaPort1: False",
            "                  neighCellConfig: ('80', 2)",
            "                  t-ReselectionEUTRA: 4",
            "            [2]:",
            "              sib4:",
            "            [3]:",
            "              sib5:",
            "                interFreqCarrierFreqList:",
            "                  [0]:",
            "                    dl-CarrierFreq: 1",
            "                    q-RxLevMin: -45",
            "                    t-ReselectionEUTRA: 0",
            "                    threshX-High: 31",
            "                    threshX-Low: 29",
            "                    allowedMeasBandwidth: mbw6",
            "                    presenceAntennaPort1: True",
            "                    neighCellConfig: ('00', 2)",
            "                    q-OffsetFreq: dB0",
            "            [4]:",
            "              sib6:",
            "                t-ReselectionUTRA: 3",
            "            [5]:",
            "              sib7:",
            "                t-ReselectionGERAN: 3",
            "            [6]:",
            "              sib8:",
            "                parameters1XRTT:",
            "                  longCodeState1XRTT: ('012345678900', 42)",
            "            [7]:",
            "              sib9:",
            "                hnb-Name: '34'",
            "            [8]:",
            "              sib10:",
            "                messageIdentifier: ('2334', 16)",
            "                serialNumber: ('1234', 16)",
            "                warningType: '3212'",
            "            [9]:",
            "              sib11:",
            "                messageIdentifier: ('6788', 16)",
            "                serialNumber: ('5435', 16)",
            "                warningMessageSegmentType: notLastSegment",
            "                warningMessageSegmentNumber: 19",
            "                warningMessageSegment: '12'"
        ]

        print(stdout.getvalue())

        for line in expected_output:
            self.assertIn(line, stdout.getvalue())

    def test_command_line_decode_bad_type_name(self):
        argv = [
            'asn1tools',
            'decode',
            'tests/files/foo.asn',
            'Question2',
            '01010993cd03156c5eb37e'
        ]

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit) as cm:
                    asn1tools._main()

                self.assertEqual(
                    str(cm.exception),
                    "error: type 'Question2' not found in types dictionary")

    def test_command_line_decode_bad_data(self):
        argv = [
            'asn1tools',
            'decode',
            'tests/files/foo.asn',
            'Question',
            '012'
        ]

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit) as cm:
                    asn1tools._main()

                self.assertEqual(str(cm.exception),
                                 "error: '012': Odd-length string")


if __name__ == '__main__':
    unittest.main()
