"""Convert ASN.1 specifications to Python data structures.

"""

import logging
import re
import sys

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
from pyparsing import nums
from pyparsing import Suppress
from pyparsing import ParseException
from pyparsing import ParseSyntaxException
from pyparsing import NotAny
from pyparsing import NoMatch
from pyparsing import QuotedString
from pyparsing import Combine
from pyparsing import ParseResults
from pyparsing import lineno

from .errors import Error


LOGGER = logging.getLogger(__name__)

EXTENSION_MARKER = None


class ParseError(Error):
    pass


class InternalParserError(Error):
    pass


class Tokens(object):

    def __init__(self, tag, tokens):
        self.tag = tag
        self.tokens = tokens

    def __getitem__(self, index):
        return self.tokens[index]

    def __len__(self):
        return len(self.tokens)

    def __iter__(self):
        for token in self.tokens:
            yield token

    def __bool__(self):
        return len(self.tokens) > 0

    def __eq__(self, other):
        return other == self.tag

    def __repr__(self):
        return "Tokens(tag='{}', tokens='{}')".format(self.tag,
                                                      self.tokens)


class Tag(Group):

    def __init__(self, tag, expr):
        super(Tag, self).__init__(expr)
        self.tag = tag

    def postParse(self, instring, loc, tokenlist):
        return Tokens(self.tag, tokenlist.asList())


def merge_dicts(dicts):
    return {k: v for d in dicts for k, v in d.items()}


def convert_integer(_s, _l, tokens):
    try:
        return int(tokens[0])
    except (IndexError, ValueError):
        return tokens


def convert_real_number(_s, _l, tokens):
    if '.' not in tokens[0]:
        tokens = int(tokens[0])

    return tokens


def convert_number(token):
    if isinstance(token, list):
        token = token[0]

    try:
        return int(token)
    except (ValueError, TypeError):
        return token


def convert_size(tokens):
    if len(tokens) == 0:
        return None

    tokens = tokens[0]

    if tokens[0] == 'SIZE':
        values = []

        for item_tokens in tokens[1].asList():
            if '..' in item_tokens:
                value = (convert_number(item_tokens[0]),
                         convert_number(item_tokens[2]))
            else:
                value = convert_number(item_tokens[0])

            values.append(value)

        return values
    elif isinstance(tokens[0], dict):
        if 'size' in tokens[0]:
            return tokens[0]['size']


def convert_table(tokens):
    tokens = tokens[0]

    try:
        if isinstance(tokens[1][0][0], list):
            defined_object_set = tokens[1][0][0][0]
        else:
            defined_object_set = tokens[1][0][0]
    except IndexError:
        return None

    try:
        component_ids = tokens[4]
    except IndexError:
        return defined_object_set

    return [defined_object_set, component_ids]


def convert_enum_values(string, location, tokens):
    number = 0
    values = []
    used_numbers = []
    root, extension = tokens
    root = root.asList()
    extension = extension.asList()

    def add_used_numbers(items):
        for item in items:
            if not isinstance(item, list):
                continue

            item_number = int(item[2])

            if item_number in used_numbers:
                raise ParseError(
                    'Duplicated ENUMERATED number {} at line {}.'.format(
                        item_number,
                        lineno(location, string)))

            used_numbers.append(item_number)

    # Root enumeration.
    add_used_numbers(root)

    for token in root:
        if isinstance(token, list):
            values.append((token[0], int(token[2])))
        else:
            while number in used_numbers:
                number += 1

            used_numbers.append(number)
            values.append((token, number))
            number += 1

    # Optional additional enumeration.
    if extension:
        values.append(EXTENSION_MARKER)
        additional = extension[1:]
        add_used_numbers(additional)

        for token in additional:
            if isinstance(token, list):
                number = int(token[2])
                values.append((token[0], number))
            else:
                if number in used_numbers:
                    raise ParseError(
                        'Duplicated ENUMERATED number {} at line {}.'.format(
                            number,
                            lineno(location, string)))

                values.append((token, number))
                used_numbers.append(number)

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
                'number': convert_number(tokens[0][1]),
                'class': tokens[0][0]
            }

        if tokens[1]:
            tag['kind'] = tokens[1][0] if tokens[1] else None

        return tag


def convert_value_range(_s, _l, tokens):
    tokens = tokens.asList()
    minimum = tokens[0]

    if isinstance(minimum, list):
        minimum = minimum[0]

    maximum = tokens[1]

    if isinstance(maximum, list):
        maximum = maximum[0]

    return (minimum, maximum)


def convert_inner_type_constraints(_s, _l, tokens):
    tokens = tokens.asList()
    components = []

    if tokens[0] == 'WITH COMPONENTS':
        for item_tokens in tokens[2]:
            if item_tokens == '...':
                value = EXTENSION_MARKER
            elif len(item_tokens) == 2:
                if isinstance(item_tokens[1], list):
                    value = item_tokens[1][0]

                    if isinstance(value, list):
                        value = value[0]

                    value = (item_tokens[0], value)
                else:
                    value = (item_tokens[0], item_tokens[1])
            else:
                value = item_tokens

            components.append(value)

        return {'with-components': components}
    else:
        return {}


def convert_size_constraint(_s, _l, tokens):
    tokens = tokens.asList()[1]
    values = []

    for item_tokens in tokens:
        if item_tokens == '...':
            value = EXTENSION_MARKER
        elif '..' in item_tokens:
            value = (convert_number(item_tokens[0]),
                     convert_number(item_tokens[2]))
        else:
            value = convert_number(item_tokens[0])

        values.append(value)

    return {'size': values}


def convert_permitted_alphabet(_s, _l, tokens):
    tokens = tokens.asList()
    values = []

    for token in tokens[1:]:
        if isinstance(token[0], list):
            for char in token[0][0]:
                values.append((char, char))
        else:
            values.append(token[0])

    return {'from': values}


def convert_constraint(_s, _l, tokens):
    tokens = tokens.asList()
    # print('constraint:', tokens)


def convert_members(tokens):
    members = []

    for member_tokens in tokens:
        if member_tokens in [['...'], '...']:
            members.append(EXTENSION_MARKER)
            continue

        if member_tokens[0] == 'COMPONENTS OF':
            members.append({
                'components-of': member_tokens[1][0]['type']
            })
            continue

        if member_tokens[0] == '[[':
            members.append(convert_members(member_tokens[1]))
            continue

        if len(member_tokens) == 2:
            member_tokens, qualifiers = member_tokens
            qualifiers = qualifiers.asList()
        else:
            qualifiers = []

        member = convert_type(member_tokens[2])
        member['name'] = member_tokens[0]

        if 'OPTIONAL' in qualifiers:
            member['optional'] = True

        if 'DEFAULT' in qualifiers:
            if len(qualifiers[1]) == 0:
                value = []
            else:
                value = convert_value(qualifiers[1], member['type'])

            member['default'] = value

        tag = convert_tag(member_tokens[1])

        if tag:
            member['tag'] = tag

        members.append(member)

    return members


