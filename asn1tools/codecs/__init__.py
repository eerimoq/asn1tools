class EncodeError(Exception):
    """General ASN.1 encode error.

    """

    pass


class DecodeError(Exception):
    """General ASN.1 decode error.

    """

    def __init__(self, message, offset, decoded=None):
        super(DecodeError, self).__init__()
        self.message = message
        self.offset = offset
        self.decoded = decoded

    def __str__(self):
        return "{} at offset {}. Decoded: {}".format(self.message,
                                                     self.offset,
                                                     self.decoded)
