import sys
import logging
import unittest

import asn1tools

sys.path.append('tests/files')

from foo import FOO
from rrc_8_6_0 import RRC_8_6_0


class Asn1ToolsTest(unittest.TestCase):

    maxDiff = None

    def test_parse_foo(self):
        foo = asn1tools.parser.parse_file('tests/files/foo.asn')
        self.assertEqual(foo, FOO)

    def test_parse_rrc_8_6_0(self):
        foo = asn1tools.parser.parse_file('tests/files/rrc_8.6.0.asn')
        self.assertEqual(foo, RRC_8_6_0)

    def test_compile_file(self):
        foo = asn1tools.compile_file('tests/files/foo.asn')
        self.assertEqual(len(foo.types), 2)
        self.assertTrue(foo.types['Question'] is not None)
        self.assertTrue(foo.types['Answer'] is not None)
        self.assertEqual(len(foo.modules), 1)
        self.assertTrue(foo.modules['Foo'] is not None)

        # Encode a question.
        encoded = foo.encode('Question',
                             {'id': 1, 'question': 'Is 1+1=3?'})
        self.assertEqual(encoded, b'0\x0e\x02\x01\x01\x16\x09Is 1+1=3?')

        # Decode the encoded question.
        decoded = foo.decode('Question', encoded)
        self.assertEqual(decoded, {'id': 1, 'question': 'Is 1+1=3?'})

        # Encode an answer.
        encoded = foo.encode('Answer', {'id': 1, 'answer': False})
        self.assertEqual(encoded, b'0\x06\x02\x01\x01\x01\x01\x00')

        # Decode the encoded answer.
        decoded = foo.decode('Answer', encoded)
        self.assertEqual(decoded, {'id': 1, 'answer': False})

    def test_complex(self):
        cmplx = asn1tools.compile_file('tests/files/complex.asn')

        decoded_message = {
            'boolean': True,
            'integer': -7,
            'bit-string': (b'\x80', 3),
            'octet-string': b'\x31\x32',
            'null': None,
            'object-identifier': '1.3.2',
            'enumerated': 'one',
            'sequence': {},
            'ia5-string': 'foo'
        }

        encoded_message = (b'\x30\x1e\x01\x01\x01\x02\x01\xf9'
                           b'\x03\x02\x05\x80\x04\x02\x31\x32'
                           b'\x05\x00\x06\x02\x2b\x02\x0a\x01'
                           b'\x01\x30\x00\x16\x03\x66\x6f\x6f')

        encoded = cmplx.encode('AllUniversalTypes', decoded_message)
        self.assertEqual(encoded, encoded_message)

        decoded = cmplx.decode('AllUniversalTypes', encoded_message)
        self.assertEqual(decoded, decoded_message)

    def _test_rrc_8_6_0(self):
        rrc = asn1tools.compile_file('tests/files/rrc_8.6.0.asn')

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
                         (b'0\x16\xa0\x14\x80\x01\x00\xa1'
                          b'\x06\x80\x01\x00\x81\x01\x01\x82'
                          b'\x02\x00\x12\x83\x03\x064V'))

    def test_snmp_v1(self):
        snmp_v1 = asn1tools.compile_file('tests/files/snmp_v1.asn')

        # First message.
        decoded_message = {
            "version": 0,
            "community": b'public',
            "data": {
                "set-request": {
                    "request-id": 60,
                    "error-status": 0,
                    "error-index": 0,
                    "variable-bindings": [
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130101",
                            "value": {
                                "simple": {
                                    "string": (b'\x31\x37\x32\x2e\x33\x31'
                                               b'\x2e\x31\x39\x2e\x37\x33')
                                }
                            }
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.5.10.14130400",
                            "value": {
                                "simple": {
                                    "number": 2
                                }
                            }
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130102",
                            "value": {
                                "simple": {
                                    "string": (b'\x32\x35\x35\x2e\x32\x35'
                                               b'\x35\x2e\x32\x35\x35\x2e'
                                               b'\x30')
                                }
                            }
                        },
                        {
                            "name": "1.3.6.1.4.1.253.8.51.10.2.1.7.10.14130104",
                            "value": {
                                "simple": {
                                    "string": (b'\x31\x37\x32\x2e\x33\x31'
                                               b'\x2e\x31\x39\x2e\x32')
                                }
                            }
                        }
                    ]
                }
            }
        }

        encoded_message = (
            b'0\x81\x9f\x02\x01\x00\x04\x06public\xa3\x81\x91\x02'
            b'\x01<\x02\x01\x00\x02\x01\x000\x81\x850"\x06\x12+\x06'
            b'\x01\x04\x01\x81}\x083\n\x02\x01\x07\n\x86\xde\xb75'
            b'\x04\x0c172.31.19.730\x17\x06\x12+\x06\x01\x04\x01\x81'
            b'}\x083\n\x02\x01\x05\n\x86\xde\xb9`\x02\x01\x020#\x06'
            b'\x12+\x06\x01\x04\x01\x81}\x083\n\x02\x01\x07\n\x86\xde'
            b'\xb76\x04\r255.255.255.00!\x06\x12+\x06\x01\x04\x01\x81'
            b'}\x083\n\x02\x01\x07\n\x86\xde\xb78\x04\x0b172.31.19.2'
        )

        encoded = snmp_v1.encode('Message', decoded_message)
        self.assertEqual(encoded, encoded_message)

        decoded = snmp_v1.decode('Message', encoded_message)
        self.assertEqual(decoded, decoded_message)

        # Next message.
        decoded_message = {
            'version': 1,
            'community': b'community',
            'data': {
                'set-request': {
                    'request-id': 1687059484,
                    'error-status': 0,
                    'error-index': 0,
                    'variable-bindings': [
                        {
                            'name': '1.3.6.1.999.1.1',
                            'value': {
                                'simple': {
                                    'number': 1
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.2.1',
                            'value': {
                                'simple': {
                                    'string': b'f00'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'address': {
                                        'internet': b'\xc0\xa8\x01\x01'
                                    }
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': {
                                'simple': {
                                    'object': '1.2.3.444.555'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.1.2',
                            'value': {
                                'simple': {
                                    'number': 1
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.2.2',
                            'value': {
                                'simple': {
                                'string': b'f00'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.2',
                            'value': {
                                'application-wide': {
                                    'address': {
                                        'internet': b'\xc0\xa8\x01\x01'
                                    }
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.2',
                            'value': {
                                'simple': {
                                    'object': '1.2.3.444.555'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.1.3',
                            'value': {
                                'simple': {
                                    'number': 1
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.2.3',
                            'value': {
                                'simple': {
                                    'string': b'f00'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.3',
                            'value': {
                                'application-wide': {
                                    'address': {
                                        'internet': b'\xc0\xa8\x01\x01'
                                    }
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.3',
                            'value': {
                                'simple': {
                                    'object': '1.2.3.444.555'
                                }
                            }
                        }
                    ]
                }
            }
        }

        encoded_message = (b'\x30\x81\xe6\x02\x01\x01\x04\x09'
                           b'\x63\x6f\x6d\x6d\x75\x6e\x69\x74'
                           b'\x79\xa3\x81\xd5\x02\x04\x64\x8e'
                           b'\x7c\x1c\x02\x01\x00\x02\x01\x00'
                           b'\x30\x81\xc6\x30\x0c\x06\x07\x2b'
                           b'\x06\x01\x87\x67\x01\x01\x02\x01'
                           b'\x01\x30\x0e\x06\x07\x2b\x06\x01'
                           b'\x87\x67\x02\x01\x04\x03\x66\x30'
                           b'\x30\x30\x0f\x06\x07\x2b\x06\x01'
                           b'\x87\x67\x03\x01\x40\x04\xc0\xa8'
                           b'\x01\x01\x30\x11\x06\x07\x2b\x06'
                           b'\x01\x87\x67\x04\x01\x06\x06\x2a'
                           b'\x03\x83\x3c\x84\x2b\x30\x0c\x06'
                           b'\x07\x2b\x06\x01\x87\x67\x01\x02'
                           b'\x02\x01\x01\x30\x0e\x06\x07\x2b'
                           b'\x06\x01\x87\x67\x02\x02\x04\x03'
                           b'\x66\x30\x30\x30\x0f\x06\x07\x2b'
                           b'\x06\x01\x87\x67\x03\x02\x40\x04'
                           b'\xc0\xa8\x01\x01\x30\x11\x06\x07'
                           b'\x2b\x06\x01\x87\x67\x04\x02\x06'
                           b'\x06\x2a\x03\x83\x3c\x84\x2b\x30'
                           b'\x0c\x06\x07\x2b\x06\x01\x87\x67'
                           b'\x01\x03\x02\x01\x01\x30\x0e\x06'
                           b'\x07\x2b\x06\x01\x87\x67\x02\x03'
                           b'\x04\x03\x66\x30\x30\x30\x0f\x06'
                           b'\x07\x2b\x06\x01\x87\x67\x03\x03'
                           b'\x40\x04\xc0\xa8\x01\x01\x30\x11'
                           b'\x06\x07\x2b\x06\x01\x87\x67\x04'
                           b'\x03\x06\x06\x2a\x03\x83\x3c\x84'
                           b'\x2b')

        encoded = snmp_v1.encode('Message', decoded_message)
        self.assertEqual(encoded, encoded_message)

        decoded = snmp_v1.decode('Message', encoded_message)
        self.assertEqual(decoded, decoded_message)

        # Next message.
        decoded_message = {
            'version': 1,
            'community': b'community',
            'data': {
                'set-request': {
                    'request-id': 1687059484,
                    'error-status': 0,
                    'error-index': 0,
                    'variable-bindings': [
                        {
                            'name': '1.3.6.1.999.1.1',
                            'value': {
                                'simple': {
                                    'number': -1
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.2.1',
                            'value': {
                                'simple': {
                                    'string': b'f00'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': {
                                'simple': {
                                    'object': '1.2.3.444.555'
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.4.1',
                            'value': {
                                'simple': {
                                    'empty': None
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'address': {
                                        'internet': b'\xc0\xa8\x01\x01'
                                    }
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'counter': 0
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'gauge': 4294967295
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'ticks': 88
                                }
                            }
                        },
                        {
                            'name': '1.3.6.1.999.3.1',
                            'value': {
                                'application-wide': {
                                    'arbitrary': b'\x31\x32\x33'
                                }
                            }
                        }
                    ]
                }
            }
        }

        encoded_message = (b'\x30\x81\xad\x02\x01\x01\x04\x09'
                           b'\x63\x6f\x6d\x6d\x75\x6e\x69\x74'
                           b'\x79\xa3\x81\x9c\x02\x04\x64\x8e'
                           b'\x7c\x1c\x02\x01\x00\x02\x01\x00'
                           b'\x30\x81\x8d\x30\x0c\x06\x07\x2b'
                           b'\x06\x01\x87\x67\x01\x01\x02\x01'
                           b'\xff\x30\x0e\x06\x07\x2b\x06\x01'
                           b'\x87\x67\x02\x01\x04\x03\x66\x30'
                           b'\x30\x30\x11\x06\x07\x2b\x06\x01'
                           b'\x87\x67\x04\x01\x06\x06\x2a\x03'
                           b'\x83\x3c\x84\x2b\x30\x0b\x06\x07'
                           b'\x2b\x06\x01\x87\x67\x04\x01\x05'
                           b'\x00\x30\x0f\x06\x07\x2b\x06\x01'
                           b'\x87\x67\x03\x01\x40\x04\xc0\xa8'
                           b'\x01\x01\x30\x0c\x06\x07\x2b\x06'
                           b'\x01\x87\x67\x03\x01\x41\x01\x00'
                           b'\x30\x10\x06\x07\x2b\x06\x01\x87'
                           b'\x67\x03\x01\x42\x05\x00\xff\xff'
                           b'\xff\xff\x30\x0c\x06\x07\x2b\x06'
                           b'\x01\x87\x67\x03\x01\x43\x01\x58'
                           b'\x30\x0e\x06\x07\x2b\x06\x01\x87'
                           b'\x67\x03\x01\x44\x03\x31\x32\x33')

        encoded = snmp_v1.encode('Message', decoded_message)
        self.assertEqual(encoded, encoded_message)

        decoded = snmp_v1.decode('Message', encoded_message)
        self.assertEqual(decoded, decoded_message)


# This file is not '__main__' when executed via 'python setup.py
# test'.
logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    unittest.main()
