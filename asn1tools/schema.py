"""ASN.1 schema (aka module) type definitions.

"""

class Item(object):
    """Abstract base class of an item. All type definitions should
    subclass this class.

    """

    def __init__(self,
                 name,
                 default=None,
                 tag=None,
                 optional=False,
                 choices=None):
        self._name = name
        self._default = default
        self._tag = tag
        self._optional = optional
        self._choices = choices

    @property
    def name(self):
        """The name of the item.

        """

        return self._name

    def dump_lines(self):
        raise NotImplementedError()

    def dump_qualifiers(self):
        string = ''

        if self._default is not None:
            if isinstance(self._default, str):
                string += ' DEFAULT "{}"'.format(self._default)
            else:
                string += ' DEFAULT {}'.format(self._default)

        if self._optional:
            string += ' OPTIONAL'

        return string

    def __str__(self):
        return '\n'.join(self.dump_lines())


class Module(Item):
    """The DEFINITIONS type.

    """

    def __init__(self, name, items, **kwargs):
        super(Module, self).__init__(name, **kwargs)
        self._items = items

    @property
    def items(self):
        """A list of all items in the module.

        """

        return self._items

    def dump_lines(self):
        return ([self.name + ' DEFINITIONS ::= BEGIN']
                + _indent_lines(_dump_list_lines(self._items))
                + ['END'])


class Sequence(Item):
    """The SEQUENCE type.

    """

    def __init__(self, name, items, **kwargs):
        super(Sequence, self).__init__(name, **kwargs)
        self._items = items

    @property
    def items(self):
        """A list of all items in the sequence.

        """

        return self._items

    def dump_lines(self):
        return ([self.name + ' ::= SEQUENCE {']
                + _indent_lines(_dump_list_lines(self._items))
                + ['}'])


class Integer(Item):
    """The INTEGER type.

    """

    def dump_lines(self):
        return [self.name + ' INTEGER' + self.dump_qualifiers()]


def _indent_lines(lines):
    return ['  ' + line for line in lines]


def _dump_list_lines(items):
    lines = []

    for item in items:
        item_lines = item.dump_lines()

        if item is not items[-1]:
            item_lines[-1] += ','

        lines += item_lines

    return lines
