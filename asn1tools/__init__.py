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
__version__ = '0.45.0'


def _decode_hexstring(codec_spec, asn1_spec, type_name, hexstring):
    try:
        encoded = binascii.unhexlify(hexstring)
    except Exception as e:
        raise TypeError("'{}': {}".format(hexstring, str(e)))

    decoded = codec_spec.decode(type_name, encoded)
    
    print(asn1_spec.encode(type_name, decoded, indent=4).decode('utf-8'))


def _do_decode(args):
    parsed = parse_files(args.specification)
    codec_spec = compile_dict(parsed, args.codec)
    asn1_spec = compile_dict(parsed, 'asn1')

    if args.hexstring == '-':
        for hexstring in sys.stdin:
            hexstring = hexstring.strip('\r\n')

            if hexstring:
                try:
                    _decode_hexstring(codec_spec,
                                      asn1_spec,
                                      args.type,
                                      hexstring)
                except TypeError:
                    print(hexstring)
                except DecodeError as e:
                    print(hexstring)
                    print(str(e))
            else:
                print(hexstring)
    else:
        _decode_hexstring(codec_spec,
                          asn1_spec,
                          args.type,
                          args.hexstring)


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
    decode_parser.add_argument(
        'hexstring',
        help='Hexstring to decode, or - to read hexstrings from standard input.')
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
