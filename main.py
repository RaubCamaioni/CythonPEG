from pyparsing import *
from collections.abc import Iterable
from functools import partial

# literals
CLASS = Literal("class")
DEF = Literal("def")
CPDEF = Literal("cpdef")
CDEF = Literal("cdef")
STRUCT = Literal("struct")

def lollipop(candy):
    return Suppress("(") + Optional(candy) + Suppress(")")

DOptional = partial(Optional, default=[])

recursive_class_definition = Forward()
recursive_def_definition = Forward()
recursive_cython_def_definition = Forward()
recursive_cython_class_definition = Forward()
recursive_cython_struct_definition = Forward()

# python type hint and argument
identifier = Word(alphanums+'_'+'*')
type_hint = Suppress(":") + identifier
default_argument = Suppress("=") + identifier
argument = Group(identifier + Optional(type_hint) + Optional(default_argument))
arguments = delimitedList(argument)
return_definition = (Suppress("->") + identifier)

# cython type hint and argument (simpler because cython is more structured than python)
colon_list = nested_expr("[", "]", content=delimitedList(Literal(":"), delim=","))
cython_argument = Group(Group(identifier + Optional(colon_list)) + identifier + Optional(default_argument))
cython_arguments = delimitedList(cython_argument)

# docstring definition
docstring = QuotedString('"""', multiline=True, escQuote='""""')

# python class definition
class_arguments = Group(lollipop(arguments))
class_decleration = (CLASS + identifier + DOptional(class_arguments) + Optional(return_definition) + Suppress(":"))
class_body = IndentedBlock(recursive_class_definition, recursive=True)
class_definition = Group(class_decleration + DOptional(docstring) + class_body)

# python function definitions
function_arguments = Group(lollipop(arguments))
function_decleration = Group(DEF + identifier + function_arguments + DOptional(return_definition) + Suppress(":"))
function_body = IndentedBlock(recursive_def_definition, recursive=True)
function_definition = Group(function_decleration + DOptional(docstring) + function_body)

# cython function definition 
cython_function_arguments = Group(lollipop(cython_arguments))
cython_function_decleration = Group(Group((CDEF | CPDEF)) + identifier + cython_function_arguments + DOptional(identifier) + Suppress(":"))
cython_function_body = IndentedBlock(recursive_cython_def_definition, recursive=True)
cython_function_definition = Group(cython_function_decleration + DOptional(docstring) + cython_function_body)

# split version
cython_function_arguments = Group(lollipop(cython_arguments))
# optional position very important, must be on second identifier NOT first
cython_function_decleration = Group(Group((CDEF | CPDEF) + identifier + Optional(identifier)) + cython_function_arguments + DOptional(identifier) + Suppress(":")) 
cython_function_body = IndentedBlock(recursive_cython_def_definition, recursive=True)
cython_function_definition = Group(cython_function_decleration + DOptional(docstring) + cython_function_body)

# cython class definition
cython_class_decleration = Group(Group(CDEF + CLASS) + identifier +  Suppress(":"))
cython_class_body = IndentedBlock(recursive_cython_class_definition, recursive=True)
cython_class_definition = Group(cython_class_decleration + Optional(docstring) + cython_class_body)

# cython struct definition
cython_struct_decleration = Group(Group(CDEF + STRUCT) + identifier + Suppress(":"))
cython_struct_body = IndentedBlock(recursive_cython_struct_definition, recursive=True)
cython_struct_definition = Group(cython_struct_decleration + Optional(docstring) + cython_struct_body)

recursive_class_definition         << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_def_definition           << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_cython_def_definition    << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_cython_class_definition  << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)
recursive_cython_struct_definition << (class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition | restOfLine)

python_script_parser = class_definition | function_definition | cython_function_definition | cython_class_definition | cython_struct_definition

with open("cython_test.py", mode="r") as f:
    input_code = f.read()

# targeted testing
input_code = """
"""

with open("cython_test.py", mode="r") as f:
    input_code = f.read()

# Parse the input code using the defined grammar
parseTree = python_script_parser.scan_string(input_code)

for branch in parseTree:
    result, startline, tokens = branch

    print(result[0][0])

    # decleration = result[0][0]
    # print(decleration)

# parseTree.pprint()