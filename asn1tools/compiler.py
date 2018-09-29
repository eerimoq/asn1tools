"""Compile ASN.1 specifications to Python objects that can be used to
encode and decode types.

"""

import diskcache

from .parser import parse_files
from .parser import parse_string
from .codecs import compiler
from .codecs import ber
from .codecs import der
from .codecs import gser
from .codecs import jer
from .codecs import oer
from .codecs import per
from .codecs import uper
from .codecs import xer
from .codecs import type_checker
from .codecs import constraints_checker
from .errors import CompileError
from .errors import EncodeError
from .errors import DecodeError


class Specification(object):
    """This class is used to encode and decode ASN.1 types found in an
    ASN.1 specification.

    Instances of this class are created by the factory functions
    :func:`~asn1tools.compile_files()`,
    :func:`~asn1tools.compile_string()` and
    :func:`~asn1tools.compile_dict()`.

    """

    def __init__(self,
                 modules,
                 decode_length,
                 type_checkers,
                 constraints_checkers):
        self._modules = modules
        self._decode_length = decode_length
        self._types = {}

        duplicated = set()

        for module_name in modules:
            types = modules[module_name]

            for type_name, type_ in types.items():
                type_.type_checker = type_checkers[module_name][type_name]
                type_.constraints_checker = constraints_checkers[module_name][type_name]

                if type_name in duplicated:
                    continue

                if type_name in self._types:
                    del self._types[type_name]
                    duplicated.add(type_name)
                    continue

                self._types[type_name] = type_

    @property
    def types(self):
        """A dictionary of all unique types in the specification. Types found
        in two or more modules are not part of this dictionary.

        >>> question = foo.types['Question']
        >>> question
        Sequence(Question, [Integer(id), IA5String(question)])
        >>> question.encode({'id': 1, 'question': 'Is 1+1=3?'})
        b'0\\x0e\\x02\\x01\\x01\\x16\\x09Is 1+1=3?'

        """

        return self._types

    @property
    def modules(self):
        """A dictionary of all modules in the specification. Unlike
        :attr:`.types`, this attribute contains every type, even if
        the type name was found in two or more modules.

        >>> question = foo.modules['Foo']['Question']
        >>> question
        Sequence(Question, [Integer(id), IA5String(question)])
        >>> question.encode({'id': 1, 'question': 'Is 1+1=3?'})
        b'0\\x0e\\x02\\x01\\x01\\x16\\x09Is 1+1=3?'

        """

        return self._modules

    def encode(self,
               name,
               data,
               check_types=True,
               check_constraints=False,
               **kwargs):
        """Encode given dictionary `data` as given type `name` and return the
        encoded data as a bytes object.

        If `check_types` is ``True`` all objects in `data` are checked
        against the expected Python type for its ASN.1 type. Set
        `check_types` to ``False`` to minimize the runtime overhead,
        but instead get less informative error messages.

        See `Types`_ for a mapping table from ASN.1 types to Python
        types.

        If `check_constraints` is ``True`` all objects in `data` are
        checked against their ASN.1 type constraints. A
        ConstraintsError exception is raised if the constraints are
        not fulfilled. Set `check_constraints` to ``False`` to skip
        the constraints check and minimize the runtime overhead, but
        instead get less informative error messages and allow encoding
        of values not fulfilling the constraints.

        >>> foo.encode('Question', {'id': 1, 'question': 'Is 1+1=3?'})
        b'0\\x0e\\x02\\x01\\x01\\x16\\x09Is 1+1=3?'

        """

        try:
            type_ = self._types[name]
        except KeyError:
            raise EncodeError(
                "Type '{}' not found in types dictionary.".format(name))

        if check_types:
            type_.check_types(data)

        if check_constraints:
            type_.check_constraints(data)

        return type_.encode(data, **kwargs)

    def decode(self, name, data, check_constraints=False):
        """Decode given bytes object `data` as given type `name` and return
        the decoded data as a dictionary.

        If `check_constraints` is ``True`` all objects in `data` are
        checked against their ASN.1 type constraints. A
        ConstraintsError exception is raised if the constraints are
        not fulfilled. Set `check_constraints` to ``False`` to skip
        the constraints check and minimize the runtime overhead, but
        instead allow decoding of values not fulfilling the
        constraints.

        >>> foo.decode('Question', b'0\\x0e\\x02\\x01\\x01\\x16\\x09Is 1+1=3?')
        {'id': 1, 'question': 'Is 1+1=3?'}

        """

        try:
            type_ = self._types[name]
        except KeyError:
            raise DecodeError(
                "Type '{}' not found in types dictionary.".format(name))

        decoded = type_.decode(data)

        if check_constraints:
            type_.check_constraints(decoded)

        return decoded

    def decode_length(self, data):
        """Decode the length of given data `data`. Returns None if not enough
        data was given to decode the length.

        This method only works for BER and DER codecs with definite
        length in the first data encoding. Other codecs and
        combinations lacks length information in the data.

        >>> foo.decode_length(b'\\x30\\x0e\\x02\\x01\\x01')
        16

        """

        return self._decode_length(data)


