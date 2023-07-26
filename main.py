from pyparsing import *
import textwrap
from functools import partial

def parentheses_suppress(content):
    return Suppress("(") + Optional(content) + Suppress(")")

def bracket_suppress(content):
    return Suppress("[") + Optional(content) + Suppress("]")

def curl_suppress(content):
    return Suppress("{") + Optional(content) + Suppress("}")

def extend_empty(tokens, n):
    if len(tokens) == 0:
        tokens.extend([""]*n)
    return tokens

# literals
CLASS = Literal("class")
STRUCT = Literal("struct")
DEF = Literal("def")
CPDEF = Literal("cpdef")
CDEF = Literal("cdef")
STRUCT = Literal("struct")

# objects
INTEGER = Word("+-" + nums) + ~FollowedBy(".")
FLOAT = Combine(Word("+-" + nums) + "." + Word(nums))
TRUE = Literal("True")
FALSE = Literal("False")
NONE = Literal("None")
STRING = QuotedString(quoteChar="'") | QuotedString(quoteChar='"')
ENUM = Word(alphanums + '.')
PRIMATIVE = (FLOAT | INTEGER | TRUE | FALSE | NONE | STRING)
OBJECT = Forward()
LIST = Group(bracket_suppress(delimitedList(OBJECT)))
TUPLE = Group(parentheses_suppress(delimited_list(OBJECT)))
DICT = Group(curl_suppress(delimitedList(Group(OBJECT + Suppress(":") + OBJECT))))
SET = Group(curl_suppress(delimited_list(OBJECT)))
NONPRIMATIVE = (LIST | TUPLE | DICT | SET | ENUM)
OBJECT << (NONPRIMATIVE | PRIMATIVE)

# operations
plus = Literal('+')
minus = Literal('-')
mult = Literal('*')
div = Literal('/')

# Define grammar for the entire expression
expression = Forward()
atom = OBJECT | Group(Literal('(') + expression + Literal(')'))
expression << infixNotation(atom, [(mult | div, 2, opAssoc.LEFT), (plus | minus, 2, opAssoc.LEFT),])

# variable and type names
VARIABLE = Word(alphanums+'_')
TWORD = Word(alphanums+'_'+'*'+'.')
TYPE = (TWORD) | Group(parentheses_suppress(delimited_list(TWORD)))
OPTIONALBRACKET = Group(Optional(bracket_suppress(delimited_list(TWORD))))

recursive_class_definition = Forward()
recursive_def_definition = Forward()
recursive_cython_def_definition = Forward()
recursive_cython_class_definition = Forward()
recursive_cython_struct_definition = Forward()

# python type hint and arguments
empty_default_return = ParseResults()
empty_default_return.extend(["", ""])

default_argument = Suppress("=") + expression
argument = Group(VARIABLE + Optional(Suppress(":") + Group(TYPE + OPTIONALBRACKET), default=["", ""]) + Optional(default_argument, default="")) # VARIABLE:TYPE=DEFAULT
arguments = delimitedList(argument)
return_definition = Group(Suppress("->") + TYPE + OPTIONALBRACKET)

# cython type hint and arguments
cython_type_hint_list = Group(bracket_suppress(delimitedList(Literal(":") | Group(VARIABLE+Optional(default_argument, default="")))))
cython_type_hint  = (TYPE + Optional(cython_type_hint_list, default=""))
cython_argument = Group(cython_type_hint + VARIABLE + Optional(default_argument, default=""))
cython_arguments = delimitedList(cython_argument)

# docstring definition
docstring = QuotedString('"""', multiline=True, escQuote='""""')

# python class definition
class_parent = Word(alphanums+'_'+'*'+'.')
class_arguments = parentheses_suppress(class_parent)
class_decleration = Group(CLASS + VARIABLE + Optional(class_arguments, default="") + Suppress(":"))
class_body = IndentedBlock(recursive_class_definition, recursive=True)
class_definition = class_decleration + Optional(docstring, default="") + class_body

