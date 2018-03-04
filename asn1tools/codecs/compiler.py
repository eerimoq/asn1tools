"""Base Compiler class used by all codecs.

"""

from copy import deepcopy
from ..errors import CompileError


def flatten(dlist):
    flist = []

    for item in dlist:
        if isinstance(item, list):
            flist.extend(item)
        else:
            flist.append(item)

    return flist


class Compiler(object):

    def __init__(self, specification):
        self._specification = specification
        self._types_backtrace = []

    def types_backtrace_push(self, type_name):
        self._types_backtrace.append(type_name)

    def types_backtrace_pop(self):
        self._types_backtrace.pop()

    @property
    def types_backtrace(self):
        return self._types_backtrace

    def process(self):
        self.pre_process()

        compiled = {}

        for module_name in self._specification:
            items = self._specification[module_name]['types'].items()

            for type_name, type_descriptor in items:
                self.types_backtrace_push(type_name)
                compiled_type = self.process_type(type_name,
                                                  type_descriptor,
                                                  module_name)
                self.types_backtrace_pop()

                if module_name not in compiled:
                    compiled[module_name] = {}

                compiled[module_name][type_name] = compiled_type

        return compiled

    def pre_process(self):
        for module_name in self._specification:
            module = self._specification[module_name]

            self.pre_process_components_of(module, module_name)

            if module['extensibility-implied']:
                self.pre_process_extensibility_implied(module)

            self.pre_process_tags(module, module_name)

        return self._specification

    def pre_process_components_of(self, module, module_name):
        for type_descriptor in module['types'].values():
            self.pre_process_components_of_type(type_descriptor,
                                                module_name)

    def pre_process_components_of_type(self, type_descriptor, module_name):
        type_name = type_descriptor['type']

        if type_name in ['SEQUENCE', 'SET', 'CHOICE']:
            type_descriptor['members'] = self.pre_process_components_of_expand_members(
                type_descriptor['members'],
                module_name)

    def pre_process_components_of_expand_members(self, members, module_name):
        expanded_members = []

        for member in members:
            if 'components-of' in member:
                type_descriptor, inner_module_name = self.lookup_type_descriptor(
                    member['components-of'],
                    module_name)
                inner_members = self.pre_process_components_of_expand_members(
                    type_descriptor['members'],
                    inner_module_name)

                for inner_member in inner_members:
                    if inner_member == '...':
                        break

                    expanded_members.append(deepcopy(inner_member))
            else:
                expanded_members.append(member)

        return expanded_members

    def pre_process_extensibility_implied(self, module):
        for type_descriptor in module['types'].values():
            self.pre_process_extensibility_implied_type(type_descriptor)

    def pre_process_extensibility_implied_type(self, type_descriptor):
        type_name = type_descriptor['type']

        if type_name in ['SEQUENCE', 'SET', 'CHOICE']:
            members = type_descriptor['members']

            for member in members:
                if member == '...' or isinstance(member, list):
                    continue

                self.pre_process_extensibility_implied_type(member)

            if '...' not in members:
                members.append('...')

    def pre_process_tags(self, module, module_name):
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

            if 'kind' not in tag:
                if self.resolve_type_name(type_name, module_name) == 'CHOICE':
                    tag['kind'] = 'EXPLICIT'
                elif module_tags in ['IMPLICIT', 'EXPLICIT']:
                    tag['kind'] = module_tags
                else:
                    tag['kind'] = 'IMPLICIT'

        if type_name in ['SEQUENCE', 'SET', 'CHOICE']:
            self.pre_process_tags_type_members(type_descriptor,
                                               module_tags,
                                               module_name)

        if type_name in ['SEQUENCE OF', 'SET OF']:
            self.pre_process_tags_type(type_descriptor['element'],
                                       module_tags,
                                       module_name)

    def pre_process_tags_type_members(self,
                                      type_descriptor,
                                      module_tags,
                                      module_name):
        def is_any_member_tagged(members):
            for member in members:
                if member == '...':
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
            if member == '...':
                continue

            if number is not None:
                if 'tag' not in member:
                    member['tag'] = {}

                member['tag']['number'] = number
                number += 1

            self.pre_process_tags_type(member,
                                       module_tags,
                                       module_name)

    def resolve_type_name(self, type_name, module_name):
        try:
            while True:
                type_descriptor, module_name = self.lookup_type_descriptor(
                    type_name,
                    module_name)
                type_name = type_descriptor['type']
        except CompileError:
            pass

        return type_name

    def process_type(self, type_name, type_descriptor, module_name):
        return NotImplementedError()

    def get_size_range(self, type_descriptor, module_name):
        """Returns a tuple of the minimum and maximum values allowed according
        the the ASN.1 specification SIZE parameter. Returns (None,
        None) if the type does not have a SIZE parameter.

        """

        size = type_descriptor.get('size', None)

        if size is None:
            minimum = None
            maximum = None
        elif isinstance(size, int):
            minimum = size
            maximum = size
        elif isinstance(size, list):
            if isinstance(size[0], tuple):
                minimum, maximum = size[0]
            else:
                minimum = size[0]
                maximum = size[0]
        else:
            raise NotImplementedError()

        if isinstance(minimum, str):
            minimum = self.lookup_value(minimum, module_name)[0]['value']

        if isinstance(maximum, str):
            maximum = self.lookup_value(maximum, module_name)[0]['value']

        return minimum, maximum

    def get_restricted_to_range(self, type_descriptor, module_name):
        restricted_to = type_descriptor.get('restricted-to', None)

        if restricted_to is None:
            minimum = None
            maximum = None
        elif isinstance(restricted_to, list):
            if isinstance(restricted_to[0], tuple):
                minimum, maximum = restricted_to[0]
            else:
                minimum = restricted_to[0]
                maximum = restricted_to[0]
        else:
            raise NotImplementedError()

        if isinstance(minimum, str):
            minimum = self.lookup_value(minimum, module_name)[0]['value']

        if isinstance(maximum, str):
            maximum = self.lookup_value(maximum, module_name)[0]['value']

        return minimum, maximum

    def is_explicit_tag(self, type_descriptor):
        try:
            return type_descriptor['tag']['kind'] == 'EXPLICIT'
        except KeyError:
            pass

        return False

    def lookup_type_descriptor(self, type_name, module_name):
        module = self._specification[module_name]
        type_descriptor = None

        if type_name in module['types']:
            type_descriptor = module['types'][type_name]
        else:
            for from_module_name, imports in module['imports'].items():
                if type_name in imports:
                    try:
                        from_module = self._specification[from_module_name]
                    except KeyError:
                        raise CompileError(
                            "Module '{}' cannot import type '{}' from missing "
                            "module '{}'.".format(module_name,
                                                  type_name,
                                                  from_module_name))

                    try:
                        type_descriptor = from_module['types'][type_name]
                    except KeyError:
                        raise CompileError(
                            "Type '{}' imported by module '{}' not found "
                            "in module '{}'.".format(type_name,
                                                     module_name,
                                                     from_module_name))

                    module_name = from_module_name
                    break

        if type_descriptor is None:
            raise CompileError("Type '{}' not found in module '{}'.".format(
                type_name,
                module_name))

        return type_descriptor, module_name

    def lookup_value(self, value_name, module_name):
        module = self._specification[module_name]
        value = None

        if value_name in module['values']:
            value = module['values'][value_name]
        else:
            for from_module_name, imports in module['imports'].items():
                if value_name in imports:
                    try:
                        from_module = self._specification[from_module_name]
                    except KeyError:
                        raise CompileError(
                            "Module '{}' cannot import value '{}' from missing "
                            "module '{}'.".format(module_name,
                                                  value_name,
                                                  from_module_name))

                    try:
                        value = from_module['values'][value_name]
                    except KeyError:
                        raise CompileError(
                            "Value '{}' imported by module '{}' not found "
                            "in module '{}'.".format(value_name,
                                                     module_name,
                                                     from_module_name))

                    module_name = from_module_name
                    break

        if value is None:
            raise CompileError("Value '{}' not found in module '{}'.".format(
                value_name,
                module_name))

        return value, module_name

    def lookup_object_class_descriptor(self, object_class_name, module_name):
        module = self._specification[module_name]
        object_class_descriptor = None

        if object_class_name in module['object-classes']:
            object_class_descriptor = module['object-classes'][object_class_name]
        else:
            raise NotImplementedError()

        if object_class_descriptor is None:
            raise CompileError("Object class '{}' not found in module '{}'.".format(
                object_class_name,
                module_name))

        return object_class_descriptor, module_name

    def convert_class_member_type(self, type_descriptor, module_name):
        type_name = type_descriptor['type']
        class_name, member_name = type_name.split('.')
        result = self.lookup_object_class_descriptor(class_name,
                                                     module_name)
        object_class_descriptor, module_name = result
        type_descriptor = deepcopy(type_descriptor)

        for member in object_class_descriptor['members']:
            if member['name'] == member_name:
                type_descriptor['type'] = member['type']
                break

        return type_descriptor


def enum_values_as_dict(values):
    return {
        value[1]: value[0]
        for value in values
        if value != '...'
    }


def enum_values_split(values):
    if '...' in values:
        index = values.index('...')
        return values[:index], values[index + 1:]
    else:
        return values, None


def pre_process(specification):
    return Compiler(specification).pre_process()
