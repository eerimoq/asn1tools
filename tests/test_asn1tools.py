import unittest
import timeit

import asn1tools
from pprint import pprint


class Asn1ToolsTest(unittest.TestCase):

    maxDiff = None

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

        # Encode a question with missing field 'id'.
        with self.assertRaises(asn1tools.EncodeError) as cm:
            encoded = foo.encode('Question', {'question': 'Is 1+1=3?'})

        self.assertEqual(
            str(cm.exception),
            "Sequence member 'id' not found in '{'question': 'Is 1+1=3?'}'.")

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

        # Ivalid enumeration value.
        decoded_message = {
            'boolean': True,
            'integer': -7,
            'bit-string': (b'\x80', 3),
            'octet-string': b'\x31\x32',
            'null': None,
            'object-identifier': '1.3.2',
            'enumerated': 'three',
            'sequence': {},
            'ia5-string': 'foo'
        }

        with self.assertRaises(asn1tools.EncodeError) as cm:
            cmplx.encode('AllUniversalTypes', decoded_message)

        self.assertEqual(
            str(cm.exception),
            "Enumeration value 'three' not found in ['one', 'two'].")

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

        # Next message with missing field 'data' -> 'set-request' ->
        # 'variable-bindings[0]' -> 'value' -> 'simple'.
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
                            }
                        }
                    ]
                }
            }
        }

        with self.assertRaises(asn1tools.EncodeError) as cm:
            snmp_v1.encode('Message', decoded_message)

        self.assertEqual(
            str(cm.exception),
            "Expected choices are ['simple', 'application-wide'], "
            "but got ''.")

    def test_performance(self):
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

        def encode():
            cmplx.encode('AllUniversalTypes', decoded_message)

        def decode():
            cmplx.decode('AllUniversalTypes', encoded_message)

        iterations = 1000

        res = timeit.timeit(encode, number=iterations)
        ms_per_call = 1000 * res / iterations
        print('{} ms per encode call.'.format(round(ms_per_call, 3)))

        res = timeit.timeit(decode, number=iterations)
        ms_per_call = 1000 * res / iterations
        print('{} ms per decode call.'.format(round(ms_per_call, 3)))

    def test_rfc5280(self):
        snmp_v1 = asn1tools.compile_file('tests/files/rfc5280.asn')

        decoded_message = {
            'signature': (b'\x14\xb6L\xbb\x81y3\xe6q\xa4\xdaQo\xcb\x08\x1d'
                          b'\x8d`\xec\xbc\x18\xc7sGY\xb1\xf2 H\xbba\xfa'
                          b'\xfcM\xad\x89\x8d\xd1!\xeb\xd5\xd8\xe5\xba'
                          b'\xd6\xa66\xfdtP\x83\xb6\x0f\xc7\x1d\xdf}\xe5.\x81'
                          b'\x7fE\xe0\x9f\xe2>y\xee\xd701\xc7 r\xd9X.*\xfe\x12'
                          b'Z4E\xa1\x19\x08|\x89G_J\x95\xbe#!JSr\xda*\x05/.\xc9'
                          b'p\xf6[\xfa\xfd\xdf\xb41\xb2\xc1J\x9c\x06%C\xa1'
                          b'\xe6\xb4\x1e\x7f\x86\x9b\x16@',
                          1024),
            'signatureAlgorithm': {
                'algorithm': '1.2.840.113549.1.1.5',
                'parameters': None
            },
            'tbsCertificate': {
                'version': 'v1',
                'serialNumber': 3578,
                'signature': {
                    'algorithm': '1.2.840.113549.1.1.5',
                    'parameters': None
                },
                'issuer': {
                    'rdnSequence': [
                        [{'type': '2.5.4.6', 'value': 'JP'}],
                        [{'type': '2.5.4.8', 'value': 'Tokyo'}],
                        [{'type': '2.5.4.7', 'value': 'Chuo-ku'}],
                        [{'type': '2.5.4.10', 'value': 'Frank4DD'}],
                        [{'type': '2.5.4.11', 'value': 'WebCert Support'}],
                        [{'type': '2.5.4.3', 'value': 'Frank4DD Web CA'}],
                        [{'type': '1.2.840.113549.1.9.1', 'value': 'support@frank4dd.com'}]]},
                'validity': {
                    'notAfter': {'utcTime': '170821052654'},
                    'notBefore': {'utcTime': '120822052654'}
                },
                'subject': {
                    'rdnSequence': [
                        [{'type': '2.5.4.6', 'value': 'JP'}],
                        [{'type': '2.5.4.8', 'value': 'Tokyo'}],
                        [{'type': '2.5.4.10', 'value': 'Frank4DD'}],
                        [{'type': '2.5.4.3', 'value': 'www.example.com'}]]},
                'subjectPublicKeyInfo': {
                    'algorithm': {
                        'algorithm': '1.2.840.113549.1.1.1',
                        'parameters': None},
                    'subjectPublicKey': (b'0H\x02A\x00\x9b\xfcf\x90y\x84B\xbb'
                                         b'\xab\x13\xfd+{\xf8\xde\x15\x12\xe5'
                                         b'\xf1\x93\xe3\x06\x8a{\xb8\xb1\xe1'
                                         b'\x9e&\xbb\x95\x01\xbf\xe70\xedd\x85'
                                         b'\x02\xdd\x15i\xa84\xb0\x06\xec?5<'
                                         b'\x1e\x1b+\x8f\xfa\x8f\x00\x1b\xdf'
                                         b'\x07\xc6\xacS\x07\x02\x03\x01\x00'
                                         b'\x01',
                                         592)
                }
            }
        }

        encoded_message = (
            b'\x30\x82\x02\x12\x30\x82\x01\x7b\x02\x02\x0d\xfa\x30\x0d\x06\x09'
            b'\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05\x05\x00\x30\x81\x9b\x31\x0b'
            b'\x30\x09\x06\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06'
            b'\x03\x55\x04\x08\x13\x05\x54\x6f\x6b\x79\x6f\x31\x10\x30\x0e\x06'
            b'\x03\x55\x04\x07\x13\x07\x43\x68\x75\x6f\x2d\x6b\x75\x31\x11\x30'
            b'\x0f\x06\x03\x55\x04\x0a\x13\x08\x46\x72\x61\x6e\x6b\x34\x44\x44'
            b'\x31\x18\x30\x16\x06\x03\x55\x04\x0b\x13\x0f\x57\x65\x62\x43\x65'
            b'\x72\x74\x20\x53\x75\x70\x70\x6f\x72\x74\x31\x18\x30\x16\x06\x03'
            b'\x55\x04\x03\x13\x0f\x46\x72\x61\x6e\x6b\x34\x44\x44\x20\x57\x65'
            b'\x62\x20\x43\x41\x31\x23\x30\x21\x06\x09\x2a\x86\x48\x86\xf7\x0d'
            b'\x01\x09\x01\x16\x14\x73\x75\x70\x70\x6f\x72\x74\x40\x66\x72\x61'
            b'\x6e\x6b\x34\x64\x64\x2e\x63\x6f\x6d\x30\x1e\x17\x0d\x31\x32\x30'
            b'\x38\x32\x32\x30\x35\x32\x36\x35\x34\x5a\x17\x0d\x31\x37\x30\x38'
            b'\x32\x31\x30\x35\x32\x36\x35\x34\x5a\x30\x4a\x31\x0b\x30\x09\x06'
            b'\x03\x55\x04\x06\x13\x02\x4a\x50\x31\x0e\x30\x0c\x06\x03\x55\x04'
            b'\x08\x0c\x05\x54\x6f\x6b\x79\x6f\x31\x11\x30\x0f\x06\x03\x55\x04'
            b'\x0a\x0c\x08\x46\x72\x61\x6e\x6b\x34\x44\x44\x31\x18\x30\x16\x06'
            b'\x03\x55\x04\x03\x0c\x0f\x77\x77\x77\x2e\x65\x78\x61\x6d\x70\x6c'
            b'\x65\x2e\x63\x6f\x6d\x30\x5c\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7'
            b'\x0d\x01\x01\x01\x05\x00\x03\x4b\x00\x30\x48\x02\x41\x00\x9b\xfc'
            b'\x66\x90\x79\x84\x42\xbb\xab\x13\xfd\x2b\x7b\xf8\xde\x15\x12\xe5'
            b'\xf1\x93\xe3\x06\x8a\x7b\xb8\xb1\xe1\x9e\x26\xbb\x95\x01\xbf\xe7'
            b'\x30\xed\x64\x85\x02\xdd\x15\x69\xa8\x34\xb0\x06\xec\x3f\x35\x3c'
            b'\x1e\x1b\x2b\x8f\xfa\x8f\x00\x1b\xdf\x07\xc6\xac\x53\x07\x02\x03'
            b'\x01\x00\x01\x30\x0d\x06\x09\x2a\x86\x48\x86\xf7\x0d\x01\x01\x05'
            b'\x05\x00\x03\x81\x81\x00\x14\xb6\x4c\xbb\x81\x79\x33\xe6\x71\xa4'
            b'\xda\x51\x6f\xcb\x08\x1d\x8d\x60\xec\xbc\x18\xc7\x73\x47\x59\xb1'
            b'\xf2\x20\x48\xbb\x61\xfa\xfc\x4d\xad\x89\x8d\xd1\x21\xeb\xd5\xd8'
            b'\xe5\xba\xd6\xa6\x36\xfd\x74\x50\x83\xb6\x0f\xc7\x1d\xdf\x7d\xe5'
            b'\x2e\x81\x7f\x45\xe0\x9f\xe2\x3e\x79\xee\xd7\x30\x31\xc7\x20\x72'
            b'\xd9\x58\x2e\x2a\xfe\x12\x5a\x34\x45\xa1\x19\x08\x7c\x89\x47\x5f'
            b'\x4a\x95\xbe\x23\x21\x4a\x53\x72\xda\x2a\x05\x2f\x2e\xc9\x70\xf6'
            b'\x5b\xfa\xfd\xdf\xb4\x31\xb2\xc1\x4a\x9c\x06\x25\x43\xa1\xe6\xb4'
            b'\x1e\x7f\x86\x9b\x16\x40'
        )

        decoded = snmp_v1.decode('Certificate', encoded_message)
        self.assertEqual(decoded, decoded_message)

        #encoded = snmp_v1.encode('Certificate', decoded_message)
        #self.assertEqual(encoded, encoded_message)


if __name__ == '__main__':
    unittest.main()
