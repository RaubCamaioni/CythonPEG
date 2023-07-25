from pyparsing import *
from collections.abc import Iterable
from functools import partial

def parentheses_suppress(content):
    return Suppress("(") + Optional(content) + Suppress(")")

def bracket_suppress(content):
    return Suppress("[") + Optional(content) + Suppress("]")

def curl_suppress(content):
    return Suppress("{") + Optional(content) + Suppress("}")

# literals
CLASS = Literal("class")
DEF = Literal("def")
CPDEF = Literal("cpdef")
CDEF = Literal("cdef")
STRUCT = Literal("struct")

# objects
INTEGER = Group(Word("+-" + nums) + ~FollowedBy("."))
FLOAT = Combine(Word("+-" + nums) + "." + Word(nums))
TRUE = Literal("True")
FALSE = Literal("False")
NONE = Literal("None")
STRING = QuotedString(quoteChar="'") | QuotedString(quoteChar='"')
PRIMATIVE = (FLOAT | INTEGER | TRUE | FALSE | NONE | STRING)
OBJECT = Forward()
LIST = Group(bracket_suppress(delimitedList(OBJECT)))
TUPLE = Group(parentheses_suppress(delimited_list(OBJECT)))
DICT = Group(curl_suppress(delimitedList(Group(OBJECT + Suppress(":") + OBJECT))))
SET = Group(curl_suppress(delimited_list(OBJECT)))
NONPRIMATIVE = (LIST | TUPLE | DICT | SET)
OBJECT << (PRIMATIVE | NONPRIMATIVE)

# variable and type names
VARIABLE = Word(alphanums+'_')
TYPE = (Word(alphanums+'_'+'*'+'.') | Group(parentheses_suppress(delimited_list(Word(alphanums+'_'+'*'+'.')))))

recursive_class_definition = Forward()
recursive_def_definition = Forward()
recursive_cython_def_definition = Forward()
recursive_cython_class_definition = Forward()
recursive_cython_struct_definition = Forward()

# python type hint and argument
default_argument = Suppress("=") + OBJECT
argument = Group(VARIABLE + Optional(Suppress(":") + TYPE) + Optional(default_argument)) # VARIABLE:TYPE=DEFAULT
arguments = delimitedList(argument)
return_definition = (Suppress("->") + VARIABLE)

# cython type hint and argument (simpler because cython is more structured than python)
cython_type_hint_list = bracket_suppress(delimitedList(Literal(":") | Group(VARIABLE+Optional(default_argument))))
cython_type_hint  = Group(TYPE + Optional(cython_type_hint_list))
cython_argument = Group(cython_type_hint + VARIABLE + Optional(default_argument))
cython_arguments = delimitedList(cython_argument)

# docstring definition
docstring = QuotedString('"""', multiline=True, escQuote='""""')

# python class definition
class_parent = Word(alphanums+'_'+'*'+'.')
class_arguments = Group(parentheses_suppress(delimitedList(class_parent)))
class_decleration = Group(CLASS + VARIABLE + Optional(class_arguments, default=[]) + Suppress(":"))
class_body = IndentedBlock(recursive_class_definition, recursive=True)
class_definition = class_decleration + Optional(docstring, default="") + class_body

# python function definitions
function_arguments = Group(parentheses_suppress(arguments))
function_decleration = Group(DEF + VARIABLE + function_arguments + Optional(return_definition) + Suppress(":"))
function_body = IndentedBlock(recursive_def_definition, recursive=True)
function_definition = function_decleration + Optional(docstring, default="") + function_body

# cython function definition 
cython_function_arguments = Group(parentheses_suppress(cython_arguments))
cython_function_decleration = Group(Group((CDEF | CPDEF) + Optional(cython_type_hint + ~cython_function_arguments)) + Group(VARIABLE + cython_function_arguments) + Optional(VARIABLE) + Suppress(":")) 
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

recursive_class_definition         << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_def_definition           << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_cython_def_definition    << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_cython_class_definition  << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_cython_struct_definition << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)

python_script_parser = class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition

# targeted testing
input_code = """
cpdef tuple warped_image_from_rays(float64[:, :, fut=[1, 2, 3]] image, float64 rays, float64 sample_freq=-1.0):
    pass
"""

with open("local/test.py", mode="r") as f:
    input_code = f.read()

# Parse the input code using the defined grammar
parseTree = python_script_parser.scan_string(input_code)

for branch in parseTree:
    result, startline, tokens = branch

    decleration, docs, body = result

    print(decleration)
    for b in body:
        if len(b) > 0:
            if b[0] == "def":
                print("\t", b)
