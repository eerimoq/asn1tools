"""Base Compiler class used by all codecs.

"""

from copy import deepcopy
from ..errors import CompileError


class Compiler(object):

    def __init__(self, specification):
        self._specification = specification

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

    def is_explicit_tag(self, type_descriptor, module_name):
        try:
            return type_descriptor['tag']['kind'] == 'EXPLICIT'
        except KeyError:
            pass

        try:
            tags = self._specification[module_name].get('tags', None)
            return bool(type_descriptor['tag']) and (tags != 'IMPLICIT')
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
