from pyparsing import ParseResults
from typing import Union, Tuple, IO
import textwrap
from cythonpeg.utilities import partial_cython_2_python, complete_cython_2_python
from cythonpeg.definitions import cython_parser

INDENT = "    "


def set_indent(indent: str):
    global INDENT
    INDENT = indent


def expression2str(expression: Union[ParseResults, str]):
    """EXPRESSION parsed tree to string"""

    if isinstance(expression, ParseResults):
        expression_string = ""

        if expression.getName() == "list":
            expression_string += "[" + ", ".join(expression2str(e) for e in expression) + "]"

        elif expression.getName() == "set":
            expression_string += "{" + ", ".join(expression2str(e) for e in expression) + "}"

        elif expression.getName() == "tuple":
            expression_string += "(" + ", ".join(expression2str(e) for e in expression) + ")"

        elif expression.getName() == "dict":
            expression_string += (
                "{" + ", ".join(f"{expression2str(k)} : {expression2str(v)}" for k, v in expression) + "}"
            )
        else:
            for e in expression:
                expression_string += expression2str(e)

        return expression_string

    elif isinstance(expression, str):
        return expression


def type2str(type_tree: ParseResults):
    """type_definition parsed tree to string"""

    def _type2_str(type_tree: ParseResults):
        type_name, type_bracket, type_default = type_tree

        if type_bracket:
            bracket_str = "[" + ", ".join(_type2_str(arg) for arg in type_bracket) + "]" if type_bracket else ""
        else:
            bracket_str = ""

        type_default_str = f"={expression2str(type_default)}" if type_default else ""

        return f"{partial_cython_2_python(type_name)}{bracket_str}{type_default_str}"

    return complete_cython_2_python(_type2_str(type_tree))


def arg2str(arg: ParseResults):
    """python_argument_definition parsed tree to string"""

    arg_name, arg_type, arg_default = arg

    if isinstance(arg_type, ParseResults):
        type_str = type2str(arg_type)
    else:
        type_str = ""

    type_str = f": {type_str}" if type_str else ""
    arg_default_str = f"={expression2str(arg_default)}" if arg_default else ""

    return f"{arg_name}{type_str}{arg_default_str}"


def args2str(args: ParseResults, newlines: bool = False):
    """python_arguments_definition parsed tree to string"""

    def format_arg(arg):
        if arg[0] == "self":
            return "self"  # handle unique case cdef inside class
        if arg.getName() == "python_argument":
            return arg2str(arg)
        elif arg.getName() == "cython_argument":
            return cythonarg2str(arg)

    joiner = f",\n{INDENT}" if newlines else ", "
    return joiner.join(format_arg(arg) for arg in args)


def def2str(result: ParseResults):
    """function_definition parsed tree to string"""

    decleration, docs, body = result
    name, args, ret = decleration

    return_str = type2str(ret) if ret else ""
    return_str = f" -> {return_str}" if return_str else ""
    doc_str = f'\n{INDENT}"""{docs}"""' if docs else ""

    arg_str = args2str(args)
    if len(arg_str) > 100:
        arg_str = args2str(args, newlines=True)

    return f"def {name}({arg_str}){return_str}:{doc_str}\n{INDENT}...\n"


def cythonarg2str(arg: ParseResults):
    t, n, d = arg
    type_str = type2str(t)
    default_str = f" = {expression2str(d)}" if d else ""
    return f"{n}: {type_str}{default_str}"


def cythonargs2str(args: ParseResults, newlines: bool = False):
    """cython_arguments_definition parsed tree to string"""

    def format_arg(arg):
        if arg[0] == "self":
            return "self"  # handle unique case cdef inside class
        if arg.getName() == "python_argument":
            return arg2str(arg)
        elif arg.getName() == "cython_argument":
            return cythonarg2str(arg)

    joiner = f",\n{INDENT}" if newlines else ", "
    return joiner.join([format_arg(arg) for arg in args])


