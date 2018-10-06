"""Convert ASN.1 specifications to Python data structures.

"""

import logging
import sys
import re
from pprint import pprint

from textparser import Parser
from textparser import Sequence
from textparser import choice
from textparser import ZeroOrMore
from textparser import OneOrMore
from textparser import DelimitedList
from textparser import Optional
from textparser import Not
from textparser import Tag
from textparser import Forward
from textparser import NoMatch

from .errors import Error


LOGGER = logging.getLogger(__name__)

EXTENSION_MARKER = None


class Asn1Parser(Parser):

    def keywords(self):
        return set([
            'ABSENT',
            'ENCODED',
            'INTEGER',
            'RELATIVE-OID',
            'ABSTRACT-SYNTAX',
            'END',
            'INTERSECTION',
            'SEQUENCE',
            'ALL',
            'ENUMERATED',
            'ISO646String',
            'SET',
            'APPLICATION',
            'EXCEPT',
            'MAX',
            'SIZE',
            'AUTOMATIC',
            'EXPLICIT',
            'MIN',
            'STRING',
            'BEGIN',
            'EXPORTS',
            'MINUS-INFINITY',
            'SYNTAX',
            'BIT',
            'EXTENSIBILITY',
            'NULL',
            'T61String',
            'BMPString',
            'EXTERNAL',
            'NumericString',
            'TAGS',
            'BOOLEAN',
            'FALSE',
            'OBJECT',
            'TeletexString',
            'BY',
            'FROM',
            'ObjectDescriptor',
            'TRUE',
            'CHARACTER',
            'GeneralizedTime',
            'OCTET',
            'TYPE-IDENTIFIER',
            'CHOICE',
            'GeneralString',
            'OF',
            'UNION',
            'CLASS',
            'GraphicString',
            'OPTIONAL',
            'UNIQUE',
            'COMPONENT',
            'IA5String',
            'PATTERN',
            'UNIVERSAL',
            'COMPONENTS',
            'IDENTIFIER',
            'PDV',
            'UniversalString',
            'CONSTRAINED',
            'IMPLICIT',
            'PLUS-INFINITY',
            'UTCTime',
            'CONTAINING',
            'IMPLIED',
            'PRESENT',
            'UTF8String',
            'DEFAULT',
            'IMPORTS',
            'PrintableString',
            'VideotexString',
            'DEFINITIONS',
            'INCLUDES',
            'PRIVATE',
            'VisibleString',
            'EMBEDDED',
            'INSTANCE',
            'REAL',
            'WITH',
            'ANY',
            'DEFINED'
        ])

    def token_specs(self):
        return [
            ('SKIP',           r'[ \r\n\t]+|--([\s\S]*?(--|\n))'),
            ('NUMBER',         r'-?\d+'),
            ('LVBRACK', '[[',  r'\[\['),
            ('RVBRACK', ']]',  r'\]\]'),
            ('LBRACE',  '{',   r'{'),
            ('RBRACE',  '}',   r'}'),
            ('LT',      '<',   r'<'),
            ('GT',      '>',   r'>'),
            ('COMMA',   ',',   r','),
            ('DOTX3',   '...', r'\.\.\.'),
            ('DOTX2',   '..',  r'\.\.'),
            ('DOT',     '.',   r'\.'),
            ('LPAREN',  '(',   r'\('),
            ('RPAREN',  ')',   r'\)'),
            ('LBRACK',  '[',   r'\['),
            ('RBRACK',  ']',   r'\]'),
            ('MINUS',   '-',   r'-'),
            ('ASSIGN',  '::=', r'::='),
            ('COLON',   ':',   r':'),
            ('EQ',      '=',   r'='),
            ('CSTRING',        r'"[^"]*"'),
            ('QMARK',   '"',   r'"'),
            ('BSTRING',        r"'[01\s]*'B"),
            ('HSTRING',        r"'[0-9A-F\s]*'H"),
            ('APSTR',   "'",   r"'"),
            ('SCOLON',  ';',   r';'),
            ('AT',      '@',   r'@'),
            ('PIPE',    '|',   r'\|'),
            ('EMARK',   '!',   r'!'),
            ('HAT',     '^',   r'\^'),
            ('AMPND',   '&',   r'&'),
            ('TREF',           r'[A-Z][a-zA-Z0-9-]*'),
            ('IDENT',          r'[a-z][a-zA-Z0-9-]*'),
            ('MISMATCH',       r'.')
        ]

    def grammar(self):
        value = Forward()
        type_ = Forward()
        object_ = Forward()
        object_set = Forward()
        primitive_field_name = Forward()
        constraint = Forward()
        element_set_spec = Forward()
        token_or_group_spec = Forward()
        value_set = Forward()
        named_type = Forward()
        root_element_set_spec = Forward()
        defined_object_set = Forward()
        syntax_list = Forward()
        object_from_object = Forward()
        object_set_from_objects = Forward()
        defined_value = Forward()
        component_type_lists = Forward()
        extension_and_exception = Forward()
        optional_extension_marker = Forward()
        additional_element_set_spec = Forward()
        reference = Forward()
        defined_object_class = Forward()
        defined_type = Forward()
        external_type_reference = Forward()
        external_value_reference = Forward()
        simple_defined_type = Forward()
        defined_object = Forward()
        referenced_value = Forward()
        builtin_value = Forward()
        named_value = Forward()
        signed_number = Forward()
        name_and_number_form = Forward()
        number_form = Forward()
        definitive_number_form = Forward()
        version_number = Forward()
        named_number = Forward()
        intersections = Forward()
        unions = Forward()

        # ToDo!
        value_set <<= NoMatch()

        # X680: 11. ASN.1 lexical items
        identifier = 'IDENT'
        value_reference = identifier
        type_reference = 'TREF'
        module_reference = type_reference
        real_number = Sequence('NUMBER', '.', Optional('NUMBER'))
        number = 'NUMBER'

        value_field_reference = Sequence('&',  value_reference)
        type_field_reference = Sequence('&', type_reference)
        word = type_reference

        # X.683: 8. Parameterized assignments
        dummy_reference = reference
        dummy_governor = dummy_reference
        governor = choice(type_, defined_object_class)
        param_governor = choice(governor, dummy_governor)
        parameter = Sequence(Optional(Sequence(param_governor, ':')),
                             dummy_reference)
        parameter_list = Optional(Sequence('{',
                                           DelimitedList(parameter),
                                           '}'))

        # X.683: 9. Referencing parameterized definitions
        actual_parameter = choice(type_,
                                  value,
                                  value_set,
                                  defined_object_class,
                                  object_,
                                  object_set)
        actual_parameter_list = Sequence('{',
                                         DelimitedList(actual_parameter),
                                         '}')
        parameterized_object = Sequence(defined_object,
                                        actual_parameter_list)
        parameterized_object_set = Sequence(defined_object_set,
                                            actual_parameter_list)
        parameterized_object_class = Sequence(defined_object_class,
                                              actual_parameter_list)
        parameterized_value_set_type = Sequence(simple_defined_type,
                                                actual_parameter_list)
        simple_defined_value = choice(external_value_reference,
                                      value_reference)
        parameterized_value = Sequence(simple_defined_value,
                                       actual_parameter_list)
        simple_defined_type <<= choice(external_type_reference,
                                       type_reference)
        parameterized_type = Sequence(simple_defined_type,
                                      actual_parameter_list)
        parameterized_reference = Sequence(reference,
                                           Optional(Sequence('{', '}')))

        # X.682: 11. Contents constraints
        contents_constraint = choice(
            Sequence('CONTAINING',
                     type_,
                     Optional(Sequence('ENCODED', 'BY', value))),
            Sequence('ENCODED', 'BY', value))

        # X.682: 10. Table constraints, including component relation constraints
        level = OneOrMore('.')
        component_id_list = identifier
        at_notation = Sequence('@',
                               choice(component_id_list,
                                      Sequence(level, component_id_list)))
        component_relation_constraint = Sequence('{',
                                                 defined_object_set,
                                                 '}',
                                                 '{',
                                                 DelimitedList(at_notation),
                                                 '}')
        simple_table_constraint = object_set
        table_constraint = choice(component_relation_constraint,
                                  simple_table_constraint)

        # X.682: 9. User-defined constants
        user_defined_constraint_parameter = choice(
            Sequence(governor,
                     ':',
                     choice(value,
                            value_set,
                            object_,
                            object_set)),
            type_,
            defined_object_class)
        user_defined_constraint = Sequence(
            'CONSTRAINED', 'BY',
            '{',
            Optional(DelimitedList(user_defined_constraint_parameter)),
            '}')

        # X.682: 8. General constraint specification
        general_constraint = choice(user_defined_constraint,
                                    table_constraint,
                                    contents_constraint)

        # X.681: 7. ASN.1 lexical items
        object_set_reference = type_reference
        value_set_field_reference = NoMatch()
        object_field_reference = NoMatch()
        object_set_field_reference = NoMatch()
        object_class_reference = type_reference
        object_reference = value_reference

        # X.681: 8. Referencing definitions
        external_object_set_reference = NoMatch()
        defined_object_set <<= choice(external_object_set_reference,
                                      object_set_reference)
        defined_object <<= NoMatch()
        defined_object_class <<= object_class_reference

        # X.681: 9. Information object class definition and assignment
        field_name = primitive_field_name
        primitive_field_name <<= choice(type_field_reference,
                                        value_field_reference,
                                        value_set_field_reference,
                                        object_field_reference,
                                        object_set_field_reference)
        object_set_field_spec = NoMatch()
        object_field_spec = NoMatch()
        variable_type_value_set_field_spec = NoMatch()
        fixed_type_value_set_field_spec = NoMatch()
        variable_type_value_field_spec = NoMatch()
        fixed_type_value_field_spec = Sequence(
            value_field_reference,
            type_,
            Optional('UNIQUE'),
            Optional(choice('OPTIONAL',
                            Sequence('DEFAULT', value))))
        type_field_spec = Sequence(
            type_field_reference,
            Optional(choice('OPTIONAL',
                            Sequence('DEFAULT', type_))))
        field_spec = choice(type_field_spec,
                            fixed_type_value_field_spec,
                            variable_type_value_field_spec,
                            fixed_type_value_set_field_spec,
                            variable_type_value_set_field_spec,
                            object_field_spec,
                            object_set_field_spec)
        with_syntax_spec = Sequence('WITH', 'SYNTAX', syntax_list)
        object_class_defn = Sequence('CLASS',
                                     '{',
                                     DelimitedList(field_spec),
                                     '}',
                                     Optional(with_syntax_spec))
        object_class = choice(object_class_defn,
                              # defined_object_class,
                              parameterized_object_class)
        parameterized_object_class_assignment = Sequence(
            object_class_reference,
            parameter_list,
            '::=',
            object_class)

        # X.681: 10. Syntax list
        literal = choice(word, ',')
        required_token = choice(literal, primitive_field_name)
        optional_group = Sequence('[',
                                  OneOrMore(token_or_group_spec),
                                  ']')
        token_or_group_spec <<= choice(required_token, optional_group)
        syntax_list <<= Sequence('{',
                                 OneOrMore(token_or_group_spec),
                                 '}')

        # X.681: 11. Information object definition and assignment
        setting = choice(type_, value, value_set, object_, object_set, 'CSTRING')
        field_setting = Sequence(primitive_field_name, setting)
        default_syntax = Sequence('{',
                                  DelimitedList(field_setting),
                                  '}')
        defined_syntax = NoMatch()
        object_defn = choice(default_syntax, defined_syntax)
        object_ <<= choice(defined_object,
                           object_defn,
                           object_from_object,
                           parameterized_object)
        parameterized_object_assignment = Sequence(object_reference,
                                                   parameter_list,
                                                   defined_object_class,
                                                   '::=',
                                                   object_)

        # X.681: 12. Information object set definition and assignment
        object_set_elements = choice(object_,
                                     defined_object_set,
                                     object_set_from_objects,
                                     parameterized_object_set)
        object_set_spec = choice(
            Sequence(
                root_element_set_spec,
                Optional(
                    Sequence(',', '...',
                             Optional(
                                 Sequence(',',
                                          additional_element_set_spec))))),
            Sequence('...',
                     Optional(Sequence(',',
                                       additional_element_set_spec))))
        object_set <<= Sequence('{', object_set_spec, '}')
        parameterized_object_set_assignment = Sequence(
            object_set_reference,
            parameter_list,
            defined_object_class,
            '::=',
            object_set)

        # X.681: 13. Associated tables

        # X.681: 14. Notation for the object class field type
        fixed_type_field_val = choice(builtin_value, referenced_value)
        open_type_field_val = Sequence(type_, ':', value)
        object_class_field_value = choice(open_type_field_val,
                                          fixed_type_field_val)
        object_class_field_type = Sequence(defined_object_class,
                                           '.',
                                           field_name)

        # X.681: 15. Information from objects
        object_set_from_objects <<= NoMatch()
        object_from_object <<= NoMatch()

        # X.680: 49. The exception identifier
        exception_identification = choice(signed_number,
                                          defined_value,
                                          Sequence(type_, ":", value))
        exception_spec = Optional(Sequence('!', exception_identification))

        # X.680: 47. Subtype elements
        pattern_constraint = Tag('PatternConstraint',
                                 Sequence('PATTERN', value))
        presence_constraint = Optional(choice('PRESENT', 'ABSENT', 'OPTIONAL'))
        value_constraint = Optional(constraint)
        component_constraint = Sequence(value_constraint, presence_constraint)
        named_constraint = Sequence(identifier, component_constraint)
        type_constraints = DelimitedList(named_constraint)
        partial_specification = Tag('PartialSpecification',
                                    Sequence('{', '...', ',', type_constraints, '}'))
        full_specification = Tag('FullSpecification',
                                 Sequence('{', type_constraints, '}'))
        multiple_type_constraints = Tag('MultipleTypeConstraints',
                                        choice(full_specification,
                                               partial_specification))
        single_type_constraint = Tag('SingleTypeConstraint', constraint)
        inner_type_constraints = Tag(
            'InnerTypeConstraint',
            choice(Sequence('WITH', 'COMPONENT', single_type_constraint),
                   Sequence('WITH', 'COMPONENTS', multiple_type_constraints)))
        permitted_alphabet = Tag('PermittedAlphabet',
                                 Sequence('FROM', constraint))
        type_constraint = Tag('TypeConstraint', type_)
        size_constraint = Tag('SizeConstraint', Sequence('SIZE', constraint))
        lower_end_value = choice(value, 'MIN')
        upper_end_value = choice(value, 'MAX')
        lower_endpoint = Sequence(lower_end_value, Optional('<'))
        upper_endpoint = Sequence(Optional('<'), upper_end_value)
        value_range = Tag('ValueRange',
                          Sequence(lower_endpoint, '..', upper_endpoint))
        includes = Optional('INCLUDES')
        contained_subtype = Tag('ContainedSubtype', Sequence(includes, type_))
        single_value = Tag('SingleValue', value)
        subtype_elements = choice(size_constraint,
                                  permitted_alphabet,
                                  value_range,
                                  inner_type_constraints,
                                  single_value,
                                  pattern_constraint,
                                  contained_subtype,
                                  type_constraint)

        # X.680: 46. Element set specification
        elements = choice(subtype_elements,
                          object_set_elements,
                          Tag('ElementSetSpec',
                              Sequence('(', element_set_spec, ')')))
        intersection_mark = choice('^', 'INTERSECTION')
        union_mark = choice('|', 'UNION')
        exclusions = Sequence('EXCEPT', elements)
        intersection_elements = Sequence(elements, Optional(exclusions))
        intersections <<= choice(intersection_elements,
                                 Sequence(intersections,
                                          intersection_mark,
                                          intersection_elements))
        unions <<= DelimitedList(elements, delim=choice(union_mark,
                                                        intersection_mark))
        element_set_spec <<= choice(unions, Sequence('ALL', exclusions))
        additional_element_set_spec <<= element_set_spec
        root_element_set_spec <<= element_set_spec
        element_set_specs = Sequence(
            root_element_set_spec,
            Optional(Sequence(',', '...',
                              Optional(
                                  Sequence(',', additional_element_set_spec)))))

        # X.680: 45. Constrained types
        subtype_constraint = element_set_specs
        constraint_spec = choice(subtype_constraint, general_constraint)
        constraint <<= Tag('Constraint',
                           Sequence('(', constraint_spec, exception_spec, ')'))
        type_with_constraint = Tag('TypeWithConstraint',
                                   Sequence(choice('SET', 'SEQUENCE'),
                                            choice(constraint, size_constraint),
                                            'OF',
                                            choice(type_, named_type)))

        # X.680: 40. Definition of unrestricted character string types
        unrestricted_character_string_type = Sequence('CHARACTER', 'STRING')
        unrestricted_character_string_value = NoMatch()

        # X.680: 39. Canonical order of characters

        # X.680: 38. Specification of the ASN.1 module "ASN.1-CHARACTER-MODULE"

        # X.680: 37. Definition of restricted character string types
        group = number
        plane = number
        row = number
        cell = number
        quadruple = Sequence('{',
                             group, ',',
                             plane, ',',
                             row, ',',
                             cell,
                             '}')
        table_column = number
        table_row = number
        tuple_ = Sequence('{', table_column, ',', table_row, '}')
        chars_defn = choice('CSTRING', quadruple, tuple_, defined_value)
        charsyms = DelimitedList(chars_defn)
        character_string_list = Sequence('{', charsyms, '}')
        restricted_character_string_value = Tag('RestrictedCharacterStringValue',
                                                choice('CSTRING',
                                                       character_string_list,
                                                       quadruple,
                                                       tuple_))
        restricted_character_string_type = choice('BMPString',
                                                  'GeneralString',
                                                  'GraphicString',
                                                  'IA5String',
                                                  'ISO646String',
                                                  'NumericString',
                                                  'PrintableString',
                                                  'TeletexString',
                                                  'UTCTime',
                                                  'GeneralizedTime',
                                                  'T61String',
                                                  'UniversalString',
                                                  'UTF8String',
                                                  'VideotexString',
                                                  'VisibleString')

        # X.680: 36. Notation for character string types
        character_string_value = choice(restricted_character_string_value,
                                        unrestricted_character_string_value)
        character_string_type = Tag('CharacterStringType',
                                    choice(restricted_character_string_type,
                                           unrestricted_character_string_type))

        # X.680: 35. The character string types

        # X.680: 34. Notation for the external type
        # external_value = sequence_value

        # X.680: 33. Notation for embedded-pdv type
        # embedded_pdv_value = sequence_value

        # X.680: 32. Notation for relative object identifier type
        relative_oid_components = choice(number_form,
                                         name_and_number_form,
                                         defined_value)
        relative_oid_component_list = OneOrMore(relative_oid_components)
        relative_oid_value = Sequence('{',
                                      relative_oid_component_list,
                                      '}')

        # X.680: 31. Notation for object identifier type
        name_and_number_form <<= Sequence(identifier,
                                          '(',
                                          number_form,
                                          ')')
        number_form <<= choice(number, defined_value)
        name_form = identifier
        obj_id_components = choice(name_and_number_form,
                                   defined_value,
                                   number_form,
                                   name_form)
        obj_id_components_list = OneOrMore(obj_id_components)
        object_identifier_value = choice(
            Sequence('{', obj_id_components_list, '}'),
            Sequence('{', defined_value, obj_id_components_list, '}'))
        object_identifier_type = Tag('ObjectIdentifierType',
                                     Sequence('OBJECT', 'IDENTIFIER'))

        # X.680: 30. Notation for tagged types
        # tagged_value = NoMatch()

        # X.680: 29. Notation for selection types

        # X.680: 28. Notation for the choice types
        alternative_type_list = DelimitedList(named_type)
        extension_addition_alternatives_group = Sequence('[[',
                                                         version_number,
                                                         alternative_type_list,
                                                         ']]')
        extension_addition_alternative = choice(extension_addition_alternatives_group,
                                                named_type)
        extension_addition_alternatives_list = DelimitedList(extension_addition_alternative)
        extension_addition_alternatives = Optional(
            Sequence(',', extension_addition_alternatives_list))
        root_alternative_type_list = alternative_type_list
        alternative_type_lists = Sequence(
            root_alternative_type_list,
            Optional(Sequence(',',
                              extension_and_exception,
                              extension_addition_alternatives,
                              optional_extension_marker)))
        choice_type = Tag('ChoiceType',
                          Sequence('CHOICE',
                                   '{',
                                   alternative_type_lists,
                                   '}'))
        choice_value = Sequence(identifier, ':', value)

        # X.680: 27. Notation for the set-of types
        set_of_type = Tag('SetOfType',
                          Sequence('SET', 'OF', choice(type_, named_type)))

        # X.680: 26. Notation for the set types
        # set_value = NoMatch()
        set_type = Tag('SetType',
                       Sequence(
                           'SET',
                           '{',
                           Optional(choice(component_type_lists,
                                           Sequence(extension_and_exception,
                                                    optional_extension_marker))),
                           '}'))

        # X.680: 25. Notation for the sequence-of types
        sequence_of_value = NoMatch()
        sequence_of_type = Tag('SequenceOfType',
                               Sequence('SEQUENCE', 'OF',
                                        choice(type_, named_type)))

        # X.680: 24. Notation for the sequence types
        component_value_list = DelimitedList(named_value)
        sequence_value = Sequence('{',
                                  Optional(component_value_list),
                                  '}')
        component_type = choice(
            Sequence(named_type,
                     Optional(choice('OPTIONAL',
                                     Sequence('DEFAULT', value)))),
            Sequence('COMPONENTS', 'OF', type_))
        version_number <<= Optional(Sequence(number, ':'))
        extension_addition_group = Sequence('[[',
                                            version_number,
                                            DelimitedList(component_type),
                                            ']]')
        extension_and_exception <<= Sequence('...', Optional(exception_spec))
        extension_addition = choice(component_type, extension_addition_group)
        extension_addition_list = DelimitedList(extension_addition)
        extension_additions = Optional(Sequence(',', extension_addition_list))
        extension_end_marker = Sequence(',', '...')
        optional_extension_marker <<= Optional(Sequence(',', '...'))
        component_type_list = DelimitedList(component_type)
        root_component_type_list = component_type_list
        component_type_lists <<= choice(
            Sequence(root_component_type_list,
                     Optional(Sequence(',',
                                       extension_and_exception,
                                       extension_additions,
                                       choice(Sequence(extension_end_marker,
                                                       ',',
                                                       root_component_type_list),
                                              optional_extension_marker)))),
            Sequence(extension_and_exception,
                     extension_additions,
                     choice(Sequence(extension_end_marker,
                                     ',',
                                     root_component_type_list),
                            optional_extension_marker)))
        sequence_type = Tag('SequenceType',
                            Sequence('SEQUENCE',
                                     '{',
                                     Optional(choice(component_type_lists,
                                                     Sequence(extension_and_exception,
                                                              optional_extension_marker))),
                                     '}'))

        # X.680: 23. Notation for the null type
        null_value = 'NULL'
        null_type = Tag('NullType', 'NULL')

        # X.680: 22. Notation for the octetstring type
        # octet_string_value = choice('BSTRING',
        #                       'HSTRING',
        #                       Sequence('CONTAINING', value))
        octet_string_type = Tag('OctetStringType',
                                Sequence('OCTET', 'STRING'))

        # X.680: 21. Notation for the bitstring type
        bit_string_value = Tag('BitStringValue',
                               choice('BSTRING',
                                      'HSTRING',
                                      Sequence('{',
                                               Optional(DelimitedList(identifier)),
                                               '}')))
        named_bit = Sequence('IDENT', '(', choice(number, defined_value), ')')
        bit_string_type = Tag('BitStringType',
                              Sequence('BIT', 'STRING',
                                       Optional(Sequence('{',
                                                         DelimitedList(named_bit),
                                                         '}'))))

        tag = Sequence('[',
                       Optional(choice('UNIVERSAL', 'APPLICATION', 'PRIVATE')),
                       number,
                       ']')
        tagged_type = Tag('TaggedType',
                          Sequence(tag,
                                   Optional(choice('IMPLICIT', 'EXPLICIT')),
                                   type_))

        # X.680: 20. Notation for the real type
        special_real_value = choice('PLUS-INFINITY', 'MINUS-INFINITY')
        numeric_real_value = choice(real_number, sequence_value)
        real_value = Tag('RealValue',
                         choice(numeric_real_value, special_real_value))
        real_type = Tag('RealType', 'REAL')

        # X.680: 19. Notation for the enumerated type
        enumerated_value = identifier
        enumeration_item = choice(named_number, identifier)
        enumeration = DelimitedList(enumeration_item)
        root_enumeration = enumeration
        additional_enumeration = enumeration
        enumerations = Sequence(
            root_enumeration,
            Optional(Sequence(',', '...', exception_spec,
                              Optional(
                                  Sequence(',', additional_enumeration)))))
        enumerated_type = Tag('EnumeratedType',
                              Sequence('ENUMERATED', '{', enumerations, '}'))

        # X.680: 18. Notation for the integer type
        integer_value = Tag('IntegerValue', choice(signed_number, identifier))
        signed_number <<= number
        named_number <<= Sequence(identifier,
                                  '(',
                                  choice(signed_number, defined_value),
                                  ')')
        integer_type = Tag('IntegerType',
                           Sequence('INTEGER',
                                    Optional(Sequence('{',
                                                      DelimitedList(named_number),
                                                      '}'))))

        # X.680: 17. Notation for the boolean type
        boolean_value = Tag('BooleanValue', choice('TRUE', 'FALSE'))
        boolean_type = Tag('BooleanType', 'BOOLEAN')

        any_defined_by_type = Sequence('ANY', 'DEFINED', 'BY', value_reference)

        # X.680: 16. Definition of types and values
        named_value <<= Sequence(identifier, value)
        referenced_value <<= NoMatch()
        builtin_value <<= choice(bit_string_value,
                                 boolean_value,
                                 character_string_value,
                                 choice_value,
                                 relative_oid_value,
                                 sequence_value,
                                 enumerated_value,
                                 real_value,
                                 integer_value,
                                 null_value,
                                 object_identifier_value,
                                 sequence_of_value)
        value <<= choice(object_class_field_value)
        # ,
        # referenced_value,
        # builtin_value)
        builtin_type = choice(choice_type,
                              integer_type,
                              null_type,
                              bit_string_type,
                              octet_string_type,
                              enumerated_type,
                              boolean_type,
                              real_type,
                              character_string_type,
                              object_class_field_type,
                              sequence_type,
                              set_type,
                              sequence_of_type,
                              set_of_type,
                              object_identifier_type,
                              tagged_type,
                              any_defined_by_type,
                              'ANY',
                              'EXTERNAL')
        named_type <<= Sequence('IDENT', type_)
        referenced_type = Tag('ReferencedType', type_reference)
        type_ <<= choice(Sequence(choice(builtin_type, referenced_type),
                                  ZeroOrMore(constraint)),
                         type_with_constraint)

        # X.680: 15. Assigning types and values
        parameterized_value_assignment = Tag('ParameterizedValueAssignment',
                                             Sequence(value_reference,
                                                      type_,
                                                      '::=',
                                                      value))
        parameterized_type_assignment = Tag('ParameterizedTypeAssignment',
                                            Sequence(type_reference,
                                                     parameter_list,
                                                     '::=',
                                                     type_))

        # X.680: 14. Notation to support references to ASN.1 components

        # X.680: 13. Referencing type and value definitions
        external_value_reference <<= Sequence(module_reference,
                                              '.',
                                              value_reference)
        external_type_reference <<= Sequence(module_reference,
                                             '.',
                                             type_reference)
        defined_type <<= choice(external_type_reference,
                                parameterized_type,
                                parameterized_value_set_type,
                                type_reference)
        defined_value <<= choice(external_value_reference,
                                 parameterized_value,
                                 value_reference)

        # X.680: 12. Module definition
        assignment = choice(parameterized_object_set_assignment,
                            parameterized_object_assignment,
                            parameterized_object_class_assignment,
                            parameterized_type_assignment,
                            parameterized_value_assignment)
        assignment_list = ZeroOrMore(assignment)
        reference <<= choice(type_reference,
                             value_reference,
                             object_class_reference,
                             object_reference,
                             object_set_reference)
        symbol = choice(parameterized_reference,
                        reference)
        symbol_list = DelimitedList(symbol)
        assigned_identifier = Optional(choice(
            object_identifier_value,
            Sequence(defined_value, Not(choice(',', 'FROM')))))
        global_module_reference = Sequence(module_reference, assigned_identifier)
        symbols_from_module = Sequence(symbol_list,
                                       'FROM',
                                       global_module_reference)
        imports = Optional(Sequence('IMPORTS',
                                    ZeroOrMore(symbols_from_module),
                                    ';'))
        symbols_exported = Optional(symbol_list)
        exports = Optional(Sequence('EXPORTS',
                                    choice('ALL', symbols_exported),
                                    ';'))
        module_body = Sequence(exports, imports, assignment_list)
        extension_default = Optional(Sequence('EXTENSIBILITY', 'IMPLIED'))
        tag_default = Optional(
            Sequence(choice('EXPLICIT', 'IMPLICIT', 'AUTOMATIC'), 'TAGS'))
        definitive_name_and_number_form = Sequence(identifier,
                                                   '(',
                                                   definitive_number_form,
                                                   ')')
        definitive_number_form <<= number
        definitive_obj_id_component = choice(definitive_name_and_number_form,
                                             name_form,
                                             definitive_number_form)
        definitive_obj_id_components_list = OneOrMore(definitive_obj_id_component)
        definitive_identifier = Optional(Sequence(
            '{',
            definitive_obj_id_components_list,
            '}'))
        module_identifier = Sequence(module_reference, definitive_identifier)
        module_definition = Sequence(module_identifier,
                                     'DEFINITIONS',
                                     tag_default,
                                     extension_default,
                                     '::=',
                                     'BEGIN',
                                     module_body,
                                     'END')

        return OneOrMore(module_definition)