def convert_sequence_type(_s, _l, tokens):
    return {
        'type': 'SEQUENCE',
        'members': convert_members(tokens[2])
    }


def convert_sequence_of_type(_s, _l, tokens):
    converted_type = {
        'type': 'SEQUENCE OF',
        'element': convert_type(tokens[4]),
    }

    if len(tokens[1]) > 0:
        converted_type['size'] = tokens[1][0]['size']

    tag = convert_tag(tokens[3])

    if tag:
        converted_type['element']['tag'] = tag

    return converted_type


def convert_set_type(_s, _l, tokens):
    return {
        'type': 'SET',
        'members': convert_members(tokens[2])
    }


def convert_set_of_type(_s, _l, tokens):
    converted_type = {
        'type': 'SET OF',
        'element': convert_type(tokens[4])
    }

    if len(tokens[1]) > 0:
        converted_type['size'] = tokens[1][0]['size']

    tag = convert_tag(tokens[3])

    if tag:
        converted_type['element']['tag'] = tag

    return converted_type


def convert_choice_type(_s, _l, tokens):
    return {
        'type': 'CHOICE',
        'members': convert_members(tokens[2])
    }


def convert_defined_type(_s, _l, tokens):
    return {
        'type': tokens[0]
    }


def convert_integer_type(_s, _l, _tokens):
    return {'type': 'INTEGER'}


def convert_real_type(_s, _l, _tokens):
    return {'type': 'REAL'}


def convert_enumerated_type(string, location, tokens):
    return {
        'type': 'ENUMERATED',
        'values': convert_enum_values(string, location, tokens[2])
    }


def convert_keyword_type(_s, _l, tokens):
    return {
        'type': tokens[0]
    }


def convert_print(_s, _l, tokens):
    print('convert_print', tokens)


def convert_object_identifier_type(_s, _l, _tokens):
    return {
        'type': 'OBJECT IDENTIFIER'
    }


def convert_bit_string_type(_s, _l, tokens):
    converted_type = {
        'type': 'BIT STRING'
    }

    named_bit_list = tokens.asList()[1]

    if named_bit_list:
        converted_type['named-bits'] = [
            tuple(named_bit) for named_bit in named_bit_list
        ]

    return converted_type


def convert_octet_string_type(_s, _l, _tokens):
    return {
        'type': 'OCTET STRING'
    }


def convert_ia5_string_type(_s, _l, _tokens):
    return {
        'type': 'IA5String'
    }


def convert_any_defined_by_type(_s, _l, tokens):
    return {
        'type': 'ANY DEFINED BY',
        'value': tokens[1],
        'choices': {}
    }


def convert_null_type(_s, _l, _tokens):
    return {
        'type': 'NULL'
    }


def convert_boolean_type(_s, _l, _tokens):
    return {
        'type': 'BOOLEAN'
    }


def convert_type(tokens):
    converted_type, constraints = tokens

    restricted_to = []

    for constraint_tokens in constraints:
        if isinstance(constraint_tokens, ParseResults):
            constraint_tokens = constraint_tokens.asList()

        if constraint_tokens == '...':
            restricted_to.append(EXTENSION_MARKER)
        elif len(constraint_tokens) == 1:
            if not isinstance(constraint_tokens[0], dict):
                restricted_to.append(convert_number(constraint_tokens[0]))
            elif 'size' in constraint_tokens[0]:
                converted_type.update(constraint_tokens[0])
            elif 'from' in constraint_tokens[0]:
                converted_type.update(constraint_tokens[0])
            elif 'with-components' in constraint_tokens[0]:
                converted_type.update(constraint_tokens[0])

    if '{' in restricted_to:
        restricted_to = []

    if restricted_to:
        converted_type['restricted-to'] = restricted_to

    types = [
        'BIT STRING',
        'OCTET STRING',
        'IA5String',
        'VisibleString',
        'UTF8String',
        'NumericString',
        'PrintableString'
    ]

    if converted_type['type'] in types:
        size = convert_size(constraints)

        if size:
            converted_type['size'] = size

    if '&' in converted_type['type']:
        converted_type['table'] = convert_table(tokens.asList()[1:])

    return converted_type


def convert_bstring(_s, _l, tokens):
    return '0b' + re.sub(r"[\sB']", '', tokens[0])


def convert_hstring(_s, _l, tokens):
    return '0x' + re.sub(r"[\sH']", '', tokens[0]).lower()


def convert_bit_string_value(tokens):
    value = tokens[0]

    if value == 'IdentifierList':
        value = value[:]
    elif isinstance(value, str):
        value = value
    else:
        value = None

    return value


def convert_value(tokens, type_=None):
    if type_ == 'INTEGER':
        value = int(tokens[0])
    elif type_ == 'OBJECT IDENTIFIER':
        value = []

        for value_tokens in tokens:
            if len(value_tokens) == 2:
                value.append((value_tokens[0], int(value_tokens[1])))
            else:
                value.append(convert_number(value_tokens[0]))
    elif type_ == 'BOOLEAN':
        value = (tokens[0] == 'TRUE')
    elif tokens[0] == 'BitStringValue':
        value = convert_bit_string_value(tokens[0])
    elif isinstance(tokens[0], str):
        value = convert_number(tokens[0])
    elif isinstance(tokens[0], int):
        value = tokens[0]
    else:
        value = None

    return value


def convert_parameterized_object_set_assignment(_s, _l, tokens):
    members = []

    try:
        for member_tokens in tokens[4].asList():
            if len(member_tokens[0]) == 1:
                member = member_tokens[0][0]
            else:
                member = {}

                for item_tokens in member_tokens[0]:
                    name = item_tokens[0]
                    value = item_tokens[1][0]

                    if isinstance(value, Tokens):
                        value = value[0]

                    member[name] = convert_number(value)

            members.append(member)
    except (IndexError, KeyError):
        pass

    converted_type = {
        'class': tokens[1],
        'members': members
    }

    return ('parameterized-object-set-assignment',
            tokens[0],
            converted_type)


def convert_parameterized_object_assignment(_s, _l, tokens):
    type_ = tokens[1]

    converted_type = {
        'type': type_,
        'value': None
    }

    return ('parameterized-object-assignment',
            tokens[0],
            converted_type)


def convert_parameterized_object_class_assignment(_s, _l, tokens):
    members = []

    for member in tokens[3]:
        if member[0][1].islower():
            converted_member = member[1][0]

            if isinstance(converted_member, Tokens):
                converted_member = converted_member[0]
        else:
            converted_member = {'type': 'OpenType'}

        converted_member['name'] = member[0]

        members.append(converted_member)

    converted_type = {
        'members': members
    }

    return ('parameterized-object-class-assignment',
            tokens[0],
            converted_type)


def convert_parameterized_type_assignment(_s, _l, tokens):
    tokens = tokens.asList()
    converted_type = convert_type(tokens[3])

    try:
        tag = convert_tag(tokens[2])
    except ValueError:
        tag = None

    if tag:
        converted_type['tag'] = tag

    return ('parameterized-type-assignment',
            tokens[0],
            converted_type)


