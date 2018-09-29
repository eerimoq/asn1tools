import os
import pickle
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

    def test_command_line_convert_ber_foo_question(self):
        argv = [
            'asn1tools',
            'convert',
            'tests/files/foo.asn',
            'Question',
            '300e0201011609497320312b313d333f'
        ]

        expected_output = (
            'question Question ::= {\n'
            '    id 1,\n'
            '    question "Is 1+1=3?"\n'
            '}\n'
        )

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        print(stdout.getvalue())

        self.assertEqual(expected_output, stdout.getvalue())

    def test_command_line_convert_uper_foo_question(self):
        argv = [
            'asn1tools',
            'convert',
            '--input-codec', 'uper',
            'tests/files/foo.asn',
            'Question',
            '01010993cd03156c5eb37e'
        ]

        expected_output = (
            'question Question ::= {\n'
            '    id 1,\n'
            '    question "Is 1+1=3?"\n'
            '}\n'
        )

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        print(stdout.getvalue())

        self.assertEqual(expected_output, stdout.getvalue())

    def test_command_line_convert_ber_foo_question_stdin(self):
        argv = [
            'asn1tools',
            'convert',
            'tests/files/foo.asn',
            'Question',
            '-'
        ]
        input_data = '''\
2018-02-24 11:22:09
300e0201011609497320312b313d333f
2018-02-24 11:24:15
300e0201011609497320312b313d333f

2018-02-24 11:24:16
ff0e0201011609497320312b313d333f
2018-02-24 13:24:16
300e0201011609497320312b313d333'''

        expected_output = (
            "2018-02-24 11:22:09\n"
            "question Question ::= {\n"
            "    id 1,\n"
            '    question "Is 1+1=3?"\n'
            "}\n"
            "2018-02-24 11:24:15\n"
            "question Question ::= {\n"
            "    id 1,\n"
            '    question "Is 1+1=3?"\n'
            "}\n"
            "\n"
            "2018-02-24 11:24:16\n"
            "ff0e0201011609497320312b313d333f\n"
            "Expected SEQUENCE with tag '30' at offset 0, but got 'ff'.\n"
            "2018-02-24 13:24:16\n"
            "300e0201011609497320312b313d333\n"
        )

        stdout = StringIO()

        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', stdout):
                with patch('sys.argv', argv):
                    asn1tools._main()

        print(stdout.getvalue())

        self.assertEqual(expected_output, stdout.getvalue())

    def test_command_line_convert_rfc1155_1157(self):
        argv = [
            'asn1tools',
            'convert',
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

        expected_output = (
            "message Message ::= {\n"
            "    version 0,\n"
            "    community '7075626C6963'H,\n"
            "    data set-request : {\n"
            "        request-id 60,\n"
            "        error-status 0,\n"
            "        error-index 0,\n"
            "        variable-bindings {\n"
            "            {\n"
            "                name 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130101,\n"
            "                value simple : string : '3137322E33312E31392E3733'H\n"
            "            },\n"
            "            {\n"
            "                name 1.3.6.1.4.1.253.8.51.10.2.1.5.10.14130400,\n"
            "                value simple : number : 2\n"
            "            },\n"
            "            {\n"
            "                name 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130102,\n"
            "                value simple : string : '3235352E3235352E3235352E30'H\n"
            "            },\n"
            "            {\n"
            "                name 1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130104,\n"
            "                value simple : string : '3137322E33312E31392E32'H\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
        )

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        print(stdout.getvalue())

        self.assertEqual(expected_output, stdout.getvalue())

    def test_command_line_convert_rrc_8_6_0_bcch_dl_sch_message(self):
        argv = [
            'asn1tools',
            'convert',
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

        expected_output = (
            "bcch-dl-sch-message BCCH-DL-SCH-Message ::= {\n"
            "    message c1 : systemInformation : {\n"
            "        criticalExtensions systemInformation-r8 : {\n"
            "            sib-TypeAndInfo {\n"
            "                sib2 : {\n"
            "                    ac-BarringInfo {\n"
            "                        ac-BarringForEmergency TRUE,\n"
            "                        ac-BarringForMO-Data {\n"
            "                            ac-BarringFactor p95,\n"
            "                            ac-BarringTime s128,\n"
            "                            ac-BarringForSpecialAC '11110'B\n"
            "                        }\n"
            "                    },\n"
            "                    radioResourceConfigCommon {\n"
            "                        rach-ConfigCommon {\n"
            "                            preambleInfo {\n"
            "                                numberOfRA-Preambles n24,\n"
            "                                preamblesGroupAConfig {\n"
            "                                    sizeOfRA-PreamblesGroupA n28,\n"
            "                                    messageSizeGroupA b144,\n"
            "                                    messagePowerOffsetGroupB minusinfinity\n"
            "                                }\n"
            "                            },\n"
            "                            powerRampingParameters {\n"
            "                                powerRampingStep dB0,\n"
            "                                preambleInitialReceivedTargetPower dBm-102\n"
            "                            },\n"
            "                            ra-SupervisionInfo {\n"
            "                                preambleTransMax n8,\n"
            "                                ra-ResponseWindowSize sf6,\n"
            "                                mac-ContentionResolutionTimer sf48\n"
            "                            },\n"
            "                            maxHARQ-Msg3Tx 8\n"
            "                        },\n"
            "                        bcch-Config {\n"
            "                            modificationPeriodCoeff n2\n"
            "                        },\n"
            "                        pcch-Config {\n"
            "                            defaultPagingCycle rf256,\n"
            "                            nB twoT\n"
            "                        },\n"
            "                        prach-Config {\n"
            "                            rootSequenceIndex 836,\n"
            "                            prach-ConfigInfo {\n"
            "                                prach-ConfigIndex 33,\n"
            "                                highSpeedFlag FALSE,\n"
            "                                zeroCorrelationZoneConfig 10,\n"
            "                                prach-FreqOffset 64\n"
            "                            }\n"
            "                        },\n"
            "                        pdsch-ConfigCommon {\n"
            "                            referenceSignalPower -60,\n"
            "                            p-b 2\n"
            "                        },\n"
            "                        pusch-ConfigCommon {\n"
            "                            pusch-ConfigBasic {\n"
            "                                n-SB 1,\n"
            "                                hoppingMode interSubFrame,\n"
            "                                pusch-HoppingOffset 10,\n"
            "                                enable64QAM FALSE\n"
            "                            },\n"
            "                            ul-ReferenceSignalsPUSCH {\n"
            "                                groupHoppingEnabled TRUE,\n"
            "                                groupAssignmentPUSCH 22,\n"
            "                                sequenceHoppingEnabled FALSE,\n"
            "                                cyclicShift 5\n"
            "                            }\n"
            "                        },\n"
            "                        pucch-ConfigCommon {\n"
            "                            deltaPUCCH-Shift ds1,\n"
            "                            nRB-CQI 98,\n"
            "                            nCS-AN 4,\n"
            "                            n1PUCCH-AN 2047\n"
            "                        },\n"
            "                        soundingRS-UL-ConfigCommon setup : {\n"
            "                            srs-BandwidthConfig bw0,\n"
            "                            srs-SubframeConfig sc4,\n"
            "                            ackNackSRS-SimultaneousTransmission TRUE\n"
            "                        },\n"
            "                        uplinkPowerControlCommon {\n"
            "                            p0-NominalPUSCH -126,\n"
            "                            alpha al0,\n"
            "                            p0-NominalPUCCH -127,\n"
            "                            deltaFList-PUCCH {\n"
            "                                deltaF-PUCCH-Format1 deltaF-2,\n"
            "                                deltaF-PUCCH-Format1b deltaF1,\n"
            "                                deltaF-PUCCH-Format2 deltaF0,\n"
            "                                deltaF-PUCCH-Format2a deltaF-2,\n"
            "                                deltaF-PUCCH-Format2b deltaF0\n"
            "                            },\n"
            "                            deltaPreambleMsg3 -1\n"
            "                        },\n"
            "                        ul-CyclicPrefixLength len1\n"
            "                    },\n"
            "                    ue-TimersAndConstants {\n"
            "                        t300 ms100,\n"
            "                        t301 ms200,\n"
            "                        t310 ms50,\n"
            "                        n310 n2,\n"
            "                        t311 ms30000,\n"
            "                        n311 n2\n"
            "                    },\n"
            "                    freqInfo {\n"
            "                        additionalSpectrumEmission 3\n"
            "                    },\n"
            "                    timeAlignmentTimerCommon sf500\n"
            "                },\n"
            "                sib3 : {\n"
            "                    cellReselectionInfoCommon {\n"
            "                        q-Hyst dB0,\n"
            "                        speedStateReselectionPars {\n"
            "                            mobilityStateParameters {\n"
            "                                t-Evaluation s180,\n"
            "                                t-HystNormal s180,\n"
            "                                n-CellChangeMedium 1,\n"
            "                                n-CellChangeHigh 16\n"
            "                            },\n"
            "                            q-HystSF {\n"
            "                                sf-Medium dB-6,\n"
            "                                sf-High dB-4\n"
            "                            }\n"
            "                        }\n"
            "                    },\n"
            "                    cellReselectionServingFreqInfo {\n"
            "                        threshServingLow 7,\n"
            "                        cellReselectionPriority 3\n"
            "                    },\n"
            "                    intraFreqCellReselectionInfo {\n"
            "                        q-RxLevMin -33,\n"
            "                        s-IntraSearch 0,\n"
            "                        presenceAntennaPort1 FALSE,\n"
            "                        neighCellConfig '10'B,\n"
            "                        t-ReselectionEUTRA 4\n"
            "                    }\n"
            "                },\n"
            "                sib4 : {\n"
            "                },\n"
            "                sib5 : {\n"
            "                    interFreqCarrierFreqList {\n"
            "                        {\n"
            "                            dl-CarrierFreq 1,\n"
            "                            q-RxLevMin -45,\n"
            "                            t-ReselectionEUTRA 0,\n"
            "                            threshX-High 31,\n"
            "                            threshX-Low 29,\n"
            "                            allowedMeasBandwidth mbw6,\n"
            "                            presenceAntennaPort1 TRUE,\n"
            "                            neighCellConfig '00'B,\n"
            "                            q-OffsetFreq dB0\n"
            "                        }\n"
            "                    }\n"
            "                },\n"
            "                sib6 : {\n"
            "                    t-ReselectionUTRA 3\n"
            "                },\n"
            "                sib7 : {\n"
            "                    t-ReselectionGERAN 3\n"
            "                },\n"
            "                sib8 : {\n"
            "                    parameters1XRTT {\n"
            "                        longCodeState1XRTT '000000010010001101000101011001111000100100'B\n"
            "                    }\n"
            "                },\n"
            "                sib9 : {\n"
            "                    hnb-Name '34'H\n"
            "                },\n"
            "                sib10 : {\n"
            "                    messageIdentifier '0010001100110100'B,\n"
            "                    serialNumber '0001001000110100'B,\n"
            "                    warningType '3212'H\n"
            "                },\n"
            "                sib11 : {\n"
            "                    messageIdentifier '0110011110001000'B,\n"
            "                    serialNumber '0101010000110101'B,\n"
            "                    warningMessageSegmentType notLastSegment,\n"
            "                    warningMessageSegmentNumber 19,\n"
            "                    warningMessageSegment '12'H\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
        )

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        print(stdout.getvalue())

        for line in expected_output:
            self.assertIn(line, stdout.getvalue())

    def test_command_line_convert_bad_type_name(self):
        argv = [
            'asn1tools',
            'convert',
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
                    "error: Type 'Question2' not found in types dictionary.")

    def test_command_line_convert_bad_data(self):
        argv = [
            'asn1tools',
            'convert',
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

    def test_command_line_convert_py(self):
        # Preparations.
        argv = [
            'asn1tools',
            'parse',
            'tests/files/foo.asn',
            'test_command_line_convert_py.py'
        ]

        if os.path.exists('test_command_line_convert_py.py'):
            os.remove('test_command_line_convert_py.py')

        with patch('sys.argv', argv):
            asn1tools._main()

        # Test convert.
        argv = [
            'asn1tools',
            'convert',
            'test_command_line_convert_py.py',
            'Question',
            '300e0201011609497320312b313d333f'
        ]

        expected_output = (
            'question Question ::= {\n'
            '    id 1,\n'
            '    question "Is 1+1=3?"\n'
            '}\n'
        )

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                asn1tools._main()

        print(stdout.getvalue())

        self.assertEqual(expected_output, stdout.getvalue())

    def test_command_line_convert_py_too_many_files(self):
        argv = [
            'asn1tools',
            'convert',
            'spec.py',
            'too-many.py',
            'Question',
            '300e0201011609497320312b313d333f'
        ]

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', argv):
                with self.assertRaises(SystemExit) as cm:
                    asn1tools._main()

                self.assertEqual(
                    str(cm.exception),
                    "error: Expected one .py-file, but got 2.")

    def test_command_line_shell(self):
        argv = ['asn1tools', 'shell']
        commands = StringIO('''\
help
compile tests/files/foo.asn
convert Question 300e0201011609497320312b313d333f
convert Foo 30
compile -i uper tests/files/foo.asn
convert Question 01010993cd03156c5eb37e
compile -i ber /x/y/missing
missing-command
exit
''')

        class PromptSession(object):

            def __init__(self, *_args, **_kwargs):
                pass

            def prompt(*_args, **_kwargs):
                return commands.readline()

        expected_output = (
            '\n'
            'Welcome to the asn1tools shell!\n'
            '\n'
            "Commands:\n"
            "  compile\n"
            "  convert\n"
            "  exit\n"
            "  help\n"
            'question Question ::= {\n'
            '    id 1,\n'
            '    question "Is 1+1=3?"\n'
            '}\n'
            'error: Type \'Foo\' not found in types dictionary.\n'
            'question Question ::= {\n'
            '    id 1,\n'
            '    question "Is 1+1=3?"\n'
            '}\n'
            'error: [Errno 2] No such file or directory: \'/x/y/missing\'\n'
            'missing-command: command not found\n'
        )

        stdout = StringIO()

        with patch('asn1tools.PromptSession', PromptSession):
            with patch('sys.stdout', stdout):
                with patch('sys.argv', argv):
                    asn1tools._main()

        print(stdout.getvalue())

        self.assertEqual(expected_output, stdout.getvalue())

    def test_command_line_shell_compile_without_arguments(self):
        argv = ['asn1tools', 'shell']
        commands = StringIO('''\
compile
exit
''')

        class PromptSession(object):

            def __init__(self, *_args, **_kwargs):
                pass

            def prompt(*_args, **_kwargs):
                return commands.readline()

        stdout = StringIO()

        with patch('asn1tools.PromptSession', PromptSession):
            with patch('sys.stdout', stdout):
                with patch('sys.argv', argv):
                    asn1tools._main()

        self.assertIn('compile: error: ', stdout.getvalue())

    def test_command_line_shell_convert_without_compile(self):
        argv = ['asn1tools', 'shell']
        commands = StringIO('''\
convert A 00
exit
''')

        expected_output = (
            '\n'
            'Welcome to the asn1tools shell!\n'
            '\n'
            "No compiled specification found. Please use the 'compile' command "
            "to compile one.\n"
        )

        class PromptSession(object):

            def __init__(self, *_args, **_kwargs):
                pass

            def prompt(*_args, **_kwargs):
                return commands.readline()

        stdout = StringIO()

        with patch('asn1tools.PromptSession', PromptSession):
            with patch('sys.stdout', stdout):
                with patch('sys.argv', argv):
                    asn1tools._main()

        self.assertEqual(expected_output, stdout.getvalue())

    def test_command_line_shell_compile_help_no_exit(self):
        argv = ['asn1tools', 'shell']
        commands = StringIO('''\
compile --help
exit
''')

        class PromptSession(object):

            def __init__(self, *_args, **_kwargs):
                pass

            def prompt(*_args, **_kwargs):
                return commands.readline()

        stdout = StringIO()

        with patch('asn1tools.PromptSession', PromptSession):
            with patch('sys.stdout', stdout):
                with patch('sys.argv', argv):
                    asn1tools._main()

        self.assertIn('usage:', stdout.getvalue())

    def test_command_line_parse(self):
        argv = [
            'asn1tools',
            'parse',
            'tests/files/foo.asn',
            'test_command_line_parse.py'
        ]

        expected_specification = {
            'Foo': {'extensibility-implied': False,
                    'imports': {},
                    'object-classes': {},
                    'object-sets': {},
                    'types': {'Answer': {'members': [{'name': 'id',
                                                      'type': 'INTEGER'},
                                                     {'name': 'answer',
                                                      'type': 'BOOLEAN'}],
                                         'type': 'SEQUENCE'},
                              'Question': {'members': [{'name': 'id',
                                                        'type': 'INTEGER'},
                                                       {'name': 'question',
                                                        'type': 'IA5String'}],
                                           'type': 'SEQUENCE'}},
                    'values': {}}}

        if os.path.exists('test_command_line_parse.py'):
            os.remove('test_command_line_parse.py')

        with patch('sys.argv', argv):
            asn1tools._main()

        from test_command_line_parse import SPECIFICATION

        self.assertEqual(SPECIFICATION, expected_specification)


if __name__ == '__main__':
    unittest.main()
