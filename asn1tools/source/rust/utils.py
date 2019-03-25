import re

from ...errors import Error


TYPE_DECLARATION_FMT = '''\
/// Type {type_name} in module {module_name}.
{members}
'''

DEFINITION_FMT = '''
impl {module_name}{type_name} {{
    pub fn encode(&mut self, mut dst: &mut [u8]) -> Result<usize, Error> {{
        let mut encoder = Encoder::new(&mut dst);

        self.encode_inner(&mut encoder);

        encoder.get_result()
    }}

    pub fn decode(&mut self, src: &[u8]) -> Result<usize, Error> {{
        let mut decoder = Decoder::new(&src);

        self.decode_inner(&mut decoder);

        decoder.get_result()
    }}

    fn encode_inner(&mut self, encoder: &mut Encoder) {{
{encode_body}\
    }}

    fn decode_inner(&mut self, decoder: &mut Decoder) {{
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

struct Encoder<'a> {
    buf: &'a mut [u8],
    size: usize,
    pos: usize,
    error: Option<Error>
}

struct Decoder<'a> {
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
                 type_code,
                 used_user_types):
        self.type_name = type_name
        self.module_name = module_name
        self.type_code = type_code
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
        location = '{}{}'.format(self.module_name,
                                 self.type_name)

        for member in self.asn1_members_backtrace:
            location += make_camel_case(member)

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

    def add_unique_variable(self, name):
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

        return unique_name

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
            '#[derive(Debug, Default, PartialEq, Copy, Clone)]',
            'pub struct {} {{'.format(self.location)
        ] + lines + [
            '    pub buf: [u8; {}]'.format(checker.maximum),
            '}'
        ]

    def format_sequence(self, type_, checker):
        helper_lines = []
        lines = []

        for member in type_.root_members:
            member_checker = self.get_member_checker(checker, member.name)

            if member.optional:
                lines += ['pub is_{}_present: bool,'.format(member.name)]

            with self.members_backtrace_push(member.name):
                member_lines = self.format_type(member, member_checker)
                member_location = self.location

            if not member_lines:
                continue

            if is_inline_member_lines(member_lines):
                member_lines[-1] = 'pub {}: {},'.format(member.name,
                                                        member_lines[-1])
            else:
                helper_lines += member_lines + ['']
                member_lines = ['pub {}: {},'.format(member.name,
                                                     member_location)]

            lines += member_lines

        if lines:
            lines[-1] = lines[-1].strip(',')

        return helper_lines + [
            '#[derive(Debug, Default, PartialEq, Copy, Clone)]',
            'pub struct {} {{'.format(self.location)
        ] + indent_lines(lines) + [
            '}'
        ]

    def format_sequence_of(self, type_, checker):
        if not checker.is_bound():
            raise self.error('SEQUENCE OF has no maximum length.')

        with self.asn1_members_backtrace_push('elem'):
            lines = self.format_type(type_.element_type,
                                     checker.element_type)

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
        lines = [
            '#[derive(Debug, PartialEq, Copy, Clone)]',
            'pub enum {} {{'.format(self.location)
        ] + [
            '    {},'.format(make_camel_case(value))
            for value in self.get_enumerated_values(type_)
        ] + [
            '}',
            '',
            'impl Default for {} {{'.format(self.location),
            '    fn default() -> Self {',
            '        {}::{}'.format(self.location,
                                    self.get_enumerated_values(type_)[0].upper()),
            '    }',
            '}'

        ]

        return lines

    def format_choice(self, type_, checker):
        helper_lines = []
        lines = []

        for member in self.get_choice_members(type_):
            member_checker = self.get_member_checker(checker,
                                                     member.name)

            with self.members_backtrace_push(member.name):
                member_lines = self.format_type(member, member_checker)
                member_location = self.location

            if not member_lines:
                continue

            if is_inline_member_lines(member_lines):
                member_lines[-1] = '{}({}),'.format(make_camel_case(member.name),
                                                    member_lines[-1])
            else:
                helper_lines += member_lines + ['']
                member_lines = ['pub {}: {},'.format(member.name,
                                                     member_location)]

            lines += member_lines

        if lines:
            lines[-1] = lines[-1].strip(',')

        return helper_lines + [
            '#[derive(Debug, PartialEq, Copy, Clone)]',
            'pub enum {} {{'.format(self.location)
        ] + indent_lines(lines) + [
            '}'
        ]

    def format_user_type(self, type_name, module_name):
        self.used_user_types.append((type_name, module_name))

        return ['{}{}'.format(module_name, type_name)]

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

        if self.helper_lines:
            self.helper_lines.append('')

        return TYPE_DECLARATION_FMT.format(module_name=self.module_name,
                                           type_name=self.type_name,
                                           members='\n'.join(lines))

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
                definition = self.generate_definition(compiled_type)
                user_type = _UserType(type_name,
                                      module_name,
                                      type_declaration + definition,
                                      self.used_user_types)
                user_types.append(user_type)

        user_types = sort_user_types_by_used_user_types(user_types)

        types_code = []

        for user_type in user_types:
            types_code.append(user_type.type_code)

        types_code = '\n'.join(types_code)
        helpers = '\n'.join(self.generate_helpers(types_code))

        return helpers, types_code

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


def make_camel_case(value):
    return value[0].upper() + value[1:]


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


def is_inline_member_lines(member_lines):
    return len(member_lines) == 1