def convert_parameterized_value_assignment(_s, _l, tokens):
    type_ = tokens[1][0][0]

    if isinstance(type_, Tokens):
        type_ = type_[0]
    elif isinstance(type_, dict):
        type_ = type_['type']

    converted_type = {
        'type': type_,
        'value': convert_value(tokens[2], type_)
    }

    return ('parameterized-value-assignment',
            tokens[0],
            converted_type)


def convert_imports(_s, _l, tokens):
    tokens = tokens.asList()
    imports = {}

    if tokens:
        for from_tokens in tokens:
            from_name = from_tokens[2]
            LOGGER.debug("Converting imports from '%s'.", from_name)
            imports[from_name] = from_tokens[0]

    return {'imports': imports}


def convert_assignment_list(_s, _l, tokens):
    types = {}
    values = {}
    object_classes = {}
    object_sets = {}

    for kind, name, value in tokens:
        if kind == 'parameterized-object-set-assignment':
            if name in object_sets:
                LOGGER.warning("Object set '%s' already defined.", name)

            object_sets[name] = value
        elif kind == 'parameterized-object-assignment':
            if name in values:
                LOGGER.warning("Object '%s' already defined.", name)

            values[name] = value
        elif kind == 'parameterized-object-class-assignment':
            if name in object_classes:
                LOGGER.warning("Object class '%s' already defined.", name)

            object_classes[name] = value
        elif kind == 'parameterized-type-assignment':
            if name in types:
                LOGGER.warning("Type '%s' already defined.", name)

            types[name] = value
        elif kind == 'parameterized-value-assignment':
            if name in values:
                LOGGER.warning("Value '%s' already defined.", name)

            values[name] = value
        else:
            raise InternalParserError(
                'Unrecognized assignment kind {}.'.format(kind))

    return {
        'types': types,
        'values': values,
        'object-classes': object_classes,
        'object-sets': object_sets
    }


def convert_module_body(_s, _l, tokens):
    return merge_dicts(tokens)


def convert_module_definition(_s, _l, tokens):
    tokens = tokens.asList()
    module = tokens[1][0]
    module['extensibility-implied'] = (tokens[0][3] != [])

    if tokens[0][2]:
        module['tags'] = tokens[0][2][0]

    return {tokens[0][0]: module}


def convert_specification(_s, _l, tokens):
    return merge_dicts(tokens)


