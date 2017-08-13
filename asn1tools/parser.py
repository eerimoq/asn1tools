"""Compile ASN.1 specifications to Python objects that can be used to
encode and decode types.

"""

import logging

from pyparsing import \
    Literal, Keyword, Word, ZeroOrMore, Regex, printables, delimitedList, \
    Group, Optional, Forward, StringEnd, OneOrMore, alphanums


LOGGER = logging.getLogger(__name__)


class ParserError(Exception):
    pass


def _convert_number(token):
    try:
        return int(token)
    except ValueError:
        return token


def _convert_size(tokens):
    if len(tokens) == 0:
        return None
    elif '..' in tokens:
        return [(_convert_number(tokens[1]),
                 _convert_number(tokens[3]))]
    else:
        return [int(tokens[1])]


def _convert_members(tokens):
    members = []

    for member_tokens in tokens:
        if member_tokens == ['...']:
            member_tokens = [['...', ''], []]

        member_tokens, qualifiers = member_tokens
        member_name = member_tokens[0]
        member = {
            'name': member_name,
            'optional': 'OPTIONAL' in qualifiers
        }

        if 'DEFAULT' in qualifiers:
            member['default'] = _convert_number(qualifiers[1])

        if member_tokens[1] == 'INTEGER':
            member_type = 'INTEGER'

            if '..' in member_tokens[2]:
                minimum = _convert_number(member_tokens[2][1])
                maximum = _convert_number(member_tokens[2][3])
                member['restricted_to'] = [(minimum, maximum)]
        elif member_tokens[1] == 'BOOLEAN':
            member_type = 'BOOLEAN'
        elif member_tokens[1] == 'IA5String':
            member_type = 'IA5String'
        elif member_tokens[1] == 'ENUMERATED':
            member_type = 'ENUMERATED'
        elif member_tokens[1] == 'CHOICE':
            member_type = 'CHOICE'
        elif member_tokens[1:3] == ['BIT', 'STRING']:
            member_type = 'BIT STRING'
        elif member_tokens[1:3] == ['OCTET', 'STRING']:
            member_type = 'OCTET STRING'
        elif member_tokens[1:3] == ['SEQUENCE', '{']:
            member_type = 'SEQUENCE'
        elif member_tokens[1] == 'SEQUENCE' and member_tokens[3] == 'OF':
            member_type = 'SEQUENCE OF'
        elif member_tokens[1] == 'NULL':
            member_type = 'NULL'
        elif member_tokens[1:3] == ['OBJECT', 'IDENTIFIER']:
            member_type = 'OBJECT IDENTIFIER'
        else:
            member_type = member_tokens[1]

        member['type'] = member_type
        members.append(member)

    return members


def _convert_type_tokens_to_sequence(tokens):
    return {
        'type': 'SEQUENCE',
        'members': _convert_members(tokens[5])
    }


def _convert_type_tokens_to_choice(tokens):
    return {
        'type': 'CHOICE',
        'members': _convert_members(tokens[5])
    }


def _convert_type_tokens_to_integer(tokens):
    return {'type': 'INTEGER'}


def _convert_type_tokens_to_boolean(tokens):
    return {'type': 'BOOLEAN'}


def _convert_type_tokens_to_sequence_of(tokens):
    return {
        'type': 'SEQUENCE OF',
        'element_type': tokens[6],
        'size': _convert_size(tokens[4][2:-1])
    }


def _convert_type_tokens_to_bit_string(tokens):
    return {'type': 'BIT STRING'}


def _convert_type_tokens_to_octet_string(tokens):
    return {'type': 'OCTET STRING'}


def _convert_type_tokens_to_enumerated(tokens):
    return {'type': 'ENUMERATED'}


def _convert_type_tokens_to_object_identifier(tokens):
    return {'type': 'OBJECT IDENTIFIER'}


def _convert_type_tokens_to_user_type(tokens):
    return {'type': tokens[3]}


