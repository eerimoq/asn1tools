"""Unaligned Packed Encoding Rules (UPER) C source code codec generator.

"""
import textwrap

from .utils import ENCODER_AND_DECODER_STRUCTS
from .utils import Generator
from .utils import camel_to_snake_case
from .utils import is_user_type
from .utils import indent_lines
from .utils import dedent_lines
from .utils import canonical
from .uper_functions import functions
from ...codecs import uper


def does_bits_match_range(number_of_bits, minimum, maximum):
    return 2 ** number_of_bits == (maximum - minimum + 1)


class _Generator(Generator):

    def format_real(self):
        return []

    def get_enumerated_values(self, type_):
        return sorted([(canonical(data), value)
                       for data, value in type_.root_data_to_value.items()])

    def get_choice_members(self, type_):
        return type_.root_index_to_member.values()

    def format_default(self, type_):
        if isinstance(type_, uper.Boolean):
            return str(type_.default).lower()
        elif isinstance(type_, uper.Enumerated):
            return self.format_default_enumerated(type_)
        else:
            return str(type_.default)

    def format_type(self, type_, checker):
        if isinstance(type_, uper.Integer):
            return self.format_integer(checker)
        elif isinstance(type_, uper.Boolean):
            return self.format_boolean()
        elif isinstance(type_, uper.Real):
            return self.format_real()
        elif isinstance(type_, uper.Null):
            return []
        elif is_user_type(type_):
            return self.format_user_type(type_.type_name,
                                         type_.module_name)
        elif isinstance(type_, uper.OctetString):
            return self.format_octet_string(checker)
        elif isinstance(type_, uper.Sequence):
            return self.format_sequence(type_, checker)
        elif isinstance(type_, uper.Choice):
            return self.format_choice(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            return self.format_sequence_of(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            return self.format_enumerated(type_)
        elif isinstance(type_, uper.BitString):
            return self.format_bit_string(type_, checker)
        else:
            raise self.error(
                "Unsupported type '{}'.".format(type_.type_name))

    def generate_type_declaration_process(self, type_, checker):
        if isinstance(type_, uper.Integer):
            lines = self.format_integer(checker)
            lines[0] += ' value;'
        elif isinstance(type_, uper.Boolean):
            lines = self.format_boolean()
            lines[0] += ' value;'
        elif isinstance(type_, uper.Real):
            lines = self.format_real()
        elif isinstance(type_, uper.Enumerated):
            lines = self.format_enumerated(type_)
            lines[0] += ' value;'
        elif isinstance(type_, uper.Sequence):
            lines = self.format_sequence(type_, checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, uper.SequenceOf):
            lines = self.format_sequence_of(type_, checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, uper.Choice):
            lines = self.format_choice(type_, checker)
            lines = dedent_lines(lines[1:-1])
        elif isinstance(type_, uper.OctetString):
            lines = self.format_octet_string(checker)[1:-1]
            lines = dedent_lines(lines)
        elif isinstance(type_, uper.Null):
            lines = []
        else:
            raise self.error(
                "Unsupported type '{}'.".format(type_.type_name))

        return lines

    def generate_definition_inner_process(self, type_, checker):
        if isinstance(type_, uper.Integer):
            return self.format_integer_inner(type_, checker)
        elif isinstance(type_, uper.Boolean):
            return self.format_boolean_inner()
        elif isinstance(type_, uper.Real):
            return self.format_real_inner()
        elif isinstance(type_, uper.Sequence):
            return self.format_sequence_inner(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            return self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, uper.Choice):
            return self.format_choice_inner(type_, checker)
        elif isinstance(type_, uper.OctetString):
            return self.format_octet_string_inner(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            return self.format_enumerated_inner(type_)
        elif isinstance(type_, uper.Null):
            return self.format_null_inner()
        else:
            return [], []

    def format_integer_inner(self, type_, checker):
        type_name = self.format_type_name(checker.minimum, checker.maximum)
        suffix = type_name[:-2]
        location = self.location_inner()

        if type_.number_of_bits in [8, 16, 32, 64] and \
                checker.minimum in [0, -128, -32768, -2147483648, -9223372036854775808]:
            return (
                [
                    'encoder_append_{}(encoder_p, src_p->{});'.format(
                        suffix,
                        location)
                ],
                [
                    'dst_p->{} = decoder_read_{}(decoder_p);'.format(location,
                                                                     suffix)
                ]
            )
        else:
            return (
                [
                    'encoder_append_non_negative_binary_integer(',
                    '    encoder_p,',
                    '    (uint64_t)(src_p->{} - {}),'.format(location, checker.minimum),
                    '    {});'.format(type_.number_of_bits)
                ],
                [
                    'dst_p->{} = decoder_read_non_negative_binary_integer('.format(
                        location),
                    '    decoder_p,',
                    '    {});'.format(type_.number_of_bits),
                    'dst_p->{} += {};'.format(location, checker.minimum)
                ]
            )

    def format_bit_string_inner(self, type_):
        location = self.location_inner()

        return (
            [
                'encoder_append_non_negative_binary_integer(',
                '    encoder_p,',
                '    (uint64_t)(src_p->{}),'.format(location),
                '    {});'.format(type_.maximum)
            ],
            [
                'dst_p->{} = decoder_read_non_negative_binary_integer('.format(
                    location),
                '    decoder_p,',
                '    {});'.format(type_.maximum)
            ]
        )

    def format_boolean_inner(self):
        return (
            [
                'encoder_append_bool(encoder_p, src_p->{});'.format(
                    self.location_inner())
            ],
            [
                'dst_p->{} = decoder_read_bool(decoder_p);'.format(
                    self.location_inner())
            ]
        )

    def format_real_inner(self):
        return [], []

    def format_sequence_inner(self, type_, checker):
        encode_lines = []
        decode_lines = []
        member_name_to_is_present = {}

        if type_.additions is not None:

            if len(type_.additions) > 0:
                if_line = 'if({}) {{'.format(self.get_addition_present_condition(type_))
                encode_lines.extend(textwrap.wrap(if_line, 120,
                                                  subsequent_indent=' ' * len('if(')))
                encode_lines.append('    encoder_abort(encoder_p, EINVAL);')
                encode_lines.append('    return;')
                encode_lines.append('}')

            encode_lines.append('encoder_append_bool(encoder_p, false);')

            if len(type_.additions) > 0:
                unique_extension_present = \
                    self.add_unique_decode_variable('bool {};', 'extension_is_present')
                decode_lines.append(
                    'extension_is_present = decoder_read_bool(decoder_p);')
            else:
                decode_lines.append('decoder_read_bool(decoder_p);')

        for member in type_.root_members:

            if member.optional:
                name = '{}is_{}_present'.format(self.location_inner('', '.'),
                                                member.name)
                encode_lines.append(
                    'encoder_append_bool(encoder_p, src_p->{});'.format(
                        name))
                decode_lines.append(
                    'dst_p->{} = decoder_read_bool(decoder_p);'.format(
                        name))
            elif member.default is not None:
                unique_is_present = self.add_unique_decode_variable('bool {};',
                                                                    'is_present')
                member_name_to_is_present[member.name] = unique_is_present

                if self.is_buffer_type(member):
                    default_variable = member.name + '_default'

                    encode_lines += [
                        'encoder_append_bool(encoder_p, (memcmp(src_p->{}{}.buf, {}, sizeof({})) != 0) ||'.format(
                            self.location_inner('', '.'),
                            member.name,
                            default_variable,
                            default_variable),
                        '                               (src_p->{}{}.length != sizeof({})));'.format(
                            self.location_inner('', '.'),
                            member.name,
                            default_variable)
                    ]
                else:
                    encode_lines.append(
                        'encoder_append_bool(encoder_p, src_p->{}{}{} != {});'.format(
                            self.location_inner('', '.'),
                            member.name,
                            '.value' if self.is_complex_user_type(member) else '',
                            self.format_default(member)))
                decode_lines.append(
                    '{} = decoder_read_bool(decoder_p);'.format(
                        unique_is_present))

        for member in type_.root_members:
            (member_encode_lines,
             member_decode_lines) = self.format_sequence_inner_member(
                 member,
                 checker,
                 member_name_to_is_present)

            encode_lines += member_encode_lines
            decode_lines += member_decode_lines

        if type_.additions is not None and len(type_.additions) > 0:
            decode_lines.append('if({}) {{'.format(unique_extension_present))
            decode_lines.append('    decoder_abort(decoder_p, EINVAL);')
            decode_lines.append('    return;')
            decode_lines.append('}')

        return encode_lines, decode_lines

    def format_octet_string_inner(self, type_, checker):
        location = self.location_inner('', '.')

        if checker.minimum == checker.maximum:
            encode_lines = [
                'encoder_append_bytes(encoder_p,',
                '                     &src_p->{}buf[0],'.format(location),
                '                     {});'.format(checker.maximum)
            ]
            decode_lines = [
                'decoder_read_bytes(decoder_p,',
                '                   &dst_p->{}buf[0],'.format(location),
                '                   {});'.format(checker.maximum)
            ]
        else:
            encode_lines = [
                'encoder_append_non_negative_binary_integer(',
                '    encoder_p,',
                '    src_p->{}length - {}u,'.format(location, checker.minimum),
                '    {});'.format(type_.number_of_bits),
                'encoder_append_bytes(encoder_p,',
                '                     &src_p->{}buf[0],'.format(location),
                '                     src_p->{}length);'.format(location)
            ]
            decode_lines = [
                'dst_p->{}length = decoder_read_non_negative_binary_integer('.format(
                    location),
                '    decoder_p,',
                '    {});'.format(type_.number_of_bits),
                'dst_p->{}length += {}u;'.format(location, checker.minimum)
            ]

            if not does_bits_match_range(type_.number_of_bits,
                                         checker.minimum,
                                         checker.maximum):
                decode_lines += [
                    '',
                    'if (dst_p->{}length > {}u) {{'.format(location, checker.maximum),
                    '    decoder_abort(decoder_p, EBADLENGTH);',
                    '',
                    '    return;',
                    '}',
                    ''
                ]

            decode_lines += [
                'decoder_read_bytes(decoder_p,',
                '                   &dst_p->{}buf[0],'.format(location),
                '                   dst_p->{}length);'.format(location)
            ]

        return encode_lines, decode_lines

    def format_user_type_inner(self, type_name, module_name):
        module_name_snake = camel_to_snake_case(module_name)
        type_name_snake = camel_to_snake_case(type_name)
        prefix = '{}_{}_{}'.format(self.namespace,
                                   module_name_snake,
                                   type_name_snake)
        encode_lines = [
            '{}_encode_inner(encoder_p, &src_p->{});'.format(
                prefix,
                self.location_inner())
        ]
        decode_lines = [
            '{}_decode_inner(decoder_p, &dst_p->{});'.format(
                prefix,
                self.location_inner())
        ]

        return encode_lines, decode_lines

    def format_choice_inner(self, type_, checker):
        encode_lines = []
        decode_lines = []
        type_name = self.format_type_name(0, max(type_.root_index_to_member))
        unique_choice = self.add_unique_decode_variable(
            '{} {{}};'.format(type_name),
            'choice')
        choice = '{}choice'.format(self.location_inner('', '.'))

        for member in type_.root_index_to_member.values():
            member_checker = self.get_member_checker(checker,
                                                     member.name)

            with self.asn1_members_backtrace_push(member.name):
                with self.c_members_backtrace_push('value'):
                    with self.c_members_backtrace_push(member.name):
                        choice_encode_lines, choice_decode_lines = self.format_type_inner(
                            member,
                            member_checker)

            index = type_.root_name_to_index[member.name]

            choice_encode_lines = [
                'encoder_append_non_negative_binary_integer(encoder_p, {}, {});'.format(
                    index,
                    type_.root_number_of_bits)
            ] + choice_encode_lines + [
                'break;'
            ]
            encode_lines += [
                'case {}_choice_{}_e:'.format(self.location, member.name)
            ] + indent_lines(choice_encode_lines) + [
                ''
            ]

            choice_decode_lines = [
                'dst_p->{} = {}_choice_{}_e;'.format(choice,
                                                     self.location,
                                                     member.name)
            ] + choice_decode_lines + [
                'break;'
            ]
            decode_lines += [
                'case {}:'.format(index)
            ] + indent_lines(choice_decode_lines) + [
                ''
            ]

        encode_lines = [
            '',
            'switch (src_p->{}) {{'.format(choice),
            ''
        ] + encode_lines + [
            'default:',
            '    encoder_abort(encoder_p, EBADCHOICE);',
            '    break;',
            '}',
            ''
        ]

        decode_lines = [
            '{} = ({})decoder_read_non_negative_binary_integer(decoder_p, {});'.format(
                unique_choice,
                type_name,
                type_.root_number_of_bits),
            '',
            'switch ({}) {{'.format(unique_choice),
            ''
        ] + decode_lines + [
            'default:',
            '    decoder_abort(decoder_p, EBADCHOICE);',
            '    break;',
            '}',
            ''
        ]

        return encode_lines, decode_lines

    def format_enumerated_inner(self, type_):
        type_name = self.format_type_name(0, max(type_.root_data_to_value.values()))
        unique_value = self.add_unique_variable(
            '{} {{}};'.format(type_name),
            'value')
        location = self.location_inner()

        value_mapping_required = any([(type_.root_data_to_index[data]
                                       != type_.root_data_to_value[data])
                                      for data in type_.root_data_to_index])

        if value_mapping_required:
            encode_lines = ['switch (src_p->{}) {{'.format(location)]

            for data, _ in self.get_enumerated_values(type_):
                encode_lines += [
                    'case {}_{}_e:'.format(self.location, data),
                    '    {} = {};'.format(unique_value, type_.root_data_to_index[data]),
                    '    break;']

            encode_lines += [
                'default:',
                '    encoder_abort(encoder_p, EBADENUM);',
                '    return;',
                '}']
        else:
            encode_lines = ['{} = src_p->{};'.format(unique_value, location)]

        encode_lines.append('encoder_append_non_negative_binary_integer(encoder_p, '
                            '{}, {});'.format(unique_value, type_.root_number_of_bits))

        decode_lines = [
            '{} = decoder_read_non_negative_binary_integer('
            'decoder_p, {});'.format(unique_value,
                                     type_.root_number_of_bits)
        ]

        if bin(len(self.get_enumerated_values(type_))).count('1') != 1 and (not
           value_mapping_required):
            decode_lines += [
                '',
                'if ({} > {}u) {{'.format(unique_value,
                                          len(self.get_enumerated_values(type_)) - 1),
                '    decoder_abort(decoder_p, EBADENUM);',
                '',
                '    return;',
                '}',
                ''
            ]

        if value_mapping_required:
            decode_lines.append('switch ({}) {{'.format(unique_value))

            for data, _ in self.get_enumerated_values(type_):
                decode_lines.append('case {}:'.format(type_.root_data_to_index[data]))
                decode_lines.append('    dst_p->{} = {}_{}_e;'.format(location,
                                                                      self.location,
                                                                      data))
                decode_lines.append('    break;')
            decode_lines += [
                'default:',
                '    decoder_abort(decoder_p, EBADENUM);',
                '    return;',
                '}']
        else:
            decode_lines += [
                'dst_p->{} = (enum {}_e){};'.format(location,
                                                    self.location,
                                                    unique_value)
            ]

        return encode_lines, decode_lines

    def format_null_inner(self):
        return (
            [
                '(void)encoder_p;',
                '(void)src_p;'
            ],
            [
                '(void)decoder_p;',
                '(void)dst_p;'
            ]
        )

    def format_sequence_of_inner(self, type_, checker):
        type_name = self.format_type_name(0, checker.maximum)
        unique_i = self.add_unique_variable('{} {{}};'.format(type_name),
                                            'i')

        with self.c_members_backtrace_push('elements[{}]'.format(unique_i)):
            encode_lines, decode_lines = self.format_type_inner(
                type_.element_type,
                checker.element_type)

        if checker.minimum == checker.maximum:
            first_encode_lines = first_decode_lines = [
                '',
                'for ({0} = 0; {0} < {1}; {0}++) {{'.format(
                    unique_i,
                    checker.maximum)
            ]
        else:
            location = self.location_inner('', '.')
            first_encode_lines = [
                'encoder_append_non_negative_binary_integer(',
                '    encoder_p,',
                '    src_p->{}length - {}u,'.format(location, checker.minimum),
                '    {});'.format(type_.number_of_bits),
                '',
                'for ({0} = 0; {0} < src_p->{1}length; {0}++) {{'.format(
                    unique_i,
                    location)
            ]
            first_decode_lines = [
                'dst_p->{}length = decoder_read_non_negative_binary_integer('.format(
                    location),
                '    decoder_p,',
                '    {});'.format(type_.number_of_bits),
                'dst_p->{}length += {}u;'.format(location, checker.minimum),
                ''
            ]

            if not does_bits_match_range(type_.number_of_bits,
                                         checker.minimum,
                                         checker.maximum):
                first_decode_lines += [
                    'if (dst_p->{}length > {}u) {{'.format(location, checker.maximum),
                    '    decoder_abort(decoder_p, EBADLENGTH);',
                    '',
                    '    return;',
                    '}',
                    ''
                ]

            first_decode_lines += [
                'for ({0} = 0; {0} < dst_p->{1}length; {0}++) {{'.format(
                    unique_i,
                    location)
            ]

        encode_lines = first_encode_lines + indent_lines(encode_lines) + ['}', '']
        decode_lines = first_decode_lines + indent_lines(decode_lines) + ['}', '']

        return encode_lines, decode_lines

    def format_type_inner(self, type_, checker):
        if isinstance(type_, uper.Integer):
            return self.format_integer_inner(type_, checker)
        elif isinstance(type_, uper.Real):
            return self.format_real_inner()
        elif isinstance(type_, uper.Null):
            return [], []
        elif isinstance(type_, uper.Boolean):
            return self.format_boolean_inner()
        elif is_user_type(type_):
            return self.format_user_type_inner(type_.type_name,
                                               type_.module_name)
        elif isinstance(type_, uper.OctetString):
            return self.format_octet_string_inner(type_, checker)
        elif isinstance(type_, uper.Sequence):
            return self.format_sequence_inner(type_, checker)
        elif isinstance(type_, uper.Choice):
            return self.format_choice_inner(type_, checker)
        elif isinstance(type_, uper.SequenceOf):
            return self.format_sequence_of_inner(type_, checker)
        elif isinstance(type_, uper.Enumerated):
            return self.format_enumerated_inner(type_)
        elif isinstance(type_, uper.BitString):
            return self.format_bit_string_inner(type_)
        else:
            raise self.error(type_)

    def is_complex_user_type(self, type_):
        return is_user_type(type_) and \
            not isinstance(type_, (uper.Integer, uper.Boolean, uper.Real, uper.Null))

    def is_buffer_type(self, type_):
        return isinstance(type_, uper.OctetString)

    def generate_helpers(self, definitions):
        helpers = []

        for pattern, definition in functions:
            is_in_helpers = any([pattern in helper for helper in helpers])

            if pattern in definitions or is_in_helpers:
                helpers.insert(0, definition)

        return [ENCODER_AND_DECODER_STRUCTS] + helpers + ['']


def generate(compiled, namespace):
    return _Generator(namespace).generate(compiled)
