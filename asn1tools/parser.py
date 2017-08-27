"""Compile ASN.1 specifications to Python objects that can be used to
encode and decode types.

"""

import logging

from pyparsing import \
    Literal, Keyword, Word, ZeroOrMore, Regex, printables, delimitedList, \
    Group, Optional, Forward, StringEnd, OneOrMore, alphanums, Suppress


LOGGER = logging.getLogger(__name__)


class ParserError(Exception):
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
        converted_type = {'type': 'BIT STRING'}

        if len(tokens) > 2 and tokens[2] == 'SIZE':
            converted_type['size'] = int(tokens[4])
    elif tokens[0:2] == ['OCTET', 'STRING']:
        converted_type = {'type': 'OCTET STRING'}
    elif tokens[0] == 'IA5String':
        converted_type = {'type': 'IA5String'}
    elif tokens[0:3] == ['ANY', 'DEFINED', 'BY']:
        converted_type = {
            'type': 'ANY DEFINED BY',
            'value': tokens[3]
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

    # Various literals.
    word = Word(printables, excludeChars=',(){}[].:=;')
    type_name = Regex(r'[A-Z][a-zA-Z0-9-]*')
    value_name = Word(alphanums + '-')
    assignment = Literal('::=')
    lparen = Literal('(')
    rparen = Literal(')')
    lbrace = Literal('{')
    rbrace = Literal('}')
    lbracket = Literal('[')
    rbracket = Literal(']')
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
    set_of = Forward()
    set_ = Forward()
    object_identifier = Forward()
    any_defined_by = Forward()

    range_ = (word + dotx2 + word)

    size = (Suppress(Optional(lparen)) + SIZE + lparen
            + (range_ | word)
            + rparen + Suppress(Optional(rparen)))

    type_ = (sequence
             | choice
             | integer
             | bit_string
             | octet_string
             | enumerated
             | sequence_of
             | set_of
             | set_
             | object_identifier
             | any_defined_by
             | (word + Optional(size)))

    item = Group(value_name + type_)

    tag = Group(Optional(Suppress(lbracket)
                         + Group(Optional(APPLICATION | PRIVATE) + word)
                         + Suppress(rbracket)
                         + Group(Optional(IMPLICIT | EXPLICIT))))

    # Type definitions.
    sequence << (SEQUENCE + lbrace
                 + Group(Optional(delimitedList(
                     Group(Group(value_name
                                 + tag
                                 + type_)
                           + Group(Optional(OPTIONAL)
                                   + Optional(DEFAULT + word))
                           | dotx3))))
                 + rbrace)

    sequence_of << (SEQUENCE
                    + Group(Optional(size))
                    + OF
                    + tag
                    + type_)

    set_of << (SET
               + Group(Optional(SIZE + lparen
                                + (range_ | word)
                                + rparen))
               + OF
               + tag
               + type_)

    set_ << (SET + lbrace
             + Group(Optional(delimitedList(
                 Group(Group(value_name
                             + tag
                             + type_)
                       + Group(Optional(OPTIONAL)
                               + Optional(DEFAULT + word))
                       | dotx3))))
             + rbrace)

    choice << (CHOICE
               + lbrace
               + Group(Optional(delimitedList(
                   Group(Group(value_name
                               + tag
                               + type_)
                         + Group(Optional(OPTIONAL)
                                 + Optional(DEFAULT + word))
                         | dotx3))))
               + rbrace)

    enumerated << (ENUMERATED + lbrace
                   + Group(delimitedList(Group((word
                                                + Optional(Suppress(lparen)
                                                           + word
                                                           + Suppress(rparen)))
                                               | dotx3)))
                   + rbrace)

    integer << (INTEGER
                + Group(Optional((lparen
                                  + (range_ | word)
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

    bit_string << (BIT + STRING
                   + Optional((lbrace
                               + Group(delimitedList(word
                                                     + lparen
                                                     + word
                                                     + rparen))
                               + rbrace))
                   + Optional(size))

    octet_string << (OCTET + STRING
                     + Optional(Suppress(lparen)
                                + ((SIZE + lparen
                                    + (range_ | word)
                                    + rparen)
                                   | (CONTAINING + word))
                                + Suppress(rparen)))

    object_identifier << (OBJECT + IDENTIFIER
                          + Optional(lparen
                                     + delimitedList(word, delim='|')
                                     + rparen))

    any_defined_by << (ANY + DEFINED + BY + word)

    # Top level definitions.
    type_definition = (type_name + assignment
                       + tag
                       + (sequence
                          | choice
                          | enumerated
                          | sequence_of
                          | set_of
                          | set_
                          | integer
                          | bit_string
                          | octet_string
                          | object_identifier
                          | any_defined_by
                          | (word + Optional(size))))

    oid = (Suppress(lbrace)
           + ZeroOrMore(Group((value_name
                               + Suppress(lparen)
                               + word
                               + Suppress(rparen))
                              | word))
           + Suppress(rbrace))

    value_definition = (word
                        + Group(INTEGER
                                | (OBJECT + IDENTIFIER)
                                | type_)
                        + assignment
                        + Group(oid | word))

    definition = Group(type_definition
                       | value_definition)

    module_body = (Group(Optional(IMPORTS
                                  + Group(delimitedList(word))
                                  + FROM
                                  + word
                                  + Suppress(Optional(oid))
                                  + scolon))
                   + Group(ZeroOrMore(definition)))

    module = Group(Group(word
                         + Group(Optional(oid))
                         + DEFINITIONS
                         + Group(Optional(AUTOMATIC | EXPLICIT | IMPLICIT)
                                 + Optional(TAGS))
                         + Group(Optional(EXTENSIBILITY + IMPLIED))
                         + assignment
                         + BEGIN)
                   + module_body
                   + END)

    # The whole specification.
    specification = OneOrMore(module) + StringEnd()
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
    tokens = grammar.parseString(string).asList()

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


def parse_file(filename):
    """Parse given ASN.1 specification file and return a dictionary of its
    contents.

    >>> foo = asn1tools.parse_file('foo.asn')

    """

    with open(filename, 'r') as fin:
        return parse_string(fin.read())
