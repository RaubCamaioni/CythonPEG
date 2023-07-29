from pyparsing import *
import textwrap
from functools import partial

# helper functions
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

def EmptyDefault(input, n=1):
    return Optional(input).addParseAction(partial(extend_empty, n=n))

# literal definitions
CLASS = Literal("class")
STRUCT = Literal("struct")
DEF = Literal("def")
CPDEF = Literal("cpdef")
CDEF = Literal("cdef")
STRUCT = Literal("struct")
DATACLASS = Literal("dataclass")
DOT = Suppress('.')
COMMA = Suppress(',')
EQUALS = Suppress('=')
COLON = Suppress(':')
PLUS = Literal('+')
MINUS = Literal('-')
MULT = Literal('*')
DIV = Literal('/')
RETURN = Literal("->")

# object definitions
VARIABLE = Word("_"+alphanums+"_"+".")
INTEGER = Word("+-" + nums) + ~FollowedBy(".")
FLOAT = Combine(Word("+-" + nums) + "." + Word(nums))
TRUE = Literal("True")
FALSE = Literal("False")
NONE = Literal("None")
STRING = QuotedString(quoteChar="'") | QuotedString(quoteChar='"')
ENUM = Word(alphanums + '.')
PRIMATIVE = (FLOAT | INTEGER | TRUE | FALSE | NONE | STRING)
OBJECT = Forward()
MEMMORYVIEW = Literal(':') + (FollowedBy(Literal(",")) | FollowedBy(Literal("]")))
LIST = Group(bracket_suppress(delimitedList(OBJECT)))("list")
TUPLE = Group(parentheses_suppress(delimited_list(OBJECT)))("tuple")
DICT = Group(curl_suppress(delimitedList(Group(OBJECT + Suppress(":") + OBJECT))))("dict")
SET = Group(curl_suppress(delimited_list(OBJECT)))("set")
CLASS_CONSTRUCTOR = Group(VARIABLE+delimited_list(parentheses_suppress(OBJECT)))("class")
NONPRIMATIVE = (LIST | TUPLE | DICT | SET | ENUM | CLASS_CONSTRUCTOR )
OBJECT << (NONPRIMATIVE | PRIMATIVE)

# EXPRESSION definition
EXPRESSION = Forward()
ATOM = OBJECT | Group(Literal('(') + EXPRESSION + Literal(')'))
EXPRESSION << infixNotation(ATOM, [(MULT | DIV, 2, opAssoc.LEFT), (PLUS | MINUS, 2, opAssoc.LEFT),])

# default_definition (part of type definition)
default_definition = (EQUALS + EXPRESSION)("default")

# type definitions
type_forward = Forward()
type_bracket = bracket_suppress(delimited_list(type_forward))
type_definition = Group((VARIABLE | MEMMORYVIEW) + EmptyDefault(Group(type_bracket)) + EmptyDefault(default_definition + ~Literal(')')))("type")
type_forward << type_definition

# return definitions
python_return_definition = Suppress(RETURN) + type_definition

# argument definition
python_argument_definition = Group(VARIABLE("name") + EmptyDefault(COLON + type_definition, 1) + EmptyDefault(default_definition))("argument")
cython_argument_definition = Group(type_definition + VARIABLE("name") + EmptyDefault(default_definition))("arguments")

# arguments definition
python_arguments_definition = parentheses_suppress(delimited_list(python_argument_definition))("arguments")
cython_arguments_definition = parentheses_suppress(delimited_list(cython_argument_definition))("arguments")

# recursive definitions 
recursive_class_definition = Forward()
recursive_def_definition = Forward()
recursive_cython_def_definition = Forward()
recursive_cython_class_definition = Forward()
recursive_cython_struct_definition = Forward()

# docstring definition
docstring = QuotedString('"""', multiline=True, escQuote='""""')

# python class definition
class_parent = Word(alphanums+'_'+'*'+'.')
class_arguments = parentheses_suppress(class_parent)
class_decleration = Group(Suppress(CLASS) + VARIABLE + EmptyDefault(class_arguments) + Suppress(":"))("class_decleration")
class_body = IndentedBlock(recursive_class_definition, recursive=True)
class_definition = (class_decleration + Optional(docstring, default="") + class_body)("class")

