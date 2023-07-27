argument_test = "test: test[test[test, test], test] = {1: {'a': 'b'}}"
parsedResult = argument_definition.parse_string(argument_test)

print(parsedResult)
print(parsedResult.name)
print(parsedResult.type)
print(parsedResult.default)