"""Basic Octet Encoding Rules (OER) codec generator.

"""

from .utils import camel_to_snake_case


STRUCT_FMT = '''\
struct {module_name}_{type_name}_t {{
}};
'''


DECLARATION_FMT = '''\
ssize_t {module_name}_{type_name}_encode(
    uint8_t *dsp_t,
    size_t size,
    struct {module_name}_{type_name}_t *src_p);

ssize_t {module_name}_{type_name}_decode(
    struct {module_name}_{type_name}_t *dsp_t,
    uint8_t *src_p,
    size_t size);
'''


DEFINITION_FMT = '''\
ssize_t {module_name}_{type_name}_encode(
    uint8_t *dsp_t,
    size_t size,
    struct {module_name}_{type_name}_t *src_p)
{{
    return (0);
}}

ssize_t {module_name}_{type_name}_decode(
    struct {module_name}_{type_name}_t *dsp_t,
    uint8_t *src_p,
    size_t size)
{{
    return (0);
}}
'''


def _generate_struct(module_name, type_name):
    return STRUCT_FMT.format(module_name=module_name,
                             type_name=type_name)


def _generate_declaration(module_name, type_name):
    return DECLARATION_FMT.format(module_name=module_name,
                                  type_name=type_name)


def _generate_definition(module_name, type_name):
    return DEFINITION_FMT.format(module_name=module_name,
                                 type_name=type_name)


def generate(compiled):
    structs = []
    declarations = []
    definitions = []

    for module_name, module in sorted(compiled.modules.items()):
        module_name = camel_to_snake_case(module_name)

        for type_name, _ in sorted(module.items()):
            type_name = camel_to_snake_case(type_name)

            struct = _generate_struct(module_name, type_name)
            structs.append(struct)

            declaration = _generate_declaration(module_name, type_name)
            declarations.append(declaration)

            definition = _generate_definition(module_name, type_name)
            definitions.append(definition)

    structs = '\n'.join(structs)
    declarations = '\n'.join(declarations)
    definitions = '\n'.join(definitions)

    return structs, declarations, definitions
