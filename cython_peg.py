from pyparsing import *
import textwrap
from functools import partial
from typing import Union, List, IO, Generator, Tuple
import re

# helper functions
def parentheses_suppress(content: ParserElement) -> ParserElement:
    return Suppress("(") + Optional(content) + Suppress(")")

def bracket_suppress(content: ParserElement) -> ParserElement:
    return Suppress("[") + Optional(content) + Suppress("]")

def curl_suppress(content: ParserElement) -> ParserElement:
    return Suppress("{") + Optional(content) + Suppress("}")

def extend_empty(tokens: List[ParserElement], n: int):
    if len(tokens) == 0:
        tokens.extend([""]*n)
    return tokens

def EmptyDefault(input: ParserElement, n: int=1) -> ParserElement:
    """returns empty string ParserResult of size n"""
    return Optional(input).addParseAction(partial(extend_empty, n=n))

def Cython2PythonType(cython_type: str) -> str:
    """basic type translation from cython to python"""
    
    if cython_type in ["float32", "float64", "double"]:
        return "float"
    elif cython_type in ["char", "short", "int", "long"]:
        return "int"
    elif cython_type in ["bint"]:
        return "bool"
    
    return cython_type

# indent used
INDENT = "    "

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
SELF = Literal("self")

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

# default_definition (python and cython)
default_definition = (EQUALS + EXPRESSION)("default")

# type definitions (python and cython)
type_forward = Forward()
type_bracket = bracket_suppress(delimited_list(type_forward))
type_definition = Group((VARIABLE | MEMMORYVIEW) + EmptyDefault(Group(type_bracket)) + EmptyDefault(default_definition + ~Literal(')')))("type")
type_forward << type_definition

# return definitions
python_return_definition = Suppress(RETURN) + type_definition

# argument definition
python_argument_definition = Group(VARIABLE("name") + EmptyDefault(COLON + type_definition, 1) + EmptyDefault(default_definition))("argument")
cython_argument_definition = Group((type_definition + VARIABLE("name") + EmptyDefault(default_definition)) | SELF)("arguments")

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
python_class_parent = Word(alphanums+'_'+'.')
python_class_arguments = parentheses_suppress(python_class_parent)
python_class_decleration = Group(Suppress(CLASS) + VARIABLE + EmptyDefault(python_class_arguments) + Suppress(":"))("class_decleration")
python_class_body = IndentedBlock(recursive_class_definition, recursive=True)
python_class_definition = (python_class_decleration + Optional(docstring, default="") + python_class_body)("class")

# python function definitions
python_function_decleration = Group(Suppress(DEF) + VARIABLE + Group(python_arguments_definition) + Optional(python_return_definition, "") + Suppress(":"))("def_decleration")
python_function_body = IndentedBlock(recursive_def_definition, recursive=True)
python_function_definition = (python_function_decleration + Optional(docstring, default="") + python_function_body)("def")

# cython function definition 
cython_function_decleration = Group(Suppress((DEF | CDEF | CPDEF)) + Optional(type_definition + ~cython_arguments_definition, default="") + VARIABLE + Group(cython_arguments_definition) + Optional(VARIABLE, default="") + Suppress(":"))("cdef_decleration")
cython_function_body = IndentedBlock(recursive_cython_def_definition, recursive=True)
cython_function_definition = (cython_function_decleration + Optional(docstring, default="") + cython_function_body)("cdef")

# cython class definition
cython_class_decleration = Group(Suppress(CDEF + CLASS) + VARIABLE +  EmptyDefault(python_class_arguments) + Suppress(":"))("cclass_decleration")
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