def cdef2str(result: ParseResults):
    """cython_function_definition parsed tree to string"""

    decleration, docs, body = result
    ret, name, args, gil = decleration

    doc_str = f'\n{INDENT}"""{docs}"""' if docs else ""
    ret_str = type2str(ret) if ret else ""
    ret_str = f" -> {ret_str}" if ret_str else ""

    arg_str = cythonargs2str(args)
    if len(arg_str) > 100:
        arg_str = cythonargs2str(args, newlines=True)

    return f"def {name}({arg_str}){ret_str}:{doc_str}\n{INDENT}..." + "\n"


def enum2str(result: ParseResults):
    """python_class_definition parsed tree to string (enum)"""

    decleration, docs, body = result
    name, parent = decleration

    class_str = ""
    doc_str = f'\n{INDENT}"""{docs}"""' if docs else ""
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}" + "\n"

    for b in body:
        class_str += INDENT + b + "\n"

    return class_str


def class2str(result: ParseResults):
    """python_class_definition parsed tree to string (enum)"""

    decleration, docs, body = result
    name, parent = decleration

    if parent == "Enum":
        return enum2str(result)

    doc_str = f'\n{INDENT}"""{docs}"""' if docs else ""
    class_str = f"class {name}{f'({parent})' if parent else ''}:{doc_str}\n\n"

    element_string = []
    for i, b in enumerate(body):
        if not isinstance(b, ParseResults):
            continue

        parser_name = b.getName()
        if parser_name == "class_decleration":
            result = (b, body[i + 1], body[i + 2])
            element_string.append(textwrap.indent(class2str(result), INDENT))

        elif parser_name == "def_decleration":
            result = (b, body[i + 1], body[i + 2])
            element_string.append(textwrap.indent(def2str(result), INDENT))

        elif parser_name == "cdef_decleration":
            result = (b, body[i + 1], body[i + 2])
            element_string.append(textwrap.indent(cdef2str(result), INDENT))

    if not len(element_string):
        class_str += f"{INDENT}...\n"
    else:
        class_str += "\n".join(element_string)

    return class_str


def cenum2str(result: ParseResults):
    """enum_definition parsed tree to string"""
    name, body = result
    str = ""
    str += f"class {name[0]}(Enum):\n{INDENT}"
    result.pop(0)
    return str + f"\n{INDENT}".join([f"{imp[0]}: int" for imp in body]) + "\n"


def struct2str(result):
    """cython_struct_definition parsed tree to string"""

    decleration, docs, body = result
    parent = ""

    class_str = ""
    doc_str = f'\n{INDENT}"""{docs}"""' if docs else ""
    class_str += f"class {decleration[0]}{f'({parent})' if parent else ''}:{doc_str}\n"

    element_string = []
    for b in body:
        type_str, names = b
        if names.length == 1:
            element_string.append(f"{INDENT}{names[0]}: {type2str(type_str)}")
        else:
            for name in names:
                element_string.append(f"{INDENT}{name}: {type2str(type_str)}")

    return class_str + "\n".join(element_string) + "\n"


def cclass2str(result: ParseResults):
    """cython_class_definition parsed tree to string"""

    decleration, docs, body = result
    name, parent = decleration

    class_str = ""
    doc_str = f'\n{INDENT}"""{docs}"""' if docs else ""
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}\n\n"

    element_string = []
    for i, b in enumerate(body):
        if not isinstance(b, ParseResults):
            continue

        parser_name = b.getName()
        if parser_name == "cclass_decleration":
            result = (b, body[i + 1], body[i + 2])
            element_string.append(textwrap.indent(cclass2str(result), INDENT))

        elif parser_name == "def_decleration":
            result = (b, body[i + 1], body[i + 2])
            element_string.append(textwrap.indent(def2str(result), INDENT))

        elif parser_name == "cdef_decleration":
            result = (b, body[i + 1], body[i + 2])
            element_string.append(textwrap.indent(cdef2str(result), INDENT))

    if not len(element_string):
        class_str += f"{INDENT}...\n"
    else:
        class_str += "\n".join(element_string)

    return class_str