def _convert_type_tokens(tokens):
    if tokens[3:5] == ['SEQUENCE', '{']:
        converted_type = _convert_type_tokens_to_sequence(tokens)
    elif tokens[3:5] == ['CHOICE', '{']:
        converted_type =  _convert_type_tokens_to_choice(tokens)
    elif tokens[3:5] == ['ENUMERATED', '{']:
        converted_type =  _convert_type_tokens_to_enumerated(tokens)
    elif tokens[3] == 'SEQUENCE' and tokens[5] == 'OF':
        converted_type =  _convert_type_tokens_to_sequence_of(tokens)
    elif tokens[3] == 'INTEGER':
        converted_type =  _convert_type_tokens_to_integer(tokens)
    elif tokens[3:5] == ['BIT', 'STRING']:
        converted_type =  _convert_type_tokens_to_bit_string(tokens)
    elif tokens[3:5] == ['OCTET', 'STRING']:
        converted_type =  _convert_type_tokens_to_octet_string(tokens)
    elif tokens[3:5] == ['OBJECT', 'IDENTIFIER']:
        converted_type =  _convert_type_tokens_to_object_identifier(tokens)
    elif tokens[3] == 'BOOLEAN':
        converted_type =  _convert_type_tokens_to_boolean(tokens)
    else:
        converted_type =  _convert_type_tokens_to_user_type(tokens)

    if len(tokens[2]) > 0:
        if tokens[2][0] == '[' and tokens[2][2] == ']':
            converted_type['tag'] = (int(tokens[2][1]),
                                     tokens[2][3])
        elif tokens[2][0] == '[' and tokens[2][3] == ']':
            converted_type['tag'] = ((tokens[2][1], int(tokens[2][2])),
                                     tokens[2][4])
        else:
            raise ParserError('Bad tag tokens {}.'.format(tokens[2]))

    return converted_type


def _convert_value(tokens):
    value_type = tokens[1]

    if value_type == 'INTEGER':
        value = int(tokens[3])
    else:
        value = tokens

    return {'type': value_type, 'value': value}


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
    IMPLICIT = Keyword('IMPLICIT')
    OBJECT = Keyword('OBJECT')
    IDENTIFIER = Keyword('IDENTIFIER')
    APPLICATION = Keyword('APPLICATION')

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
    object_identifier = Forward()

    range_ = (word + dotx2 + word)
    type_ = (sequence
             | choice
             | integer
             | bit_string
             | octet_string
             | enumerated
             | sequence_of
             | object_identifier
             | word)
    item = Group(value_name + type_)

    tag = (lbracket
           + Optional(APPLICATION) + word
           + rbracket)

    # Type definitions.
    sequence << (SEQUENCE + lbrace
                 + Group(Optional(delimitedList(
                     Group((item
                            + Group(Optional(OPTIONAL)
                                    + Optional(DEFAULT + word)))
                           | dotx3))))
                 + rbrace)
    sequence_of << (SEQUENCE
                    + Group(Optional(lparen + SIZE + lparen
                                     + (range_ | word)
                                     + rparen + rparen))
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
                + Group(Optional((lparen
                                  + (range_ | word)
                                  + rparen)
                                 | (lbrace
                                    + Group(delimitedList(word
                                                          + lparen
                                                          + word
                                                          + rparen))
                                    + rbrace))))
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
    object_identifier << (OBJECT + IDENTIFIER)

    # Top level definitions.
    type_definition = (type_name + assignment
                       + Group(Optional(tag)
                               + Optional(IMPLICIT))
                       + (sequence
                          | choice
                          | enumerated
                          | sequence_of
                          | integer
                          | bit_string
                          | octet_string
                          | object_identifier
                          | word))
    value_definition = (word + INTEGER + assignment + word)
    definition = Group(type_definition
                       | value_definition)
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


def parse_string(string):
    """Parse given ASN.1 specification string and return a JSON dictionary
    of its contents.

    >>> with open('foo.asn') as fin:
    ...     foo = asn1tools.parse_string(fin.read())

    """

    grammar = _create_grammar()
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
                types[name] = _convert_type_tokens(definition)
            else:
                LOGGER.debug("Found value '%s'.", name)
                values[name] = _convert_value(definition)

        modules[module_name] = {
            'imports': imports,
            'types': types,
            'values': values
        }

    return modules


def parse_file(filename):
    """Parse given ASN.1 specification file and return a JSON dictionary
    of its contents.

    >>> foo = asn1tools.parse_file('foo.asn')

    """

    with open(filename, 'r') as fin:
        return parse_string(fin.read())