# python function definitions
function_arguments = Group(parentheses_suppress(arguments))
function_decleration = Group(DEF + VARIABLE + function_arguments + Optional(return_definition, default=["", []]) + Suppress(":"))
function_body = IndentedBlock(recursive_def_definition, recursive=True)
function_definition = function_decleration + Optional(docstring, default="") + function_body

# cython function definition 
cython_function_arguments = Group(parentheses_suppress(cython_arguments))
cython_function_decleration = Group(Group((DEF | CDEF | CPDEF) + Optional(cython_type_hint + ~cython_function_arguments, default="")) + VARIABLE + cython_function_arguments + Optional(VARIABLE, default="") + Suppress(":")) 
cython_function_body = IndentedBlock(recursive_cython_def_definition, recursive=True)
cython_function_definition = cython_function_decleration + Optional(docstring, default="") + cython_function_body

# cython class definition
cython_class_decleration = Group(Group(CDEF + CLASS) + VARIABLE +  Suppress(":"))
cython_class_body = IndentedBlock(recursive_cython_class_definition, recursive=True)
cython_class_definition = cython_class_decleration + Optional(docstring, default="") + cython_class_body

# cython struct definition
cython_struct_decleration = Group(Group(CDEF + STRUCT) + VARIABLE + Suppress(":"))
cython_struct_body = IndentedBlock(recursive_cython_struct_definition, recursive=True)
cython_struct_definition = cython_struct_decleration + Optional(docstring, default="") + cython_struct_body

