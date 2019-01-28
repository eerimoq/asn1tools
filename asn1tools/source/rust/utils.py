import re

from ...errors import Error


TYPE_DECLARATION_FMT = '''\
// Type {type_name} in module {module_name}.
{helper_types}\
struct {module_name}{type_name} {{
{members}
}};
'''

DEFINITION_FMT = '''\
impl {module_name}{type_name} {{
    pub fn to_bytes(&mut self,
                    dst: &mut [u8])
                    -> Result<usize, &'static str> {{
        let mut encoder = Encoder::new(&mut dst);

        self.to_bytes_inner(&mut encoder);

        return encoder.get_result();
    }}

    pub fn from_bytes(&mut self, src: &[u8]) -> Result<usize, &'static str> {{
        let mut decoder = Decoder::new(&src);

        self.from_bytes_inner(&mut decoder);

        return decoder.get_result();
    }}

    fn to_bytes_inner(&mut self, encoder: &mut Encoder) {{
{encode_body}\
    }}

    fn from_bytes_inner(&mut self, decoder: &mut Decoder) {{
{decode_body}\
    }}
}}
'''

ENCODER_AND_DECODER_STRUCTS = '''\
#[derive(Debug, PartialEq, Copy, Clone)]
pub enum Error {
    BadChoice,
    BadEnum,
    BadLength,
    OutOfData,
    OutOfMemory
}

pub struct Encoder<'a> {
    buf: &'a mut [u8],
    size: usize,
    pos: usize,
    error: Option<Error>
}

pub struct Decoder<'a> {
    buf: &'a[u8],
    size: usize,
    pos: usize,
    error: Option<Error>
}
'''

ENCODER_ABORT = '''
    fn abort(&mut self, error: Error) {
        if self.error.is_none() {
            self.error = Some(error);
        }
    }\
'''