def create_grammar():
    """Return the ASN.1 grammar as Pyparsing objects.

    """

    # Keywords.
    SEQUENCE = Keyword('SEQUENCE').setName('SEQUENCE')
    CHOICE = Keyword('CHOICE').setName('CHOICE')
    ENUMERATED = Keyword('ENUMERATED').setName('ENUMERATED')
    DEFINITIONS = Keyword('DEFINITIONS').setName('DEFINITIONS')
    BEGIN = Keyword('BEGIN').setName('BEGIN')
    END = Keyword('END').setName('END')
    AUTOMATIC = Keyword('AUTOMATIC').setName('AUTOMATIC')
    TAGS = Keyword('TAGS').setName('TAGS')
    OPTIONAL = Keyword('OPTIONAL').setName('OPTIONAL')
    OF = Keyword('OF').setName('OF')
    SIZE = Keyword('SIZE').setName('SIZE')
    INTEGER = Keyword('INTEGER').setName('INTEGER')
    REAL = Keyword('REAL').setName('REAL')
    BIT_STRING = Keyword('BIT STRING').setName('BIT STRING')
    OCTET_STRING = Keyword('OCTET STRING').setName('OCTET STRING')
    DEFAULT = Keyword('DEFAULT').setName('DEFAULT')
    IMPORTS = Keyword('IMPORTS').setName('IMPORTS')
    EXPORTS = Keyword('EXPORTS').setName('EXPORTS')
    FROM = Keyword('FROM').setName('FROM')
    CONTAINING = Keyword('CONTAINING').setName('CONTAINING')
    ENCODED_BY = Keyword('ENCODED_BY').setName('ENCODED_BY')
    IMPLICIT = Keyword('IMPLICIT').setName('IMPLICIT')
    EXPLICIT = Keyword('EXPLICIT').setName('EXPLICIT')
    OBJECT_IDENTIFIER = Keyword('OBJECT IDENTIFIER').setName('OBJECT IDENTIFIER')
    UNIVERSAL = Keyword('UNIVERSAL').setName('UNIVERSAL')
    APPLICATION = Keyword('APPLICATION').setName('APPLICATION')
    PRIVATE = Keyword('PRIVATE').setName('PRIVATE')
    SET = Keyword('SET').setName('SET')
    ANY_DEFINED_BY = Keyword('ANY DEFINED BY').setName('ANY DEFINED BY')
    EXTENSIBILITY_IMPLIED = Keyword('EXTENSIBILITY IMPLIED').setName(
        'EXTENSIBILITY IMPLIED')
    BOOLEAN = Keyword('BOOLEAN').setName('BOOLEAN')
    TRUE = Keyword('TRUE').setName('TRUE')
    FALSE = Keyword('FALSE').setName('FALSE')
    CLASS = Keyword('CLASS').setName('CLASS')
    WITH_SYNTAX = Keyword('WITH SYNTAX').setName('WITH SYNTAX')
    UNIQUE = Keyword('UNIQUE').setName('UNIQUE')
    NULL = Keyword('NULL').setName('NULL')
    WITH_COMPONENT = Keyword('WITH COMPONENT').setName('WITH COMPONENT')
    WITH_COMPONENTS = Keyword('WITH COMPONENTS').setName('WITH COMPONENTS')
    COMPONENTS_OF = Keyword('COMPONENTS OF').setName('COMPONENTS OF')
    PRESENT = Keyword('PRESENT').setName('PRESENT')
    ABSENT = Keyword('ABSENT').setName('ABSENT')
    ALL = Keyword('ALL').setName('ALL')
    EXCEPT = Keyword('EXCEPT').setName('EXCEPT')
    MIN = Keyword('MIN').setName('MIN')
    MAX = Keyword('MAX').setName('MAX')
    INCLUDES = Keyword('INCLUDES').setName('INCLUDES')
    PATTERN = Keyword('PATTERN').setName('PATTERN')
    CONSTRAINED_BY = Keyword('CONSTRAINED BY').setName('CONSTRAINED BY')
    UNION = Keyword('UNION').setName('UNION')
    INTERSECTION = Keyword('INTERSECTION').setName('INTERSECTION')
    PLUS_INFINITY = Keyword('PLUS-INFINITY').setName('PLUS-INFINITY')
    MINUS_INFINITY = Keyword('MINUS-INFINITY').setName('MINUS-INFINITY')
    BMPString = Keyword('BMPString').setName('BMPString')
    GeneralString = Keyword('GeneralString').setName('GeneralString')
    GraphicString = Keyword('GraphicString').setName('GraphicString')
    IA5String = Keyword('IA5String').setName('IA5String')
    ISO646String = Keyword('ISO646String').setName('ISO646String')
    NumericString = Keyword('NumericString').setName('NumericString')
    PrintableString = Keyword('PrintableString').setName('PrintableString')
    TeletexString = Keyword('TeletexString').setName('TeletexString')
    UTCTime = Keyword('UTCTime').setName('UTCTime')
    GeneralizedTime = Keyword('GeneralizedTime').setName('GeneralizedTime')
    T61String = Keyword('T61String').setName('T61String')
    UniversalString = Keyword('UniversalString').setName('UniversalString')
    UTF8String = Keyword('UTF8String').setName('UTF8String')
    VideotexString = Keyword('VideotexString').setName('VideotexString')
    VisibleString = Keyword('VisibleString').setName('VisibleString')
    CHARACTER_STRING = Keyword('CHARACTER STRING').setName('CHARACTER STRING')

    # Various literals.
    word = Word(printables, excludeChars=',(){}[].:=;"|').setName('word')
    identifier = Regex(r'[a-z][a-zA-Z0-9-]*').setName('identifier')
    assign = Literal('::=').setName('::=')
    left_parenthesis = Literal('(')
    right_parenthesis = Literal(')')
    left_brace = Literal('{')
    right_brace = Literal('}')
    left_bracket = Literal('[')
    right_bracket = Literal(']')
    left_version_brackets = Literal('[[')
    right_version_brackets = Literal(']]')
    colon = Literal(':')
    semi_colon = Literal(';')
    dot = Literal('.')
    range_separator = Literal('..')
    ellipsis = Literal('...')
    pipe = Literal('|')
    caret = Literal('^')
    comma = Literal(',')
    at = Literal('@')
    exclamation_mark = Literal('!')
    integer = Word(nums + '-')
    real_number = Regex(r'[+-]?\d+\.?\d*([eE][+-]?\d+)?')
    bstring = Regex(r"'[01\s]*'B")
    hstring = Regex(r"'[0-9A-F\s]*'H")
    cstring = QuotedString('"')
    number = (Word(nums).setName('number') + ~dot)
    ampersand = Literal('&')
    less_than = Literal('<')

    reserved_words = Regex(r'(END|SEQUENCE|ENUMERATED|WITH)(\s|$)')

    # Forward declarations.
    value = Forward()
    type_ = Forward()
    object_ = Forward()
    object_set = Forward()
    primitive_field_name = Forward()
    constraint = Forward()
    element_set_spec = Forward()
    token_or_group_spec = Forward()
    value_reference = Forward().setName('valuereference')
    type_reference = Forward().setName('typereference')
    value_set = Forward().setName('"valueSet" not implemented')
    named_type = Forward()
    root_element_set_spec = Forward()
    defined_object_set = Forward()
    syntax_list = Forward()
    object_from_object = Forward()
    object_set_from_objects = Forward()
    defined_value = Forward().setName('DefinedValue')
    component_type_lists = Forward()
    extension_and_exception = Forward()
    optional_extension_marker = Forward()
    additional_element_set_spec = Forward()
    reference = Forward()
    defined_object_class = Forward()
    defined_type = Forward()
    module_reference = Forward()
    external_type_reference = Forward()
    external_value_reference = Forward()
    simple_defined_type = Forward()
    defined_object = Forward()
    referenced_value = Forward()
    builtin_value = Forward()
    named_value = Forward()
    sequence_value = Forward()
    signed_number = Forward()
    name_and_number_form = Forward()
    number_form = Forward().setName('numberForm')
    definitive_number_form = Forward().setName('definitiveNumberForm')
    version_number = Forward()
    union_mark = Forward()
    named_number = Forward()
    size_constraint = Forward()

    value_field_reference = Combine(ampersand + value_reference)
    type_field_reference = Combine(ampersand + type_reference)

    # ToDo: Remove size_paren as they are a workaround for
    #       SEQUENCE/SET OF.
    size_paren = (Suppress(Optional(left_parenthesis))
                  + size_constraint
                  + Suppress(Optional(right_parenthesis)))

    class_number = (number | defined_value).setName('ClassNumber')
    tag = Group(Optional(Suppress(left_bracket)
                         - Group(Optional(UNIVERSAL
                                          | APPLICATION
                                          | PRIVATE)
                                 + class_number)
                         - Suppress(right_bracket)
                         + Group(Optional(IMPLICIT | EXPLICIT))))

    any_defined_by_type = (ANY_DEFINED_BY + word)
    any_defined_by_type.setName('ANY DEFINED BY')

    identifier_list = delimitedList(identifier)

    # X.683: 8. Parameterized assignments
    dummy_reference = reference
    dummy_governor = dummy_reference
    governor = (type_ | defined_object_class)
    param_governor = (governor | dummy_governor)
    parameter = (Optional(param_governor + colon) + dummy_reference)
    parameter_list = Suppress(Optional(left_brace
                                       + delimitedList(parameter)
                                       + right_brace))

    # X.683: 9. Referencing parameterized definitions
    actual_parameter = Group(type_
                             | value
                             | value_set
                             | defined_object_class
                             | object_
                             | object_set)
    actual_parameter_list = Group(Suppress(left_brace)
                                  + delimitedList(actual_parameter)
                                  + Suppress(right_brace))
    parameterized_object = (defined_object + actual_parameter_list)
    parameterized_object_set = (defined_object_set + actual_parameter_list)
    parameterized_object_class = (defined_object_class + actual_parameter_list)
    parameterized_value_set_type = (simple_defined_type
                                    + actual_parameter_list)
    simple_defined_value = (external_value_reference
                            | value_reference)
    parameterized_value = (simple_defined_value
                           + actual_parameter_list)
    simple_defined_type <<= (external_type_reference
                             | type_reference)
    parameterized_type = (simple_defined_type
                          + actual_parameter_list)
    parameterized_reference = (reference + Optional(left_brace + right_brace))

    # X.682: 11. Contents constraints
    contents_constraint = ((CONTAINING + type_)
                           | (ENCODED_BY + value)
                           | (CONTAINING + type_ + ENCODED_BY + value))

    # X.682: 10. Table constraints, including component relation constraints
    level = OneOrMore(dot)
    component_id_list = identifier
    at_notation = (Suppress(at)
                   - (component_id_list
                      | Combine(level + component_id_list)))
    component_relation_constraint = (left_brace
                                     + Group(Group(defined_object_set))
                                     + right_brace
                                     + left_brace
                                     - Group(delimitedList(at_notation))
                                     - right_brace)
    component_relation_constraint.setName('"{"')
    simple_table_constraint = object_set
    table_constraint = (component_relation_constraint
                        | simple_table_constraint)

    # X.682: 9. User-defined constants
    user_defined_constraint_parameter = ((governor
                                          + colon
                                          + (value
                                             | value_set
                                             | object_
                                             | object_set))
                                         | type_
                                         | defined_object_class)
    user_defined_constraint = (CONSTRAINED_BY
                               - left_brace
                               - Optional(delimitedList(
                                   user_defined_constraint_parameter))
                               - right_brace)
    user_defined_constraint.setName('CONSTRAINED_BY')

    # X.682: 8. General constraint specification
    general_constraint = (user_defined_constraint
                          | table_constraint
                          | contents_constraint)

    # X.681: 7. ASN.1 lexical items
    object_set_reference = type_reference
    value_set_field_reference = NoMatch().setName(
        '"valueSetFieldReference" not implemented')
    object_field_reference = NoMatch().setName(
        '"objectFieldReference" not implemented')
    object_set_field_reference = NoMatch().setName(
        '"objectSetFieldReference" not implemented')
    object_class_reference = (NotAny(reserved_words)
                              + Regex(r'[A-Z][A-Z0-9-]*'))
    object_reference = value_reference

    # X.681: 8. Referencing definitions
    external_object_set_reference = NoMatch().setName(
        '"externalObjectSetReference" not implemented')
    defined_object_set <<= (external_object_set_reference
                            | object_set_reference)
    defined_object <<= NoMatch().setName('"definedObject" not implemented')
    defined_object_class <<= object_class_reference

    # X.681: 9. Information object class definition and assignment
    field_name = primitive_field_name
    primitive_field_name <<= (type_field_reference
                              | value_field_reference
                              | value_set_field_reference
                              | object_field_reference
                              | object_set_field_reference)
    object_set_field_spec = NoMatch().setName('"objectSetFieldSpec" not implemented')
    object_field_spec = NoMatch().setName('"objectFieldSpec" not implemented')
    variable_type_value_set_field_spec = NoMatch().setName(
        '"variableTypeValueSetFieldSpec" not implemented')
    fixed_type_value_set_field_spec = NoMatch().setName(
        '"fixedTypeValueSetFieldSpec" not implemented')
    variable_type_value_field_spec = NoMatch().setName(
        '"variableTypeValueFieldSpec" not implemented')
    fixed_type_value_field_spec = (value_field_reference
                                   + type_
                                   + Optional(UNIQUE)
                                   + Optional(OPTIONAL
                                              | (DEFAULT - value)))
    type_field_spec = (type_field_reference
                       + Optional(OPTIONAL
                                  | (DEFAULT - type_)))
    field_spec = Group(type_field_spec
                       | fixed_type_value_field_spec
                       | variable_type_value_field_spec
                       | fixed_type_value_set_field_spec
                       | variable_type_value_set_field_spec
                       | object_field_spec
                       | object_set_field_spec)
    with_syntax_spec = (WITH_SYNTAX - syntax_list)
    object_class_defn = (CLASS
                         - Suppress(left_brace)
                         - Group(delimitedList(field_spec))
                         - Suppress(right_brace)
                         - Optional(with_syntax_spec))
    object_class = (object_class_defn
                    # | defined_object_class
                    | parameterized_object_class)
    parameterized_object_class_assignment = (object_class_reference
                                             + parameter_list
                                             + assign
                                             + object_class)

    # X.681: 10. Syntax list
    literal = (word | comma)
    required_token = (literal | primitive_field_name)
    optional_group = (left_bracket
                      + OneOrMore(token_or_group_spec)
                      + right_bracket)
    token_or_group_spec <<= (required_token | optional_group)
    syntax_list <<= (left_brace
                     + OneOrMore(token_or_group_spec)
                     + right_brace)

    # X.681: 11. Information object definition and assignment
    setting = (type_ | value | value_set | object_ | object_set | QuotedString('"'))
    field_setting = Group(primitive_field_name + setting)
    default_syntax = (Suppress(left_brace)
                      + delimitedList(field_setting)
                      + Suppress(right_brace))
    defined_syntax_token = (literal | setting)
    defined_syntax = (left_brace + ZeroOrMore(defined_syntax_token) + right_brace)
    object_defn = Group(default_syntax | defined_syntax)
    object_ <<= (defined_object
                 | object_defn
                 | object_from_object
                 | parameterized_object)
    parameterized_object_assignment = (object_reference
                                       + parameter_list
                                       + defined_object_class
                                       + Suppress(assign)
                                       + object_)

    # X.681: 12. Information object set definition and assignment
    object_set_elements = (object_
                           | defined_object_set
                           | object_set_from_objects
                           | parameterized_object_set)
    object_set_spec = ((root_element_set_spec
                        + Optional(comma
                                   + ellipsis
                                   + Optional(comma
                                              + additional_element_set_spec)))
                       | (ellipsis + Optional(comma + additional_element_set_spec)))
    object_set <<= (left_brace + Group(object_set_spec) + right_brace)
    object_set.setName('"{"')
    parameterized_object_set_assignment = (object_set_reference
                                           + parameter_list
                                           + defined_object_class
                                           - assign
                                           - object_set)

    # X.681: 13. Associated tables

    # X.681: 14. Notation for the object class field type
    fixed_type_field_val = (builtin_value | referenced_value)
    open_type_field_val = (type_ + colon + value)
    object_class_field_value = (open_type_field_val
                                | fixed_type_field_val)
    object_class_field_type = Combine(defined_object_class
                                      + dot
                                      + field_name)
    object_class_field_type.setName('ObjectClassFieldType')

    # X.681: 15. Information from objects
    object_set_from_objects <<= NoMatch().setName(
        '"objectSetFromObjects" not implemented')
    object_from_object <<= NoMatch().setName('"objectFromObject" not implemented')

    # X.680: 49. The exception identifier
    exception_spec = Optional(
        exclamation_mark
        + NoMatch().setName('"exceptionSpec" not implemented'))

    # X.680: 47. Subtype elements
    pattern_constraint = (PATTERN + value)
    value_constraint = constraint
    presence_constraint = (PRESENT | ABSENT | OPTIONAL)
    component_constraint = (Optional(value_constraint)
                            + Optional(presence_constraint))
    named_constraint = Group(identifier + component_constraint)
    type_constraints = delimitedList(named_constraint)
    full_specification = (left_brace + Group(type_constraints) + right_brace)
    partial_specification = (left_brace
                             + Group(ellipsis
                                     + Suppress(comma)
                                     + type_constraints)
                             + right_brace)
    single_type_constraint = constraint
    multiple_type_constraints = (full_specification | partial_specification)
    inner_type_constraints = ((WITH_COMPONENT - single_type_constraint)
                              | (WITH_COMPONENTS - multiple_type_constraints))
    permitted_alphabet = (FROM - constraint)
    type_constraint = type_
    size_constraint <<= (SIZE - Group(constraint))
    upper_end_value = (value | MAX)
    lower_end_value = (value | MIN)
    upper_endpoint = (Optional(less_than) + upper_end_value)
    lower_endpoint = (lower_end_value + Optional(less_than))
    value_range = (((Combine(integer + dot) + Suppress(range_separator))
                    | (integer + Suppress(range_separator))
                    | (lower_endpoint + Suppress(range_separator)))
                   - upper_endpoint)
    contained_subtype = (Optional(INCLUDES) + type_)
    single_value = value
    subtype_elements = (size_constraint
                        | permitted_alphabet
                        | value_range
                        | inner_type_constraints
                        | single_value
                        | pattern_constraint
                        | contained_subtype
                        | type_constraint)
    # X.680: 46. Element set specification
    union_mark <<= (pipe | UNION)
    intersection_mark = (caret | INTERSECTION)
    elements = Group(subtype_elements
                     | object_set_elements
                     | (left_parenthesis + element_set_spec + right_parenthesis))
    unions = delimitedList(elements, delim=(union_mark | intersection_mark))
    exclusions = (EXCEPT + elements)
    element_set_spec <<= (Suppress(ALL + exclusions) | unions)
    root_element_set_spec <<= element_set_spec
    additional_element_set_spec <<= element_set_spec
    element_set_specs = (root_element_set_spec
                         + Optional(Suppress(comma) - ellipsis
                                    + Optional(Suppress(comma)
                                               - additional_element_set_spec)))

    # X.680: 45. Constrained types
    subtype_constraint = element_set_specs
    constraint_spec = (general_constraint
                       | subtype_constraint)
    constraint_spec.setName('one or more constraints')
    constraint <<= (Suppress(left_parenthesis)
                    - constraint_spec
                    - Suppress(right_parenthesis))

    # X.680: 40. Definition of unrestricted character string types
    unrestricted_character_string_type = CHARACTER_STRING
    unrestricted_character_string_value = NoMatch().setName(
        '"unrestrictedCharacterStringValue" not implemented')

    # X.680: 39. Canonical order of characters

    # X.680: 38. Specification of the ASN.1 module "ASN.1-CHARACTER-MODULE"

    # X.680: 37. Definition of restricted character string types
    group = number
    plane = number
    row = number
    cell = number
    quadruple = (left_brace
                 + group + comma
                 + plane + comma
                 + row + comma
                 + cell
                 + right_brace)
    table_column = number
    table_row = number
    tuple_ = (left_brace + table_column + comma + table_row + right_brace)
    chars_defn = (cstring | quadruple | tuple_ | defined_value)
    charsyms = delimitedList(chars_defn)
    character_string_list = (left_brace + charsyms + right_brace)
    restricted_character_string_value = (cstring
                                         | character_string_list
                                         | quadruple
                                         | tuple_)
    restricted_character_string_type = (BMPString
                                        | GeneralString
                                        | GraphicString
                                        | IA5String
                                        | ISO646String
                                        | NumericString
                                        | PrintableString
                                        | TeletexString
                                        | UTCTime
                                        | GeneralizedTime
                                        | T61String
                                        | UniversalString
                                        | UTF8String
                                        | VideotexString
                                        | VisibleString)

    # X.680: 36. Notation for character string types
    character_string_value = (restricted_character_string_value
                              | unrestricted_character_string_value)
    character_string_type = (restricted_character_string_type
                             | unrestricted_character_string_type)

    # X.680: 35. The character string types

    # X.680: 34. Notation for the external type
    # external_value = sequence_value

    # X.680: 33. Notation for embedded-pdv type
    # embedded_pdv_value = sequence_value

    # X.680: 32. Notation for relative object identifier type
    relative_oid_components = Group(number_form
                                    | name_and_number_form
                                    | defined_value)
    relative_oid_component_list = OneOrMore(relative_oid_components)
    relative_oid_value = (Suppress(left_brace)
                          + relative_oid_component_list
                          + Suppress(right_brace))

    # X.680: 31. Notation for object identifier type
    name_and_number_form <<= (identifier
                              + Suppress(left_parenthesis)
                              - number_form
                              - Suppress(right_parenthesis))
    number_form <<= (number | defined_value)
    name_form = identifier
    obj_id_components = Group(name_and_number_form
                              | defined_value
                              | number_form
                              | name_form)
    obj_id_components_list = OneOrMore(obj_id_components)
    object_identifier_value = ((Suppress(left_brace)
                                + obj_id_components_list
                                + Suppress(right_brace))
                               | (Suppress(left_brace)
                                  + defined_value
                                  + obj_id_components_list
                                  + Suppress(right_brace)))

    object_identifier_type = (OBJECT_IDENTIFIER
                              + Optional(left_parenthesis
                                         + delimitedList(word, delim='|')
                                         + right_parenthesis))
    object_identifier_type.setName('OBJECT IDENTIFIER')

    # X.680: 30. Notation for tagged types
    tagged_value = NoMatch()

    # X.680: 29. Notation for selection types

    # X.680: 28. Notation for the choice types
    alternative_type_list = delimitedList(named_type)
    extension_addition_alternatives_group = Group(left_version_brackets
                                                  + Suppress(version_number)
                                                  - Group(alternative_type_list)
                                                  - right_version_brackets)
    extension_addition_alternative = (extension_addition_alternatives_group
                                      | named_type)
    extension_addition_alternatives_list = delimitedList(extension_addition_alternative)
    extension_addition_alternatives = Optional(Suppress(comma)
                                               + extension_addition_alternatives_list)
    root_alternative_type_list = alternative_type_list
    alternative_type_lists = (root_alternative_type_list
                              + Optional(Suppress(comma)
                                         + extension_and_exception
                                         + extension_addition_alternatives
                                         + optional_extension_marker))
    choice_type = (CHOICE
                   - left_brace
                   + Group(alternative_type_lists)
                   - right_brace)
    choice_type.setName('CHOICE')
    choice_value = (identifier + colon + value)

    # X.680: 27. Notation for the set-of types
    # set_of_value = NoMatch()
    set_of_type = (SET
                   + Group(Optional(size_paren))
                   + OF
                   + Optional(Suppress(identifier))
                   - tag
                   - type_)
    set_of_type.setName('SET OF')

    # X.680: 26. Notation for the set types
    # set_value = NoMatch()
    set_type = (SET
                + left_brace
                + Group(Optional(component_type_lists
                                 | (extension_and_exception
                                    + optional_extension_marker)))
                - right_brace)
    set_type.setName('SET')

    # X.680: 25. Notation for the sequence-of types
    sequence_of_value = NoMatch()
    sequence_of_type = (SEQUENCE
                        + Group(Optional(size_paren))
                        + OF
                        + Optional(Suppress(identifier))
                        - tag
                        - type_)
    sequence_of_type.setName('SEQUENCE OF')

    # X.680: 24. Notation for the sequence types
    component_value_list = delimitedList(named_value)
    sequence_value <<= (left_brace
                        + Optional(component_value_list)
                        + right_brace)
    component_type = Group(named_type
                           + Group(Optional(OPTIONAL
                                            | (DEFAULT + value)))
                           | (COMPONENTS_OF - type_))
    version_number <<= Optional(number + Suppress(colon))
    extension_addition_group = Group(left_version_brackets
                                     + Suppress(version_number)
                                     + Group(delimitedList(component_type))
                                     + right_version_brackets)
    extension_and_exception <<= (ellipsis + Optional(exception_spec))
    extension_addition = (component_type | extension_addition_group)
    extension_addition_list = delimitedList(extension_addition)
    extension_additions = Optional(Suppress(comma) + extension_addition_list)
    extension_end_marker = (Suppress(comma) + ellipsis)
    optional_extension_marker <<= Optional(Suppress(comma) + ellipsis)
    component_type_list = delimitedList(component_type)
    root_component_type_list = component_type_list
    component_type_lists <<= ((root_component_type_list
                               + Optional(Suppress(comma)
                                          + extension_and_exception
                                          + extension_additions
                                          + ((extension_end_marker
                                              + Suppress(comma)
                                              + root_component_type_list)
                                             | optional_extension_marker)))
                              | (extension_and_exception
                                 + extension_additions
                                 + ((extension_end_marker
                                     + Suppress(comma)
                                     + root_component_type_list)
                                    | optional_extension_marker)))
    sequence_type = (SEQUENCE
                     - left_brace
                     + Group(Optional(component_type_lists
                                      | (extension_and_exception
                                         + optional_extension_marker)))
                     - right_brace)
    sequence_type.setName('SEQUENCE')

    # X.680: 23. Notation for the null type
    null_value = NULL
    null_type = NULL

    # X.680: 22. Notation for the octetstring type
    # octet_string_value = (bstring
    #                       | hstring
    #                       | (CONTAINING + value))
    octet_string_type = OCTET_STRING
    octet_string_type.setName('OCTET STRING')

    # X.680: 21. Notation for the bitstring type
    bit_string_type = (BIT_STRING
                       + Group(Optional(
                           Suppress(left_brace)
                           + delimitedList(Group(word
                                                 + Suppress(left_parenthesis)
                                                 + word
                                                 + Suppress(right_parenthesis)))
                           + Suppress(right_brace))))
    bit_string_type.setName('BIT STRING')
    bit_string_value = Tag('BitStringValue',
                           bstring
                           | hstring
                           | Tag('IdentifierList',
                                 Suppress(left_brace)
                                 + Optional(identifier_list)
                                 + Suppress(right_brace))
                           | (CONTAINING - value))

    # X.680: 20. Notation for the real type
    special_real_value = (PLUS_INFINITY
                          | MINUS_INFINITY)
    numeric_real_value = (real_number
                          | sequence_value)
    real_value = (numeric_real_value
                  | special_real_value)
    real_type = REAL
    real_type.setName('REAL')

    # X.680: 19. Notation for the enumerated type
    enumerated_value = identifier
    enumeration_item = (Group(named_number) | identifier)
    enumeration = delimitedList(enumeration_item)
    root_enumeration = enumeration
    additional_enumeration = enumeration
    enumerations = Group(Group(root_enumeration)
                         + Group(Optional(Group(Suppress(comma
                                                         - ellipsis
                                                         + exception_spec))
                                          + Optional(Suppress(comma)
                                                     - additional_enumeration))))
    enumerated_type = (ENUMERATED
                       - left_brace
                       + enumerations
                       - right_brace)
    enumerated_type.setName('ENUMERATED')

    # X.680: 18. Notation for the integer type
    integer_value = (signed_number | identifier)
    signed_number <<= Combine(Optional('-') + number)
    named_number <<= (identifier
                      + left_parenthesis
                      + (signed_number | defined_value)
                      + right_parenthesis)
    named_number_list = delimitedList(named_number)
    integer_type = (INTEGER
                    + Group(Optional(left_brace
                                     + named_number_list
                                     + right_brace)))
    integer_type.setName('INTEGER')

    # X.680: 17. Notation for boolean type
    boolean_type = BOOLEAN
    boolean_value = (TRUE | FALSE)

    # X.680: 16. Definition of types and values
    named_value <<= (identifier + value)
    referenced_value <<= NoMatch().setName('"referencedValue" not implemented')
    builtin_value <<= (bit_string_value
                       | boolean_value
                       | character_string_value
                       | choice_value
                       | relative_oid_value
                       | sequence_value
                       # | embedded_pdv_value
                       | enumerated_value
                       # | external_value
                       # | instance_of_value
                       | real_value
                       | integer_value
                       | null_value
                       | object_identifier_value
                       # | octet_string_value
                       | sequence_of_value
                       # | set_value
                       # | set_of_value
                       | tagged_value)
    value <<= Group(object_class_field_value)
    # | referenced_value
    # | builtin_value)
    named_type <<= Group(identifier
                         - tag
                         - type_)
    referenced_type = defined_type
    referenced_type.setName('ReferencedType')
    builtin_type = (choice_type
                    | integer_type
                    | null_type
                    | real_type
                    | bit_string_type
                    | octet_string_type
                    | enumerated_type
                    | sequence_of_type
                    | sequence_type
                    | object_class_field_type
                    | set_of_type
                    | set_type
                    | object_identifier_type
                    | boolean_type
                    | character_string_type)
    type_ <<= Group((builtin_type
                     | any_defined_by_type
                     | referenced_type).setName('Type')
                    + Group(ZeroOrMore(constraint)))

    # X.680: 15. Assigning types and values
    type_reference <<= (NotAny(reserved_words)
                        + Regex(r'[A-Z][a-zA-Z0-9-]*'))
    value_reference <<= Regex(r'[a-z][a-zA-Z0-9-]*')
    value_set <<= NoMatch().setName('"valueSet" not implemented')
    parameterized_type_assignment = (type_reference
                                     + parameter_list
                                     - assign
                                     - tag
                                     - type_)
    parameterized_value_assignment = (value_reference
                                      + parameter_list
                                      - Group(type_)
                                      - Suppress(assign)
                                      - value)

    # X.680: 14. Notation to support references to ASN.1 components

    # X.680: 13. Referencing type and value definitions
    external_value_reference <<= (module_reference
                                  + dot
                                  + value_reference)
    external_type_reference <<= (module_reference
                                 + dot
                                 + type_reference)
    defined_type <<= (external_type_reference
                      | parameterized_type
                      | parameterized_value_set_type
                      | type_reference)
    defined_value <<= (external_value_reference
                       | parameterized_value
                       | value_reference)

    # X.680: 12. Module definition
    module_reference <<= (NotAny(reserved_words)
                          + Regex(r'[A-Z][a-zA-Z0-9-]*').setName('modulereference'))
    assigned_identifier = Suppress(Optional(object_identifier_value
                                            | (defined_value + ~(comma | FROM))))
    global_module_reference = (module_reference + assigned_identifier)
    reference <<= (type_reference
                   | value_reference
                   | object_class_reference
                   | object_reference
                   | object_set_reference)
    symbol = (parameterized_reference
              | reference)
    symbol_list = Group(delimitedList(symbol))
    symbols_from_module = (symbol_list
                           + FROM
                           + global_module_reference)
    symbols_imported = OneOrMore(Group(symbols_from_module))
    imports = Optional(Suppress(IMPORTS)
                       - symbols_imported
                       - Suppress(semi_colon))
    symbols_exported = OneOrMore(symbol_list)
    exports = Suppress(Optional(EXPORTS
                                - (ALL | symbols_exported) + semi_colon))
    assignment = (parameterized_object_set_assignment
                  | parameterized_object_assignment
                  | parameterized_object_class_assignment
                  | parameterized_type_assignment
                  | parameterized_value_assignment)
    assignment_list = ZeroOrMore(assignment)
    module_body = (exports + imports + assignment_list)
    definitive_name_and_number_form = (identifier
                                       + Suppress(left_parenthesis)
                                       - definitive_number_form
                                       - Suppress(right_parenthesis))
    definitive_number_form <<= number
    definitive_obj_id_component = Group(definitive_name_and_number_form
                                        | name_form
                                        | definitive_number_form)
    definitive_obj_id_components_list = OneOrMore(definitive_obj_id_component)
    definitive_identifier = Group(Optional(Suppress(left_brace)
                                           - definitive_obj_id_components_list
                                           - Suppress(right_brace)))
    module_identifier = (module_reference
                         + definitive_identifier)
    tag_default = Group(Optional((AUTOMATIC | EXPLICIT | IMPLICIT) + TAGS))
    extension_default = Group(Optional(EXTENSIBILITY_IMPLIED))
    module_definition = (Group(module_identifier
                               - Suppress(DEFINITIONS)
                               + tag_default
                               + extension_default
                               - Suppress(assign)
                               - Suppress(BEGIN))
                         + Group(module_body)
                         - Suppress(END))

    # The whole specification.
    specification = OneOrMore(module_definition) + StringEnd()

    # Parse actions converting tokens to asn1tools representation.
    integer.setParseAction(convert_integer)
    signed_number.setParseAction(convert_integer)
    real_number.setParseAction(convert_real_number)
    bstring.setParseAction(convert_bstring)
    hstring.setParseAction(convert_hstring)
    value_range.setParseAction(convert_value_range)
    inner_type_constraints.setParseAction(convert_inner_type_constraints)
    size_constraint.setParseAction(convert_size_constraint)
    permitted_alphabet.setParseAction(convert_permitted_alphabet)
    constraint.setParseAction(convert_constraint)
    module_body.setParseAction(convert_module_body)
    specification.setParseAction(convert_specification)
    module_definition.setParseAction(convert_module_definition)
    assignment_list.setParseAction(convert_assignment_list)
    imports.setParseAction(convert_imports)
    parameterized_object_set_assignment.setParseAction(
        convert_parameterized_object_set_assignment)
    parameterized_object_assignment.setParseAction(
        convert_parameterized_object_assignment)
    parameterized_object_class_assignment.setParseAction(
        convert_parameterized_object_class_assignment)
    parameterized_type_assignment.setParseAction(
        convert_parameterized_type_assignment)
    parameterized_value_assignment.setParseAction(
        convert_parameterized_value_assignment)
    sequence_type.setParseAction(convert_sequence_type)
    sequence_of_type.setParseAction(convert_sequence_of_type)
    set_type.setParseAction(convert_set_type)
    set_of_type.setParseAction(convert_set_of_type)
    integer_type.setParseAction(convert_integer_type)
    real_type.setParseAction(convert_real_type)
    boolean_type.setParseAction(convert_boolean_type)
    bit_string_type.setParseAction(convert_bit_string_type)
    octet_string_type.setParseAction(convert_octet_string_type)
    null_type.setParseAction(convert_null_type)
    object_identifier_type.setParseAction(convert_object_identifier_type)
    enumerated_type.setParseAction(convert_enumerated_type)
    choice_type.setParseAction(convert_choice_type)
    defined_type.setParseAction(convert_defined_type)
    character_string_type.setParseAction(convert_keyword_type)
    object_class_field_type.setParseAction(convert_keyword_type)
    any_defined_by_type.setParseAction(convert_any_defined_by_type)

    return specification


