"""ASN.1 schema (aka module) type definitions.

"""

class Item(object):
    """Abstract base class of an item. All ASN.1 type definitions should
    subclass this class.

    """

    def __init__(self,
                 name=None,
                 default=None,
                 tag=None,
                 optional=False,
                 values=None):
        self._name = name
        self._default = default
        self._tag = tag
        self._optional = optional
        self._values = values

    @property
    def name(self):
        """The name of the item, or None if unavailable.

        """

        return self._name

    @property
    def default(self):
        """The default value of the item, or None is unavailable.

        """

        return self._default

    @property
    def tag(self):
        """The tag of the item, or None is unavailable.

        """

        return self._tag

    @property
    def optional(self):
        """``True`` if the item is optional, otherwise ``False``.

        """

        return self._optional

    @property
    def values(self):
        """The values of the item, or None is unavailable.

        """

        return self._values

    def dump_lines(self, assignment=False):
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
    """The ASN.1 DEFINITIONS type.

    """

    def __init__(self, name, items, **kwargs):
        super(Module, self).__init__(name, **kwargs)
        self.items = items

    def get_item_by_name(self, name):
        for item in self.items:
            if item.name == name:
                return item

        raise LookupError("No item with name '{}'.".format(name))

    def dump_lines(self, assignment=False):
        return ([self.name + ' DEFINITIONS ::= BEGIN']
                + _indent_lines(_dump_list_lines(self.items, assignment=True))
                + ['END'])


class Sequence(Item):
    """The ASN.1 SEQUENCE type.

    """

    def __init__(self, name=None, items=None, **kwargs):
        super(Sequence, self).__init__(name, **kwargs)

        if items is None:
            items = getattr(self.__class__, 'items')

        self.items = items

    def dump_lines(self, assignment=False):
        if self.name is None:
            header = ['SEQUENCE {']
        elif assignment:
            header = [self.name + ' ::= SEQUENCE {']
        else:
            header = [self.name + ' SEQUENCE {']

        return (header
                + _indent_lines(_dump_list_lines(self.items))
                + ['}' + self.dump_qualifiers()])


class Choice(Item):
    """The ASN.1 CHOICE type.

    """

    def __init__(self, name, items=None, **kwargs):
        super(Choice, self).__init__(name, **kwargs)

        if items is None:
            items = getattr(self.__class__, 'items')

        self.items = items

    def dump_lines(self, assignment=False):
        return ([self.name + ' CHOICE {']
                + _indent_lines(_dump_list_lines(self.items))
                + ['}' + self.dump_qualifiers()])


class Enumerated(Item):
    """The ASN.1 ENUMERATED type.

    """

    def __init__(self, name=None, values=None, **kwargs):
        super(Enumerated, self).__init__(name, **kwargs)

        if values is None:
            values = getattr(self.__class__, 'values')

        self.values = values

    def dump_lines(self, assignment=False):
        return ([self.name + ' ENUMERATED {']
                + _indent_lines(['{}({})'.format(value, key)
                                 for key, value in self.values.items()])
                + ['}' + self.dump_qualifiers()])


class Boolean(Item):
    """The ASN.1 BOOLEAN type.

    """

    def dump_lines(self, assignment=False):
        return [self.name + ' BOOLEAN' + self.dump_qualifiers()]


class Integer(Item):
    """The ASN.1 INTEGER type.

    """

    def dump_lines(self, assignment=False):
        return [self.name + ' INTEGER' + self.dump_qualifiers()]


class IA5String(Item):
    """The ASN.1 IA5String type.

    """

    def dump_lines(self, assignment=False):
        return [self.name + ' IA5String' + self.dump_qualifiers()]


class UTF8String(Item):
    """The ASN.1 UTF8String type.

    """

    def dump_lines(self, assignment=False):
        return [self.name + ' UTF8String' + self.dump_qualifiers()]


class SequenceOf(Item):
    """The ASN.1 SEQUENCE OF type.

    """

    def __init__(self, name=None, item=None, **kwargs):
        super(SequenceOf, self).__init__(name, **kwargs)

        if item is None:
            item = getattr(self.__class__, 'item')

        self.item = item

    def dump_lines(self, assignment=False):
        return ([self.name + ' SEQUENCE OF']
                + _indent_lines(self.item.dump_lines())
                + [self.dump_qualifiers()])


class BitString(Item):
    """The ASN.1 BIT STRING type.

    """

    def dump_lines(self, assignment=False):
        return [self.name + ' BIT STRING' + self.dump_qualifiers()]


class OctetString(Item):
    """The ASN.1 OCTET STRING type.

    """

    def dump_lines(self, assignment=False):
        return [self.name + ' OCTET STRING' + self.dump_qualifiers()]


def _indent_lines(lines):
    return ['    ' + line for line in lines]


def _dump_list_lines(items, assignment=False):
    lines = []

    for item in items:
        item_lines = item.dump_lines(assignment)

        if item is not items[-1]:
            item_lines[-1] += ','

        lines += item_lines

    return lines