# recursive definitions (could be individually assigned for parsing performance improvements: i.e cython_class never defined inside python_function)
definitions = (python_class_definition | python_function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_class_definition         << definitions
recursive_def_definition           << definitions
recursive_cython_def_definition    << definitions
recursive_cython_class_definition  << definitions
recursive_cython_struct_definition << definitions

# full recursive definition
cython_parser = python_class_definition | python_function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | dataclass_definition

def expression2str(expression: Union[ParseResults, str]):
    """EXPRESSION parsed tree to string"""
    
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

def type2str(type_tree: ParseResults):
    """type_definition parsed tree to string"""
    type_name, type_bracket, type_default = type_tree
    
    if type_name == ":": # memory view conversion (could return np.ndarray as subsititude)
        type_name = "COLON"
    
    if type_bracket:
        bracket_str = "["+", ".join(type2str(arg) for arg in type_bracket)+"]" if type_bracket else ""
    else:
        bracket_str = ""
        
    type_default_str = f'={expression2str(type_default)}' if type_default else ''
    return f"{Cython2PythonType(type_name)}{bracket_str}{type_default_str}"
        

def arg2str(arg: ParseResults):
    """python_argument_definition parsed tree to string"""

    arg_name, arg_type, arg_default = arg

    if isinstance(arg_type, ParseResults):
        type_str = type2str(arg_type)
    else:
        type_str = ""

    type_str = f': {type_str}' if type_str else ''
    arg_default_str = f'={expression2str(arg_default)}' if arg_default else ''

    return f'{arg_name}{type_str}{arg_default_str}'
    
def args2str(args: ParseResults, newlines: bool=False):
    """python_arguments_definition parsed tree to string"""
    joiner = f',\n{INDENT}' if newlines else ', '
    return joiner.join(arg2str(arg) for arg in args)

def def2str(result: ParseResults):
    """function_definition parsed tree to string"""
    
    decleration, docs, body = result
    name, args, ret = decleration
            
    return_str = arg2str(ret) if ret else ""
    return_str = f" -> {return_str}" if return_str else ''
    doc_str = f'\n{INDENT}\"""{docs}\"""' if docs else ''
    
    arg_str = args2str(args)
    if len(arg_str) > 100:
        arg_str = args2str(args, newlines=True)

    return f"def {name}({arg_str}){return_str}:{doc_str}\n{INDENT}...\n"

def cythonargs2str(args: ParseResults, newlines: bool=False):
    """cython_arguments_definition parsed tree to string"""

    def format_arg(arg):
        if arg[0] == "self": return "self" # handle unique case cdef inside class
        t, n, d = arg
        type_str = type2str(t)
        default_str = f' = {d}' if d else ''
        return f'{n}: {type_str}{default_str}'

    joiner = f',\n{INDENT}' if newlines else ', '
    return joiner.join([format_arg(arg) for arg in args])

def cdef2str(result: ParseResults):
    """cython_function_definition parsed tree to string"""
    decleration, docs, body = result
    ret, name, args, gil = decleration
            
    doc_str = f'\n{INDENT}\"""{docs}\"""' if docs else ''
    ret_str = type2str(ret) if ret else "" 
    ret_str = f" -> {ret_str}" if ret_str else ''
    arg_str = cythonargs2str(args)
    if len(arg_str) > 100:
        arg_str = cythonargs2str(args, newlines=True)
    return f"def {name}({arg_str}){ret_str}:{doc_str}\n{INDENT}..." + '\n'

def enum2str(result: ParseResults):
    """python_class_definition parsed tree to string (enum)"""
    
    decleration, docs, body = result
    name, parent = decleration
            
    class_str = ""
    doc_str = f'\n{INDENT}\"""{docs}\"""' if docs else ''
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}" + '\n'

    for b in body:
        class_str += INDENT + b + '\n'
        
    return class_str
            
def class2str(result: ParseResults):
    """python_class_definition parsed tree to string (enum)"""
    
    decleration, docs, body = result
    name, parent = decleration
    
    if parent == "Enum":
        return enum2str(result) + '\n'
            
    class_str = ""
    doc_str = f'\n{INDENT}\"""{docs}\"""' if docs else ''
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}"

    definitions_preset = False
    for i, b in enumerate(body):
        
        if not isinstance(b, ParseResults):
            continue
            
        if b.getName() == "def_decleration":
            definitions_preset = True
            docs = body[i+1]
            name, args, ret = b
            class_str += '\n' + textwrap.indent(def2str(name, args, ret, docs), INDENT) + '\n'
    
    if not definitions_preset:
        class_str += f"{INDENT}..."

    return class_str + '\n'

