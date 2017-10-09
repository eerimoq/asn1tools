"""Base Compiler class used by all codecs.

"""

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

        try:
            minimum = self.lookup_value(minimum, module_name)[0]['value']
        except KeyError:
            pass

        try:
            maximum = self.lookup_value(maximum, module_name)[0]['value']
        except KeyError:
            pass

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

        try:
            minimum = self.lookup_value(minimum, module_name)[0]['value']
        except KeyError:
            pass

        try:
            maximum = self.lookup_value(maximum, module_name)[0]['value']
        except KeyError:
            pass

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
                    from_module = self._specification[from_module_name]
                    type_descriptor = from_module['types'][type_name]
                    module_name = from_module_name
                    break

        if type_descriptor is None:
            raise KeyError("Type '{}' not found.".format(type_name))

        return type_descriptor, module_name

    def lookup_value(self, value_name, module_name):
        module = self._specification[module_name]
        value = None

        if value_name in module['values']:
            value = module['values'][value_name]
        else:
            for from_module_name, imports in module['imports'].items():
                if value_name in imports:
                    from_module = self._specification[from_module_name]
                    value = from_module['values'][value_name]
                    module_name = from_module_name
                    break

        if value is None:
            raise KeyError("Value '{}' not found.".format(value_name))

        return value, module_name
