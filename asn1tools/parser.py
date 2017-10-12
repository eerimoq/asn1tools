"""Convert ASN.1 specifications to Python data structures.

"""

import logging

from pyparsing import Literal
from pyparsing import Keyword
from pyparsing import Word
from pyparsing import ZeroOrMore
from pyparsing import Regex
from pyparsing import printables
from pyparsing import delimitedList
from pyparsing import Group
from pyparsing import Optional
from pyparsing import Forward
from pyparsing import StringEnd
from pyparsing import OneOrMore
from pyparsing import alphanums
from pyparsing import nums
from pyparsing import Suppress
from pyparsing import ParseException
from pyparsing import ParseSyntaxException
from pyparsing import NotAny
from pyparsing import NoMatch


LOGGER = logging.getLogger(__name__)


class ParseError(Exception):
    pass


def convert_number(token):
    try:
        return int(token)
    except ValueError:
        return token


def convert_size(tokens):
    if len(tokens) == 0:
        return None
    elif '..' in tokens:
        return [(convert_number(tokens[0]),
                 convert_number(tokens[2]))]
    else:
        return [int(tokens[0])]


def convert_enum_values(tokens):
    number = 0
    values = {}

    for token in tokens:
        if len(token) == 2:
            number = int(token[1])

        values[number] = token[0]
        number += 1

    return values


def convert_tag(tokens):
    if len(tokens) > 0:
        if len(tokens[0]) == 1:
            tag = {
                'number': int(tokens[0][0])
            }
        else:
            tag = {
                'number': int(tokens[0][1]),
                'class': tokens[0][0]
            }

        if tokens[1]:
            tag['kind'] = tokens[1][0] if tokens[1] else None

        return tag


def convert_members(tokens):
    members = []

    for member_tokens in tokens:
        if member_tokens == ['...']:
            member_tokens = [['...', [], ''], []]

        member_tokens, qualifiers = member_tokens
        member = convert_type(member_tokens[2:])
        member['name'] = member_tokens[0]
        member['optional'] = 'OPTIONAL' in qualifiers

        if 'DEFAULT' in qualifiers:
            member['default'] = convert_number(qualifiers[1])

        tag = convert_tag(member_tokens[1])

        if tag:
            member['tag'] = tag

        members.append(member)

    return members


def convert_type(tokens):
    if tokens[0:2] == ['SEQUENCE', '{']:
        converted_type = {
            'type': 'SEQUENCE',
            'members': convert_members(tokens[2])
        }
    elif tokens[0] == 'SEQUENCE' and tokens[2] == 'OF':
        converted_type = {
            'type': 'SEQUENCE OF',
            'element': convert_type(tokens[4:]),
            'size': convert_size(tokens[1][2:-1])
        }

        tag = convert_tag(tokens[3])

        if tag:
            converted_type['element']['tag'] = tag
    elif tokens[0:2] == ['SET', '{']:
        converted_type = {
            'type': 'SET',
            'members': convert_members(tokens[2])
        }
    elif tokens[0] == 'SET' and tokens[2] == 'OF':
        converted_type = {
            'type': 'SET OF',
            'element': convert_type(tokens[4:]),
            'size': convert_size(tokens[1][2:-1])
        }

        tag = convert_tag(tokens[3])

        if tag:
            converted_type['element']['tag'] = tag
    elif tokens[0:2] == ['CHOICE', '{']:
        converted_type = {
            'type': 'CHOICE',
            'members': convert_members(tokens[2])
        }
    elif tokens[0] == 'INTEGER':
        converted_type = {'type': 'INTEGER'}

        if '..' in tokens[1]:
            minimum = convert_number(tokens[1][1])
            maximum = convert_number(tokens[1][3])
            converted_type['restricted-to'] = [(minimum, maximum)]
    elif tokens[0] == 'BOOLEAN':
        converted_type = {'type': 'BOOLEAN'}
    elif tokens[0:2] == ['ENUMERATED', '{']:
        converted_type = {
            'type': 'ENUMERATED',
            'values': convert_enum_values(tokens[2])
        }
    elif tokens[0:2] == ['OBJECT', 'IDENTIFIER']:
        converted_type = {'type': 'OBJECT IDENTIFIER'}
    elif tokens[0:2] == ['BIT', 'STRING']:
        converted_type = {'type': 'BIT STRING',
                          'size': convert_size(tokens[3][2:-1])}
    elif tokens[0:2] == ['OCTET', 'STRING']:
        converted_type = {'type': 'OCTET STRING',
                          'size': convert_size(tokens[2][2:-1])}
    elif tokens[0] == 'IA5String':
        converted_type = {'type': 'IA5String'}
    elif tokens[0:3] == ['ANY', 'DEFINED', 'BY']:
        converted_type = {
            'type': 'ANY DEFINED BY',
            'value': tokens[3],
            'choices': {}
        }
    else:
        converted_type = {'type': tokens[0]}

    return converted_type


