"""Base Compiler class used by all codecs.

"""

from operator import attrgetter
import bitstruct

from copy import copy
from copy import deepcopy
from ..errors import CompileError
from ..parser import EXTENSION_MARKER


def flatten(dlist):
    flist = []

    for item in dlist:
        if isinstance(item, list):
            flist.extend(item)
        else:
            flist.append(item)

    return flist


def is_object_class_type_name(type_name):
    return '&' in type_name


def is_open_type(type_name):
    index = type_name.find('&')

    if index == -1:
        return False

    return type_name[index + 1].isupper()


def is_class_value(name):
    return is_object_class_type_name(name) and not is_open_type(name)


def is_type_name(type_name):
    """Does not handle keywords.

    """

    return type_name[0].isupper()


def lowest_set_bit(value):
    offset = (value & -value).bit_length() - 1

    if offset < 0:
        offset = 0

    return offset


def rstrip_bit_string_zeros(data):
    data = data.rstrip(b'\x00')

    if len(data) == 0:
        number_of_bits = 0
    else:
        number_of_bits = 8 * len(data) - lowest_set_bit(data[-1])

    return (data, number_of_bits)


def clean_bit_string_value(value, has_named_bits):
    data = bytearray(value[0])
    number_of_bits = value[1]
    number_of_bytes, number_of_rest_bits = divmod(number_of_bits, 8)

    if number_of_rest_bits == 0:
        data = data[:number_of_bytes]
    else:
        data = data[:number_of_bytes + 1]
        data[number_of_bytes] &= ((0xff >> number_of_rest_bits) ^ 0xff)

    if has_named_bits:
        return rstrip_bit_string_zeros(data)
    else:
        return (data, number_of_bits)


class CompiledType(object):

    def __init__(self):
        self.constraints_checker = None
        self.type_checker = None

    def check_types(self, data):
        return self.type_checker.encode(data)

    def check_constraints(self, data):
        return self.constraints_checker.encode(data)


class Recursive(object):
    pass


class OpenType(object):

    def __init__(self, name, object_set, table):
        self.name = name
        self._object_set = object_set
        self._table = []

        for item in table:
            offset = item.count('.')
            offset *= -1
            self._table.append((offset, item.lstrip('.')))

        print('a', self._object_set)
        print('b', self._table)

    def encode(self, stack, data):
        print('open type encode:', stack, data)
        print(self._object_set)

        for offset, item in self._table:
            print(stack[offset][item])

    def __repr__(self):
        return 'OpenType({}, {}, {})'.format(self.name,
                                             self._object_set,
                                             self._table)


class OpenTypeSequence(object):

    def __init__(self, name, members):
        self._name = name
        self._members = members

    def encode(self, stack, data):
        stack.append(data)

        for member in self._members:
            member.encode(stack, data[member.name])

        stack.pop()

    def __repr__(self):
        return 'OpenTypeSequence({}, {})'.format(self._name, self._members)


class OpenTypeSequenceOf(object):

    def __init__(self, name, element_type):
        self._name = name
        self._element_type = element_type

    def encode(self, stack, data):
        stack.append(data)
        self._element_type.encode(stack, data)
        stack.pop()

    def __repr__(self):
        return 'OpenTypeSequenceOf({}, {})'.format(self._name,
                                                   self._element_type)


class CompiledOpenTypes(CompiledType):

    def __init__(self, compiled_open_types, compiled_type):
        super(CompiledOpenTypes, self).__init__()
        self._compiled_open_types = compiled_open_types
        self._inner = compiled_type
        self._tables = {
            'Items': {}
        }

    @property
    def type(self):
        return self._inner.type

    def encode(self, data, **kwargs):
        # print()
        # print('data:', data)
        # print(self._compiled_open_types)

        stack = []
        self._compiled_open_types.encode(stack, data)

        return self._inner.encode(data, **kwargs)

    def decode(self, data):
        return self._inner.decode(data)

    def __repr__(self):
        return repr(self._inner)