# python function definitions
function_decleration = Group(Suppress(DEF) + VARIABLE + Group(python_arguments_definition) + Optional(python_return_definition, "") + Suppress(":"))("def_decleration")
function_body = IndentedBlock(recursive_def_definition, recursive=True)
function_definition = (function_decleration + Optional(docstring, default="") + function_body)("def")

# cython function definition 
cython_function_decleration = Group(Suppress((DEF | CDEF | CPDEF)) + Optional(type_definition + ~cython_arguments_definition, default="") + VARIABLE + Group(cython_arguments_definition) + Optional(VARIABLE, default="") + Suppress(":"))
cython_function_body = IndentedBlock(recursive_cython_def_definition, recursive=True)
cython_function_definition = (cython_function_decleration + Optional(docstring, default="") + cython_function_body)("cdef")

# cython class definition
cython_class_decleration = Group(Suppress(CDEF + CLASS) + VARIABLE +  Suppress(":"))
cython_class_body = IndentedBlock(recursive_cython_class_definition, recursive=True)
cython_class_definition = (cython_class_decleration + Optional(docstring, default="") + cython_class_body)("cclass")

# cython struct definition
cython_struct_decleration = Group(Suppress(CDEF + STRUCT) + VARIABLE + Suppress(":"))
cython_struct_body = IndentedBlock(recursive_cython_struct_definition, recursive=True)
cython_struct_definition = (cython_struct_decleration + Optional(docstring, default="") + cython_struct_body)("cstruct")

# dataclass definition
dataclass_decleration = (Suppress(Literal("@") + DATACLASS + CLASS) + VARIABLE + Suppress(":"))
dataclass_body = IndentedBlock(rest_of_line, recursive=True)
dataclass_definition = (dataclass_decleration + Optional(docstring, default="") + dataclass_body)("dataclass")