def convert_type_tokens(tokens):
    converted_type = convert_type(tokens[3:])
    tag = convert_tag(tokens[2])

    if tag:
        converted_type['tag'] = tag

    return converted_type


def convert_value_tokens(tokens):
    type_ = tokens[1]

    if type_ == ['INTEGER']:
        value_type = 'INTEGER'
        value = int(tokens[3][0])
    elif type_ == ['OBJECT', 'IDENTIFIER']:
        value_type = 'OBJECT IDENTIFIER'
        value = []

        for value_tokens in tokens[3]:
            if len(value_tokens) == 2:
                value.append((value_tokens[0], int(value_tokens[1])))
            else:
                value.append(convert_number(value_tokens[0]))
    else:
        value_type = type_[0]
        value = tokens[3]

    return {'type': value_type, 'value': value}


def create_grammar():
    '''Return the ASN.1 grammar as Pyparsing objects.

    '''

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
    REAL = Keyword('REAL')
    BIT = Keyword('BIT')
    STRING = Keyword('STRING')
    OCTET = Keyword('OCTET')
    DEFAULT = Keyword('DEFAULT')
    IMPORTS = Keyword('IMPORTS')
    FROM = Keyword('FROM')
    CONTAINING = Keyword('CONTAINING')
    IMPLICIT = Keyword('IMPLICIT')
    EXPLICIT = Keyword('EXPLICIT')
    OBJECT = Keyword('OBJECT')
    IDENTIFIER = Keyword('IDENTIFIER')
    APPLICATION = Keyword('APPLICATION')
    PRIVATE = Keyword('PRIVATE')
    SET = Keyword('SET')
    ANY = Keyword('ANY')
    DEFINED = Keyword('DEFINED')
    BY = Keyword('BY')
    EXTENSIBILITY = Keyword('EXTENSIBILITY')
    IMPLIED = Keyword('IMPLIED')
    BOOLEAN = Keyword('BOOLEAN')
    TRUE = Keyword('TRUE')
    FALSE = Keyword('FALSE')

    # Various literals.
    word = Word(printables, excludeChars=',(){}[].:=;"|')
    type_reference = (NotAny(END) + Regex(r'[A-Z][a-zA-Z0-9-]*'))
    identifier = Regex(r'[a-z][a-zA-Z0-9-]*')
    value_reference = identifier
    value_name = Word(alphanums + '-')
    assign = Literal('::=')
    lparen = Literal('(')
    rparen = Literal(')')
    lbrace = Literal('{')
    rbrace = Literal('}')
    lbracket = Literal('[')
    rbracket = Literal(']')
    colon = Literal(':')
    scolon = Literal(';')
    dot = Literal('.')
    dotx2 = Literal('..')
    dotx3 = Literal('...')
    qmark = Literal('"')
    pipe = Literal('|')
    comma = Literal(',')
    integer = Word(nums)
    real_number = Regex(r'[+-]?\d+\.?\d*([eE][+-]?\d+)?')
    bstring = Regex(r"'[01\s]*'B")
    hstring = Regex(r"'[0-9A-F\s]*'H")
    cstring = NoMatch()
    number = word

    # Forward declarations.
    sequence_type = Forward().setName('SEQUENCE')
    choice_type = Forward().setName('CHOICE')
    integer_type = Forward().setName('INTEGER')
    real_type = Forward().setName('REAL')
    bit_string_type = Forward().setName('BIT STRING')
    octet_string_type = Forward().setName('OCTET STRING')
    enumerated_type = Forward().setName('ENUMERATED')
    sequence_of_type = Forward().setName('SEQUENCE OF')
    set_of_type = Forward().setName('SET OF')
    set_type = Forward().setName('SET')
    object_identifier_type = Forward().setName('OBJECT IDENTIFIER')
    boolean_type = Forward().setName('BOOLEAN')
    any_defined_by_type = Forward().setName('ANY DEFINED BY')

    bit_string_value = Forward()
    boolean_value = Forward()
    character_string_value = Forward()
    choice_value = Forward()

    range_ = (word + dotx2 + word)

    size = (SIZE
            + lparen
            + delimitedList(range_ | word, delim=pipe)
            + rparen)

    size_paren = (Suppress(Optional(lparen))
                  + size
                  + Suppress(Optional(rparen)))

    unions = Suppress(FROM
                      + delimitedList(qmark + word + qmark
                                      + dotx2
                                      + qmark + word + qmark, delim=pipe))

    element_set_spec = unions

    root_element_set_spec = element_set_spec

    root_element_set_specs = root_element_set_spec

    element_set_specs = root_element_set_specs

    subtype_constraint = element_set_specs

    constraint_spec = (size | subtype_constraint)

    constraint = (Suppress(lparen)
                  + constraint_spec
                  + Suppress(rparen))

    builtin_type = (choice_type
                    | integer_type
                    | real_type
                    | bit_string_type
                    | octet_string_type
                    | enumerated_type
                    | sequence_of_type
                    | sequence_type
                    | set_of_type
                    | set_type
                    | object_identifier_type
                    | boolean_type)

    type_ = (builtin_type
             | any_defined_by_type
             | (word + Optional(constraint)).setName('...'))

    tag = Group(Optional(Suppress(lbracket)
                         + Group(Optional(APPLICATION | PRIVATE) + word)
                         + Suppress(rbracket)
                         + Group(Optional(IMPLICIT | EXPLICIT))))

    sequence_type <<= (SEQUENCE
                       - lbrace
                       + Group(Optional(delimitedList(
                           Group(Group(identifier
                                       - tag
                                       - type_)
                                 + Group(Optional(OPTIONAL)
                                         + Optional(DEFAULT + word))
                                 | dotx3))))
                       - rbrace)

    sequence_of_type <<= (SEQUENCE
                          + Group(Optional(size_paren))
                          + OF
                          - tag
                          - type_)

    set_of_type <<= (SET
                     + Group(Optional(size))
                     + OF
                     - tag
                     - type_)

    set_type <<= (SET
                  - lbrace
                  + Group(Optional(delimitedList(
                      Group(Group(identifier
                                  - tag
                                  - type_)
                            + Group(Optional(OPTIONAL)
                                    + Optional(DEFAULT + word))
                            | dotx3))))
                  - rbrace)

    choice_type <<= (CHOICE
                     - lbrace
                     + Group(Optional(delimitedList(
                         Group(Group(identifier
                                     - tag
                                     - type_)
                               + Group(Optional(OPTIONAL)
                                       + Optional(DEFAULT + word))
                               | dotx3))))
                     - rbrace)

    enumerated_type <<= (ENUMERATED
                         - lbrace
                         + Group(delimitedList(Group((word
                                                      + Optional(Suppress(lparen)
                                                                 + word
                                                                 + Suppress(rparen)))
                                                     | dotx3)))
                         - rbrace)

    integer_type <<= (INTEGER
                      + Group(Optional((lparen
                                        + delimitedList(range_ | word, delim=pipe)
                                        + rparen)
                                       | (lbrace
                                          + Group(delimitedList(word
                                                                + lparen
                                                                + word
                                                                + rparen))
                                          + rbrace)))
                      + Optional(lparen
                                 + range_
                                 + rparen))

    real_type <<= (REAL
                   + Optional(lparen
                              + ((integer + dot + dotx2)
                                 | (integer + dotx2)
                                 | (real_number + dotx2))
                              + real_number
                              + rparen))

    bit_string_type <<= (BIT - STRING
                         + Group(Optional((lbrace
                                           + Group(delimitedList(word
                                                                 + lparen
                                                                 + word
                                                                 + rparen))
                                           + rbrace)))
                         + Group(Optional(constraint)))

    octet_string_type <<= (OCTET - STRING
                           + Group(Optional(Suppress(lparen)
                                            + (size | (CONTAINING + word))
                                            + Suppress(rparen))))

    object_identifier_type <<= (OBJECT - IDENTIFIER
                                + Optional(lparen
                                           + delimitedList(word, delim='|')
                                           + rparen))

    boolean_type <<= BOOLEAN

    any_defined_by_type <<= (ANY + DEFINED + BY + word)

    type_assignment = (type_reference
                       - assign
                       - tag
                       - type_)

    oid = (Suppress(lbrace)
           + ZeroOrMore(Group((value_name
                               + Suppress(lparen)
                               + word
                               + Suppress(rparen))
                              | word))
           + Suppress(rbrace))

    identifier_list = delimitedList(identifier)

    builtin_value = (bit_string_value
                     | boolean_value
                     | character_string_value
                     | choice_value
                     | word)

    value = Group(oid | builtin_value)

    bit_string_value <<= (bstring
                          | hstring
                          | (lbrace + Optional(identifier_list) + rbrace)
                          | (CONTAINING - value))

    boolean_value <<= (TRUE | FALSE)

    charsyms = NoMatch()

    character_string_list = (lbrace + charsyms + rbrace)

    group = number
    plane = number
    row = number
    cell = number
    quadruple = (lbrace
                 + group + comma
                 + plane + comma
                 + row + comma +
                 cell
                 + rbrace)

    table_column = number
    table_row = number
    tuple_ = (lbrace + table_column + comma + table_row + rbrace)

    restricted_character_string_value = (cstring
                                         | character_string_list
                                         | quadruple
                                         | tuple_)

    unrestricted_character_string_value = NoMatch()

    character_string_value <<= (restricted_character_string_value
                                | unrestricted_character_string_value)

    choice_value <<= (identifier + colon + value)

    value_assignment = (value_reference
                        - Group(INTEGER
                                | type_)
                        - assign
                        - value)

    assignment = Group(type_assignment
                       | value_assignment)

    symbols_imported = (Group(delimitedList(word))
                        + FROM
                        + word
                        + Suppress(Optional(oid)))

    imports = Group(Optional(IMPORTS
                             + symbols_imported
                             + scolon))

    assignment_list = Group(ZeroOrMore(assignment))

    module_body = (imports + assignment_list)

    module_reference = word

    definitive_identification = Group(Optional(oid))

    module_identifier = (module_reference + definitive_identification)

    tag_default = Group(Optional((AUTOMATIC | EXPLICIT | IMPLICIT) + TAGS))

    extension_default = Group(Optional(EXTENSIBILITY + IMPLIED))

    module_definition = Group(Group(module_identifier
                                    - DEFINITIONS
                                    + tag_default
                                    + extension_default
                                    - assign
                                    - BEGIN)
                              + module_body
                              - END)

    # The whole specification.
    specification = OneOrMore(module_definition) + StringEnd()
    comment = (Regex(r"--[\s\S]*?(--|\n)") | Regex(r"--(?:\\\n|[^\n])*"))
    specification.ignore(comment)

    return specification


