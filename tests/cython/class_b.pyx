from enum import Enum

class SimpleClass:
    """simple docs"""

    class SimpleInnerClass(Enum):
        """inner enum for organizing"""
        a: int
        b: int

    def __init__(self, a):
        pass

    def simple_method(self, a: int) -> int:
        """simple method docs"""
        return 1