DECODER_ABORT = '''
    fn abort(&mut self, error: Error) {
        if self.error.is_none() {
            self.error = Some(error);
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
                 definition,
                 used_user_types):
        self.type_name = type_name
        self.module_name = module_name
        self.type_declaration = type_declaration
        self.definition = definition
        self.used_user_types = used_user_types


class Generator(object):

    def __init__(self):
        self.namespace = 'a'
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
        if minimum < -4294967296:
            minimum_length = 64
        elif minimum < -65536:
            minimum_length = 32
        elif minimum < -256:
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

    def format_type_name(self, minimum, maximum):
        length = self.type_length(minimum, maximum)

        if minimum >= 0:
            type_name = 'u{}'.format(length)
        else:
            type_name = 'i{}'.format(length)

        return type_name

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
            lines = ['    let length: u8;']
        else:
            lines = ['    let length: u32;']

        return [
            'struct {'
        ] + lines + [
            '    uint8_t buf[{}];'.format(checker.maximum),
            '}'
        ]

    def format_sequence(self, type_, checker):
        lines = []

        for member in type_.root_members:
            member_checker = self.get_member_checker(checker, member.name)

            if member.optional:
                lines += ['is_{}_present: bool;'.format(member.name)]

            with self.members_backtrace_push(member.name):
                member_lines = self.format_type(member, member_checker)

            if member_lines:
                # member_lines[-1] += ' {};'.format(member.name)
                member_lines[-1] = '{}: {};'.format(member.name,
                                                    member_lines[-1])

            lines += member_lines

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
            length_lines = ['let length: u8;']
        else:
            length_lines = ['let length: u32;']

        return ['struct {'] + indent_lines(length_lines + lines) + ['}']

    def format_enumerated(self, type_):
        lines = ['enum {}_e'.format(self.location)]

        values = [
            '    {}_{}_e'.format(self.location, value)
            for value in self.get_enumerated_values(type_)
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

            with self.members_backtrace_push(member.name):
                choice_lines = self.format_type(member, member_checker)

            if choice_lines:
                choice_lines[-1] += ' {};'.format(member.name)

            lines += choice_lines
            choices.append('    {}_choice_{}_e'.format(self.location,
                                                       member.name))

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
                                     default_condition_by_member_name):
        member_checker = self.get_member_checker(checker, member.name)

        with self.members_backtrace_push(member.name):
            encode_lines, decode_lines = self.format_type_inner(
                member,
                member_checker)

        location = self.location_inner('', '.')

        if member.optional:
            is_present = '{}is_{}_present'.format(location, member.name)
            encode_lines = [
                '',
                'if src.{} {{'.format(is_present)
            ] + indent_lines(encode_lines) + [
                '}',
                ''
            ]
            decode_lines = [
                '',
                'if dst.{} {{'.format(is_present)
            ] + indent_lines(decode_lines) + [
                '}',
                ''
            ]
        elif member.default is not None:
            name = '{}{}'.format(location, member.name)
            encode_lines = [
                '',
                'if src.{} != {} {{'.format(name, member.default)
            ] + indent_lines(encode_lines) + [
                '}',
                ''
            ]
            decode_lines = [
                '',
                'if {} {{'.format(default_condition_by_member_name[member.name])
            ] + indent_lines(decode_lines) + [
                '} else {',
                '    dst.{} = {};'.format(name, member.default),
                '}',
                ''
            ]

        return encode_lines, decode_lines

    def generate_type_declaration(self, compiled_type):
        type_ = compiled_type.type
        checker = compiled_type.constraints_checker.type

        lines = self.generate_type_declaration_process(type_, checker)

        if not lines:
            lines = ['dummy: u8;']

        lines = indent_lines(lines)

        if self.helper_lines:
            self.helper_lines.append('')

        return [
            TYPE_DECLARATION_FMT.format(namespace=self.namespace,
                                        module_name=self.module_name,
                                        type_name=self.type_name,
                                        helper_types='\n'.join(self.helper_lines),
                                        members='\n'.join(lines))
        ]

    def generate_definition(self, compiled_type):
        encode_lines, decode_lines = self.generate_definition_inner_process(
            compiled_type.type,
            compiled_type.constraints_checker.type)

        if self.encode_variable_lines:
            encode_lines = self.encode_variable_lines + [''] + encode_lines

        if self.decode_variable_lines:
            decode_lines = self.decode_variable_lines + [''] + decode_lines

        encode_lines = indent_lines(indent_lines(encode_lines)) + ['']
        decode_lines = indent_lines(indent_lines(decode_lines)) + ['']

        return DEFINITION_FMT.format(module_name=self.module_name,
                                     type_name=self.type_name,
                                     encode_body='\n'.join(encode_lines),
                                     decode_body='\n'.join(decode_lines))

    def generate(self, compiled):
        user_types = []

        for module_name, module in sorted(compiled.modules.items()):
            self.module_name = module_name

            for type_name, compiled_type in sorted(module.items()):
                self.type_name = type_name
                self.reset_type()

                type_declaration = self.generate_type_declaration(compiled_type)

                if not type_declaration:
                    continue

                definition = self.generate_definition(compiled_type)

                user_type = _UserType(type_name,
                                      module_name,
                                      type_declaration,
                                      definition,
                                      self.used_user_types)
                user_types.append(user_type)

        user_types = sort_user_types_by_used_user_types(user_types)

        type_declarations = []
        definitions = []

        for user_type in user_types:
            type_declarations.extend(user_type.type_declaration)
            definitions.append(user_type.definition)

        type_declarations = '\n'.join(type_declarations)
        definitions = '\n'.join(definitions)
        helpers = '\n'.join(self.generate_helpers(definitions))

        return type_declarations, helpers, definitions

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


def indent_lines(lines, width=4):
    indented_lines = []

    for line in lines:
        if line:
            indented_line = width * ' ' + line
        else:
            indented_line = line

        indented_lines.append(indented_line)

    return strip_blank_lines(indented_lines)


def dedent_lines(lines, width=4):
    return [line[width:] for line in lines]


def sort_user_types_by_used_user_types(user_types):
    reversed_sorted_user_types = []

    for user_type in user_types:
        user_type_name_tuple = (user_type.type_name, user_type.module_name)

        # Insert first in the reversed list if there are no types
        # using this type.
        insert_index = 0

        for i, reversed_sorted_user_type in enumerate(reversed_sorted_user_types, 1):
            if user_type_name_tuple in reversed_sorted_user_type.used_user_types:
                if i > insert_index:
                    insert_index = i

        reversed_sorted_user_types.insert(insert_index, user_type)

    return reversed(reversed_sorted_user_types)
