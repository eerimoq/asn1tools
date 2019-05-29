"""Permitted alphabet.

"""

import string

try:
    unichr
except NameError:
    unichr = chr


NUMERIC_STRING = ' 0123456789'

PRINTABLE_STRING = (string.ascii_uppercase
                    + string.ascii_lowercase
                    + string.digits
                    + " '()+,-./:=?")

IA5_STRING = ''.join([chr(v) for v in range(128)])

# ud800 - udfff are reserved code points for utf-16 surrogates.
# at this point, do not support code points in supplementary planes.
BMP_STRING = ''.join([unichr(v) for v in range(65536) if v < 0xd800 or v > 0xdfff])

VISIBLE_STRING = ''.join([chr(v) for v in range(32, 127)])