def ignore_comments(string):
    """Ignore comments in given string by replacing them with spaces. This
    reduces the parsing time by roughly a factor of two.

    """

    comments = [
        (mo.start(), mo.group(0))
        for mo in re.finditer(r'(/\*|\*/|--|\n)', string)
    ]

    comments.sort()

    in_single_line_comment = False
    multi_line_comment_depth = 0
    start_offset = 0
    non_comment_offset = 0
    chunks = []

    for offset, kind in comments:
        if in_single_line_comment:
            if kind in ['--', '\n']:
                in_single_line_comment = False

                if kind == '--':
                    offset += 2

                chunks.append(' ' * (offset - start_offset))
                non_comment_offset = offset
        elif multi_line_comment_depth > 0:
            if kind == '/*':
                multi_line_comment_depth += 1
            elif kind == '*/':
                multi_line_comment_depth -= 1

                if multi_line_comment_depth == 0:
                    offset += 2
                    chunks.append(' ' * (offset - start_offset))
                    non_comment_offset = offset
        elif kind == '--':
            in_single_line_comment = True
            start_offset = offset
            chunks.append(string[non_comment_offset:start_offset])
        elif kind == '/*':
            multi_line_comment_depth = 1
            start_offset = offset
            chunks.append(string[non_comment_offset:start_offset])

    if in_single_line_comment:
        raise ParseSyntaxException(
            string,
            start_offset,
            'Missing newline or -- for single line comment')

    if multi_line_comment_depth > 0:
        raise ParseSyntaxException(
            string,
            start_offset,
            'Missing */ for multi line comment')

    chunks.append(string[non_comment_offset:])

    return ''.join(chunks)


