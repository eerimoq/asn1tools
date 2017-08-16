#!/usr/bin/env python

"""Encoding and decoding of a question.

"""

from __future__ import print_function
import sys
sys.path.insert(0, '..')
import asn1tools

question = {'id': 1, 'question': 'Is 1+1=3?'}

# Encode the question.
foo = asn1tools.compile_file('../tests/files/foo.asn')
encoded_question = foo.encode('Question', question)

print('Encoded question:', encoded_question)

# Decode the question.
decoded_question = foo.decode('Question', encoded_question)

print('Decoded question:', decoded_question)
