from pyparsing import (
    ParserElement,
    Suppress,
    Optional,
)
from functools import partial
from typing import List, Callable


def partial_cython_2_python(type_str: str) -> str:
    """partial type component"""
    return type_str


def complete_cython_2_python(type_str: str) -> str:
    """complete type component"""
    return type_str


def set_type_converter_partial(func: Callable[[str], str]):
    global partial_cython_2_python
    partial_cython_2_python = func


def set_type_converter_complete(func: Callable[[str], str]):
    global complete_cython_2_python
    complete_cython_2_python = func


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
