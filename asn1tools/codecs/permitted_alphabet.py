"""Permitted alphabet.

"""

import string


NUMERIC_STRING = ' 0123456789'

PRINTABLE_STRING = (string.ascii_uppercase
                    + string.ascii_lowercase
                    + string.digits
                    + " '()+,-./:=?")

IA5_STRING = ''.join([chr(v) for v in range(128)])

VISIBLE_STRING = ''.join([chr(v) for v in range(32, 127)])
