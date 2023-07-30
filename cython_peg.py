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
cython_function_decleration = Group(Suppress((DEF | CDEF | CPDEF)) + Optional(type_definition + ~cython_arguments_definition, default="") + VARIABLE + Group(cython_arguments_definition) + Optional(VARIABLE, default="") + Suppress(":"))("cdef_decleration")
cython_function_body = IndentedBlock(recursive_cython_def_definition, recursive=True)
cython_function_definition = (cython_function_decleration + Optional(docstring, default="") + cython_function_body)("cdef")

# cython class definition
cython_class_decleration = Group(Suppress(CDEF + CLASS) + VARIABLE +  EmptyDefault(class_arguments) + Suppress(":"))("cclass_decleration")
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
    
    if type_name == ":": # memory view conversion (could return np.ndarray as subsititude)
        type_name = "COLON"
    
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

def def2str(name, args, ret, docs):
    
    return_str = arg2str(ret) if ret else ""
    return_str = f" -> {return_str}" if return_str else ''
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    
    arg_str = args2str(args)
    if len(arg_str) > 100:
        arg_str = args2str(args, newlines=True)

    return f"def {name}({arg_str}){return_str}:{doc_str}\n    ...\n"

def cythonargs2str(args, newlines=False):
    """convert argument format List[(name, type, default)] into a string representation."""

    def format_arg(arg):
        if arg[0] == "self": return "self" # handle unique case cdef inside class
        t, n, d = arg
        type_str = type2str(t)
        default_str = f' = {d}' if d else ''
        return f'{n}: {type_str}{default_str}'

    joiner = ',\n    ' if newlines else ', '
    return joiner.join([format_arg(arg) for arg in args])

def cdef2str(ret, name, args, gil, docs):
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    ret_str = type2str(ret) if ret else "" 
    ret_str = f" -> {ret_str}" if ret_str else ''
    arg_str = cythonargs2str(args)
    if len(arg_str) > 100:
        arg_str = cythonargs2str(args, newlines=True)
    return f"def {name}({arg_str}){ret_str}:{doc_str}\n    ..." + '\n'

def enum2str(name, parent, docs, body):
    class_str = ""
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}" + '\n'

    for b in body:
        class_str += '    ' + b + '\n'
        
    return class_str
            
def class2str(name, parent, docs, body):
    
    class_str = ""
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}"

    definitions_preset = False
    for i, b in enumerate(body):
        
        if not isinstance(b, ParseResults):
            continue
            
        if b.getName() == "def_decleration":
            definitions_preset = True
            docs = body[i+1]
            name, args, ret = b
            class_str += '\n' + textwrap.indent(def2str(name, args, ret, docs), "    ") + '\n'
    
    if not definitions_preset:
        class_str += "    ..."

    return class_str + '\n'

def struct2str(name, parent, docs, body):
    
    class_str = ""
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}"

    for b in body:
        class_str += "    " + b + '\n'
    
    return class_str + '\n'

def cclass2str(name, parent, docs, body):
    
    class_str = ""
    doc_str = f'\n    \"""{docs}\"""' if docs else ''
    class_str += f"class {name}{f'({parent})' if parent else ''}:{doc_str}" + '\n'*2

    for i, b in enumerate(body):

        if not isinstance(b, ParseResults):
            continue
        
        parser_name = b.getName()
        
        if parser_name == "cclass_decleration":
            class_str += textwrap.indent(cclass2str(b[0], "", body[i+1], body[i+2]), "    ")
        
        if parser_name == "cdef_decleration":
            ret, name, args, gil = b
            class_str += textwrap.indent(cdef2str(ret, name, args, gil, body[i+1]), "    ") + '\n'
        
    return class_str + '\n'

def recursive_body(body, indent=0):
    body_str = ""
    for b in body:
        
        if isinstance(b, ParseResults):
            body_str_indented = recursive_body(b, indent=indent+1)
            body_str += body_str_indented
            
        elif isinstance(b, str):
            body_str += b + '\n'
            
    return textwrap.indent(body_str, "    "*indent) + '\n'
    
def parse_tree_to_stub_file(parseTree):
    
    stub_file = ""
    
    for result, _, _ in parseTree:
        
        definitionName = result.getName()
        
        # print(f"Parsing Definition: {definitionName}")
        
        if definitionName == "def":
            decleration, docs, body = result
            name, args, ret = decleration
            stub_file += def2str(name, args, ret, docs) + '\n'

        elif definitionName == "cdef":
            decleration, docs, body = result
            ret, name, args, gil = decleration
            stub_file += cdef2str(ret, name, args, gil, docs) + '\n'
        
        elif definitionName == "cclass":
            decleration, docs, body = result
            stub_file += cclass2str(decleration[0], "", docs, body) + "\n"
        
        elif definitionName == "cstruct":
            decleration, docs, body = result
            stub_file += class2str(decleration[1], "", docs, body) + "\n"
            
        elif definitionName == "class":
            decleration, docs, body = result
            name, parent = decleration
            
            if parent == "Enum":
                stub_file += enum2str(name, parent, docs, body) + '\n'
            else:
                stub_file += class2str(name, parent, docs, body) + '\n'
            
        elif definitionName == "dataclass":
            name, docs, body = result
            stub_file += "@dataclass" + '\n'
            stub_file += f"class {name}:" + '\n'
            stub_file += recursive_body(body, indent=1) + '\n'

    return stub_file

def cython2stub(file):
    with open(file, mode="r") as f:
        input_code = f.read()
    tree = list(cython_parser.scan_string(input_code+"\n\n"))
    return parse_tree_to_stub_file(tree)

def test_cython_peg():
    from pathlib import Path
    example = Path(r"./examples/example1.pyx")
    
    # generate stub file
    stub_file = cython2stub(example)
    
    # save the type file
    output_file = example.parent / (example.stem + "peg.pyi")
    with open(output_file, mode='w') as f:
        f.write(stub_file)

if __name__ == "__main__":
    
    test_cython_peg()