"""Various exceptions/errors.

"""


class Error(Exception):
    """Base exception of all asn1tools exceptions.

    """


class CompileError(Error):
    """General ASN.1 compile error.

    """


class EncodeError(Error):
    """General ASN.1 encode error.

    """


class DecodeError(Error):
    """General ASN.1 decode error.

    """


class ConstraintsError(Error):
    """General ASN.1 constraints error.

    """
