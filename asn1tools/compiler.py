import logging
from collections import OrderedDict

from pyparsing import \
    Literal, Keyword, Word, ZeroOrMore, Regex, printables, delimitedList, \
    Group, Optional, Forward, StringEnd, OneOrMore, alphanums

from .codecs import ber
from .schema import \
    Module, Sequence, Integer, Boolean, IA5String, Enumerated, \
    BitString, Choice, SequenceOf, OctetString, Null


LOGGER = logging.getLogger(__name__)


class CompilerError(Exception):
    pass


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

    def __init__(self, modules, codec):
        self._modules = modules
        self._codec = codec

    def encode(self, name, data):
        """Encode given dictionary `data` as given type `name` and return the
        encoded data as a bytes object.

        >>> my_protocol.encode('Foo', {'bar': 1, 'fie': True})
        b'0\\x06\\x02\\x01\\x01\\x01\\x01\\x01'

        """

        for module in self._modules:
            try:
                return self._codec.encode(data,
                                          module.get_type_by_name(name))
            except LookupError:
                pass

        raise LookupError("Type '{}' not found.".format(name))

    def decode(self, name, data):
        """Decode given bytes object `data` as given type `name` and return
        the decoded data as a dictionary.

        >>> my_protocol.decode('Foo', b'0\\x06\\x02\\x01\\x01\\x01\\x01\\x01')
        {'bar': 1, 'fie': True}

        """

        for module in self._modules:
            try:
                return self._codec.decode(data,
                                          module.get_type_by_name(name))
            except LookupError:
                pass

        raise LookupError("Type '{}' not found.".format(name))

    def get_type(self, name):
        """Return a :class:`Type` object of type with given name `name`. The
        type object inherits the schema codec, and can be used to
        encode and decode data of the specific type.

        """

        for module in self._modules:
            try:
                return Type(module.get_type_by_name(name), self._codec)
            except LookupError:
                pass

        raise LookupError("Type '{}' not found.".format(name))

    def get_type_names(self):
        """Returns a dictionary of lists of all type names per module.

        """

        types = {}

        for module in self._modules:
            types[module.name] = [type_.name for type_ in module.types]

        return types

    def __str__(self):
        return '\n'.join([str(module) for module in self._modules])


def _convert_values(value, module, modules):
    """Convert a list of values tokens to classes. Each value has a name
    and a data part.

    """

    values = []

    for member in value:
        # Ignore '...'.
        if member == ['...']:
            continue

        item, _ = member
        value_name = item[0]

        if item[1] == 'INTEGER':
            item = Integer(value_name)
        elif item[1] == 'BOOLEAN':
            item = Boolean(value_name)
        elif item[1] == 'IA5String':
            item = IA5String(value_name)
        elif item[1] == 'ENUMERATED':
            item = Enumerated(value_name, {i: v
                                           for i, v in enumerate(item[3])
                                           if v != '...'})
        elif item[1] == 'CHOICE':
            item = Choice(value_name,
                          _convert_values(item[3],
                                          module,
                                          modules))
        elif item[1:3] == ['BIT', 'STRING']:
            item = BitString(value_name)
        elif item[1:3] == ['OCTET', 'STRING']:
            item = OctetString(value_name)
        elif item[1:3] == ['SEQUENCE', '{']:
            item = Sequence(value_name,
                            _convert_values(item[3],
                                            module,
                                            modules))
        elif item[1] == 'SEQUENCE' and item[3] == 'OF':
            item = SequenceOf(value_name, [])
        elif item[1] == 'NULL':
            item = Null(value_name)
        else:
            # User defined type.
            type_name = item[1]

            if type_name in module['types']:
                _convert_type_tokens_to_class(type_name,
                                              module['types'][type_name],
                                              module,
                                              modules)
                item = module['classes'][type_name](value_name)
            else:
                item = None

                for from_module, import_types in module['import'].items():
                    if type_name in import_types:
                        if type_name not in modules[from_module]['types']:
                            _convert_type_tokens_to_class(
                                type_name,
                                modules[from_module]['types'][type_name],
                                modules[from_module],
                                modules)
                        item = modules[from_module]['classes'][type_name](value_name)
                        break

                if item is None:
                    raise CompilerError('Type {} not found.'.format(
                        type_name))

        values.append(item)

    return values


