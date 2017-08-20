class EncodeError(Exception):
    """General ASN.1 encode error.

    """

    pass


class DecodeError(Exception):
    """General ASN.1 decode error.

    """

    def __init__(self, message):
        super(DecodeError, self).__init__()
        self.message = message
        self.location = []

    def __str__(self):
        return "{}: {}".format(': '.join(self.location[::-1]),
                               self.message)
