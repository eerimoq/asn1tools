import unittest
from binascii import hexlify

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
            print('Actual:', hexlify(encoded))
            print('Expected:', hexlify(encoded_message))
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