def _convert_type_tokens_to_sequence(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    values = _convert_values(value[4], module, modules)

    module['types'][name] = Sequence(name, values)
    module['classes'][name] = type(name, (Sequence, ), {'values': values})


def _convert_type_tokens_to_choice(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    values = _convert_values(value[4], module, modules)

    module['types'][name] = Choice(name, values)
    module['classes'][name] = type(name, (Choice, ), {'values': values})


def _convert_type_tokens_to_integer(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    module['types'][name] = Integer(name)
    module['classes'][name] = type(name, (Integer, ), {})


def _convert_type_tokens_to_boolean(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    module['types'][name] = Boolean(name)
    module['classes'][name] = type(name, (Boolean, ), {})


def _convert_type_tokens_to_sequence_of(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    module['types'][name] = SequenceOf(name, [])
    module['classes'][name] = type(name, (SequenceOf, ), {'item': []})


def _convert_type_tokens_to_bit_string(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    module['types'][name] = BitString(name)
    module['classes'][name] = type(name, (BitString, ), {})


def _convert_type_tokens_to_octet_string(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    module['types'][name] = OctetString(name)
    module['classes'][name] = type(name, (OctetString, ), {})


def _convert_type_tokens_to_enumerated(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    module['classes'][name] = type(name,
                                   (Enumerated, ),
                                   {'values': {i: v
                                               for i, v in enumerate(value[4])
                                               if v != '...'}})
    module['types'][name] = module['classes'][name](name)


def _convert_type_tokens_to_user_type(name, value, module, modules):
    """Recursively convert tokens to classes.

    """

    type_name = value[2]

    if type_name in module['types']:
        _convert_type_tokens_to_class(type_name,
                                      module['types'][type_name],
                                      module,
                                      modules)
        class_ = module['classes'][type_name]
    else:
        class_ = None

        for from_module, import_types in module['import'].items():
            if type_name in import_types:
                if type_name not in modules[from_module]['types']:
                    _convert_type_tokens_to_class(
                        type_name,
                        modules[from_module]['types'][type_name],
                        modules[from_module],
                        modules)
                class_ = modules[from_module]['classes'][type_name]
                break

        if class_ is None:
            raise CompilerError('Type {} not found.'.format(
                type_name))

    module['types'][name] = class_(name)
    module['classes'][name] = class_


def _convert_type_tokens_to_class(name, value, module, modules):
    """Recursively convert type tokens to classes.

    """

    # Return immediately if the type is already converted to a class.
    if not isinstance(value, list):
        return

    if value[1:4] == ['::=', 'SEQUENCE', '{']:
        _convert_type_tokens_to_sequence(name, value, module, modules)
    elif value[1:4] == ['::=', 'CHOICE', '{']:
        _convert_type_tokens_to_choice(name, value, module, modules)
    elif value[1:3] == ['::=', 'INTEGER']:
        _convert_type_tokens_to_integer(name, value, module, modules)
    elif value[1:3] == ['::=', 'BOOLEAN']:
        _convert_type_tokens_to_boolean(name, value, module, modules)
    elif value[1:3] == ['::=', 'SEQUENCE'] and value[4] == 'OF':
        _convert_type_tokens_to_sequence_of(name, value, module, modules)
    elif value[1:4] == ['::=', 'BIT', 'STRING']:
        _convert_type_tokens_to_bit_string(name, value, module, modules)
    elif value[1:4] == ['::=', 'OCTET', 'STRING']:
        _convert_type_tokens_to_octet_string(name, value, module, modules)
    elif value[1:4] == ['::=', 'ENUMERATED', '{']:
        _convert_type_tokens_to_enumerated(name, value, module, modules)
    elif len(value) == 3:
        _convert_type_tokens_to_user_type(name, value, module, modules)
    else:
        raise NotImplementedError(value)


def compile_string(string, codec=None):
    """Compile given ASN.1 specification string and return a
    :class:`~asn1tools.compiler.Schema` object that can be used to
    encode and decode data structures.

    >>> with open('my_protocol.asn') as fin:
    ...     my_protocol = asn1tools.compile_string(fin.read())

    """

    # BER as default codec.
    if codec is None:
        codec = ber

    grammar = _create_grammar()
    tokens = grammar.parseString(string).asList()

    modules = OrderedDict()

    # Put tokens into dictionaries.
    for module in tokens:
        module_name = module[0][0]

        LOGGER.debug("Found module '%s'.", module_name)

        import_tokens = OrderedDict()
        types_tokens = OrderedDict()
        values_tokens = OrderedDict()

        if module[1]:
            from_name = module[1][-2]
            LOGGER.debug("Found imports from '%s'.", from_name)
            import_tokens[from_name] = module[1][1]

        for definition in module[2]:
            name = definition[0]

            if name[0].isupper():
                LOGGER.debug("Found type '%s'.", name)
                types_tokens[name] = definition
            else:
                LOGGER.debug("Found value '%s'.", name)
                values_tokens[name] = definition

        modules[module_name] = {
            'import': import_tokens,
            'types': types_tokens,
            'values': values_tokens,
            'classes': {}
        }

    # Recursively convert token lists to schema classes and their
    # instances.
    for module in modules.values():
        for name, value in module['types'].items():
            _convert_type_tokens_to_class(name, value, module, modules)

    return Schema([Module(name,
                          [v for v in values['types'].values()],
                          values['import'],
                          values['values'])
                   for name, values in modules.items()],
                  codec)


def compile_file(filename, codec=None):
    """Compile given ASN.1 specification file and return a
    :class:`~asn1tools.compiler.Schema` object that can be used to
    encode and decode data structures.

    >>> my_protocol = asn1tools.compile_file('my_protocol.asn')

    """

    with open(filename, 'r') as fin:
        return compile_string(fin.read(), codec)


def _create_grammar():
    # Keywords.
    SEQUENCE = Keyword('SEQUENCE')
    CHOICE = Keyword('CHOICE')
    ENUMERATED = Keyword('ENUMERATED')
    DEFINITIONS = Keyword('DEFINITIONS')
    BEGIN = Keyword('BEGIN')
    END = Keyword('END')
    AUTOMATIC = Keyword('AUTOMATIC')
    TAGS = Keyword('TAGS')
    OPTIONAL = Keyword('OPTIONAL')
    OF = Keyword('OF')
    SIZE = Keyword('SIZE')
    INTEGER = Keyword('INTEGER')
    BIT = Keyword('BIT')
    STRING = Keyword('STRING')
    OCTET = Keyword('OCTET')
    DEFAULT = Keyword('DEFAULT')
    IMPORTS = Keyword('IMPORTS')
    FROM = Keyword('FROM')
    CONTAINING = Keyword('CONTAINING')

    # Various literals.
    word = Word(printables, excludeChars=',(){}.:=;')
    type_name = Regex(r'[A-Z][a-zA-Z0-9-]*')
    value_name = Word(alphanums + '-')
    assignment = Literal('::=')
    lparen = Literal('(')
    rparen = Literal(')')
    lbrace = Literal('{')
    rbrace = Literal('}')
    scolon = Literal(';')
    dotx2 = Literal('..')
    dotx3 = Literal('...')

    # Forward declarations.
    sequence = Forward()
    choice = Forward()
    integer = Forward()
    bit_string = Forward()
    octet_string = Forward()
    enumerated = Forward()
    sequence_of = Forward()

    range_ = (word + dotx2 + word)
    type_ = (sequence
             | choice
             | integer
             | bit_string
             | octet_string
             | enumerated
             | sequence_of
             | word)
    item = Group(value_name + type_)

    # Type definitions.
    sequence << (SEQUENCE + lbrace
                 + Group(Optional(delimitedList(
                     Group((item
                            + Group(Optional(OPTIONAL)
                                    + Optional(DEFAULT + word)))
                           | dotx3))))
                 + rbrace)
    sequence_of << (SEQUENCE
                    + Group(lparen + SIZE + lparen
                            + (range_ | word)
                            + rparen + rparen)
                    + OF
                    + type_)
    choice << (CHOICE + lbrace
               + Group(Optional(delimitedList(
                   Group((item
                          + Group(Optional(OPTIONAL)))
                         | dotx3))))
               + rbrace)
    enumerated << (ENUMERATED + lbrace
                   + Group(delimitedList(word | dotx3))
                   + rbrace)
    integer << (INTEGER
                + Optional(lparen + (range_ | word) + rparen))
    bit_string << (BIT + STRING
                   + lparen + SIZE + lparen
                   + word
                   + rparen + rparen)
    octet_string << (OCTET + STRING
                     + Optional(lparen
                                + ((SIZE + lparen
                                    + (range_ | word)
                                    + rparen)
                                   | (CONTAINING + word))
                                + rparen))

    # Top level definitions.
    definition = Group((type_name + assignment + (sequence
                                                  | choice
                                                  | enumerated
                                                  | sequence_of
                                                  | integer
                                                  | bit_string
                                                  | octet_string
                                                  | word))
                       | (word + INTEGER + assignment + word))
    module_body = (Group(Optional(IMPORTS
                                  + Group(delimitedList(word))
                                  + FROM + word + scolon))
                   + Group(ZeroOrMore(definition)))
    module = Group(Group(word
                         + DEFINITIONS
                         + Optional(AUTOMATIC)
                         + Optional(TAGS)
                         + assignment
                         + BEGIN)
                   + module_body
                   + END)

    # The whole specification.
    specification = OneOrMore(module) + StringEnd()
    comment = Regex(r"--(?:\\\n|[^\n])*")
    specification.ignore(comment)

    return specification