def struct2str(result):
    """cython_struct_definition parsed tree to string"""
    
    decleration, docs, body = result
    parent = ""
    
    class_str = ""
    doc_str = f'\n{INDENT}\"""{docs}\"""' if docs else ''
    class_str += f"class {decleration[0]}{f'({parent})' if parent else ''}:{doc_str}\n"

    for b in body:
        class_str += INDENT + b + '\n'
    
    return class_str + '\n'

def cclass2str(result: ParseResults):
    """cython_class_definition parsed tree to string"""
    
    decleration, docs, body = result
    name, parent = decleration
                
    class_str = ""
    doc_str = f'\n{INDENT}\"""{docs}\"""' if docs else ''
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}" + '\n'*2

    for i, b in enumerate(body):

        if not isinstance(b, ParseResults):
            continue
        
        parser_name = b.getName()
        
        if parser_name == "cclass_decleration":
            result = (b, body[i+1], body[i+2])
            class_str += textwrap.indent(cclass2str(result), INDENT)
        
        if parser_name == "cdef_decleration":
            result = (b, body[i+1], body[i+2])
            class_str += textwrap.indent(cdef2str(result), INDENT) + '\n'
        
    return class_str + '\n'

def dataclass2str(result: ParseResults):
    name, docs, body = result
    dataclass_str = ""
    dataclass_str += "@dataclass" + '\n'
    dataclass_str += f"class {name}:" + '\n'
    dataclass_str += f'{INDENT}\"""{docs}\"""\n' 
    dataclass_str += textwrap.indent(recursive_body(body), INDENT) + '\n'
    return dataclass_str

def recursive_body(body: ParseResults):
    """IndentedBlock(restOfLine) parsed tree to string"""
    body_str = ""
    for b in body:
        
        if isinstance(b, ParseResults):
            body_str += textwrap.indent(recursive_body(b), INDENT)
            
        elif isinstance(b, str):
            body_str += b + '\n'
            
    return body_str + '\n'
    
def cython_string_2_stub(input_code: str) -> Tuple[str, str]:
    """tree traversal and translation of ParseResults to string representation"""
    
    # force blank lines EOF for indentblock parser
    input_code += "\n"
    tree = list(cython_parser.scan_string(input_code))
    
    # 3.8+ compatible switch
    parser = {
        "def": def2str,
        "cdef": cdef2str,
        "cclass": cclass2str,
        "cstruct": struct2str, 
        "class": class2str,
        "dataclass": dataclass2str,
    }
    
    # ParseResults -> Python Stub Element
    # TODO: remove outer reference to mutable_string
    mutable_string = list(input_code+" ")
    def parse_branch(branch: Tuple[ParseResults, int, int]):
        result, start, end = branch
    
        for i in range(start, end):
            mutable_string[i] = ""
    
        definitionName = result.getName()        
        if definitionName in parser:
           return parser[definitionName](result)
       
    # join Python Stub Elements
    stub_file = "\n".join(parse_branch(b) for b in tree)

    return stub_file, "".join(mutable_string).strip()

def cython_file_2_stub(file: IO[str]) -> Tuple[str, str]:
    with open(file, mode="r") as f:
        input_code = f.read()
    return cython_string_2_stub(input_code)

def example_testing():
    from pathlib import Path
    
    # testing file
    input_file = Path(r"./examples/example2.pyx")
    
    # read stub file
    with open(input_file, mode='r') as f:
        input_string = f.read()
    
    stub_file, unparsed_lines = cython_string_2_stub(input_string)
    
    # lines in the original file that did not match a parsing rule
    print(f"Percentage Parsed: {1 - len(unparsed_lines)/len(input_string)}")
    print(f"Unparsed Lines:")
    print(f'\"""\n{textwrap.indent(unparsed_lines, INDENT)}\n\"""')
    
    # save the type file
    with open(input_file.with_suffix(".pyi"), mode='w') as f:
        f.write(stub_file)

if __name__ == "__main__":
    example_testing()