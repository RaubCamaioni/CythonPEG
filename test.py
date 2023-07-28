argument_test = "test: test[test=1] = {1: {'a': 'b'}}"
parsedResult = argument_definition.parse_string(argument_test)

for v in parsedResult:
    print('\t', v)
    
print(parsedResult.name)
print(parsedResult.type)
print(parsedResult.default)

import sys
sys.exit()

# def argument_definition():
#     identifier = Word(alphanums)
#     argument_forward = Forward()
#     bracketed_arguments = Group(bracket_suppress(delimited_list(argument_forward)))
#     argument = Group(OneOrMore(identifier+Optional(DOT)) + Optional(bracketed_arguments))
#     argument_forward << bracketed_arguments
#     return argument


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