def parse_string(string):
    """Parse given ASN.1 specification string and return a dictionary of
    its contents.

    >>> with open('foo.asn') as fin:
    ...     foo = asn1tools.parse_string(fin.read())

    """

    grammar = create_grammar()

    try:
        tokens = grammar.parseString(string).asList()
    except ParseException as e:
        raise ParseError("Invalid ASN.1 syntax at line {}, column {}: '{}'.".format(
            e.lineno,
            e.column,
            e.markInputline()))
    except ParseSyntaxException as e:
        raise ParseError("Invalid ASN.1 syntax at line {}, column {}: '{}': {}.".format(
            e.lineno,
            e.column,
            e.markInputline(),
            e.msg))

    modules = {}

    for module in tokens:
        module_name = module[0][0]

        LOGGER.debug("Found module '%s'.", module_name)

        imports = {}
        types = {}
        values = {}

        if module[1]:
            from_name = module[1][-2]
            LOGGER.debug("Found imports from '%s'.", from_name)
            imports[from_name] = module[1][1]

        for definition in module[2]:
            name = definition[0]

            if name[0].isupper():
                LOGGER.debug("Found type '%s'.", name)
                types[name] = convert_type_tokens(definition)
            else:
                LOGGER.debug("Found value '%s'.", name)
                values[name] = convert_value_tokens(definition)

        modules[module_name] = {
            'imports': imports,
            'types': types,
            'values': values
        }

        if module[0][3]:
            modules[module_name]['tags'] = module[0][3][0]

        modules[module_name]['extensibility-implied'] = (module[0][4] != [])

    return modules


def parse_files(filenames):
    """Parse given ASN.1 specification file(s) and return a dictionary of
    its/their contents.

    >>> foo = asn1tools.parse_files('foo.asn')

    """

    if isinstance(filenames, str):
        filenames = [filenames]

    string = ''

    for filename in filenames:
        with open(filename, 'r') as fin:
            string += fin.read()
            string += '\n'

    return parse_string(string)
