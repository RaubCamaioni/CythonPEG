from pyparsing import (
    Suppress,
    Optional,
    Literal,
    Word,
    alphanums,
    alphas,
    Group,
    DelimitedList,
    nums,
    FollowedBy,
    Forward,
    Combine,
    QuotedString,
    infixNotation,
    opAssoc,
    OneOrMore,
    ZeroOrMore,
    LineStart,
    LineEnd,
    SkipTo,
    IndentedBlock,
    originalTextFor,
    restOfLine,
)

from cythonpeg.utilities import (
    parentheses_suppress,
    bracket_suppress,
    curl_suppress,
    EmptyDefault,
)

# LITERALS
CLASS = Literal("class")
STRUCT = Literal("struct")
DEF = Literal("def")
CPDEF = Literal("cpdef")
CDEF = Literal("cdef")
CTYPEDEF = Literal("ctypedef")
STRUCT = Literal("struct")
DATACLASS = Literal("dataclass")
ENUM = Literal("enum")
DOT = Suppress(".")
COMMA = Suppress(",")
EQUALS = Suppress("=")
COLON = Suppress(":")
PLUS = Literal("+")
MINUS = Literal("-")
MULT = Literal("*")
DIV = Literal("/")
RETURN = Literal("->")
SELF = Literal("self")
EXTERN = Literal("extern")

# OBJECTS
VARIABLE = Combine(Word("_" + alphanums + "_" + ".") + ZeroOrMore("*"))
INTEGER = Word("+-" + nums) + ~FollowedBy(".")
FLOAT = Combine(Word("+-" + nums) + "." + Word(nums))
TRUE = Literal("True")
FALSE = Literal("False")
NONE = Literal("None")
STRING = QuotedString(quoteChar="'", unquote_results=False) | QuotedString(quoteChar='"', unquote_results=False)
PRIMITIVE = FLOAT | INTEGER | TRUE | FALSE | NONE | STRING
ARRAY_SYNTAX = PRIMITIVE
OBJECT = Forward()
MEMMORYVIEW = Word(":" + nums) + (FollowedBy(Literal(",")) | FollowedBy(Literal("]")))
LIST = Group(bracket_suppress(DelimitedList(OBJECT)))("list")
TUPLE = Group(parentheses_suppress(DelimitedList(OBJECT)))("tuple")
DICT = Group(curl_suppress(DelimitedList(Group(OBJECT + Suppress(":") + OBJECT))))("dict")
SET = Group(curl_suppress(DelimitedList(OBJECT)))("set")
CLASS_CONSTRUCTOR = Group(VARIABLE + DelimitedList(parentheses_suppress(OBJECT)))("class")
NONPRIMATIVE = LIST | TUPLE | DICT | SET | CLASS_CONSTRUCTOR | VARIABLE
OBJECT << (NONPRIMATIVE | PRIMITIVE)

# EXPRESSIONS
EXPRESSION = Forward()
ATOM = OBJECT | Group(Literal("(") + EXPRESSION + Literal(")"))
EXPRESSION << infixNotation(
    ATOM,
    [
        (MULT | DIV, 2, opAssoc.LEFT),
        (PLUS | MINUS, 2, opAssoc.LEFT),
    ],
)

# IMPORTS
IMPORT = Literal("import")
CIMPORT = Literal("cimport")
FROM = Literal("from")
import_as_definition = Group(VARIABLE + EmptyDefault(Suppress(Literal("as")) + VARIABLE))
import_definition = Group(Suppress(IMPORT | CIMPORT) + Group(DelimitedList(import_as_definition)))("import")
from_import_defintion = Group(
    Suppress(FROM)
    + VARIABLE
    + Suppress(IMPORT | CIMPORT)
    + Optional(Suppress(Literal("(")))
    + Group(DelimitedList(import_as_definition))
    + Optional(Suppress(Literal(")")))
)("from")
import_and_from_import_definition = (from_import_defintion | import_definition)("import")
import_section = OneOrMore(import_and_from_import_definition)("import_section")

# RESERVED
reserved_words = CLASS | STRUCT | DEF | CPDEF | CDEF | ENUM | DATACLASS | SELF | EXTERN

# DEFAULT DEFINTIONS
default_definition = (EQUALS + EXPRESSION)("default")

# TYPING
UNSIGNED = Literal("unsigned")
type_forward = Forward()
type_bracket = bracket_suppress(DelimitedList(type_forward))
type_definition = Group(
    Suppress(EmptyDefault(UNSIGNED))
    + (VARIABLE | MEMMORYVIEW)
    + EmptyDefault(Group(type_bracket))
    + EmptyDefault(default_definition + ~Literal(")"))
)("type")
type_forward << type_definition

# return definition
python_return_definition = Suppress(RETURN) + type_definition

# alias definition
ctypedef_definition = Group(Suppress(CTYPEDEF) + ~reserved_words + type_definition + VARIABLE)("ctypedef")
ctypedef_section = OneOrMore(ctypedef_definition)("ctypedef_section")

