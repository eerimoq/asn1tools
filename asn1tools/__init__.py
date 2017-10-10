"""The top level of the ASN.1 tools package contains commonly used
functions and classes.

"""

import sys
import argparse
import binascii

from .compiler import compile_dict, compile_string, compile_file
from .parser import parse_string, parse_file, ParseError
from .codecs import EncodeError, DecodeError


__author__ = 'Erik Moqvist'
__version__ = '0.12.0'


def print_list(list_, indent):
    for i, element in enumerate(list_):
        print('{}[{}]:'.format(indent * ' ', i))
        if isinstance(element, list):
            print_list(element, indent + 2)
        elif isinstance(element, dict):
            print_dict(element, indent + 2)
        elif isinstance(element, tuple):
            decoded = binascii.hexlify(element[0]).decode('ascii')
            print('{}"{}"'.format(indent * ' ', decoded))
        elif isinstance(element, bytearray):
            decoded = binascii.hexlify(element).decode('ascii')
            print("{}'{}'".format(indent * ' ', decoded))
        else:
            print('{}{}'.format(indent * ' ', element))


def print_dict(dict_, indent=0):
    for key, value in dict_.items():
        if isinstance(value, list):
            print('{}{}:'.format(indent * ' ', key))
            print_list(value, indent + 2)
        elif isinstance(value, dict):
            print('{}{}:'.format(indent * ' ', key))
            print_dict(value, indent + 2)
        elif isinstance(value, tuple):
            decoded = binascii.hexlify(value[0]).decode('ascii')
            print('{}{}: "{}"'.format(indent * ' ', key, decoded))
        elif isinstance(value, bytearray):
            decoded = binascii.hexlify(value).decode('ascii')
            print("{}{}: '{}'".format(indent * ' ', key, decoded))
        else:
            print('{}{}: {}'.format(indent * ' ', key, value))


def _do_decode(args):
    specification = compile_file(args.specification, args.codec)
    encoded = binascii.unhexlify(args.hexstring)
    print_dict(specification.decode(args.type, encoded))


def _main():
    parser = argparse.ArgumentParser(
        description='Various ASN.1 utilities.')

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    # Workaround to make the subparser required in Python 3.
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subcommand')
    subparsers.required = True

    # The 'decode' subparser.
    decode_parser = subparsers.add_parser(
        'decode',
        description='Decode given hextring and print it to standard output.')
    decode_parser.add_argument('-c', '--codec',
                               choices=('ber', 'der', 'per', 'uper'),
                               default='ber',
                               help='Codec (default: ber).')
    decode_parser.add_argument('specification', help='ASN.1 specification file (.asn).')
    decode_parser.add_argument('type', help='Type to decode.')
    decode_parser.add_argument('hexstring', help='Hexstring to decode.')
    decode_parser.set_defaults(func=_do_decode)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit(str(e))