def parse_string(string):
    """Parse given ASN.1 specification string and return a dictionary of
    its contents.

    The dictionary can later be compiled with
    :func:`~asn1tools.compile_dict()`.

    >>> with open('foo.asn') as fin:
    ...     foo = asn1tools.parse_string(fin.read())

    """

    grammar = create_grammar()

    try:
        string = ignore_comments(string)
        tokens = grammar.parseString(string).asList()
    except (ParseException, ParseSyntaxException) as e:
        raise ParseError("Invalid ASN.1 syntax at line {}, column {}: '{}': {}.".format(
            e.lineno,
            e.column,
            e.markInputline(),
            e.msg))

    return tokens[0]


def parse_files(filenames, encoding='utf-8'):
    """Parse given ASN.1 specification file(s) and return a dictionary of
    its/their contents.

    The dictionary can later be compiled with
    :func:`~asn1tools.compile_dict()`.

    `encoding` is the text encoding. This argument is passed to the
    built-in function `open()`.

    >>> foo = asn1tools.parse_files('foo.asn')

    """

    if isinstance(filenames, str):
        filenames = [filenames]

    string = ''

    for filename in filenames:
        if sys.version_info[0] < 3:
            with open(filename, 'r') as fin:
                string += fin.read()
                string += '\n'
        else:
            with open(filename, 'r', encoding=encoding, errors='replace') as fin:
                string += fin.read()
                string += '\n'

    return parse_string(string)