def _compile_any_defined_by_type(type_, choices):
    type_['choices'] = {}

    for key, value in choices.items():
        specification = 'A DEFINITIONS ::= BEGIN B ::= {} END'.format(value)
        type_['choices'][key] = parse_string(specification)['A']['types']['B']


def _compile_any_defined_by_choices(specification,
                                    any_defined_by_choices):
    for location, choices in any_defined_by_choices.items():
        module_name = location[0]
        type_names = location[1:-1]
        member_name = location[-1]
        types = specification[module_name]['types']

        if len(type_names) == 0:
            _compile_any_defined_by_type(types[member_name], choices)
        else:
            for type_name in type_names:
                types = types[type_name]

            for member in types['members']:
                if member['name'] != member_name:
                    continue

                _compile_any_defined_by_type(member, choices)
                break


def _compile_files_cache(filenames,
                         codec,
                         any_defined_by_choices,
                         encoding,
                         cache_dir):
    key = [codec.encode('ascii')]

    if isinstance(filenames, str):
        filenames = [filenames]

    for filename in filenames:
        with open(filename, 'rb') as fin:
            key.append(fin.read())

    key = b''.join(key)
    cache = diskcache.Cache(cache_dir)

    try:
        return cache[key]
    except KeyError:
        compiled = compile_dict(parse_files(filenames, encoding),
                                codec,
                                any_defined_by_choices)
        cache[key] = compiled

        return compiled


def compile_dict(specification, codec='ber', any_defined_by_choices=None):
    """Compile given ASN.1 specification dictionary and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec
    `codec`. `codec` may be one of ``'ber'``, ``'der'``, ``'gser'``,
    ``'jer'``, ``oer``, ``'per'``, ``'uper'`` and ``'xer'``.

    >>> foo = asn1tools.compile_dict(asn1tools.parse_files('foo.asn'))

    """

    codecs = {
        'ber': ber,
        'der': der,
        'gser': gser,
        'jer': jer,
        'oer': oer,
        'per': per,
        'uper': uper,
        'xer': xer
    }

    try:
        codec = codecs[codec]
    except KeyError:
        raise CompileError("Unsupported codec '{}'.".format(codec))

    if any_defined_by_choices:
        _compile_any_defined_by_choices(specification,
                                        any_defined_by_choices)

    return Specification(codec.compile_dict(specification),
                         codec.decode_length,
                         type_checker.compile_dict(specification),
                         constraints_checker.compile_dict(specification))


def compile_string(string, codec='ber', any_defined_by_choices=None):
    """Compile given ASN.1 specification string and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec
    `codec`. `codec` may be one of ``'ber'``, ``'der'``, ``'gser'``,
    ``'jer'``, ``oer``, ``'per'``, ``'uper'`` and ``'xer'``.

    >>> with open('foo.asn') as fin:
    ...     foo = asn1tools.compile_string(fin.read())

    """

    return compile_dict(parse_string(string),
                        codec,
                        any_defined_by_choices)


def compile_files(filenames,
                  codec='ber',
                  any_defined_by_choices=None,
                  encoding='utf-8',
                  cache_dir=None):
    """Compile given ASN.1 specification file(s) and return a
    :class:`~asn1tools.compiler.Specification` object that can be used
    to encode and decode data structures with given codec
    `codec`. `codec` may be one of ``'ber'``, ``'der'``, ``'gser'``,
    ``'jer'``, ``oer``, ``'per'``, ``'uper'`` and ``'xer'``.

    `encoding` is the text encoding. This argument is passed to the
    built-in function `open()`.

    `cache_dir` specifies the compiled files cache location in the
    file system. Give as ``None`` to disable the cache. By default the
    cache is disabled. The cache key is the concatenated contents of
    given files and the codec name. Using a cache will significantly
    reduce the compile time when recompiling the same files. The cache
    directory is automatically created if it does not exist. Remove
    the cache directory `cache_dir` to clear the cache.

    >>> foo = asn1tools.compile_files('foo.asn')

    Give `cache_dir` as a string to use a cache.

    >>> foo = asn1tools.compile_files('foo.asn', cache_dir='my_cache')

    """

    if cache_dir is None:
        return compile_dict(parse_files(filenames, encoding),
                            codec,
                            any_defined_by_choices)
    else:
        return _compile_files_cache(filenames,
                                    codec,
                                    any_defined_by_choices,
                                    encoding,
                                    cache_dir)


def pre_process_dict(specification):
    """Pre-process given specification dictionary, expanding COMPONENTS OF
    and adding extension markers if EXTENSIBILITY IMPLIED is active.

    """

    return compiler.pre_process(specification)