# argument definition
python_argument_definition = Group(
    VARIABLE("name") + EmptyDefault(COLON + type_definition) + EmptyDefault(default_definition)
)("python_argument")
cython_argument_definition = Group(
    SELF | (type_definition + Suppress(EmptyDefault("*")) + VARIABLE("name") + EmptyDefault(default_definition))
)("cython_argument")

# arguments definition
arguments_definition = parentheses_suppress(DelimitedList(cython_argument_definition | python_argument_definition))(
    "arguments"
)

# recursive definitions
recursive_definitions = Forward()

# compiler directives
DIRECTIVE = LineStart() + Literal("#") + SkipTo(LineEnd()) + LineEnd()
directive_section = OneOrMore(DIRECTIVE)("directive_section")

# docstring definition
docstring = QuotedString('"""', multiline=True, escQuote='""""')

# cython enum definition
cenum_declaration = Group(Suppress(CPDEF | CDEF) + Suppress(ENUM) + VARIABLE + Suppress(":"))("cenum_declaration")
cenum_body = IndentedBlock(Group(VARIABLE + Optional(Suppress("=" + INTEGER), "") + Optional(",", "")))
cenum_definition = (cenum_declaration + cenum_body)("cenum")

# external declarations
NAMESPACE = Literal("namespace")
external_directive = Word(alphas)
external_declaration = Group(
    Suppress(CDEF + EXTERN + FROM)
    + QuotedString('"')
    + Suppress(EmptyDefault(NAMESPACE))
    + EmptyDefault(QuotedString('"'))
    + EmptyDefault(external_directive)
    + Suppress(":")
)("external_declaration")
external_body = IndentedBlock(recursive_definitions, recursive=True)
external_definition = (external_declaration + originalTextFor(external_body))("external")

# python class definition
python_class_parent = Word(alphanums + "_" + ".")
python_class_arguments = parentheses_suppress(python_class_parent)
python_class_decleration = Group(
    Suppress(CLASS) + VARIABLE + EmptyDefault(python_class_arguments) + Suppress(":"),
)("class_decleration")
python_class_body = IndentedBlock(recursive_definitions, recursive=True)
python_class_definition = (python_class_decleration + Optional(docstring, default="") + python_class_body)("class")

# python function definitions
python_function_decleration = Group(
    Suppress(DEF) + VARIABLE + Group(arguments_definition) + Optional(python_return_definition, "") + Suppress(":")
)("def_decleration")
python_function_body = IndentedBlock(recursive_definitions, recursive=True)
python_function_definition = (python_function_decleration + Optional(docstring, default="") + python_function_body)(
    "def"
)

# cython function definition
cython_function_decleration = Group(
    Suppress((CDEF | CPDEF))
    + Optional(type_definition + ~arguments_definition, default="")
    + VARIABLE
    + Group(arguments_definition)
    + Optional(VARIABLE, default="")
    + Suppress(":")
)("cdef_decleration")
cython_function_body = IndentedBlock(recursive_definitions, recursive=True)
cython_function_definition = (cython_function_decleration + Optional(docstring, default="") + cython_function_body)(
    "cdef"
)

# cython class definition
cython_class_decleration = Group(
    Suppress(CDEF + CLASS) + VARIABLE + EmptyDefault(python_class_arguments) + Suppress(":")
)("cclass_decleration")
cython_class_body = IndentedBlock(recursive_definitions, recursive=True)
cython_class_definition = (cython_class_decleration + Optional(docstring, default="") + cython_class_body)("cclass")

# cython struct definition
cython_struct_decleration = Group(Suppress(CDEF + STRUCT) + VARIABLE + Suppress(":"))
cython_struct_body = IndentedBlock(Group(type_definition + Group(DelimitedList(VARIABLE))), recursive=True)
cython_struct_definition = (cython_struct_decleration + Optional(docstring, default="") + cython_struct_body)("cstruct")

# dataclass definition
dataclass_decleration = Suppress(Literal("@") + DATACLASS + CLASS) + VARIABLE + Suppress(":")
dataclass_body = IndentedBlock(restOfLine, recursive=True)
dataclass_definition = (dataclass_decleration + Optional(docstring, default="") + dataclass_body)("dataclass")

# recursive definitions (could be individually assigned for parsing performance improvements: i.e cython_class never defined inside python_function)
definitions = (
    python_class_definition
    | python_function_definition
    | cython_class_definition
    | cython_function_definition
    | cython_struct_definition
    | restOfLine
)
recursive_definitions << definitions

# full recursive definition
cython_parser = (
    python_class_definition
    | python_function_definition
    | cython_class_definition
    | cython_function_definition
    | cython_struct_definition
    | dataclass_definition
    | import_section
    | directive_section
    | cenum_definition
    | external_definition
    | ctypedef_section
)
