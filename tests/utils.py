import unittest
from binascii import hexlify


def format_encoded(encoded):
    hexstring = hexlify(encoded).decode('ascii')
    binstring = bin(int('80' + hexstring, 16))[10:]
    binstring = ' '.join([binstring[i:i + 8]
                          for i in range(0, len(binstring), 8)])

    return '{} ({})'.format(hexstring, binstring)


class Asn1ToolsBaseTest(unittest.TestCase):

    def assert_encode_decode(self,
                             specification,
                             type_name,
                             decoded_message,
                             encoded_message):
        try:
            encoded = specification.encode(type_name, decoded_message)
        except:
            print('Failed to encode type with name {}.'.format(type_name))
            raise

        try:
            self.assertEqual(encoded, encoded_message)
        except:
            print('Wrong encoding of type with name {}.'.format(type_name))
            print('Actual:', format_encoded(encoded))
            print('Expected:', format_encoded(encoded_message))
            raise

        try:
            decoded = specification.decode(type_name, encoded_message)
        except:
            print('Failed to decode type with name {}.'.format(type_name))
            raise

        try:
            self.assertEqual(decoded, decoded_message)
        except:
            print('Wrong decoding of type with name {}.'.format(type_name))
            print('Actual:', decoded)
            print('Expected:', decoded_message)
            raise

    def assert_encode_decode_string(self,
                                    specification,
                                    type_name,
                                    decoded_message,
                                    encoded_message,
                                    indent=None):
        try:
            encoded = specification.encode(type_name,
                                           decoded_message,
                                           indent=indent)
        except:
            print('Failed to encode type with name {}.'.format(type_name))
            raise

        try:
            self.assertEqual(encoded, encoded_message)
        except:
            print('Wrong encoding of type with name {}.'.format(type_name))
            print('Actual:', encoded)
            print('Expected:', encoded_message)
            raise

        try:
            decoded = specification.decode(type_name, encoded_message)
        except:
            print('Failed to decode type with name {}.'.format(type_name))
            raise

        try:
            self.assertEqual(decoded, decoded_message)
        except:
            print('Wrong decoding of type with name {}.'.format(type_name))
            print('Actual:', decoded)
            print('Expected:', decoded_message)
            raise
