#!/usr/bin/env python3

"""A performance example comparing the compile time and storage size
of three compile methods; pickle, compile string and compile
dictionary.

Example execution:

$ ./compile_methods.py

Parsing and compiling '/home/erik/asn1tools/tests/files/3gpp/rrc_8_6_0.asn' 5 times... done.
Compiling RRC_8_6_0 dictionary 5 times... done.
Unpickling compiled object 5 times... done.

METHOD               TIME  STORAGE-SIZE
unpickle           0.2258       1051696
compile-string    7.01243        122595
compile-dict      0.92199        175035
$

"""

from __future__ import print_function

import os
import timeit
import pickle
import asn1tools

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
RRC_8_6_0_ASN_PATH = os.path.realpath(os.path.join(SCRIPT_DIR,
                                                   '..',
                                                   '..',
                                                   'tests',
                                                   'files',
                                                   '3gpp',
                                                   'rrc_8_6_0.asn'))
ITERATIONS = 5


def method_compile_string():
    with open(RRC_8_6_0_ASN_PATH, 'r') as fin:
        string = fin.read()

    print("Parsing and compiling '{}' {} times... ".format(RRC_8_6_0_ASN_PATH,
                                                           ITERATIONS),
          end='',
          flush=True)

    def compile_string():
        asn1tools.compile_string(string)

    time = timeit.timeit(compile_string, number=ITERATIONS)

    print('done.')

    return round(time, 5), len(string)


def method_compile_dict():
    dictionary = asn1tools.parse_files(RRC_8_6_0_ASN_PATH)

    print("Compiling RRC_8_6_0 dictionary {} times... ".format(ITERATIONS),
          end='',
          flush=True)

    def compile_dict():
        asn1tools.compile_dict(dictionary)

    time = timeit.timeit(compile_dict, number=ITERATIONS)

    print('done.')

    return round(time, 5), len(str(dictionary))


def method_unpickle():
    pickled = pickle.dumps(asn1tools.compile_files(RRC_8_6_0_ASN_PATH))

    print("Unpickling compiled object {} times... ".format(ITERATIONS),
          end='',
          flush=True)

    def unpickle():
        pickle.loads(pickled)

    time = timeit.timeit(unpickle, number=ITERATIONS)

    print('done.')

    return round(time, 5), len(pickled)


print()

compile_string_time, compile_string_size = method_compile_string()
compile_dict_time, compile_dict_size = method_compile_dict()
unpickle_time, unpickle_size = method_unpickle()

print()
print('METHOD               TIME  STORAGE-SIZE')
print('unpickle        {:>9} {:>13}'.format(unpickle_time,
                                            unpickle_size))
print('compile-string  {:>9} {:>13}'.format(compile_string_time,
                                            compile_string_size))
print('compile-dict    {:>9} {:>13}'.format(compile_dict_time,
                                            compile_dict_size))
