"""Compile ASN.1 specifications to Python objects that can be used to
encode and decode types.

"""

from .parser import parse_string
from .codecs import ber, per


class Specification(object):
    """This class is used to encode and decode ASN.1 types found in an
    ASN.1 specification.

    Instances of this class are created by the factory functions
    :func:`~asn1tools.compile_file()`,
    :func:`~asn1tools.compile_string()` and
    :func:`~asn1tools.compile_dict()`.

    """

    def __init__(self, modules):
        self._modules = modules
        self._types = {}

        try:
            for module_name in modules:
                types = modules[module_name]

                for type_name in types:
                    if type_name in self._types:
                        raise RuntimeError()

                    self._types[type_name] = types[type_name]

        except RuntimeError:
            self._types = None

    @property
    def types(self):
        """A dictionary of all types in the specification, or ``None`` if a
        type name was found in two or more modules.

        """

        return self._types

    @property
    def modules(self):
        """A dictionary of all modules in the specification.

        """

        return self._modules

    def encode(self, name, data):
        """Encode given dictionary `data` as given type `name` and return the
        encoded data as a bytes object.

        >>> foo.encode('Question', {'id': 1, 'question': 'Is 1+1=3?'})
        b'0\\x0e\\x02\\x01\\x01\\x16\\x09Is 1+1=3?'

        """

        return self._types[name].encode(data)

    def decode(self, name, data):
        """Decode given bytes object `data` as given type `name` and return
        the decoded data as a dictionary.

        >>> foo.decode('Question', b'0\\x0e\\x02\\x01\\x01\\x16\\x09Is 1+1=3?')
        {'id': 1, 'question': 'Is 1+1=3?'}

        """

        return self._types[name].decode(data)


def compile_dict(specification, codec='ber'):
    """Compile given ASN.1 specification dictionary and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec `codec`.

    >>> foo = asn1tools.compile_dict(asn1tools.parse_file('foo.asn'))

    """

    if codec == 'ber':
        codec = ber
    elif codec == 'per':
        codec = per
    else:
        raise ValueError('unsupported codec {}'.format(codec))

    return Specification(codec.compile_dict(specification))


def compile_string(string, codec='ber'):
    """Compile given ASN.1 specification string and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec `codec`.

    >>> with open('foo.asn') as fin:
    ...     foo = asn1tools.compile_string(fin.read())

    """

    return compile_dict(parse_string(string), codec)


def compile_file(filename, codec='ber'):
    """Compile given ASN.1 specification file and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec `codec`.

    >>> foo = asn1tools.compile_file('foo.asn')

    """

    with open(filename, 'r') as fin:
        return compile_string(fin.read(), codec)
