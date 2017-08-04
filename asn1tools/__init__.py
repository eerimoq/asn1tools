__author__ = 'Erik Moqvist'
__version__ = '0.2.0'


from pyparsing import \
    Literal, Keyword, Word, ZeroOrMore, Regex, printables, delimitedList, \
    Group

from .codecs import ber
from .schema import \
    Module, Sequence, Integer, Boolean, IA5String


class Type(object):

    def __init__(self, schema, codec):
        self._schema = schema
        self._codec = codec

    def encode(self, data):
        """Encode given dictionary `data` and return the encoded data as a
        bytes object.

        >>> foo.encode({'bar': 1, 'fie': True})
        b'0\\x06\\x02\\x01\\x01\\x01\\x01\\x01'

        """

        return self._codec.encode(data, self._schema)

    def decode(self, data):
        """Decode given bytes object `data` and return the decoded data as a
        dictionary.

        >>> foo.decode(b'0\\x06\\x02\\x01\\x01\\x01\\x01\\x01')
        {'bar': 1, 'fie': True}

        """

        return self._codec.decode(data, self._schema)

    def __str__(self):
        return str(self._schema)


class Schema(object):

    def __init__(self, schema, codec):
        self._schema = schema
        self._codec = codec

    def encode(self, name, data):
        """Encode given dictionary `data` as given type `name` and return the
        encoded data as a bytes object.

        >>> my_protocol.encode('Foo', {'bar': 1, 'fie': True})
        b'0\\x06\\x02\\x01\\x01\\x01\\x01\\x01'

        """

        item = self._schema.get_item_by_name(name)

        return self._codec.encode(data, item)

    def decode(self, name, data):
        """Decode given bytes object `data` as given type `name` and return
        the decoded data as a dictionary.

        >>> my_protocol.decode('Foo', b'0\\x06\\x02\\x01\\x01\\x01\\x01\\x01')
        {'bar': 1, 'fie': True}

        """

        item = self._schema.get_item_by_name(name)

        return self._codec.decode(data, item)

    def get_type(self, name):
        """Return a :class:`Type` object of type with given name `name`. The
        type object inherits the schema codec, and can be used to
        encode and decode data of the specific type.

        """

        return Type(self._schema.get_item_by_name(name), self._codec)

    def __str__(self):
        return str(self._schema)


def compile_string(string, codec=None):
    """Compile given ASN.1 specification string and return a
    :class:`~asn1tools.Schema` object that can be used to encode and
    decode data structures.

    >>> with open('my_protocol.asn') as fin:
    ...     my_protocol = asn1tools.compile_string(fin.read())

    """

    # BER as default codec.
    if codec is None:
        codec = ber

    grammar = _create_grammar()
    tokens = grammar.parseString(string)

    #print(tokens)

    definitions = []

    for definition in tokens[1]:
        if definition[2] == 'SEQUENCE':
            items = []

            for item in definition[4]:
                if item[1] == 'INTEGER':
                    items.append(Integer(item[0]))
                elif item[1] == 'BOOLEAN':
                    items.append(Boolean(item[0]))
                elif item[1] == 'IA5String':
                    items.append(IA5String(item[0]))
                else:
                    raise NotImplementedError(item[1])

            definitions.append(Sequence(definition[0], items))
        else:
            raise NotImplementedError(definition[2])

    schema = Module(tokens[0][0], definitions)

    return Schema(schema, codec)


def compile_file(filename, codec=None):
    """Compile given ASN.1 specification file and return a
    :class:`~asn1tools.Schema` object that can be used to encode and
    decode data structures.

    >>> my_protocol = asn1tools.compile_file('my_protocol.asn')

    """

    with open(filename, 'r') as fin:
        return compile_string(fin.read(), codec)


def _create_grammar():
    # Keywords.
    SEQUENCE = Keyword('SEQUENCE')
    ENUMERATED = Keyword('ENUMERATED')
    DEFINITIONS = Keyword('DEFINITIONS')
    BEGIN = Keyword('BEGIN')
    END = Keyword('END')

    word = Word(printables, excludeChars=',')
    assignment = Literal('::=')
    lbrace = Literal('{')
    rbrace = Literal('}')

    type_ = word
    item = Group(word + type_)
    sequence = (SEQUENCE + lbrace
                + Group(delimitedList(item))
                + rbrace)
    enumerated = word
    definition = Group(word + assignment + (sequence | enumerated))
    module_body = Group(ZeroOrMore(definition))
    module = (Group(word + DEFINITIONS + assignment + BEGIN)
              + module_body
              + END)
    comment = Regex(r"--(?:\\\n|[^\n])*")
    module.ignore(comment)

    return module
