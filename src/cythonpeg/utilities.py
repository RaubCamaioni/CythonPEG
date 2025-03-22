from pyparsing import (
    ParserElement,
    Suppress,
    Optional,
)
from functools import partial
from typing import List


def parentheses_suppress(content: ParserElement) -> ParserElement:
    return Suppress("(") + Optional(content) + Suppress(")")


def bracket_suppress(content: ParserElement) -> ParserElement:
    return Suppress("[") + Optional(content) + Suppress("]")


def curl_suppress(content: ParserElement) -> ParserElement:
    return Suppress("{") + Optional(content) + Suppress("}")


def extend_empty(tokens: List[ParserElement], n: int):
    if len(tokens) == 0:
        tokens.extend([""] * n)
    return tokens


def EmptyDefault(input: ParserElement, n: int = 1) -> ParserElement:
    """returns empty string ParserResult of size n"""
    return Optional(input).addParseAction(partial(extend_empty, n=n))