def name_alias_2_str(name, alias):
    alias_str = f" as {alias}" if alias else ""
    return f"{name}{alias_str}"


def import2str(result: ParseResults, newlines=True):
    """import2str_definition parsed tree to string"""

    import_str = ""
    if len(result) == 1:
        import_str += f"import {', '.join(name_alias_2_str(n, a) for n, a in result[0])}"

    elif len(result) == 2:
        if newlines and len(result[1]) > 2:
            # import_str += f"from {result[0]} import (\n"
            # for i, r in enumerate(result[1]):
            #     import_str += f"{INDENT}{r}"
            #     import_str += "\n" if len(result[1]) == i+1 else ",\n"
            # import_str += ')'

            nl = "\n"
            tab = "\t"
            import_str += f"from {result[0]} import ({nl}{f',{nl}'.join(f'{tab}{name_alias_2_str(n, a)}' for n, a in result[1])}{nl})"
        else:
            import_str += f"from {result[0]} import {', '.join(name_alias_2_str(n, a) for n, a in result[1])}"

    return import_str


def import_section2str(result: ParseResults):
    """import_section2str_definition parsed tree to string"""
    return "\n".join([import2str(imp) for imp in result]) + "\n"


def dataclass2str(result: ParseResults):
    name, docs, body = result
    dataclass_str = ""
    dataclass_str += "@dataclass" + "\n"
    dataclass_str += f"class {name}:" + "\n"
    dataclass_str += f'{INDENT}"""{docs}"""\n'
    dataclass_str += textwrap.indent(recursive_body(body), INDENT)
    return dataclass_str


def unimplimented2str(result: ParseResults):
    return ""


def recursive_body(body: ParseResults):
    """IndentedBlock(restOfLine) parsed tree to string"""
    element_string = []
    for b in body:
        if isinstance(b, ParseResults):
            element_string.append(textwrap.indent(recursive_body(b), INDENT))

        elif isinstance(b, str):
            element_string.append(b)

    return "\n".join(element_string) + "\n"


def ctypedef2str(result: ParseResults):
    """ctypedef parsed tree to string"""

    t, n = result
    return n + " = " + t[0]


def ctypedef_section2str(result: ParseResults):
    """ctypedef section parsed tree to string"""

    return "\n".join([ctypedef2str(imp) for imp in result]) + "\n"


def cython_string_2_stub(input_code: str) -> Tuple[str, str]:
    """tree traversal and translation of ParseResults to string representation"""

    # indentblock needs newline as sentinal
    input_code += "\n"

    # PEG top down scan generator
    tree = cython_parser.scan_string(input_code)

    # 3.8+ compatible switch
    parser = {
        "def": def2str,
        "cdef": cdef2str,
        "class": class2str,
        "cenum": cenum2str,
        "cclass": cclass2str,
        "cstruct": struct2str,
        "dataclass": dataclass2str,
        "import_section": import_section2str,
        "ctypedef_section": ctypedef_section2str,
    }

    # ParseResults -> Python Stub Element
    def parse_branch(branch: Tuple[ParseResults, int, int]):
        result, start, end = branch
        return parser.get(result.getName(), unimplimented2str)(result), start, end

    parsed_tree = [parse_branch(b) for b in tree]

    if len(parsed_tree) == 0:
        return "", input_code

    tree_str, start, end = zip(*parsed_tree)

    # TODO: this code is ugly
    mutable_string = list(input_code + " ")
    for s, e in zip(start, end):
        for i in range(s, e):
            mutable_string[i] = ""

    tree_str = [s for s in tree_str if s]
    stub_file = ""
    stub_file += "\n".join(tree_str)
    unparsed_lines = "".join(mutable_string).strip()

    return stub_file, unparsed_lines


def cython_file_2_stub(file: IO[str]) -> Tuple[str, str]:
    with open(file, mode="r") as f:
        input_code = f.read()
    return cython_string_2_stub(input_code)