def integer(value):
    try:
        return int(value)
    except ValueError:
        if value.startswith('"'):
            value = value[1:-1]

        return value


class Transformer(object):

    def __init__(self):
        self._modules = None

    def transform(self, parse_tree):
        self._modules = {}

        for module_definition in parse_tree:
            _imports, assignment_list = module_definition[6][1:]
            types = {}
            values = {}

            for tag, assignment in assignment_list:
                if tag == 'ParameterizedTypeAssignment':
                    type_name = assignment[0].value
                    types[type_name] = self.transform_type(assignment[3])
                elif tag == 'ParameterizedValueAssignment':
                    pass
                else:
                    pass

            transformed = {
                'extensibility-implied': False,
                'imports': {},
                'object-classes': {},
                'object-sets': {},
                'types': types,
                'values': values
            }

            if module_definition[2]:
                transformed['tags'] = module_definition[2][0][0].value

            module_name = module_definition[0][0].value
            self._modules[module_name] = transformed

        return self._modules

    def transform_type(self, type_):
        tag = type_[0][0]

        try:
            return {
                'IntegerType': self.transform_integer_type,
                'BooleanType': self.transform_boolean_type,
                'SequenceType': self.transform_sequence_type,
                'SetType': self.transform_set_type,
                'SequenceOfType': self.transform_sequence_of_type,
                'SetOfType': self.transform_set_of_type,
                'CharacterStringType': self.transform_character_string_type,
                'TaggedType': self.transform_tagged_type,
                'ReferencedType': self.transform_referenced_type,
                'OctetStringType': self.transform_octet_string_type,
                'BitStringType': self.transform_bit_string_type,
                'RealType': self.transform_real_type,
                'NullType': self.transform_null_type,
                'ObjectIdentifierType': self.transform_object_identifier_type,
                'EnumeratedType': self.transform_enumerated_type,
                'ChoiceType': self.transform_choice_type,
                'ANY': self.transform_any_type
            }[tag](type_)
        except KeyError:
            raise NotImplementedError(tag)

    def transform_integer_type(self, type_):
        transformed = {
            'type': 'INTEGER'
        }

        if type_[1]:
            transformed.update(self.transform_constraint(type_[1][0]))

        return transformed

    def transform_boolean_type(self, type_):
        transformed = {
            'type': 'BOOLEAN'
        }

        if type_[1]:
            transformed.update(self.transform_constraint(type_[1][0]))

        return transformed

    def transform_sequence_type(self, type_):
        members = []
        type_members = type_[0][1][2]

        if type_members:
            for type_member in type_members[0][0]:
                name = type_member[0][0].value

                member = {
                    'name': name
                }

                member.update(self.transform_type(type_member[0][1]))

                if len(type_member[1]) > 0:
                    if isinstance(type_member[1][0], list):
                        member['default'] = self.transform_value(type_member[1][0][1])
                    else:
                        member['optional'] = True

                members.append(member)

            if type_members[0][1]:
                members.append(None)

                if type_members[0][1][0][2]:
                    pprint(type_members[0][1][0][2][0][1][0])

                if type_members[0][1][0][3]:
                    pprint(type_members[0][1][0][3])

        return {
            'type': 'SEQUENCE',
            'members': members
        }

    def transform_set_type(self, _type):
        return {
            'type': 'SET',
            'members': []
        }

    def transform_sequence_of_type(self, type_):
        return {
            'type': 'SEQUENCE OF',
            'element': self.transform_type(type_[0][1][2])
        }

    def transform_set_of_type(self, type_):
        return {
            'type': 'SET OF',
            'element': self.transform_type(type_[0][1][2])
        }

    def transform_character_string_type(self, type_):
        transformed = {
            'type': type_[0][1].value
        }

        if type_[1]:
            transformed.update(self.transform_constraint(type_[1][0]))

        return transformed

    def transform_bit_string_type(self, type_):
        transformed = {
            'type': 'BIT STRING'
        }

        if type_[0][1][2]:
            named_bits = []

            for item in type_[0][1][2][0][1]:
                named_bits.append((item[0].value, item[2].value))


            transformed['named-bits'] = named_bits

        if type_[1]:
            transformed.update(self.transform_constraint(type_[1][0]))

        return transformed

    def transform_real_type(self, type_):
        transformed = {
            'type': 'REAL'
        }

        if type_[1]:
            transformed.update(self.transform_constraint(type_[1][0]))

        return transformed

    def transform_null_type(self, _type):
        return {
            'type': 'NULL'
        }

    def transform_object_identifier_type(self, _type):
        return {
            'type': 'OBJECT IDENTIFIER'
        }

    def transform_enumerated_type(self, type_):
        def transform_values(values):
            return [
                (value[0].value, integer(value[2].value))
                for value in values
            ]


        values = []
        type_values = type_[0][1][2]

        if type_values:
            values += transform_values(type_values[0])

            if type_values[1]:
                values.append(None)
                values += transform_values(type_values[1][0][3][0][1])

        return {
            'type': 'ENUMERATED',
            'values': values
        }

    def transform_choice_type(self, type_):
        members = []

        if type_[0][1][2]:
            for type_member in type_[0][1][2][0]:
                name = type_member[0].value

                member = {
                    'name': name
                }

                member.update(self.transform_type(type_member[1]))
                members.append(member)

        return {
            'type': 'CHOICE',
            'members': members
        }

    def transform_any_type(self, _type):
        return {
            'type': 'ANY'
        }

    def transform_tag(self, tag, tag_kind):
        transformed = {
            'number': int(tag[2].value)
        }

        if tag[1]:
            transformed['class'] = tag[1][0].value

        if tag_kind:
            transformed['kind'] = tag_kind[0].value

        return transformed

    def transform_tagged_type(self, type_):
        tag, tag_kind, type_ = type_[0][1]
        transformed = self.transform_type(type_)

        if tag:
            transformed['tag'] = self.transform_tag(tag, tag_kind)

        return transformed

    def transform_referenced_type(self, type_):
        transformed = {
            'type': type_[0][1].value
        }

        if type_[1]:
            transformed.update(self.transform_constraint(type_[1][0]))

        return transformed

    def transform_octet_string_type(self, type_):
        transformed = {
            'type': 'OCTET STRING'
        }

        if type_[1]:
            transformed.update(self.transform_constraint(type_[1][0]))

        return transformed

    def transform_constraint(self, constraint):
        transformed = {}
        size = []
        restricted_to = []
        from_ = []
        with_components = None

        for item in constraint[1][1][0]:
            if item[0] == 'SizeConstraint':
                size += self.transform_size_constraint(item[1][1][1][1])
            elif item[0] == 'SingleValue':
                restricted_to.append(self.transform_value(item[1]))
            elif item[0] == 'PermittedAlphabet':
                item = item[1][1][1][1][0]

                for value in item:
                    if value[0] == 'ValueRange':
                        from_.append((self.transform_value(value[1][0][0]),
                                      self.transform_value(value[1][2][1])))
                    else:
                        raise NotImplementedError(value[0])
            elif item[0] == 'ValueRange':
                restricted_to.append((self.transform_value(item[1][0][0]),
                                      self.transform_value(item[1][2][1])))
            elif item[0] == 'ElementSetSpec':
                # ToDo
                pass
            elif item[0] == 'InnerTypeConstraint':
                with_components = self.transform_inner_type_constraint(item[1])
            elif item[0] == 'ContainedSubtype':
                pass
            else:
                raise NotImplementedError(item[0])

        if constraint[1][1][1]:
            restricted_to.append(None)

        if size:
            transformed['size'] = size

        if restricted_to:
            transformed['restricted-to'] = restricted_to

        if from_:
            transformed['from'] = from_

        if with_components:
            transformed['with-components'] = with_components

        return transformed

    def transform_inner_type_constraint(self, constraint):
        with_components = []
        tag, constraints = constraint[2]

        if tag == 'MultipleTypeConstraints':
            tag, constraints = constraints

            if tag == 'FullSpecification':
                for identifer, component_constraint in constraints[1]:
                    value_constraint, presence_constraint = component_constraint
                    components = [identifer.value]

                    if value_constraint:
                        value = self.transform_constraint(value_constraint[0])

                        if 'restricted-to' in value:
                            value = value['restricted-to'][0]
                        elif 'with-components' in value:
                            value = [value]

                        components.append(value)

                    if presence_constraint:
                        components.append(presence_constraint[0].value)

                    with_components.append(components)
            elif tag == 'PartialSpecification':
                with_components.append(None)

                for identifer, component_constraint in constraints[3]:
                    value_constraint, presence_constraint = component_constraint

                    if value_constraint:
                        raise NotImplementedError(value_constraint)

                    if presence_constraint:
                        with_components.append((identifer.value,
                                                presence_constraint[0].value))
            else:
                raise NotImplementedError(tag)
        else:
            raise NotImplementedError(tag)

        return with_components

    def transform_size_constraint(self, constraint):
        size = []

        for item in constraint[0]:
            if item[0] == 'SingleValue':
                size.append(self.transform_value(item[1]))
            elif item[0] == 'ValueRange':
                size.append((self.transform_value(item[1][0][0]),
                             self.transform_value(item[1][2][1])))
            else:
                raise NotImplementedError(constraint[0])

        return size

    def transform_value(self, value):
        if value[0] == 'IntegerValue':
            return int(value[1].value)
        elif value[0] == 'BooleanValue':
            return value[1].value
        elif value[0] == 'RestrictedCharacterStringValue':
            return value[1].value[1:-1]
        elif value[0] == 'RealValue':
            real = value[1][0].value + value[1][1].value

            if value[1][2]:
                real += value[1][2][0].value

            return real
        elif value[0] == 'BitStringValue':
            if isinstance(value[1], list):
                return [item.value for item in value[1][1][0]]
            elif value[1].kind == 'BSTRING':
                return '0b' + re.sub(r"[\sB']", '', value[1].value)
            elif value[1].kind == 'HSTRING':
                return '0x' + re.sub(r"[\sH']", '', value[1].value).lower()
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError(value[0])


class ParseError(Error):
    pass


def merge_dicts(dicts):
    return {k: v for d in dicts for k, v in d.items()}


def parse_string(string):
    """Parse given ASN.1 specification string and return a dictionary of
    its contents.

    The dictionary can later be compiled with
    :func:`~asn1tools.compile_dict()`.

    >>> with open('foo.asn') as fin:
    ...     foo = asn1tools.parse_string(fin.read())

    """

    try:
        parse_tree = Asn1Parser().parse(string, token_tree=True)
        modules = Transformer().transform(parse_tree)
    except ParseError as e:
        raise ParseError("Invalid ASN.1 syntax at line {}, column {}: '{}'.".format(
            e.line,
            e.column,
            markup_line(e.text, e.offset)))

    return modules


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
