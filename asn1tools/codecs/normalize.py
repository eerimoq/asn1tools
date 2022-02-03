def choice(data):
    """Choices should be represented as a tuple of (name, value).  Some parsers
    that aren't aware of ASN.1 parse things that look like choices into a dict
    with a single entry: {name: value}. Convert those into the tuple, to
    accommodate more parsers."""
    if isinstance(data, dict) and len(data) == 1:
        key = data.keys().__iter__().__next__()
        if isinstance(key, str):
            return (key, data[key])

    return data
