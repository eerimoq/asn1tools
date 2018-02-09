"""The top level of the ASN.1 tools package contains commonly used
functions and classes, and the command line interface.

"""

import sys
import argparse
import binascii
import logging

from .compiler import compile_dict
from .compiler import compile_string
from .compiler import compile_files
from .compiler import pre_process_dict
from .parser import parse_string
from .parser import parse_files
from .parser import ParseError
from .errors import EncodeError
from .errors import DecodeError
from .errors import CompileError


__author__ = 'Erik Moqvist'
__version__ = '0.27.0'


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
    specification = compile_files(args.specification, args.codec)

    try:
        encoded = binascii.unhexlify(args.hexstring)
    except Exception as e:
        raise TypeError("'{}': {}".format(args.hexstring, str(e)))

    print_dict(specification.decode(args.type, encoded))


def _main():
    parser = argparse.ArgumentParser(
        description='Various ASN.1 utilities.')

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-v', '--verbose',
                        choices=(0, 1, 2),
                        type=int,
                        default=1,
                        help=('Control the verbosity; disable(0), warning(1) '
                              'and debug(2). (default: 1).'))
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
                               choices=('ber', 'der', 'jer', 'per', 'uper', 'xer'),
                               default='ber',
                               help='Codec (default: ber).')
    decode_parser.add_argument('specification',
                               nargs='+',
                               help='ASN.1 specification as one or more .asn files.')
    decode_parser.add_argument('type', help='Type to decode.')
    decode_parser.add_argument('hexstring', help='Hexstring to decode.')
    decode_parser.set_defaults(func=_do_decode)

    args = parser.parse_args()

    levels = [logging.CRITICAL, logging.WARNING, logging.DEBUG]
    level = levels[args.verbose]

    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=level)

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit('error: {}'.format(str(e)))
