import re
from operator import itemgetter

from ...errors import Error


TYPE_DECLARATION_FMT = '''\
/**
 * Type {type_name} in module {module_name}.
 */
{helper_types}\
struct {namespace}_{module_name_snake}_{type_name_snake}_t {{
{members}
}};
'''

DECLARATION_FMT = '''\
/**
 * Encode type {type_name} defined in module {module_name}.
 *
 * @param[out] dst_p Buffer to encode into.
 * @param[in] size Size of dst_p.
 * @param[in] src_p Data to encode.
 *
 * @return Encoded data length or negative error code.
 */
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_encode(
    uint8_t *dst_p,
    size_t size,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p);

/**
 * Decode type {type_name} defined in module {module_name}.
 *
 * @param[out] dst_p Decoded data.
 * @param[in] src_p Data to decode.
 * @param[in] size Size of src_p.
 *
 * @return Number of bytes decoded or negative error code.
 */
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_decode(
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p,
    const uint8_t *src_p,
    size_t size);
'''

DEFINITION_INNER_FMT = '''\
static void {namespace}_{module_name_snake}_{type_name_snake}_encode_inner(
    struct encoder_t *encoder_p,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p)
{{
{encode_body}\
}}

static void {namespace}_{module_name_snake}_{type_name_snake}_decode_inner(
    struct decoder_t *decoder_p,
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p)
{{
{decode_body}\
}}
'''

DEFINITION_FMT = '''\
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_encode(
    uint8_t *dst_p,
    size_t size,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p)
{{
    struct encoder_t encoder;

    encoder_init(&encoder, dst_p, size);
    {namespace}_{module_name_snake}_{type_name_snake}_encode_inner(&encoder, src_p);

    return (encoder_get_result(&encoder));
}}

ssize_t {namespace}_{module_name_snake}_{type_name_snake}_decode(
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p,
    const uint8_t *src_p,
    size_t size)
{{
    struct decoder_t decoder;

    decoder_init(&decoder, src_p, size);
    {namespace}_{module_name_snake}_{type_name_snake}_decode_inner(&decoder, dst_p);

    return (decoder_get_result(&decoder));
}}
'''

ENCODER_AND_DECODER_STRUCTS = '''\
struct encoder_t {
    uint8_t *buf_p;
    ssize_t size;
    ssize_t pos;
};

struct decoder_t {
    const uint8_t *buf_p;
    ssize_t size;
    ssize_t pos;
};
'''

ENCODER_ABORT = '''
static void encoder_abort(struct encoder_t *self_p,
                          ssize_t error)
{
    if (self_p->size >= 0) {
        self_p->size = -error;
        self_p->pos = -error;
    }
}\
'''

DECODER_ABORT = '''
static void decoder_abort(struct decoder_t *self_p,
                          ssize_t error)
{
    if (self_p->size >= 0) {
        self_p->size = -error;
        self_p->pos = -error;
    }
}\
'''


class _MembersBacktracesContext(object):

    def __init__(self, backtraces, member_name):
        self.backtraces = backtraces
        self.member_name = member_name

    def __enter__(self):
        for backtrace in self.backtraces:
            backtrace.append(self.member_name)

    def __exit__(self, *args):
        for backtrace in self.backtraces:
            backtrace.pop()


class _UserType(object):

    def __init__(self,
                 type_name,
                 module_name,
                 type_declaration,
                 declaration,
                 definition_inner,
                 definition):
        self.type_name = type_name
        self.module_name = module_name
        self.type_declaration = type_declaration
        self.declaration = declaration
        self.definition_inner = definition_inner
        self.definition = definition


