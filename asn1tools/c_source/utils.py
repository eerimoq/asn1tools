import re


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
