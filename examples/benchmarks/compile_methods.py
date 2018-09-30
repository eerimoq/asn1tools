#!/usr/bin/env python3

"""A performance example comparing the compile time and storage size
of three compile methods; pickle, compile string and compile
dictionary.

Example execution:

$ ./compile_methods.py

Parsing and compiling '/home/erik/asn1tools/tests/files/3gpp/rrc_8_6_0.asn' from file... done.
Using cached compilation... done.
Parsing and compiling '/home/erik/asn1tools/tests/files/3gpp/rrc_8_6_0.asn'... done.
Compiling RRC_8_6_0 dictionary... done.
Unpickling compiled object... done.

METHOD                    TIME  STORAGE-SIZE
unpickle               0.01985     546.72 KB
compile-cached-file    0.04645     679.65 KB
compile-dict           0.11395     175.03 KB
compile-string         1.00467     122.59 KB
compile-file           1.13757     122.59 KB
$

"""

from __future__ import print_function

import shutil
import os
import timeit
import pickle
import asn1tools
from humanfriendly import format_size


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
RRC_8_6_0_ASN_PATH = os.path.realpath(os.path.join(SCRIPT_DIR,
                                                   '..',
                                                   '..',
                                                   'tests',
                                                   'files',
                                                   '3gpp',
                                                   'rrc_8_6_0.asn'))
ITERATIONS = 1
CACHE_DIR = os.path.join(SCRIPT_DIR, 'compile_methods_cache')


def method_compile_file():
    print("Parsing and compiling '{}' from file... ".format(RRC_8_6_0_ASN_PATH),
          end='',
          flush=True)

    def compile_file():
        asn1tools.compile_files(RRC_8_6_0_ASN_PATH)

    time = timeit.timeit(compile_file, number=ITERATIONS)

    print('done.')

    with open(RRC_8_6_0_ASN_PATH, 'rb') as fin:
        string = fin.read()

    return round(time, 5), len(string)


def method_compile_cached_file():
    print("Using cached compilation... ",
          end='',
          flush=True)

    asn1tools.compile_files(RRC_8_6_0_ASN_PATH, cache_dir=CACHE_DIR)

    def compile_file():
        asn1tools.compile_files(RRC_8_6_0_ASN_PATH, cache_dir=CACHE_DIR)

    time = timeit.timeit(compile_file, number=ITERATIONS)

    print('done.')

    def dir_size(path):
        total = 0

        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += dir_size(entry.path)

        return total

    return round(time, 5), dir_size(CACHE_DIR)


def method_compile_string():
    with open(RRC_8_6_0_ASN_PATH, 'r') as fin:
        string = fin.read()

    print("Parsing and compiling '{}'... ".format(RRC_8_6_0_ASN_PATH),
          end='',
          flush=True)

    def compile_string():
        asn1tools.compile_string(string)

    time = timeit.timeit(compile_string, number=ITERATIONS)

    print('done.')

    return round(time, 5), len(string)


def method_compile_dict():
    dictionary = asn1tools.parse_files(RRC_8_6_0_ASN_PATH)

    print("Compiling RRC_8_6_0 dictionary... ",
          end='',
          flush=True)

    def compile_dict():
        asn1tools.compile_dict(dictionary)

    time = timeit.timeit(compile_dict, number=ITERATIONS)

    print('done.')

    return round(time, 5), len(str(dictionary))


def method_unpickle():
    pickled = pickle.dumps(asn1tools.compile_files(RRC_8_6_0_ASN_PATH))

    print("Unpickling compiled object... ",
          end='',
          flush=True)

    def unpickle():
        pickle.loads(pickled)

    time = timeit.timeit(unpickle, number=ITERATIONS)

    print('done.')

    return round(time, 5), len(pickled)


print()

if os.path.exists(CACHE_DIR):
    print('Removing {}... '.format(CACHE_DIR), end='', flush=True)
    shutil.rmtree(CACHE_DIR)
    print('done.')

compile_file_stats = method_compile_file()
compile_cached_file_stats = method_compile_cached_file()
compile_string_stats = method_compile_string()
compile_dict_stats = method_compile_dict()
unpickle_stats = method_unpickle()

# Comparison output.
measurements = [
    ('compile-file', *compile_file_stats),
    ('compile-cached-file', *compile_cached_file_stats),
    ('compile-string', *compile_string_stats),
    ('compile-dict', *compile_dict_stats),
    ('unpickle', *unpickle_stats)
]

measurements = sorted(measurements, key=lambda m: m[1])

print()
print('METHOD                    TIME  STORAGE-SIZE')

for name, execution_time, size in measurements:
    print('{:20} {:>9} {:>13}'.format(name,
                                      execution_time,
                                      format_size(size)))