class Generator(object):

    def __init__(self, namespace):
        self.namespace = canonical(namespace)
        self.asn1_members_backtrace = []
        self.c_members_backtrace = []
        self.module_name = None
        self.type_name = None
        self.helper_lines = []
        self.base_variables = set()
        self.used_suffixes_by_base_variables = {}
        self.encode_variable_lines = []
        self.decode_variable_lines = []
        self.used_user_types = []

    def reset_type(self):
        self.helper_lines = []
        self.base_variables = set()
        self.used_suffixes_by_base_variables = {}
        self.encode_variable_lines = []
        self.decode_variable_lines = []
        self.used_user_types = []

    @property
    def module_name_snake(self):
        return camel_to_snake_case(self.module_name)

    @property
    def type_name_snake(self):
        return camel_to_snake_case(self.type_name)

    def type_length(self, minimum, maximum):
        # Make sure it fits in 64 bits.
        if minimum < -9223372036854775808:
            raise self.error(
                '{} does not fit in int64_t.'.format(minimum))
        elif maximum > 18446744073709551615:
            raise self.error(
                '{} does not fit in uint64_t.'.format(maximum))
        elif minimum < 0 and maximum > 9223372036854775807:
            raise self.error(
                '{} does not fit in int64_t.'.format(maximum))

        # Calculate the number of bytes needed.
        if minimum < -2147483648:
            minimum_length = 64
        elif minimum < -32768:
            minimum_length = 32
        elif minimum < -128:
            minimum_length = 16
        elif minimum < 0:
            minimum_length = 8
        else:
            minimum_length = 0

        if maximum > 4294967295:
            maximum_length = 64
        elif maximum > 65535:
            maximum_length = 32
        elif maximum > 255:
            maximum_length = 16
        elif maximum > 0:
            maximum_length = 8
        else:
            maximum_length = 0

        if minimum_length == maximum_length == 0:
            length = 8
        else:
            length = max(minimum_length, maximum_length)

        return length

    @staticmethod
    def value_length(value):
        if value < 256:
            length = 1
        elif value < 65536:
            length = 2
        elif value < 16777216:
            length = 3
        elif value < 4294967296:
            length = 4
        else:
            length = 8
        return length

    def format_type_name(self, minimum, maximum):
        length = self.type_length(minimum, maximum)
        type_name = 'int{}_t'.format(length)

        if minimum >= 0:
            type_name = 'u' + type_name

        return type_name

    def format_default_enumerated(self, type_):
        if is_user_type(type_):
            return '{}_{}_e'.format(self.get_user_type_prefix(type_.type_name,
                                                              type_.module_name),
                                    type_.default)
        else:
            with self.members_backtrace_push(type_.name):
                return '{}_{}_e'.format(self.location, type_.default)

    def get_addition_present_condition(self, type_):
        return ' || '.join(['src_p->{}is_{}_addition_present'.
                            format(self.location_inner('', '.'), addition.name)
                            for addition in type_.additions])

    def get_named_number_values(self, type_):
        if type_.named_bits is not None:
            return sorted([(canonical(data), value)
                           for data, value in type_.named_bits],
                          key=itemgetter(1))

    def get_user_type_prefix(self, type_name, module_name):
        module_name_snake = camel_to_snake_case(module_name)
        type_name_snake = camel_to_snake_case(type_name)

        return '{}_{}_{}'.format(self.namespace,
                                 module_name_snake,
                                 type_name_snake)

    @property
    def location(self):
        location = '{}_{}_{}'.format(self.namespace,
                                     self.module_name_snake,
                                     self.type_name_snake)

        if self.asn1_members_backtrace:
            location += '_{}'.format('_'.join(self.asn1_members_backtrace))

        return location

    def location_inner(self, default='value', end=''):
        if self.c_members_backtrace:
            return '.'.join(self.c_members_backtrace) + end
        else:
            return default

    def location_error(self):
        location = '{}.{}'.format(self.module_name, self.type_name)

        if self.asn1_members_backtrace:
            location += '.{}'.format('.'.join(self.asn1_members_backtrace))

        return location

    def members_backtrace_push(self, member_name):
        backtraces = [
            self.asn1_members_backtrace,
            self.c_members_backtrace
        ]

        return _MembersBacktracesContext(backtraces, member_name)

    def asn1_members_backtrace_push(self, member_name):
        backtraces = [self.asn1_members_backtrace]

        return _MembersBacktracesContext(backtraces, member_name)

    def c_members_backtrace_push(self, member_name):
        backtraces = [self.c_members_backtrace]

        return _MembersBacktracesContext(backtraces, member_name)

    def get_member_checker(self, checker, name):
        for member in checker.members:
            if member.name == name:
                return member

        raise Error('No member checker found for {}.'.format(name))

    def add_unique_variable(self, fmt, name, variable_lines=None):
        if name in self.base_variables:
            try:
                suffix = self.used_suffixes_by_base_variables[name]
                suffix += 1
            except KeyError:
                suffix = 2

            self.used_suffixes_by_base_variables[name] = suffix
            unique_name = '{}_{}'.format(name, suffix)
        else:
            self.base_variables.add(name)
            unique_name = name

        line = fmt.format(unique_name)

        if variable_lines is None:
            self.encode_variable_lines.append(line)
            self.decode_variable_lines.append(line)
        elif variable_lines == 'encode':
            self.encode_variable_lines.append(line)
        else:
            self.decode_variable_lines.append(line)

        return unique_name

    def add_unique_encode_variable(self, fmt, name):
        return self.add_unique_variable(fmt, name, 'encode')

    def add_unique_decode_variable(self, fmt, name):
        return self.add_unique_variable(fmt, name, 'decode')

    def add_sequence_member(self, member, checker):
        member_checker = self.get_member_checker(checker, member.name)

        with self.members_backtrace_push(canonical(member.name)):
            member_lines = self.format_type(member, member_checker)

        if member_lines:
            member_lines[-1] += ' {};'.format(canonical(member.name))

        return member_lines

    def error(self, message):
        return Error('{}: {}'.format(self.location_error(), message))

    def format_integer(self, checker):
        if not checker.has_lower_bound():
            raise self.error('INTEGER has no minimum value.')

        if not checker.has_upper_bound():
            raise self.error('INTEGER has no maximum value.')

        type_name = self.format_type_name(checker.minimum, checker.maximum)

        return [type_name]

    def format_boolean(self):
        return ['bool']

    def format_octet_string(self, checker):
        if not checker.has_upper_bound():
            raise self.error('OCTET STRING has no maximum length.')

        if checker.minimum == checker.maximum:
            lines = []
        elif checker.maximum < 256:
            lines = ['    uint8_t length;']
        else:
            lines = ['    uint32_t length;']

        return [
            'struct {'
        ] + lines + [
            '    uint8_t buf[{}];'.format(checker.maximum),
            '}'
        ]

    def format_bit_string(self, type_, checker):
        def get_value(value):
            byte = (length - 1) - (value // 8)
            bit = 7 - (value % 8)
            return ('0x{:0' + str(length // 4) + 'x}').format(1 << (bit + byte * 8))

        if checker.minimum != checker.maximum:
            raise self.error('BIT STRING with variable SIZE not supported.')
        if checker.minimum > 64:
            raise self.error('BIT STRING with a length of more than 64 bits are not '
                             'supported.')

        max_value = 2**checker.minimum - 1

        length = self.value_length(max_value)
        named_bits = self.get_named_number_values(type_)
        type_name = self.format_type_name(max_value, max_value)

        if named_bits is not None:
            self.helper_lines += [
                'static const {} {}_{} = {};'.format(type_name, self.location.upper(),
                                                     name.upper(), get_value(value))
                for name, value in self.get_named_number_values(type_)
            ]

        return [type_name]

    def format_sequence(self, type_, checker):
        lines = []

        for member in type_.root_members:

            if member.optional:
                lines += ['bool is_{}_present;'.format(canonical(member.name))]

            lines += self.add_sequence_member(member, checker)

        if type_.additions is not None and len(type_.additions) > 0:
            for addition in type_.additions:
                lines += ['bool is_{}_addition_present;'.format(addition.name)]

                lines += self.add_sequence_member(addition, checker)

        return ['struct {'] + indent_lines(lines) + ['}']

    def format_sequence_of(self, type_, checker):
        if not checker.is_bound():
            raise self.error('SEQUENCE OF has no maximum length.')

        lines = self.format_type(type_.element_type, checker.element_type)

        if lines:
            lines[-1] += ' elements[{}];'.format(checker.maximum)

        if checker.minimum == checker.maximum:
            length_lines = []
        elif checker.maximum < 256:
            length_lines = ['uint8_t length;']
        else:
            length_lines = ['uint32_t length;']

        return ['struct {'] + indent_lines(length_lines + lines) + ['}']

    def format_enumerated(self, type_):
        lines = ['enum {}_e'.format(self.location)]

        values = [
            '    {}_{}_e = {}'.format(self.location, name, value)
            for name, value in self.get_enumerated_values(type_)
        ]
        self.helper_lines += [
            'enum {}_e {{'.format(self.location)
        ] + join_lines(values, ',') + [
            '};',
            ''
        ]

        return lines

    def format_choice(self, type_, checker):
        lines = []
        choices = []

        for member in self.get_choice_members(type_):
            member_checker = self.get_member_checker(checker,
                                                     member.name)

            with self.members_backtrace_push(canonical(member.name)):
                choice_lines = self.format_type(member, member_checker)

            if choice_lines:
                choice_lines[-1] += ' {};'.format(canonical(member.name))

            lines += choice_lines
            choices.append('    {}_choice_{}_e'.format(self.location,
                                                       canonical(member.name)))

        self.helper_lines += [
            'enum {}_choice_e {{'.format(self.location)
        ] + join_lines(choices, ',') + [
            '};',
            ''
        ]

        lines = [
            'enum {}_choice_e choice;'.format(self.location),
            'union {'
        ] + indent_lines(lines) + [
            '} value;'
        ]

        lines = ['struct {'] + indent_lines(lines) + ['}']

        return lines

    def format_user_type(self, type_name, module_name):
        module_name_snake = camel_to_snake_case(module_name)
        type_name_snake = camel_to_snake_case(type_name)

        self.used_user_types.append((type_name, module_name))

        return ['struct {}_{}_{}_t'.format(self.namespace,
                                           module_name_snake,
                                           type_name_snake)]

    def format_sequence_inner_member(self,
                                     member,
                                     checker,
                                     default_condition_by_member_name,
                                     skip_when_not_present=True):
        member_checker = self.get_member_checker(checker, member.name)

        with self.members_backtrace_push(canonical(member.name)):
            encode_lines, decode_lines = self.format_type_inner(
                member,
                member_checker)

        location = self.location_inner('', '.')

        if member.optional and skip_when_not_present:
            is_present = '{}is_{}_present'.format(location, canonical(member.name))
            encode_lines = [
                '',
                'if (src_p->{}) {{'.format(is_present)
            ] + indent_lines(encode_lines) + [
                '}',
                ''
            ]
            decode_lines = [
                '',
                'if (dst_p->{}) {{'.format(is_present)
            ] + indent_lines(decode_lines) + [
                '}',
                ''
            ]
        elif member.default is not None and skip_when_not_present:
            name = '{}{}'.format(location, canonical(member.name))

            if self.is_buffer_type(member):
                default_value = '{{' + ', '.join(['0x%02X' % m for m in member.default]) + '}};'
                default_variable = self.add_unique_variable('static const uint8_t {}[] = ' + default_value,
                                                            canonical(member.name) + '_default')

                encode_lines = [
                                   '',
                                   'if ((memcmp(src_p->{}.buf, {}, sizeof({})) != 0) ||'.format(
                                       name,
                                       default_variable,
                                       default_variable),
                                   '    (src_p->{}.length != sizeof({}))) {{'.format(
                                       name,
                                       default_variable)
                               ] + indent_lines(encode_lines) + [
                                   '}',
                                   ''
                               ]
                decode_lines = [
                                   '',
                                   'if ({}) {{'.format(default_condition_by_member_name[member.name])
                               ] + indent_lines(decode_lines) + [
                                   '} else {',
                                   '    memcpy(dst_p->{}.buf, {}, sizeof({}));'.format(
                                       name,
                                       default_variable,
                                       default_variable),
                                   '    dst_p->{}.length = sizeof({});'.format(
                                       name,
                                       default_variable
                                   ),
                                   '}',
                                   ''
                               ]
            else:
                encode_lines = [
                    '',
                    'if (src_p->{}{} != {}) {{'.format(
                        name,
                        '.value' if self.is_complex_user_type(member) else '',
                        self.format_default(member))
                ] + indent_lines(encode_lines) + [
                    '}',
                    ''
                ]
                decode_lines = [
                    '',
                    'if ({}) {{'.format(default_condition_by_member_name[member.name])
                ] + indent_lines(decode_lines) + [
                    '} else {',
                    '    dst_p->{}{} = {};'.format(
                        name,
                        '.value' if self.is_complex_user_type(member) else '',
                        self.format_default(member)),
                    '}',
                    ''
                ]

        return encode_lines, decode_lines

    def generate_type_declaration(self, compiled_type):
        type_ = compiled_type.type
        checker = compiled_type.constraints_checker.type

        lines = self.generate_type_declaration_process(type_, checker)

        if not lines:
            lines = ['uint8_t dummy;']

        lines = indent_lines(lines)

        if self.helper_lines:
            self.helper_lines.append('')

        return [
            TYPE_DECLARATION_FMT.format(namespace=self.namespace,
                                        module_name=self.module_name,
                                        type_name=self.type_name,
                                        module_name_snake=self.module_name_snake,
                                        type_name_snake=self.type_name_snake,
                                        helper_types='\n'.join(self.helper_lines),
                                        members='\n'.join(lines))
        ]

    def generate_declaration(self):
        return DECLARATION_FMT.format(namespace=self.namespace,
                                      module_name=self.module_name,
                                      type_name=self.type_name,
                                      module_name_snake=self.module_name_snake,
                                      type_name_snake=self.type_name_snake)

    def generate_definition(self):
        return DEFINITION_FMT.format(namespace=self.namespace,
                                     module_name_snake=self.module_name_snake,
                                     type_name_snake=self.type_name_snake)

    def generate_definition_inner(self, compiled_type):
        encode_lines, decode_lines = self.generate_definition_inner_process(
            compiled_type.type,
            compiled_type.constraints_checker.type)

        if self.encode_variable_lines:
            encode_lines = self.encode_variable_lines + [''] + encode_lines

        if self.decode_variable_lines:
            decode_lines = self.decode_variable_lines + [''] + decode_lines

        encode_lines = indent_lines(encode_lines) + ['']
        decode_lines = indent_lines(decode_lines) + ['']

        return DEFINITION_INNER_FMT.format(namespace=self.namespace,
                                           module_name_snake=self.module_name_snake,
                                           type_name_snake=self.type_name_snake,
                                           encode_body='\n'.join(encode_lines),
                                           decode_body='\n'.join(decode_lines))

    def generate(self, compiled):
        user_types = {}
        user_type_dependencies = {}

        for module_name, module in sorted(compiled.modules.items()):
            self.module_name = module_name

            for type_name, compiled_type in sorted(module.items()):
                self.type_name = type_name
                self.reset_type()

                type_declaration = self.generate_type_declaration(compiled_type)

                if not type_declaration:
                    continue

                declaration = self.generate_declaration()
                definition_inner = self.generate_definition_inner(compiled_type)
                definition = self.generate_definition()

                user_type = _UserType(type_name,
                                      module_name,
                                      type_declaration,
                                      declaration,
                                      definition_inner,
                                      definition)
                user_type_name_tuple = (user_type.type_name, user_type.module_name)
                user_types[user_type_name_tuple] = user_type
                user_type_dependencies[user_type_name_tuple] = self.used_user_types

        user_type_sorted_names = topological_sort(user_type_dependencies)

        type_declarations = []
        declarations = []
        definitions_inner = []
        definitions = []

        for user_type_name in user_type_sorted_names:
            user_type = user_types[user_type_name]
            type_declarations.extend(user_type.type_declaration)
            declarations.append(user_type.declaration)
            definitions_inner.append(user_type.definition_inner)
            definitions.append(user_type.definition)

        type_declarations = '\n'.join(type_declarations)
        declarations = '\n'.join(declarations)
        definitions = '\n'.join(definitions_inner + definitions)
        helpers = '\n'.join(self.generate_helpers(definitions))

        return type_declarations, declarations, helpers, definitions

    def format_default(self, type_):
        raise NotImplementedError('To be implemented by subclasses.')

    def format_type(self, type_, checker):
        raise NotImplementedError('To be implemented by subclasses.')

    def format_type_inner(self, type_, checker):
        raise NotImplementedError('To be implemented by subclasses.')

    def get_enumerated_values(self, type_):
        raise NotImplementedError('To be implemented by subclasses.')

    def get_choice_members(self, type_):
        raise NotImplementedError('To be implemented by subclasses.')

    def generate_type_declaration_process(self, type_, checker):
        raise NotImplementedError('To be implemented by subclasses.')

    def generate_definition_inner_process(self, type_, checker):
        raise NotImplementedError('To be implemented by subclasses.')

    def generate_helpers(self, definitions):
        raise NotImplementedError('To be implemented by subclasses.')

    def is_complex_user_type(self, type_):
        raise NotImplementedError('To be implemented by subclasses.')

    def is_buffer_type(self, type_):
        raise NotImplementedError('To be implemented by subclasses.')


def canonical(value):
    """Replace anything but 'a-z', 'A-Z' and '0-9' with '_'.

    """

    return re.sub(r'[^a-zA-Z0-9]', '_', value)


def camel_to_snake_case(value):
    value = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', value)
    value = re.sub(r'(_+)', '_', value)
    value = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', value).lower()
    value = canonical(value)

    return value


def join_lines(lines, suffix):
    return[line + suffix for line in lines[:-1]] + lines[-1:]


def is_user_type(type_):
    return type_.module_name is not None


def strip_blank_lines(lines):
    try:
        while lines[0] == '':
            del lines[0]

        while lines[-1] == '':
            del lines[-1]
    except IndexError:
        pass

    stripped = []

    for line in lines:
        if line == '' and stripped[-1] == '':
            continue

        stripped.append(line)

    return stripped


def indent_lines(lines):
    indented_lines = []

    for line in lines:
        if line:
            indented_line = 4 * ' ' + line
        else:
            indented_line = line

        indented_lines.append(indented_line)

    return strip_blank_lines(indented_lines)


def dedent_lines(lines):
    return [line[4:] for line in lines]


def topological_sort(graph):
    """Topological sort algorithm to return a list of keys to a dictionary
    of lists of dependencies. The returned keys define an order so
    that all dependent items are in front of the originating item.

    """

    def recurse(node, path):
        if node not in path:
            edges = graph[node]

            for edge in edges:
                if edge not in path:
                    path = recurse(edge, path)

            path = path + [node]

        return path

    path = []

    for node in sorted(graph):
        path = recurse(node, path)

    return path