# recursive definitions
definitions = (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_class_definition         << definitions
recursive_def_definition           << definitions
recursive_cython_def_definition    << definitions
recursive_cython_class_definition  << definitions
recursive_cython_struct_definition << definitions

python_script_parser = class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition

def args2str(args, newlines=False):
    """convert argument format List[(name, type, default)] into a string representation."""

    def format_arg(n, t, d):

        t = t[0]
        if isinstance(t, ParseResults):
            t = f"{t[0]}[{','.join([t for t in t[1:]])}]"

        type_str = f': {t}' if t else ''
        default_str = f' = {d}' if d else ''
        return f'{n}{type_str}{default_str}'

    joiner = ',\n    ' if newlines else ', '
    return joiner.join(format_arg(n, t, d) for n, t, d in args)

def def2str(name, args, ret, docs, indent=0):

    if len(ret[0]) == 0:
        return_str = ""

    elif isinstance(ret[0], str):
        return_str = ret[0]

        if isinstance(ret[1], ParseResults) and len(ret[1]):
            return_str = return_str + f"[{', '.join([r for r in ret[1]])}]"

    # syntax is not valid for the following
    elif isinstance(ret[0], ParseResults):
        return_str = f"{ret[0]}[{', '.join([t for t in ret[1:]])}]"

    return_str = f" -> {return_str}" if return_str else ''
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    arg_str = args2str(args)

    if len(arg_str) > 150:
        arg_str = args2str(args, newlines=True)

    return textwrap.indent(f"def {name}({arg_str}){return_str}:{doc_str}\n    ...", "    "*indent)

def cythonargs2str(args, newlines=False):
    """convert argument format List[(name, type, default)] into a string representation."""

    def format_arg(t, a, n, d):
        default_str = f' = {d}' if d else ''
        return f'{n}: {t}{default_str}'

    joiner = ',\n    ' if newlines else ', '

    return joiner.join(format_arg(t, a, b, d) for t, a, b, d in args)

def cdef2str(ret, name, args, gil, docs, indent=0):
    doc_str = f'\n    \"""{docs}\"""' if docs else ''

    if isinstance(ret[1], ParseResults):
        ret_str =  f"Tuple[{', '.join(r for r in ret[1])}]"
    elif isinstance(ret[1], str):
        return_check = len(ret) == 3 and isinstance(ret[2], ParseResults)
        return_type = "np.ndarray" if return_check else ret[1] # all memmory views returned as numpy arrays 
        ret_str = f"{return_type}"
    
    ret_str = f" -> {ret_str}" if ret_str else ''
    # return f"def {name}({cythonargs2str(args)}) -> {ret_str}:{doc_str}"
    return textwrap.indent(f"def {name}({cythonargs2str(args)}){ret_str}:{doc_str}\n    ...", "    "*indent)

def cpdef2str(ret, name, args, gil, docs, indent=0):
    doc_str = f'\n    \"""{docs}\"""' if docs else ''

    if isinstance(ret[1], ParseResults):    
        ret_str =  f"Tuple[{', '.join(r for r in ret[1])}]"
        
    elif isinstance(ret[1], str):
        return_check = len(ret) == 3 and isinstance(ret[2], ParseResults)
        return_type = "np.ndarray" if return_check else ret[1] # all memmory views returned as numpy arrays 
        ret_str = f"{return_type}"
    
    ret_str = f" -> {ret_str}" if ret_str else ''
    # return f"def {name}({cythonargs2str(args)}) -> {ret_str}:{doc_str}"
    return textwrap.indent(f"def {name}({cythonargs2str(args)}){ret_str}:{doc_str}\n    ...", "    "*indent)

def class2str(name, parent, docs):
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    return f"class {name}{f'({parent})' if parent else ''}:{doc_str}"

def parse_tree_to_stub_file(parseTree):
    stub_file = "\n".join([
    "import numpy as np",
    "from enum import Enum",
    "from typing import Optional, Tuple, Dict, List, Generator, Union, DefaultDict",
    "\n# type convertions from cython to python",
    "float64 = float32 = double = long = longlong = float",
    "uint64 = uint32 = uint16 = uint8 = short = int",
    "\n"])

    for branch in parseTree:
        result, _, _ = branch

        decleration, docs, body = result
        state = decleration[0]

        if state == "def":
            _, name, args, ret = decleration
            stub_file += def2str(name, args, ret, docs) + '\n'*2

        elif len(state) > 0 and state[0] == "cdef":

            if decleration[0][1] in ["class", "struct"]:

                stub_file += class2str(decleration[1], "", docs) + "\n"
                
                if decleration[0][1] == "struct":
                    for b in body:
                        stub_file += "    " + b + '\n'
                    stub_file += "\n"
                
                elif decleration[0][1] == "class":
                    for i, b in enumerate(body):
                        if len(b) > 0 and b[0][0] in ["def", "cdef"]:
                            docs = body[i+1]
                            print("body", b)
                            ret, name, args, gil = b
                            stub_file += '\n' + cdef2str(ret, name, args, gil, docs, indent=1) + '\n'
                    stub_file += '\n'
                        
                continue
            else:
                ret, name, args, gil = decleration
                stub_file += cdef2str(ret, name, args, gil, docs) + '\n'*2

        elif len(state) > 0 and state[0] == "cpdef":
            ret, name, arg, gil = decleration
            stub_file += cpdef2str(ret, name, arg, gil, docs) + '\n'*2

        elif state == "class":
            _, name, parent = decleration
            stub_file += class2str(name, parent, docs) + '\n'

            definitions_preset = False

            if parent == "Enum":
                definitions_preset = True
                for b in body:
                    stub_file += '    ' + b + '\n'
            
            else:
                for i, b in enumerate(body):
                    if len(b) > 0 and b[0] in ["def", "cdef"]:
                        definitions_preset = True
                        docs = body[i+1]
                        state, name, args, ret = b
                        stub_file += '\n' + def2str(name, args, ret, docs, indent=1) + '\n'
            
            if not definitions_preset:
                stub_file += "    ..." + '\n'

            stub_file += '\n'

    return stub_file


if __name__ == "__main__":

    with open("local/test.py", mode="r") as f:
        input_code = f.read()

    # Parse the input code using the defined grammar
    parseTree = list(python_script_parser.scan_string(input_code+"\n\n"))

    stub_file = parse_tree_to_stub_file(parseTree)
    print(stub_file)