class Compiler(object):

    def __init__(self, specification):
        self._specification = specification
        self._types_backtrace = []
        self.recursive_types = []
        self.compiled = {}
        self.compiled_sets = {}

    def types_backtrace_push(self, type_name):
        self._types_backtrace.append(type_name)

    def types_backtrace_pop(self):
        self._types_backtrace.pop()

    @property
    def types_backtrace(self):
        return self._types_backtrace

    def process(self):
        self.pre_process()

        # Compile types in object sets.
        for module_name in self._specification:
            items = self._specification[module_name]['object-sets'].items()

            for set_name, set_descriptor in items:
                compiled_set = []

                for member in set_descriptor['members']:
                    if not isinstance(member, dict):
                        continue

                    compiled_set_member = {}

                    for member_name, member_value in member.items():
                        if is_class_value(member_name):
                            compiled_set_member[member_name] = member_value
                        else:
                            self.types_backtrace_push(member_name)
                            compiled_member = self.process_type(member_name,
                                                                member_value,
                                                                module_name)
                            self.types_backtrace_pop()
                            compiled_set_member[member_name] = compiled_member

                    compiled_set.append(compiled_set_member)

                if module_name not in self.compiled_sets:
                    self.compiled_sets[module_name] = {}

                self.compiled_sets[module_name][set_name] = compiled_set

        # Compile types.
        compiled = {}

        for module_name in self._specification:
            items = self._specification[module_name]['types'].items()

            for type_name, type_descriptor in items:
                self.types_backtrace_push(type_name)
                compiled_type = self.process_type(type_name,
                                                  type_descriptor,
                                                  module_name)

                # ToDo: Remove once parameterization has been
                #       implemented.
                try:
                    compiled_open_types = self.compile_open_types(
                        type_name,
                        type_descriptor,
                        module_name)
                except CompileError:
                    compiled_open_types = None

                if compiled_open_types:
                    compiled_type = CompiledOpenTypes(compiled_open_types,
                                                      compiled_type)

                self.types_backtrace_pop()

                if module_name not in compiled:
                    compiled[module_name] = {}

                compiled[module_name][type_name] = compiled_type

        for recursive_type in self.recursive_types:
            compiled_module = compiled[recursive_type.module_name]
            inner_type = compiled_module[recursive_type.type_name].type
            recursive_type.set_inner_type(inner_type)

        return compiled

    def pre_process(self):
        for module_name in self._specification:
            module = self._specification[module_name]
            types = module['types']
            type_descriptors = types.values()

            self.pre_process_components_of(type_descriptors, module_name)
            self.pre_process_extensibility_implied(module, type_descriptors)
            self.pre_process_tags(module, module_name)
            self.pre_process_default_value(type_descriptors, module_name)

        return self._specification

    def pre_process_components_of(self, type_descriptors, module_name):
        """COMPONENTS OF expansion.

        """

        for type_descriptor in type_descriptors:
            self.pre_process_components_of_type(type_descriptor,
                                                module_name)

    def pre_process_components_of_type(self, type_descriptor, module_name):
        if 'members' not in type_descriptor:
            return

        type_descriptor['members'] = self.pre_process_components_of_expand_members(
            type_descriptor['members'],
            module_name)

    def pre_process_components_of_expand_members(self, members, module_name):
        expanded_members = []

        for member in members:
            if member != EXTENSION_MARKER and 'components-of' in member:
                type_descriptor, inner_module_name = self.lookup_type_descriptor(
                    member['components-of'],
                    module_name)
                inner_members = self.pre_process_components_of_expand_members(
                    type_descriptor['members'],
                    inner_module_name)

                for inner_member in inner_members:
                    if inner_member == EXTENSION_MARKER:
                        break

                    expanded_members.append(deepcopy(inner_member))
            else:
                expanded_members.append(member)

        return expanded_members

    def pre_process_extensibility_implied(self, module, type_descriptors):
        """Make all types extensible.

        """

        if not module['extensibility-implied']:
            return

        for type_descriptor in type_descriptors:
            self.pre_process_extensibility_implied_type(type_descriptor)

    def pre_process_extensibility_implied_type(self, type_descriptor):
        if 'members' not in type_descriptor:
            return

        members = type_descriptor['members']

        for member in members:
            if member == EXTENSION_MARKER:
                continue

            if isinstance(member, list):
                for type_descriptor in member:
                    self.pre_process_extensibility_implied_type(type_descriptor)
            else:
                self.pre_process_extensibility_implied_type(member)

        if EXTENSION_MARKER not in members:
            members.append(EXTENSION_MARKER)

    def pre_process_tags(self, module, module_name):
        """Add tags where missing.

        """

        module_tags = module.get('tags', 'EXPLICIT')

        for type_descriptor in module['types'].values():
            self.pre_process_tags_type(type_descriptor,
                                       module_tags,
                                       module_name)

    def pre_process_tags_type(self,
                              type_descriptor,
                              module_tags,
                              module_name):
        type_name = type_descriptor['type']

        if 'tag' in type_descriptor:
            tag = type_descriptor['tag']
            resolved_type_name = self.resolve_type_name(type_name, module_name)

            if 'kind' not in tag:
                if resolved_type_name == 'CHOICE':
                    tag['kind'] = 'EXPLICIT'
                elif module_tags in ['IMPLICIT', 'EXPLICIT']:
                    tag['kind'] = module_tags
                else:
                    tag['kind'] = 'IMPLICIT'

        # SEQUENCE, SET and CHOICE.
        if 'members' in type_descriptor:
            self.pre_process_tags_type_members(type_descriptor,
                                               module_tags,
                                               module_name)

        # SEQUENCE OF and SET OF.
        if 'element' in type_descriptor:
            self.pre_process_tags_type(type_descriptor['element'],
                                       module_tags,
                                       module_name)

    def pre_process_tags_type_members(self,
                                      type_descriptor,
                                      module_tags,
                                      module_name):
        def is_any_member_tagged(members):
            for member in members:
                if member == EXTENSION_MARKER:
                    continue

                if 'tag' in member:
                    return True

            return False

        number = None
        members = flatten(type_descriptor['members'])

        # Add tag number to all members if AUTOMATIC TAGS are
        # selected and no member is tagged.
        if module_tags == 'AUTOMATIC' and not is_any_member_tagged(members):
            number = 0

        for member in members:
            if member == EXTENSION_MARKER:
                continue

            if number is not None:
                if 'tag' not in member:
                    member['tag'] = {}

                member['tag']['number'] = number
                number += 1

            self.pre_process_tags_type(member,
                                       module_tags,
                                       module_name)

    def pre_process_default_value(self, type_descriptors, module_name):
        """SEQUENCE and SET default member value cleanup.

        """

        sequences_and_sets = self.get_type_descriptors(
            type_descriptors,
            ['SEQUENCE', 'SET'])

        for type_descriptor in sequences_and_sets:
            for member in type_descriptor['members']:
                if member == EXTENSION_MARKER:
                    continue

                if 'default' not in member:
                    continue

                resolved_member = self.resolve_type_descriptor(member,
                                                               module_name)

                if resolved_member['type'] == 'BIT STRING':
                    self.pre_process_default_value_bit_string(member,
                                                              resolved_member)

    def pre_process_default_value_bit_string(self, member, resolved_member):
        default = member['default']

        if isinstance(default, tuple):
            # Already pre-processed.
            return

        if isinstance(default, list):
            named_bits = dict(resolved_member['named-bits'])
            reversed_mask = 0

            for name in default:
                reversed_mask |= (1 << int(named_bits[name]))

            mask = int(bin(reversed_mask)[2:][::-1], 2)
            number_of_bits = reversed_mask.bit_length()
        elif default.startswith('0x'):
            if len(default) % 2 == 1:
                default += '0'

            default = '01' + default[2:]
            mask = int(default, 16)
            mask >>= lowest_set_bit(mask)
            number_of_bits = mask.bit_length() - 1
            mask ^= (1 << number_of_bits)
        else:
            mask = int(default, 2)
            mask >>= lowest_set_bit(mask)
            number_of_bits = len(default) - 2

        mask = bitstruct.pack('u{}'.format(number_of_bits), mask)
        member['default'] = (mask, number_of_bits)

    def resolve_type_name(self, type_name, module_name):
        """Returns the ASN.1 type name of given type.

        """

        try:
            while True:
                if is_object_class_type_name(type_name):
                    type_name, module_name = self.lookup_object_class_type_name(
                        type_name,
                        module_name)
                else:
                    type_descriptor, module_name = self.lookup_type_descriptor(
                        type_name,
                        module_name)
                    type_name = type_descriptor['type']
        except CompileError:
            pass

        return type_name

    def resolve_type_descriptor(self, type_descriptor, module_name):
        type_name = type_descriptor['type']

        try:
            while True:
                if is_object_class_type_name(type_name):
                    type_name, module_name = self.lookup_object_class_type_name(
                        type_name,
                        module_name)
                else:
                    type_descriptor, module_name = self.lookup_type_descriptor(
                        type_name,
                        module_name)
                    type_name = type_descriptor['type']
        except CompileError:
            pass

        return type_descriptor

    def get_type_descriptors(self, type_descriptors, type_names):
        result = []

        for type_descriptor in type_descriptors:
            result += self.get_type_descriptors_type(type_descriptor,
                                                     type_names)

        return result

    def get_type_descriptors_type(self, type_descriptor, type_names):
        type_descriptors = []
        type_name = type_descriptor['type']

        if type_name in type_names:
            type_descriptors.append(type_descriptor)

        if 'members' in type_descriptor:
            for member in type_descriptor['members']:
                if member == EXTENSION_MARKER:
                    continue

                if isinstance(member, list):
                    type_descriptors.extend(self.get_type_descriptors(member,
                                                                      type_names))
                else:
                    type_descriptors += self.get_type_descriptors_type(member,
                                                                       type_names)

        if 'element' in type_descriptor:
            type_descriptors += self.get_type_descriptors_type(
                type_descriptor['element'],
                type_names)

        return type_descriptors

    def process_type(self, type_name, type_descriptor, module_name):
        return NotImplementedError('To be implemented by subclasses.')

    def compile_type(self, name, type_descriptor, module_name):
        return NotImplementedError('To be implemented by subclasses.')

    def compile_open_types(self,
                           name,
                           type_descriptor,
                           module_name):
        """Compile the open types wrapper for given type. Returns ``None`` if
        given type does not have any open types.

        """

        compiled = None
        type_name = type_descriptor['type']

        if type_name in ['SEQUENCE', 'SET']:
            compiled_members = []

            for member in type_descriptor['members']:
                if member == EXTENSION_MARKER:
                    continue

                if isinstance(member, list):
                    # ToDo: Handle groups.
                    continue

                if is_open_type(member['type']):
                    if 'table' not in member:
                        continue

                    table = member['table']

                    if isinstance(table, list):
                        compiled_members.append(
                            OpenType(member['name'],
                                     self.get_object_set(
                                         table,
                                         member['type'].split('.')[1],
                                         module_name),
                                     table[1]))
                else:
                    compiled_member = self.compile_open_types(member['name'],
                                                              member,
                                                              module_name)

                    if compiled_member is not None:
                        compiled_members.append(compiled_member)

            if compiled_members:
                compiled = OpenTypeSequence(name, compiled_members)
        elif type_name in ['SEQUENCE OF', 'SET OF']:
            compiled_element = self.compile_open_types('',
                                                       type_descriptor['element'],
                                                       module_name)

            if compiled_element:
                compiled = OpenTypeSequenceOf(name, compiled_element)
        elif type_name == 'CHOICE':
            # ToDo: Handle CHOICE.
            pass

        return compiled

    def compile_user_type(self, name, type_name, module_name):
        compiled = self.get_compiled_type(name,
                                          type_name,
                                          module_name)

        if compiled is None:
            self.types_backtrace_push(type_name)
            compiled = self.compile_type(
                name,
                *self.lookup_type_descriptor(
                    type_name,
                    module_name))
            self.types_backtrace_pop()
            self.set_compiled_type(name,
                                   type_name,
                                   module_name,
                                   compiled)

        return compiled

    def compile_members(self,
                        members,
                        module_name,
                        sort_by_tag=False):
        compiled_members = []

        for member in members:
            if member == EXTENSION_MARKER:
                continue

            if isinstance(member, list):
                compiled_members.extend(self.compile_members(member,
                                                             module_name))
                continue

            compiled_member = self.compile_member(member, module_name)
            compiled_members.append(compiled_member)

        if sort_by_tag:
            compiled_members = sorted(compiled_members, key=attrgetter('tag'))

        return compiled_members

    def compile_root_member(self, member, module_name, compiled_members):
        compiled_member = self.compile_member(member,
                                              module_name)
        compiled_members.append(compiled_member)

    def compile_member(self, member, module_name):
        if is_object_class_type_name(member['type']):
            member, class_module_name = self.convert_object_class_type_descriptor(
                member,
                module_name)
            compiled_member = self.compile_type(member['name'],
                                                member,
                                                class_module_name)
        else:
            compiled_member = self.compile_type(member['name'],
                                                member,
                                                module_name)

        if 'optional' in member:
            compiled_member = self.copy(compiled_member)
            compiled_member.optional = member['optional']

        if 'default' in member:
            compiled_member = self.copy(compiled_member)
            compiled_member.default = member['default']

        if 'size' in member:
            compiled_member = self.copy(compiled_member)
            compiled_member.set_size_range(*self.get_size_range(member,
                                                                module_name))

        return compiled_member

    def get_size_range(self, type_descriptor, module_name):
        """Returns a tuple of the minimum and maximum values allowed according
        the the ASN.1 specification SIZE parameter. Returns (None,
        None, None) if the type does not have a SIZE parameter.

        """

        size = type_descriptor.get('size', None)

        if size is None:
            minimum = None
            maximum = None
            has_extension_marker = None
        else:
            if isinstance(size[0], tuple):
                minimum, maximum = size[0]
            else:
                minimum = size[0]
                maximum = size[0]

            has_extension_marker = (EXTENSION_MARKER in size)

        if isinstance(minimum, str):
            if minimum != 'MIN':
                minimum = self.lookup_value(minimum, module_name)[0]['value']

        if isinstance(maximum, str):
            if maximum != 'MAX':
                maximum = self.lookup_value(maximum, module_name)[0]['value']

        return minimum, maximum, has_extension_marker

    def get_restricted_to_range(self, type_descriptor, module_name):
        restricted_to = type_descriptor['restricted-to']

        if isinstance(restricted_to[0], tuple):
            minimum, maximum = restricted_to[0]
        else:
            minimum = restricted_to[0]
            maximum = restricted_to[0]

        if isinstance(minimum, str):
            try:
                minimum = float(minimum)
            except ValueError:
                if not is_type_name(minimum):
                    minimum = self.lookup_value(minimum, module_name)[0]['value']

        if isinstance(maximum, str):
            try:
                maximum = float(maximum)
            except ValueError:
                if not is_type_name(maximum):
                    maximum = self.lookup_value(maximum, module_name)[0]['value']

        has_extension_marker = (EXTENSION_MARKER in restricted_to)

        return minimum, maximum, has_extension_marker

    def get_with_components(self, type_descriptor):
        return type_descriptor.get('with-components', None)

    def get_object_set(self,
                       table,
                       type_name,
                       module_name):
        name, location = table
        print('location', location)
        compiled_set = self.compiled_sets[module_name][name]
        object_set_descriptor, _ = self.lookup_object_set_descriptor(
            name,
            module_name)
        object_class_descriptor, _ = self.lookup_object_class_descriptor(
            object_set_descriptor['class'],
            module_name)
        object_set = {}
        members = object_set_descriptor['members']

        for object_set_item, compiled_item in zip(members, compiled_set):
            if not isinstance(object_set_item, dict):
                continue

            compiled_type = compiled_item[type_name]
            keys = []

            for member in object_class_descriptor['members']:
                member_name = member['name']

                if is_class_value(member_name):
                    keys.append(object_set_item[member_name])

            value_object_set = object_set

            for key in keys[:-1]:
                if key not in value_object_set:
                    value_object_set[key] = {}

                value_object_set = value_object_set[key]

            if keys[-1] in value_object_set:
                raise CompileError('Duplicated object set entry values.')

            value_object_set[keys[-1]] = compiled_type

        return object_set

    def is_explicit_tag(self, type_descriptor):
        try:
            return type_descriptor['tag']['kind'] == 'EXPLICIT'
        except KeyError:
            pass

        return False

    def lookup_in_modules(self, section, debug_string, name, module_name):
        begin_debug_string = debug_string[:1].upper() + debug_string[1:]
        module = self._specification[module_name]
        value = None

        if name in module[section]:
            value = module[section][name]
        else:
            for from_module_name, imports in module['imports'].items():
                if name in imports:
                    try:
                        from_module = self._specification[from_module_name]
                    except KeyError:
                        raise CompileError(
                            "Module '{}' cannot import {} '{}' from missing "
                            "module '{}'.".format(module_name,
                                                  debug_string,
                                                  name,
                                                  from_module_name))

                    try:
                        value = from_module[section][name]
                    except KeyError:
                        raise CompileError(
                            "{} '{}' imported by module '{}' not found in "
                            "module '{}'.".format(begin_debug_string,
                                                  name,
                                                  module_name,
                                                  from_module_name))

                    module_name = from_module_name
                    break

        if value is None:
            raise CompileError("{} '{}' not found in module '{}'.".format(
                begin_debug_string,
                name,
                module_name))

        return value, module_name

    def lookup_type_descriptor(self, type_name, module_name):
        return self.lookup_in_modules('types', 'type', type_name, module_name)

    def lookup_value(self, value_name, module_name):
        return self.lookup_in_modules('values', 'value', value_name, module_name)

    def lookup_object_class_descriptor(self, object_class_name, module_name):
        return self.lookup_in_modules('object-classes',
                                      'object class',
                                      object_class_name,
                                      module_name)

    def lookup_object_class_type_name(self, type_name, module_name):
        class_name, member_name = type_name.split('.')
        result = self.lookup_object_class_descriptor(class_name,
                                                     module_name)
        object_class_descriptor, module_name = result

        for member in object_class_descriptor['members']:
            if member['name'] == member_name:
                return member['type'], module_name

    def lookup_object_set_descriptor(self, object_set_name, module_name):
        return self.lookup_in_modules('object-sets',
                                      'object set',
                                      object_set_name,
                                      module_name)

    def get_compiled_type(self, name, type_name, module_name):
        try:
            return self.compiled[module_name][type_name][name]
        except KeyError:
            return None

    def set_compiled_type(self, name, type_name, module_name, compiled):
        if module_name not in self.compiled:
            self.compiled[module_name] = {}

        if type_name not in self.compiled[module_name]:
            self.compiled[module_name][type_name] = {}

        self.compiled[module_name][type_name][name] = compiled

    def convert_object_class_type_descriptor(self, type_descriptor, module_name):
        type_name, module_name = self.lookup_object_class_type_name(
            type_descriptor['type'],
            module_name)
        type_descriptor = deepcopy(type_descriptor)
        type_descriptor['type'] = type_name

        return type_descriptor, module_name

    def copy(self, compiled_type):
        if not isinstance(compiled_type, Recursive):
            compiled_type = copy(compiled_type)

        return compiled_type

    def set_compiled_restricted_to(self, compiled, type_descriptor, module_name):
        compiled = self.copy(compiled)
        compiled.set_restricted_to_range(
            *self.get_restricted_to_range(type_descriptor,
                                          module_name))

        return compiled

    def external_type_descriptor(self):
        return {
            'type': 'SEQUENCE',
            'tag': {
                'class': 'UNIVERSAL',
                'number': 8,
                'kind': 'IMPLICIT'
            },
            'members': [
                {
                    'name': 'direct-reference',
                    'type': 'OBJECT IDENTIFIER',
                    'optional': True
                },
                {
                    'name': 'indirect-reference',
                    'type': 'INTEGER',
                    'optional': True
                },
                {
                    'name': 'data-value-descriptor',
                    'type': 'ObjectDescriptor',
                    'optional': True
                },
                {
                    'name': 'encoding',
                    'type': 'CHOICE',
                    'members': [
                        {
                            'name': 'single-ASN1-type',
                            'type': 'NULL',  # ToDo: Should be ABSTRACT-SYNTAX.&Type
                            'tag': {
                                'number': 0
                            }
                        },
                        {
                            'name': 'octet-aligned',
                            'type': 'OCTET STRING',
                            'tag': {
                                'number': 1,
                                'kind': 'IMPLICIT'
                            }
                        },
                        {
                            'name': 'arbitrary',
                            'type': 'BIT STRING',
                            'tag': {
                                'number': 2,
                                'kind': 'IMPLICIT'
                            }
                        }
                    ]
                }
            ]
        }

    def object_descriptor_type_descriptor(self):
        return {
            'type': 'GraphicString',
            'tag': {
                'class': 'UNIVERSAL',
                'number': 7,
                'kind': 'IMPLICIT'
            }
        }


def enum_values_as_dict(values):
    return {
        value[1]: value[0]
        for value in values
        if value != EXTENSION_MARKER
    }


def enum_values_split(values):
    if EXTENSION_MARKER in values:
        index = values.index(EXTENSION_MARKER)

        return values[:index], values[index + 1:]
    else:
        return values, None


def pre_process(specification):
    return Compiler(specification).pre_process()