# recursive definitions
definitions = (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_class_definition         << definitions
recursive_def_definition           << definitions
recursive_cython_def_definition    << definitions
recursive_cython_class_definition  << definitions
recursive_cython_struct_definition << definitions

cython_parser = class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | dataclass_definition

def expression2str(expression):
    
    expression_string = ""
    
    if isinstance(expression, ParseResults):
             
        if expression.getName() == 'list':
            expression_string += "[" + ', '.join(expression2str(e) for e in expression) + "]"

        elif expression.getName() == 'set':
            expression_string += "{" + ', '.join(expression2str(e) for e in expression) + "}"
            
        elif expression.getName() == 'tuple':
            expression_string += "(" + ', '.join(expression2str(e) for e in expression) + ")"
            
        elif expression.getName() == 'dict':
            expression_string += "{" + ', '.join(f"{expression2str(k)} : {expression2str(v)}" for k, v in expression) + "}"
        
        elif isinstance(expression, ParseResults):
            for e in expression:
                expression_string += expression2str(e)
            
    if isinstance(expression, str):
        return expression
    
    return expression_string

def type2str(type_tree):
    type_name, type_bracket, type_default = type_tree
    
    if type_bracket:
        bracket_str = "["+", ".join(type2str(arg) for arg in type_bracket)+"]" if type_bracket else ""
    else:
        bracket_str = ""
        
    type_default_str = f'={expression2str(type_default)}' if type_default else ''
    return f"{type_name}{bracket_str}{type_default_str}"
        

def arg2str(arg):

    arg_name, arg_type, arg_default = arg

    if isinstance(arg_type, ParseResults):
        type_str = type2str(arg_type)        
    else:
        type_str = ""

    type_str = f': {type_str}' if type_str else ''
    arg_default_str = f'={expression2str(arg_default)}' if arg_default else ''

    return f'{arg_name}{type_str}{arg_default_str}'
    
def args2str(args, newlines=False):
    """convert argument format List[(name, type, default)] into a string representation."""
    joiner = ',\n    ' if newlines else ', '
    return joiner.join(arg2str(arg) for arg in args)

def def2str(name, args, ret, docs, indent=0):
    
    return_str = arg2str(ret) if ret else ""
    return_str = f" -> {return_str}" if return_str else ''
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    
    arg_str = args2str(args)
    if len(arg_str) > 100:
        arg_str = args2str(args, newlines=True)

    return textwrap.indent(f"def {name}({arg_str}){return_str}:{doc_str}\n    ...", "    "*indent)

def cythonargs2str(args, newlines=False):
    """convert argument format List[(name, type, default)] into a string representation."""

    def format_arg(t, n, d):
        type_str = type2str(t)
        default_str = f' = {d}' if d else ''
        return f'{n}: {type_str}{default_str}'

    joiner = ',\n    ' if newlines else ', '
    return joiner.join([format_arg(t, n, d) for t, n, d in args])

def cdef2str(ret, name, args, gil, docs, indent=0):
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    ret_str = type2str(ret) if ret else "" 
    ret_str = f" -> {ret_str}" if ret_str else ''
    arg_str = cythonargs2str(args)
    if len(arg_str) > 100:
        arg_str = cythonargs2str(args, newlines=True)
    return textwrap.indent(f"def {name}({arg_str}){ret_str}:{doc_str}\n    ...", "    "*indent)

def class2str(name, parent, docs):
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    return f"class {name}{f'({parent})' if parent else ''}:{doc_str}"

def recursive_body(body, indent=0):
    body_str = ""
    for b in body:
        
        if isinstance(b, ParseResults):
            body_str_indented = recursive_body(b, indent=indent+1)
            body_str += body_str_indented
            
        elif isinstance(b, str):
            body_str += b + '\n'
            
    return textwrap.indent(body_str, "    "*indent)
    
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
        
        definitionName = result.getName()
        
        if definitionName == "def":
            decleration, docs, body = result
            name, args, ret = decleration
            stub_file += def2str(name, args, ret, docs) + '\n'*2

        elif definitionName == "cdef":
            decleration, docs, body = result
            ret, name, args, gil = decleration
            stub_file += cdef2str(ret, name, args, gil, docs) + '\n'*2
        
        elif definitionName == "cclass":
            decleration, docs, body = result
            stub_file += class2str(decleration[1], "", docs) + "\n"
            for i, b in enumerate(body):
                if len(b) > 0 and b[0][0] in ["def", "cdef"]:
                    docs = body[i+1]
                    ret, name, args, gil = b
                    stub_file += '\n' + cdef2str(ret, name, args, gil, docs, indent=1) + '\n'
            stub_file += '\n'
        
        elif definitionName == "cstruct":
            decleration, docs, body = result
            stub_file += class2str(decleration[1], "", docs) + "\n"
            for b in body:
                stub_file += "    " + b + '\n'
            stub_file += "\n"
            
        elif definitionName == "class":
            decleration, docs, body = result
            name, parent = decleration
            stub_file += class2str(name, parent, docs) + '\n'

            definitions_preset = False

            if parent == "Enum":
                definitions_preset = True
                for b in body:
                    stub_file += '    ' + b + '\n'
                    
            else:
                for i, b in enumerate(body):
                    if isinstance(b, ParseResults):
                        if b.getName() == "def_decleration":
                            definitions_preset = True
                            docs = body[i+1]
                            name, args, ret = b
                            stub_file += '\n' + def2str(name, args, ret, docs, indent=1) + '\n'
            
            if not definitions_preset:
                stub_file += "    ..." + '\n'

            stub_file += '\n'
            
        elif definitionName == "dataclass":
            name, docs, body = result
            stub_file += "@dataclass" + '\n'
            stub_file += f"class {name}:" + '\n'
            stub_file += recursive_body(body, indent=1) + '\n'

    return stub_file


if __name__ == "__main__":

    with open("local/test.py", mode="r") as f:
        input_code = f.read()

    # Parse the input code using the defined grammar
    parseTree = list(cython_parser.scan_string(input_code+"\n\n"))

    stub_file = parse_tree_to_stub_file(parseTree)
    print(stub_file)