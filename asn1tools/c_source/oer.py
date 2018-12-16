"""Basic Octet Encoding Rules (OER) codec generator.

"""

from .utils import camel_to_snake_case
from ..codecs import oer
from ..errors import Error


STRUCT_FMT = '''\
struct {namespace}_{module_name_snake}_{type_name_snake}_t {{
{members}
}};
'''


DECLARATION_FMT = '''\
/**
 * Encode type {type_name} defined in module {module_name}.
 *
 * @param[out] dst_p Buffer to encode into.
 * @param[in] size Size of dst_p.
 * @param[in] src_p Data to encode.
 *
 * @return Encoded data length or negative error code.
 */
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_encode(
    uint8_t *dst_p,
    size_t size,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p);

/**
 * Decode type {type_name} defined in module {module_name}.
 *
 * @param[out] dst_p Decoded data.
 * @param[in] src_p Data to decode.
 * @param[in] size Size of src_p.
 *
 * @return Number of bytes decoded or negative error code.
 */
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_decode(
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p,
    const uint8_t *src_p,
    size_t size);
'''


DEFINITION_FMT = '''\
ssize_t {namespace}_{module_name_snake}_{type_name_snake}_encode(
    uint8_t *dst_p,
    size_t size,
    const struct {namespace}_{module_name_snake}_{type_name_snake}_t *src_p)
{{
    return (0);
}}

ssize_t {namespace}_{module_name_snake}_{type_name_snake}_decode(
    struct {namespace}_{module_name_snake}_{type_name_snake}_t *dst_p,
    const uint8_t *src_p,
    size_t size)
{{
    return (0);
}}
'''


def _format_type_name(length, is_signed):
    type_name = 'int{}_t'.format(length)

    if not is_signed:
        type_name = 'u' + type_name

    return type_name


def type_length(length):
    if length <= 8:
        return 8
    elif length <= 16:
        return 16
    elif length <= 32:
        return 32
    else:
        return 64


def _format_integer(compiled_type):
    if compiled_type.fmt is None:
        raise Error('INTEGER not fixed size.')

    type_name = _format_type_name(8 * compiled_type.length,
                                  compiled_type.fmt[1].islower())

    return '    {} value;'.format(type_name)


def _format_sequence(compiled_type):
    members = []

    for member in compiled_type.root_members:
        members.append('    bool {};'.format(member.name))

    return members


def _generate_struct(namespace, compiled_type, module_name, type_name):
    module_name_snake = camel_to_snake_case(module_name)
    type_name_snake = camel_to_snake_case(type_name)
    members = []

    if isinstance(compiled_type, oer.Integer):
        members.append(_format_integer(compiled_type))
    elif isinstance(compiled_type, oer.Sequence):
        members.extend(_format_sequence(compiled_type))

    return STRUCT_FMT.format(namespace=namespace,
                             module_name_snake=module_name_snake,
                             type_name_snake=type_name_snake,
                             members='\n'.join(members))


def _generate_declaration(namespace, module_name, type_name):
    module_name_snake = camel_to_snake_case(module_name)
    type_name_snake = camel_to_snake_case(type_name)

    return DECLARATION_FMT.format(namespace=namespace,
                                  module_name=module_name,
                                  type_name=type_name,
                                  module_name_snake=module_name_snake,
                                  type_name_snake=type_name_snake)


def _generate_definition(namespace, module_name, type_name):
    module_name_snake = camel_to_snake_case(module_name)
    type_name_snake = camel_to_snake_case(type_name)

    return DEFINITION_FMT.format(namespace=namespace,
                                 module_name_snake=module_name_snake,
                                 type_name_snake=type_name_snake)


def generate(compiled, namespace):
    structs = []
    declarations = []
    definitions = []

    for module_name, module in sorted(compiled.modules.items()):
        for type_name, compiled_type in sorted(module.items()):
            struct = _generate_struct(namespace,
                                      compiled_type.type,
                                      module_name,
                                      type_name)
            structs.append(struct)

            declaration = _generate_declaration(namespace,
                                                module_name,
                                                type_name)
            declarations.append(declaration)

            definition = _generate_definition(namespace,
                                              module_name,
                                              type_name)
            definitions.append(definition)

    structs = '\n'.join(structs)
    declarations = '\n'.join(declarations)
    definitions = '\n'.join(definitions)

    return structs, declarations, definitions
